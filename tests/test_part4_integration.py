"""Verify Part 4 runner routing and reproducible outputs."""
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import run_all

ROOT = Path(__file__).resolve().parents[1]


class Part4IntegrationTests(unittest.TestCase):
    def test_registry_keeps_part4_out_of_other_parts(self):
        self.assertEqual(run_all.PART_TASKS["4"],
                         ("validate_inputs", "part4_analysis", "part4_figures"))
        self.assertFalse(any(name.startswith("part4_") for name in run_all.PART_TASKS["2"]))
        self.assertFalse(any(name.startswith("part4_") for name in run_all.PART_TASKS["3"]))
        self.assertLess(list(run_all.TASKS).index("part4_analysis"),
                        list(run_all.TASKS).index("part4_figures"))

    def test_runner_tasks_produce_part4_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data/raw"
            data.mkdir(parents=True)
            shutil.copyfile(ROOT / "data/raw/product_innovation.xlsx",
                            data / "product_innovation.xlsx")
            run_all.TASKS["part4_analysis"](root)
            run_all.TASKS["part4_figures"](root)
            out = root / "outputs/part4"
            daily = pd.read_csv(out / "daily_returns.csv")
            regression = pd.read_csv(out / "regression.csv").set_index("coefficient")
            returns = pd.read_csv(out / "cumulative_returns.csv").set_index("period")
            self.assertEqual(len(daily), 147)
            self.assertAlmostEqual(regression.loc["NVDA_slope", "estimate"], 1.99597492257, places=8)
            self.assertAlmostEqual(returns.loc["2024-08", "NVDL"], -0.01600943714, places=8)
            for name in ("cumulative_growth.png", "daily_risk_comparison.png",
                         "daily_return_regression.png", "monthly_return_comparison.png"):
                self.assertGreater((out / name).stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
