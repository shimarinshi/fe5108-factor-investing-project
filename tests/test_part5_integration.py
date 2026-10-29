"""Verify Part 5 runner isolation and numerical reproducibility."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import run_all

ROOT = Path(__file__).resolve().parents[1]
CSVS = ("monthly_panel.csv", "regression.csv", "replication_metrics.csv",
        "active_performance.csv", "risk_decomposition.csv", "component_active_metrics.csv")
FIGURES = ("replication_growth.png", "active_risk_decomposition.png",
           "factor_exposures.png", "active_return_vs_tracking_error.png",
           "replication_metrics_comparison.png")


class Part5IntegrationTests(unittest.TestCase):
    def test_task_routing_isolated(self):
        self.assertEqual(run_all.PART_TASKS["5"],
                         ("validate_inputs", "part5_analysis", "part5_figures"))
        for part in ("2", "3", "4"):
            self.assertFalse(any(name.startswith("part5_") for name in run_all.PART_TASKS[part]))
        self.assertEqual(run_all.PART_TASKS["4"],
                         ("validate_inputs", "part4_analysis", "part4_figures"))
        names = list(run_all.TASKS)
        self.assertEqual(names[-2:], ["part5_analysis", "part5_figures"])
        self.assertLess(names.index("part4_figures"), names.index("part5_analysis"))

    def test_generated_results_match_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data/raw"
            data.mkdir(parents=True)
            shutil.copyfile(ROOT / "data/raw/ff_msci_shared.xlsx", data / "ff_msci_shared.xlsx")
            run_all.TASKS["part5_analysis"](root)
            run_all.TASKS["part5_figures"](root)
            actual, reference = root / "outputs/part5", ROOT / "outputs/part5"
            for name in CSVS:
                with self.subTest(file=name):
                    pd.testing.assert_frame_equal(
                        pd.read_csv(actual / name), pd.read_csv(reference / name),
                        check_dtype=False, check_exact=False, rtol=1e-7, atol=1e-9)
            for name in FIGURES:
                self.assertGreater((actual / name).stat().st_size, 0)
            diag = json.loads((actual / "diagnostics.json").read_text(encoding="utf-8"))
            ref = json.loads((reference / "diagnostics.json").read_text(encoding="utf-8"))
            self.assertEqual(diag["workbook_sha256"], ref["workbook_sha256"])
            self.assertEqual(diag["months"], 343)
            self.assertAlmostEqual(diag["replication_correlation"], ref["replication_correlation"], places=7)


if __name__ == "__main__":
    unittest.main()
