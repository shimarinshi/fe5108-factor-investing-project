"""Part 3B: evaluate the December 2004 weights on their estimation sample."""
import numpy as np
import pandas as pd

from .data_loading import (
    LABELS, STRATEGIES, annualized_volatility, monthly_window, output_directory,
    portfolio_returns, read_industry_returns, read_weights_2004, save_csv,
)


def evaluate_volatility(industry, weights):
    returns = portfolio_returns(industry, weights)
    volatility = annualized_volatility(returns)
    covariance = industry.cov(ddof=1).to_numpy()
    aligned = weights.loc[industry.columns]
    alternative = np.array([np.sqrt(12 * (w @ covariance @ w)) for w in aligned.to_numpy().T])
    np.testing.assert_allclose(volatility.to_numpy(), alternative, rtol=1e-8, atol=1e-10)
    return returns, volatility


def run(root):
    industry = monthly_window(read_industry_returns(root), "1995-01", "2004-12")
    returns, volatility = evaluate_volatility(industry, read_weights_2004(root))
    if (volatility.iloc[0] > volatility.iloc[1] + 1e-8
            or volatility.iloc[1] > volatility.iloc[2] + 1e-8):
        raise ValueError("Unexpected in-sample volatility ordering.")
    summary = pd.DataFrame({
        "strategy": [LABELS[s] for s in STRATEGIES], "months": len(returns),
        "annualized_volatility": volatility,
    }).rename_axis("strategy_code")
    out = output_directory(root, "in_sample_effectiveness")
    save_csv(returns, out / "in_sample_portfolio_returns.csv")
    save_csv(summary, out / "in_sample_volatility.csv")
    print("Part 3B: in-sample volatility\n" + summary.to_string())
    return summary
