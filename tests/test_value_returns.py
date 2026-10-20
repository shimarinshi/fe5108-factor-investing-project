import unittest
import numpy as np
from src.part_2.value_portfolios.value_returns import value_weights, annualized_return, annualized_volatility

class ValueReturnsTest(unittest.TestCase):
    def test_reverse_scores_and_product_weights(self):
        weights, bp = value_weights([.01, .50, 1], [.2, .4, 1])
        np.testing.assert_allclose(bp, [1,.51,.01])
        np.testing.assert_allclose(weights[1], np.array([1,.51,.01])/1.52)
        np.testing.assert_allclose(weights[2], np.array([.2,.204,.01])/.414)
        for w in weights:
            self.assertAlmostEqual(w.sum(), 1)
            self.assertTrue((w>=0).all())

    def test_boundary_ties_not_broken_by_order(self):
        weights,_=value_weights([.01,.01,.2,.3,.4,.6], [1]*6)
        np.testing.assert_allclose(weights[0], [.5,.5,0,0,0,0])

    def test_geometric_return_not_arithmetic(self):
        self.assertAlmostEqual(annualized_return([.1,-.1]*12), .99**6-1)
        self.assertAlmostEqual(annualized_return([.01]*240), 1.01**12-1)

    def test_invalid_scores_fail(self):
        for pb in ([0,1],[.015,1],[float('nan'),1]):
            with self.assertRaises(ValueError): value_weights(pb,[1,1])

    def test_volatility_sample_arithmetic_center(self):
        # Mean = 0.02; sample variance = (0.01^2 + 0.01^2)/(3-1).
        self.assertAlmostEqual(annualized_volatility([.01,.02,.03]), .01 * 12**.5)
        self.assertAlmostEqual(annualized_volatility([.02,.02,.02]), 0)
        for values in ([], [.01], [.01,float('nan')]):
            with self.assertRaises(ValueError): annualized_volatility(values)
