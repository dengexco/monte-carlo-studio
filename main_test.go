package main

import (
	"github.com/dengexco/monte-carlo-studio/internal/simulation"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestAPI(t *testing.T) {
	m := simulation.New()
	h := handler(m, "127.0.0.1:1234", "token")
	for _, tc := range []struct {
		method, path, body, host, token string
		code                            int
	}{
		{"GET", "/", "", "127.0.0.1:1234", "", 200},
		{"GET", "/api/state", "", "evil.test", "", 403},
		{"POST", "/api/start", "{}", "127.0.0.1:1234", "", 403},
		{"POST", "/api/start", "null", "127.0.0.1:1234", "token", 400},
		{"POST", "/api/start", `{"sizes":[10],"runs":2,"seed":1,"experiment":"pi"} {}`, "127.0.0.1:1234", "token", 400},
		{"POST", "/api/start", `{"sizes":[10],"runs":2,"seed":1,"experiment":"pi"}`, "127.0.0.1:1234", "token", 200},
		{"GET", "/export.csv", "", "127.0.0.1:1234", "", 200},
		{"GET", "/assets/app.js", "", "127.0.0.1:1234", "", 200},
		{"GET", "/odev.py", "", "127.0.0.1:1234", "", 404},
	} {
		r := httptest.NewRequest(tc.method, tc.path, strings.NewReader(tc.body))
		r.Host = tc.host
		r.Header.Set("X-App-Token", tc.token)
		w := httptest.NewRecorder()
		h.ServeHTTP(w, r)
		if w.Code != tc.code {
			t.Fatalf("%s: %d %s", tc.path, w.Code, w.Body.String())
		}
		m.Wait()
		if tc.path == "/export.csv" && len(strings.Split(strings.TrimSpace(w.Body.String()), "\n")) != 3 {
			t.Fatal("missing CSV rows")
		}
	}
}
