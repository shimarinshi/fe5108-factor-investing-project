"""Part 3D: update the long-only allocation and compare a common future window."""
import pandas as pd

from .data_loading import (
    WEIGHT_TOLERANCE, monthly_window, output_directory, read_industry_returns,
    read_weights_2004, save_csv, save_json, software_versions, validate_weights,
)
from .in_sample_effectiveness import evaluate_volatility
from .portfolio_optimization import minimum_variance, sample_covariance


def run(root):
    industry = read_industry_returns(root)
    training = monthly_window(industry, "2006-01", "2015-12")
    updated, optimizer = minimum_variance(sample_covariance(training), long_only=True)
    weights = pd.DataFrame({
        "original_2004": read_weights_2004(root)["min_var_long_only"],
        "updated_2015": pd.Series(updated, index=training.columns),
    }).loc[industry.columns].rename_axis("industry")
    validate_weights(weights, weights.columns.tolist())
    evaluation = monthly_window(industry, "2016-01", "2023-07")
    returns, volatility = evaluate_volatility(evaluation, weights)
    summary = pd.DataFrame({
        "portfolio": ["Original long-only minimum variance", "Updated long-only minimum variance"],
        "estimation_period": ["Jan 1995–Dec 2004", "Jan 2006–Dec 2015"],
        "evaluation_months": len(evaluation), "annualized_volatility": volatility,
    }).rename_axis("portfolio_code")
    out = output_directory(root, "reoptimization")
    save_csv(weights, out / "long_only_weights_2004_vs_2015.csv")
    save_csv(returns, out / "reoptimization_evaluation_returns.csv")
    save_csv(summary, out / "reoptimization_volatility.csv")
    change = float(100 * (volatility["updated_2015"] - volatility["original_2004"]))
    save_json({
        "source": "data/raw/industry_portfolios.xlsx",
        "original_estimation_period": ["1995-01", "2004-12"],
        "updated_estimation_period": ["2006-01", "2015-12"],
        "updated_formation_date": "2015-12-31",
        "evaluation_period": ["2016-01", "2023-07"], "evaluation_months": len(evaluation),
        "rebalancing": "Monthly to fixed target weights", "transaction_costs": "Excluded",
        "covariance_ddof": 1, "solver": "SLSQP", "solver_ftol": 1e-12,
        "solver_maxiter": 5000, "solver_success": bool(optimizer.success),
        "solver_iterations": int(optimizer.nit), "weight_tolerance": WEIGHT_TOLERANCE,
        "volatility_change_percentage_points": change, "software_versions": software_versions(),
    }, out / "reoptimization_metadata.json")
    print(f"Part 3D: updated minus original volatility = {change:+.6f} percentage points.")
    return summary
