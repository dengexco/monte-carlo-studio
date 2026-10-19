import csv
import io
import json
import math
import secrets
import socketserver
import statistics
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


class Simulation:
    def __init__(self, engine):
        self.engine = engine
        self.lock = threading.Lock()
        self.cancel = threading.Event()
        self.state = dict(status="ready", progress=0, results={}, logs=[], settings=None, error=None)

    def snapshot(self):
        with self.lock:
            return json.loads(json.dumps(self.state))

    def start(self, settings):
        if not isinstance(settings, dict):
            raise ValueError("Settings must be a JSON object.")
        sizes = settings.get("sizes")
        runs = settings.get("runs")
        seed = settings.get("seed")
        experiment = settings.get("experiment")
        if not isinstance(sizes, list) or not 1 <= len(sizes) <= 8:
            raise ValueError("Use 1 to 8 sample sizes.")
        if any(type(n) is not int or not 1 <= n <= 1000000 for n in sizes):
            raise ValueError("Sample sizes must be integers from 1 to 1,000,000.")
        if type(runs) is not int or not 2 <= runs <= 50:
            raise ValueError("Runs must be an integer from 2 to 50.")
        if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
            raise ValueError("Seed must be an integer from 0 to 4,294,967,295.")
        if experiment not in ("both", "pi", "e"):
            raise ValueError("Select a valid experiment.")
        config = dict(sizes=sorted(set(sizes)), runs=runs, seed=seed, experiment=experiment)
        with self.lock:
            if self.state["status"] == "running":
                raise RuntimeError("A simulation is already running.")
            self.cancel = threading.Event()
            self.state = dict(status="running", progress=0, results={}, logs=[], settings=config, error=None)
        threading.Thread(target=self.work, args=(config,), daemon=True).start()

    def stop(self):
        self.cancel.set()

    def work(self, settings):
        import random
        rng = random.Random(settings["seed"])
        choices = [("pi", self.engine.pi_tahmini, math.pi), ("e", self.engine.e_tahmini, math.e)]
        choices = [x for x in choices if settings["experiment"] in ("both", x[0])]
        total = len(choices) * len(settings["sizes"]) * settings["runs"]
        count = 0
        self.engine.IPTAL = self.cancel
        try:
            for name, function, reference in choices:
                with self.lock:
                    self.state["results"][name] = []
                for n in settings["sizes"]:
                    values = []
                    for run in range(settings["runs"]):
                        if self.cancel.is_set():
                            raise InterruptedError()
                        value = function(n, rng)
                        values.append(value)
                        count += 1
                        with self.lock:
                            self.state["progress"] = count / total * 100
                            self.state["logs"].append(dict(experiment=name, n=n, run=run + 1, estimate=value))
                    if self.cancel.is_set():
                        raise InterruptedError()
                    mean = statistics.mean(values)
                    row = dict(n=n, runs=values, mean=mean, reference=reference,
                               error=abs(mean-reference), sd=statistics.stdev(values))
                    with self.lock:
                        self.state["results"][name].append(row)
            with self.lock:
                self.state["status"] = "complete"
        except InterruptedError:
            with self.lock:
                self.state["status"] = "stopped"
        except Exception as exc:
            with self.lock:
                self.state["status"] = "error"
                self.state["error"] = str(exc)


def launch(engine, port=0, open_browser=True):
    simulation = Simulation(engine)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, body, content_type="application/json", status=200, filename=None):
            if not isinstance(body, bytes):
                body = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            if filename:
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def do_GET(self):
            if not self.valid_host():
                return self.send('{"error":"Invalid host"}', status=403)
            path = urlparse(self.path).path
            if path == "/":
                html = (ROOT / "assets/index.html").read_text().replace("__TOKEN__", token)
                return self.send(html, "text/html; charset=utf-8")
            if path == "/api/state":
                return self.send(json.dumps(simulation.snapshot()))
            if path in ("/export.json", "/export.csv"):
                state = simulation.snapshot()
                if path.endswith("json"):
                    return self.send(json.dumps(state, indent=2), filename="simulation-results.json")
                buffer = io.StringIO()
                writer = csv.writer(buffer)
                writer.writerow(["experiment", "n", "run", "estimate", "mean", "reference", "absolute_error", "sample_sd"])
                for name, rows in state["results"].items():
                    for row in rows:
                        for i, value in enumerate(row["runs"], 1):
                            writer.writerow([name, row["n"], i, value, row["mean"], row["reference"], row["error"], row["sd"]])
                return self.send(buffer.getvalue(), "text/csv; charset=utf-8", filename="simulation-results.csv")
            allowed = {"/assets/app.css": "text/css", "/assets/app.js": "text/javascript",
                       "/assets/vendor/dengex-app.css": "text/css",
                       "/assets/vendor/dengex-marketing.css": "text/css",
                       "/assets/vendor/plotly.min.js": "text/javascript"}
            if path in allowed:
                return self.send((ROOT / path.lstrip("/")).read_bytes(), allowed[path])
            return self.send('{"error":"Not found"}', status=404)

        def do_POST(self):
            if not self.valid_host() or self.headers.get("X-App-Token") != token:
                return self.send('{"error":"Unauthorized request"}', status=403)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 <= length <= 8192:
                    raise ValueError("Request too large.")
                body = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/api/start":
                    simulation.start(body)
                elif self.path == "/api/stop":
                    simulation.stop()
                else:
                    return self.send('{"error":"Not found"}', status=404)
                self.send('{"ok":true}')
            except (ValueError, TypeError) as exc:
                self.send(json.dumps(dict(error=str(exc))), status=400)
            except RuntimeError as exc:
                self.send(json.dumps(dict(error=str(exc))), status=409)

    class LocalServer(ThreadingHTTPServer):
        def server_bind(self):
            socketserver.TCPServer.server_bind(self)
            self.server_name = "127.0.0.1"
            self.server_port = self.server_address[1]

    server = LocalServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Monte Carlo Studio: {url}", flush=True)
    print("Press Ctrl+C in this terminal to stop the application.", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        simulation.stop()
        server.server_close()
