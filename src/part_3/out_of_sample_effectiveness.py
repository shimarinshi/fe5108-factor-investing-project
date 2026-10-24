"""Part 3C: hold the December 2004 target weights fixed out of sample."""
from pathlib import Path

import pandas as pd

from .data_loading import (
    LABELS, STRATEGIES, OUTPUT_ROOT, monthly_window, output_directory,
    read_industry_returns, read_weights_2004, save_csv,
)
from .in_sample_effectiveness import evaluate_volatility


def run(root):
    reference = Path(root) / OUTPUT_ROOT / "in_sample_effectiveness/in_sample_volatility.csv"
    if not reference.is_file():
        raise FileNotFoundError("Run part3_in_sample_effectiveness before this task.")
    in_sample = pd.read_csv(reference, index_col="strategy_code")
    if tuple(in_sample.index) != STRATEGIES or not (in_sample["months"] == 120).all():
        raise ValueError("Invalid Part 3B volatility summary.")
    industry = monthly_window(read_industry_returns(root), "2005-01", "2023-07")
    returns, volatility = evaluate_volatility(industry, read_weights_2004(root))
    comparison = pd.DataFrame({
        "strategy": [LABELS[s] for s in STRATEGIES],
        "in_sample_volatility": in_sample["annualized_volatility"],
        "out_of_sample_volatility": volatility,
        "change_percentage_points": (volatility - in_sample["annualized_volatility"]) * 100,
    }).rename_axis("strategy_code")
    out = output_directory(root, "out_of_sample_effectiveness")
    save_csv(comparison, out / "in_sample_vs_out_of_sample_volatility.csv")
    save_csv(returns, out / "out_of_sample_portfolio_returns.csv")
    print("Part 3C: out-of-sample volatility ranking\n" + volatility.sort_values().to_string())
    return comparison
