"""Part 3A: three industry allocation rules estimated as of December 2004."""
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .data_loading import (
    WEIGHT_TOLERANCE, monthly_window, output_directory, read_industry_returns,
    save_csv, save_json, software_versions, source_hash, validate_weights,
)


def sample_covariance(returns):
    covariance = returns.cov(ddof=1).to_numpy()
    if not np.isfinite(covariance).all() or not np.allclose(covariance, covariance.T):
        raise ValueError("Invalid sample covariance matrix.")
    if np.linalg.eigvalsh(covariance).min() <= 0:
        raise ValueError("Covariance is not positive definite; investigate the input.")
    return covariance


def minimum_variance(covariance, long_only=False):
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("Covariance must be a square matrix.")
    if not np.isfinite(covariance).all() or not np.allclose(covariance, covariance.T):
        raise ValueError("Invalid covariance matrix.")
    if np.linalg.eigvalsh(covariance).min() <= 0:
        raise ValueError("Covariance must be positive definite.")
    n = len(covariance)
    ones = np.ones(n)
    if not long_only:
        solution = np.linalg.solve(covariance, ones)
        denominator = solution.sum()
        if not np.isfinite(denominator) or denominator <= 0:
            raise ValueError("Invalid minimum-variance normalization.")
        return solution / denominator, None
    annual = 12 * covariance
    result = minimize(
        fun=lambda weights: float(weights @ annual @ weights),
        x0=ones / n, jac=lambda weights: 2 * annual @ weights,
        method="SLSQP", bounds=[(0, None)] * n,
        constraints={"type": "eq", "fun": lambda weights: float(weights.sum() - 1),
                     "jac": lambda weights: ones},
        options={"ftol": 1e-12, "maxiter": 5000},
    )
    if not result.success:
        raise RuntimeError(f"Minimum-variance optimization failed: {result.message}")
    return result.x, result


def highlight_extremes(column):
    values = column.drop(index="Total")
    styles = pd.Series("", index=column.index)
    bottom = values.sort_values(kind="stable").head(5).index
    top = values.sort_values(ascending=False, kind="stable").head(5).index
    styles.loc[bottom] = "background-color: #F8D7DA; color: #842029"
    styles.loc[top] = "background-color: #D1E7DD; color: #0F5132"
    return styles


def run(root):
    training = monthly_window(read_industry_returns(root), "1995-01", "2004-12")
    covariance = sample_covariance(training)
    short, _ = minimum_variance(covariance)
    long_only, optimizer = minimum_variance(covariance, long_only=True)
    inverse = 1 / training.std(ddof=1).to_numpy()
    weights = pd.DataFrame({
        "min_var_short": short, "min_var_long_only": long_only,
        "inverse_volatility": inverse / inverse.sum(),
    }, index=training.columns).rename_axis("industry")
    validate_weights(weights, ("min_var_long_only", "inverse_volatility"))
    variances = [w @ covariance @ w for w in weights.to_numpy().T]
    if variances[0] > variances[1] + 1e-10 or variances[1] > variances[2] + 1e-10:
        raise ValueError("Unexpected in-sample variance ordering.")
    out = output_directory(root, "portfolio_optimization")
    save_csv(weights, out / "industry_weights_2004.csv")
    table = weights.copy()
    table.loc["Total"] = weights.sum()
    styled = table.style.set_uuid("industry_weights_2004").format("{:.2%}").apply(
        highlight_extremes, axis=0
    ).set_caption(
        "Industry weights as of December 31, 2004. Source: supplied Fama–French "
        "49-industry value-weighted monthly returns; estimation: January 1995–December 2004."
    )
    (out / "industry_weights_2004.html").write_text(styled.to_html(), encoding="utf-8")
    save_json({
        "source": "data/raw/industry_portfolios.xlsx",
        "source_sha256": source_hash(root, "data/raw/industry_portfolios.xlsx"),
        "worksheet": "49_Industry_Portfolios", "return_units": "Decimal",
        "return_type": "Value-weighted monthly total returns",
        "estimation_start": "1995-01", "estimation_end": "2004-12",
        "formation_date": "2004-12-31", "estimation_months": 120, "industries": 49,
        "covariance_ddof": 1, "solver": "SLSQP", "solver_ftol": 1e-12,
        "solver_maxiter": 5000, "solver_success": bool(optimizer.success),
        "solver_iterations": int(optimizer.nit), "weight_tolerance": WEIGHT_TOLERANCE,
        "highlight_ties": "Original industry order for exact ties",
        "software_versions": software_versions(),
    }, out / "optimization_metadata.json")
    print("Part 3A: 49 industries; three valid portfolios; estimation January 1995–December 2004.")
    return weights
