import unittest
import statistics
from src.part_2.active_returns.tracking_error import aligned_differences

class TrackingErrorTests(unittest.TestCase):
    def test_join_by_month_and_constant_outperformance(self):
        # Volatile strategy with a constant active return has zero tracking error.
        active = aligned_differences({'b':.5,'a':.25}, {'a':.125,'b':.375}, ['a','b'])
        self.assertEqual(active,[.125,.125])
        self.assertEqual(statistics.stdev(active),0)

    def test_incomplete_or_nonfinite_fails(self):
        for series in ({'a':.1},{'a':.1,'b':float('nan')}):
            with self.assertRaises(ValueError):
                aligned_differences(series,{'a':.1,'b':.2},['a','b'])
