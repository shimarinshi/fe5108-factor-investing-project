import unittest
import numpy as np
from src.part_2.data_validation.valuation_sanity_check import average_ranks, spearman


class RankCorrelationTests(unittest.TestCase):
    def test_average_tie_ranks(self):
        np.testing.assert_allclose(average_ranks([3, 1, 1, 2]), [4, 1.5, 1.5, 3])

    def test_expected_signs_and_undefined_cases(self):
        x = np.arange(20)
        self.assertAlmostEqual(spearman(x, x**2), 1)
        self.assertAlmostEqual(spearman(x, -x), -1)
        self.assertTrue(np.isnan(spearman(x, np.ones(20))))
        self.assertTrue(np.isnan(spearman([1, 2], [1, 2])))
