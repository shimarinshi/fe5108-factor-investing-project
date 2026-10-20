import unittest
import numpy as np
from src.return_distribution import winsorize_month


class ReturnWinsorizationTests(unittest.TestCase):
    def test_linear_percentile_bounds_and_missing_preservation(self):
        values = list(range(100)) + [float('nan')]
        clean, lo, hi = winsorize_month(values)
        self.assertAlmostEqual(lo, .99)
        self.assertAlmostEqual(hi, 98.01)
        self.assertAlmostEqual(clean[0], .99)
        self.assertAlmostEqual(clean[99], 98.01)
        np.testing.assert_array_equal(clean[1:99], np.arange(1,99))
        self.assertTrue(np.isnan(clean[-1]))
        self.assertEqual(len(clean),len(values))

    def test_ties_and_empty_month(self):
        clean,lo,hi = winsorize_month([.1]*20)
        np.testing.assert_array_equal(clean, [.1]*20)
        self.assertEqual(lo,hi)
        clean,lo,hi = winsorize_month([float('nan')])
        self.assertTrue(np.isnan(clean).all())
        self.assertTrue(np.isnan(lo) and np.isnan(hi))
