package simulation

import (
	"context"
	"encoding/json"
	"errors"
	"math"
	"math/rand/v2"
	"sort"
	"sync"
)

type Config struct {
	Sizes      []int   `json:"sizes"`
	Runs       int     `json:"runs"`
	Seed       *uint32 `json:"seed"`
	Experiment string  `json:"experiment"`
}
type Row struct {
	N         int       `json:"n"`
	Runs      []float64 `json:"runs"`
	Mean      float64   `json:"mean"`
	Reference float64   `json:"reference"`
	Error     float64   `json:"error"`
	SD        float64   `json:"sd"`
}
type Log struct {
	Experiment string  `json:"experiment"`
	N          int     `json:"n"`
	Run        int     `json:"run"`
	Estimate   float64 `json:"estimate"`
}
type State struct {
	Status   string           `json:"status"`
	Progress float64          `json:"progress"`
	Results  map[string][]Row `json:"results"`
	Logs     []Log            `json:"logs"`
	Settings *Config          `json:"settings"`
	Error    *string          `json:"error"`
	Engine   string           `json:"engine"`
}
type Manager struct {
	mu     sync.Mutex
	state  State
	cancel context.CancelFunc
	done   chan struct{}
}

var ErrBusy = errors.New("A simulation is already running.")

func New() *Manager {
	return &Manager{state: State{Status: "ready", Results: map[string][]Row{}, Logs: []Log{}, Engine: "Go · PCG"}}
}
func (c *Config) Validate() error {
	if len(c.Sizes) < 1 || len(c.Sizes) > 8 {
		return errors.New("Use 1 to 8 sample sizes.")
	}
	for _, n := range c.Sizes {
		if n < 1 || n > 1000000 {
			return errors.New("Sample sizes must be integers from 1 to 1,000,000.")
		}
	}
	if c.Runs < 2 || c.Runs > 50 {
		return errors.New("Runs must be an integer from 2 to 50.")
	}
	if c.Seed == nil {
		return errors.New("Seed is required (0 to 4,294,967,295).")
	}
	if c.Experiment != "both" && c.Experiment != "pi" && c.Experiment != "e" {
		return errors.New("Select a valid experiment.")
	}
	return nil
}
func (m *Manager) Snapshot() State {
	m.mu.Lock()
	defer m.mu.Unlock()
	b, _ := json.Marshal(m.state)
	var s State
	_ = json.Unmarshal(b, &s)
	return s
}
func (m *Manager) Start(c Config) error {
	if err := c.Validate(); err != nil {
		return err
	}
	c.Sizes = append([]int(nil), c.Sizes...)
	sort.Ints(c.Sizes)
	unique := c.Sizes[:0]
	for _, n := range c.Sizes {
		if len(unique) == 0 || unique[len(unique)-1] != n {
			unique = append(unique, n)
		}
	}
	c.Sizes = unique
	seed := *c.Seed
	c.Seed = &seed
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.state.Status == "running" {
		return ErrBusy
	}
	ctx, cancel := context.WithCancel(context.Background())
	m.cancel = cancel
	m.done = make(chan struct{})
	m.state = State{Status: "running", Results: map[string][]Row{}, Logs: []Log{}, Settings: &c, Engine: "Go · PCG"}
	go m.work(ctx, c, m.done)
	return nil
}
func (m *Manager) Stop() {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.cancel != nil {
		m.cancel()
	}
}
func (m *Manager) Wait() {
	m.mu.Lock()
	done := m.done
	m.mu.Unlock()
	if done != nil {
		<-done
	}
}
func Estimate(ctx context.Context, name string, n int, random func() float64) (float64, error) {
	if n < 1 || (name != "pi" && name != "e") {
		return 0, errors.New("Invalid experiment")
	}
	count := 0
	for i := 0; i < n; i++ {
		if i%256 == 0 {
			if err := ctx.Err(); err != nil {
				return 0, err
			}
		}
		if name == "pi" {
			x, y := random(), random()
			if x*x+y*y <= 1 {
				count++
			}
		} else {
			sum := 0.0
			for sum <= 1 {
				sum += random()
				count++
				if count%256 == 0 {
					if err := ctx.Err(); err != nil {
						return 0, err
					}
				}
			}
		}
	}
	value := float64(count) / float64(n)
	if name == "pi" {
		value *= 4
	}
	return value, nil
}
func summarize(n int, values []float64, reference float64) Row {
	mean := 0.0
	for _, v := range values {
		mean += v
	}
	mean /= float64(len(values))
	variance := 0.0
	for _, v := range values {
		variance += (v - mean) * (v - mean)
	}
	return Row{n, values, mean, reference, math.Abs(mean - reference), math.Sqrt(variance / float64(len(values)-1))}
}
func (m *Manager) work(ctx context.Context, c Config, done chan struct{}) {
	defer close(done)
	status := "complete"
	defer func() { m.mu.Lock(); m.state.Status = status; m.mu.Unlock() }()
	names := []string{"pi", "e"}
	if c.Experiment != "both" {
		names = []string{c.Experiment}
	}
	total := len(names) * len(c.Sizes) * c.Runs
	count := 0
	for _, name := range names {
		for _, n := range c.Sizes {
			values := make([]float64, 0, c.Runs)
			for run := 0; run < c.Runs; run++ {
				tag := uint64(1)
				if name == "e" {
					tag = 2
				}
				rng := rand.New(rand.NewPCG(uint64(*c.Seed), uint64(n)<<32|uint64(run)<<8|tag))
				value, err := Estimate(ctx, name, n, rng.Float64)
				if err != nil {
					status = "stopped"
					return
				}
				values = append(values, value)
				count++
				m.mu.Lock()
				m.state.Logs = append(m.state.Logs, Log{name, n, run + 1, value})
				m.state.Progress = float64(count) * 100 / float64(total)
				m.mu.Unlock()
			}
			if ctx.Err() != nil {
				status = "stopped"
				return
			}
			reference := math.Pi
			if name == "e" {
				reference = math.E
			}
			row := summarize(n, values, reference)
			m.mu.Lock()
			m.state.Results[name] = append(m.state.Results[name], row)
			m.mu.Unlock()
		}
	}
}
