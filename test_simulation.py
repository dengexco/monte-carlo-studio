import random
import threading
import time
import unittest
import odev
from web_app import Simulation


class SimulationTests(unittest.TestCase):
    def tearDown(self):
        odev.IPTAL = None

    def wait_for(self, simulation):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            state = simulation.snapshot()
            if state['status'] != 'running':
                return state
            time.sleep(.01)
        self.fail('Simulation timed out')

    def test_default_results(self):
        sim = Simulation(odev)
        sim.start(dict(sizes=[10,100,1000,10000], runs=5, seed=20261019, experiment='both'))
        state = self.wait_for(sim)
        self.assertEqual(state['status'], 'complete')
        self.assertEqual(len(state['logs']), 40)
        self.assertAlmostEqual(state['results']['pi'][-1]['mean'], 3.13968)
        self.assertAlmostEqual(state['results']['e'][-1]['mean'], 2.71792)
        self.assertEqual(state['results']['pi'][0]['runs'], [3.6,3.2,2.4,3.2,2.8])

    def test_e_strict_threshold(self):
        class Sequence:
            def __init__(self): self.values=iter([.5,.5,.25])
            def random(self): return next(self.values)
        self.assertEqual(odev.e_tahmini(1,Sequence()),3)

    def test_pi_boundary(self):
        class Sequence:
            def __init__(self): self.values=iter([0,0,.8,.8])
            def random(self): return next(self.values)
        self.assertEqual(odev.pi_tahmini(2,Sequence()),2)

    def test_settings_validation(self):
        sim=Simulation(odev)
        base=dict(sizes=[10],runs=5,seed=1,experiment='both')
        for key,value in [('runs',1),('runs',51),('sizes',[0]),('sizes',[True]),('seed',-1),('experiment','unknown')]:
            with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                sim.start({**base,key:value})

    def test_cancellation(self):
        sim=Simulation(odev)
        sim.start(dict(sizes=[1000000],runs=50,seed=1,experiment='both'))
        sim.stop()
        self.assertEqual(self.wait_for(sim)['status'],'stopped')

    def test_custom_runs_and_seed(self):
        sim=Simulation(odev)
        config=dict(sizes=[20,200],runs=3,seed=7,experiment='e')
        sim.start(config)
        first=self.wait_for(sim)
        sim.start(config)
        second=self.wait_for(sim)
        self.assertEqual(first['results'],second['results'])
        self.assertEqual(len(first['logs']),6)
        self.assertEqual(set(first['results']),{'e'})


if __name__ == '__main__':
    unittest.main()
