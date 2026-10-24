"""Analytical checks and end-to-end reproduction of Part 3 reference CSVs."""
import contextlib
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np
import pandas as pd

from src.part_3.data_loading import (
    cumulative_return, levels_to_returns, monthly_window, portfolio_returns, validate_weights,
)
from src.part_3.portfolio_optimization import minimum_variance, run as optimization
from src.part_3.in_sample_effectiveness import run as in_sample
from src.part_3.out_of_sample_effectiveness import run as out_of_sample
from src.part_3.reoptimization import run as reoptimization
from src.part_3.performance_expectations import run as performance, wealth_from_returns

ROOT = Path(__file__).resolve().parents[1]


class IndustryPortfolioTests(unittest.TestCase):
    def test_diagonal_covariance_has_known_minimum_variance_solution(self):
        covariance = np.diag([1.0, 4.0])
        for long_only in (False, True):
            weights, _ = minimum_variance(covariance, long_only=long_only)
            np.testing.assert_allclose(weights, [0.8, 0.2], atol=1e-6)

    def test_long_only_constraint_changes_an_unconstrained_short(self):
        covariance = np.array([[1.0, 2.0], [2.0, 9.0]])
        short, _ = minimum_variance(covariance)
        long_only, _ = minimum_variance(covariance, long_only=True)
        self.assertLess(short[1], 0)
        np.testing.assert_allclose(long_only, [1.0, 0.0], atol=1e-6)
        self.assertLessEqual(short @ covariance @ short, long_only @ covariance @ long_only)

    def test_singular_covariance_is_rejected(self):
        with self.assertRaises(ValueError):
            minimum_variance(np.ones((2, 2)))

    def test_monthly_window_rejects_missing_or_duplicate_months(self):
        frame = pd.DataFrame({"a": [0.01, 0.02]}, index=pd.PeriodIndex(["2005-01", "2005-03"], freq="M"))
        with self.assertRaises(ValueError):
            monthly_window(frame, "2005-01", "2005-03")
        frame.index = pd.PeriodIndex(["2005-01", "2005-01"], freq="M")
        with self.assertRaises(ValueError):
            monthly_window(frame, "2005-01", "2005-01")

    def test_industry_labels_control_weight_alignment(self):
        returns = pd.DataFrame({"b": [0.20], "a": [0.10]})
        weights = pd.DataFrame({"p": [0.75, 0.25]}, index=["a", "b"])
        self.assertAlmostEqual(portfolio_returns(returns, weights).iloc[0, 0], 0.125)
        with self.assertRaises(ValueError):
            portfolio_returns(returns.rename(columns={"b": "c"}), weights)

    def test_long_only_negative_weights_are_rejected(self):
        weights = pd.DataFrame({"p": [1.1, -0.1]}, index=["a", "b"])
        with self.assertRaises(ValueError):
            validate_weights(weights, ["p"])

    def test_msci_return_requires_the_preceding_level(self):
        levels = pd.Series([100.0, 110.0, 99.0], index=pd.period_range("2004-12", "2005-02", freq="M"))
        result = levels_to_returns(levels, "2005-01", "2005-02")
        np.testing.assert_allclose(result, [0.10, -0.10])
        with self.assertRaises(ValueError):
            levels_to_returns(levels.iloc[1:], "2005-01", "2005-02")

    def test_crisis_returns_are_compounded_not_added(self):
        self.assertAlmostEqual(cumulative_return(pd.DataFrame({"p": [-0.1, -0.2]}))["p"], -0.28)
        with self.assertRaises(ValueError):
            cumulative_return(pd.DataFrame({"p": [np.nan]}))

    def test_wealth_includes_one_initial_dollar(self):
        returns = pd.DataFrame({"p": [0.10, -0.10]}, index=pd.period_range("2005-01", "2005-02", freq="M"))
        wealth = wealth_from_returns(returns)
        self.assertEqual(wealth.index[0], pd.Period("2004-12", freq="M"))
        np.testing.assert_allclose(wealth["p"], [1.0, 1.1, 0.99])

    def test_standalone_consumer_reports_missing_upstream_weights(self):
        with tempfile.TemporaryDirectory() as directory:
            from src.part_3.data_loading import read_weights_2004
            with self.assertRaisesRegex(FileNotFoundError, "part3_portfolio_optimization"):
                read_weights_2004(directory)


class IndustryReproductionTests(unittest.TestCase):
    def test_all_sections_match_reference_csvs_and_repeat_stably(self):
        references = sorted((ROOT / "outputs/part_3").rglob("*.csv"))
        self.assertEqual(len(references), 13, "Include all 13 Part 3 reference CSVs in the commit.")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/raw").mkdir(parents=True)
            for name in ("industry_portfolios.xlsx", "ff_msci_shared.xlsx"):
                shutil.copy2(ROOT / "data/raw" / name, root / "data/raw" / name)
            with contextlib.redirect_stdout(io.StringIO()):
                for task in (optimization, in_sample, out_of_sample, reoptimization, performance):
                    task(root)
            for reference in references:
                relative = reference.relative_to(ROOT)
                actual = pd.read_csv(root / relative, float_precision="round_trip")
                expected = pd.read_csv(reference, float_precision="round_trip")
                pd.testing.assert_frame_equal(actual, expected, check_exact=False, rtol=1e-7, atol=1e-9)
            before = {
                path.relative_to(root): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (root / "outputs/part_3").rglob("*") if path.is_file()
            }
            self.assertEqual(len(before), 18)
            with contextlib.redirect_stdout(io.StringIO()):
                optimization(root)
                performance(root)
            after = {relative: hashlib.sha256((root / relative).read_bytes()).hexdigest() for relative in before}
            self.assertEqual(before, after, "Repeated generation changed the Part 3 outputs.")


if __name__ == "__main__":
    unittest.main()
