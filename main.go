package main

import (
	"context"
	"crypto/rand"
	"embed"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"github.com/dengexco/monte-carlo-studio/internal/simulation"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"runtime"
	"strconv"
	"strings"
	"syscall"
	"time"
)

//go:embed assets
var assets embed.FS

func respond(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
func handler(m *simulation.Manager, host, token string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Cache-Control", "no-store")
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("X-Frame-Options", "DENY")
		fail := func(status int, message string) { respond(w, status, map[string]string{"error": message}) }
		if r.Host != host {
			fail(403, "Invalid host")
			return
		}
		if r.Method == "POST" {
			if r.Header.Get("X-App-Token") != token {
				fail(403, "Unauthorized request")
				return
			}
			switch r.URL.Path {
			case "/api/start":
				var c simulation.Config
				decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, 8192))
				decoder.DisallowUnknownFields()
				if err := decoder.Decode(&c); err != nil {
					fail(400, "Invalid settings JSON: "+err.Error())
					return
				}
				if decoder.Decode(new(any)) != io.EOF {
					fail(400, "Expected a single JSON object")
					return
				}
				if err := m.Start(c); err != nil {
					code := 400
					if errors.Is(err, simulation.ErrBusy) {
						code = 409
					}
					fail(code, err.Error())
					return
				}
			case "/api/stop":
				m.Stop()
			default:
				fail(404, "Not found")
				return
			}
			respond(w, 200, map[string]bool{"ok": true})
			return
		}
		if r.Method != "GET" {
			w.Header().Set("Allow", "GET, POST")
			fail(405, "Method not allowed")
			return
		}
		switch r.URL.Path {
		case "/api/state":
			respond(w, 200, m.Snapshot())
		case "/export.json":
			w.Header().Set("Content-Disposition", `attachment; filename="simulation-results.json"`)
			respond(w, 200, m.Snapshot())
		case "/export.csv":
			w.Header().Set("Content-Type", "text/csv; charset=utf-8")
			w.Header().Set("Content-Disposition", `attachment; filename="simulation-results.csv"`)
			writer := csv.NewWriter(w)
			defer writer.Flush()
			_ = writer.Write([]string{"experiment", "n", "run", "estimate", "mean", "reference", "absolute_error", "sample_sd"})
			s := m.Snapshot()
			f := func(v float64) string { return strconv.FormatFloat(v, 'g', -1, 64) }
			for _, name := range []string{"pi", "e"} {
				for _, row := range s.Results[name] {
					for i, v := range row.Runs {
						_ = writer.Write([]string{name, strconv.Itoa(row.N), strconv.Itoa(i + 1), f(v), f(row.Mean), f(row.Reference), f(row.Error), f(row.SD)})
					}
				}
			}
		case "/":
			b, _ := assets.ReadFile("assets/index.html")
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
			_, _ = io.WriteString(w, strings.ReplaceAll(string(b), "__TOKEN__", token))
		default:
			allowed := map[string]string{"/assets/app.css": "text/css", "/assets/app.js": "text/javascript", "/assets/vendor/dengex-app.css": "text/css", "/assets/vendor/dengex-marketing.css": "text/css", "/assets/vendor/plotly.min.js": "text/javascript"}
			contentType, ok := allowed[r.URL.Path]
			if !ok {
				fail(404, "Not found")
				return
			}
			b, err := assets.ReadFile(strings.TrimPrefix(r.URL.Path, "/"))
			if err != nil {
				fail(500, "Asset unavailable")
				return
			}
			w.Header().Set("Content-Type", contentType)
			_, _ = w.Write(b)
		}
	})
}
func openBrowser(url string) {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "darwin":
		cmd = exec.Command("open", url)
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}
	if err := cmd.Run(); err != nil {
		log.Printf("Open the URL manually: %v", err)
	}
}
func main() {
	port := flag.Int("port", 0, "Local port (0 chooses a free port)")
	noBrowser := flag.Bool("no-browser", false, "Do not open a browser")
	batch := flag.Bool("no-gui", false, "Run default experiments and export JSON")
	flag.Parse()
	m := simulation.New()
	if *batch {
		seed := uint32(20261019)
		_ = m.Start(simulation.Config{Sizes: []int{10, 100, 1000, 10000}, Runs: 5, Seed: &seed, Experiment: "both"})
		m.Wait()
		s := m.Snapshot()
		for _, l := range s.Logs {
			fmt.Printf("%s n=%d run=%d estimate=%.6f\n", l.Experiment, l.N, l.Run, l.Estimate)
		}
		b, err := json.MarshalIndent(s, "", "  ")
		if err == nil {
			err = os.MkdirAll("odev_ciktilari", 0755)
		}
		if err == nil {
			err = os.WriteFile("odev_ciktilari/results.json", b, 0644)
		}
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println("Saved odev_ciktilari/results.json")
		return
	}
	if *port < 0 || *port > 65535 {
		log.Fatal("Port must be between 0 and 65535")
	}
	listener, err := net.Listen("tcp", fmt.Sprintf("127.0.0.1:%d", *port))
	if err != nil {
		log.Fatal(err)
	}
	secret := make([]byte, 32)
	if _, err = rand.Read(secret); err != nil {
		log.Fatal(err)
	}
	server := &http.Server{Handler: handler(m, listener.Addr().String(), hex.EncodeToString(secret)), ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second, WriteTimeout: 30 * time.Second, IdleTimeout: 60 * time.Second}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	go func() {
		<-ctx.Done()
		m.Stop()
		shutdown, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(shutdown)
	}()
	url := "http://" + listener.Addr().String() + "/"
	fmt.Println("Monte Carlo Studio · Go engine:", url)
	fmt.Println("Press Ctrl+C to stop.")
	if !*noBrowser {
		go openBrowser(url)
	}
	if err = server.Serve(listener); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatal(err)
	}
	m.Stop()
	m.Wait()
}
