package simulation

import (
	"context"
	"math"
	"reflect"
	"testing"
)

func config() Config {
	seed := uint32(20261019)
	return Config{[]int{10, 100, 1000, 10000}, 5, &seed, "both"}
}
func TestExperiments(t *testing.T) {
	m := New()
	if err := m.Start(config()); err != nil {
		t.Fatal(err)
	}
	m.Wait()
	s := m.Snapshot()
	if s.Status != "complete" || len(s.Logs) != 40 || s.Progress != 100 {
		t.Fatal(s)
	}
	if math.Abs(s.Results["pi"][3].Mean-math.Pi) > .1 || math.Abs(s.Results["e"][3].Mean-math.E) > .1 {
		t.Fatal("estimates out of bounds")
	}
	_ = m.Start(config())
	m.Wait()
	if !reflect.DeepEqual(s.Results, m.Snapshot().Results) {
		t.Fatal("not reproducible")
	}
	c := config()
	c.Experiment = "e"
	_ = m.Start(c)
	m.Wait()
	if !reflect.DeepEqual(s.Results["e"], m.Snapshot().Results["e"]) {
		t.Fatal("experiment streams changed")
	}
}
func TestBoundaries(t *testing.T) {
	v := []float64{.5, .5, .25}
	i := 0
	got, err := Estimate(context.Background(), "e", 1, func() float64 { x := v[i]; i++; return x })
	if err != nil || got != 3 {
		t.Fatal(got, err)
	}
	v = []float64{0, 1, .8, .8}
	i = 0
	got, err = Estimate(context.Background(), "pi", 2, func() float64 { x := v[i]; i++; return x })
	if err != nil || got != 2 {
		t.Fatal(got, err)
	}
}
func TestStopAndBusy(t *testing.T) {
	m := New()
	c := config()
	c.Sizes = []int{1000000}
	c.Runs = 50
	_ = m.Start(c)
	if m.Start(c) != ErrBusy {
		t.Fatal("expected busy")
	}
	m.Stop()
	m.Wait()
	if m.Snapshot().Status != "stopped" {
		t.Fatal("not stopped")
	}
}
func TestValidation(t *testing.T) {
	for _, mutate := range []func(*Config){func(c *Config) { c.Sizes = []int{0} }, func(c *Config) { c.Runs = 1 }, func(c *Config) { c.Seed = nil }, func(c *Config) { c.Experiment = "unknown" }} {
		c := config()
		mutate(&c)
		if c.Validate() == nil {
			t.Fatal("accepted invalid config")
		}
	}
}
func TestSummary(t *testing.T) {
	r := summarize(10, []float64{2, 3, 4}, math.Pi)
	if r.Mean != 3 || r.SD != 1 || math.Abs(r.Error-(math.Pi-3)) > 1e-14 {
		t.Fatal(r)
	}
}
