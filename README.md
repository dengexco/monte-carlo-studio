# Monte Carlo Studio

Go-powered local Monte Carlo application for estimating π and Euler’s number e. Includes UI TripleD components and custom dashboard styling, configurable experiments, interactive charts, run logs, and CSV/JSON exports. UI assets are embedded in the executable; the Go runtime has no third-party package dependencies.

## Build and run

Requires Go 1.24+ to build:

```sh
go build -trimpath -o bin/monte-carlo-studio .
./bin/monte-carlo-studio
```

Optional Python launcher (standard library only): `python3 odev.py`. Python only launches the compiled Go executable. On Windows build to `bin/monte-carlo-studio.exe`.

Options: `--port 8765`, `--no-browser`, `--no-gui` (default batch results as JSON). The browser automatically starts the default 40 runs. Stop the server with Ctrl+C.

```sh
go test -race ./...
go vet ./...
```

See [read.md](read.md) for detailed Turkish methodology, code explanations, and migration notes. Go uses PCG streams, so results differ from the previous Python implementation even with the same seed. Existing reports are not automatically regenerated.

Third-party styling and Plotly sources: [SOURCES.md](assets/vendor/SOURCES.md). Prepared with AI assistance.

## UI build

React components adapted from UI TripleD (MIT): Native Tabs and Native Magnetic. To rebuild them: `npm ci && npm run build`, then rebuild the Go executable. The prebuilt bundle is included; Node.js is not required to run the application.
