import unittest
import numpy as np
from src.part_2.broad_market.market_portfolio import portfolio

class MarketPortfolioTests(unittest.TestCase):
    def test_weighting_and_return(self):
        w,r=portfolio([.9,.6,.3],[.1,-.2,.3])
        np.testing.assert_allclose(w,[.5,1/3,1/6])
        self.assertAlmostEqual(r,1/30)
        scaled,r_scaled=portfolio([90,60,30],[.1,-.2,.3])
        np.testing.assert_allclose(w,scaled)
        self.assertAlmostEqual(r,r_scaled)
    def test_missing_return_not_silently_dropped(self):
        with self.assertRaises(ValueError): portfolio([.5,.5],[.1,float('nan')])
        with self.assertRaises(ValueError): portfolio([-.1,.5],[.1,.2])
