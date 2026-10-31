"""Rule-level tests; run python -m unittest discover -s tests -v"""
import unittest
import importlib.util
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('peers',ROOT/'src/02_build_peer_benchmarks.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class TestPeerRules(unittest.TestCase):
    def test_haversine_same_location(self):
        self.assertAlmostEqual(float(mod.haversine_km(25.2048,55.2708,25.2048,55.2708)),0.,places=7)
    def test_haversine_approximately_one_degree(self):
        km=float(mod.haversine_km(0,0,1,0));self.assertTrue(110<km<112)
    def test_chord_increases_with_radius(self):
        self.assertTrue(0<mod.chord(2)<mod.chord(5))
    def test_peer_threshold(self):
        self.assertEqual(mod.MIN_PEERS,10)

if __name__=='__main__':unittest.main()
