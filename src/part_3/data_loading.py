"""Canonical Part 3 inputs, validation, and deterministic result writers."""
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd

STRATEGIES = ("min_var_short", "min_var_long_only", "inverse_volatility")
LABELS = {
    "min_var_short": "Minimum variance (shorting allowed)",
    "min_var_long_only": "Minimum variance (long only)",
    "inverse_volatility": "Inverse volatility",
}
WEIGHT_TOLERANCE = 1e-8
OUTPUT_ROOT = Path("outputs/part_3")
CRISIS_WINDOWS = {
    "Global Financial Crisis": ("2008-09", "2009-02", 6),
    "COVID sell-off": ("2020-02", "2020-03", 2),
}


def monthly_window(frame, start, end):
    """Reject duplicate, missing, or invalid observations instead of dropping them."""
    if not isinstance(frame.index, pd.PeriodIndex) or frame.index.freqstr != "M":
        raise ValueError("Expected a monthly PeriodIndex.")
    if not frame.index.is_unique:
        raise ValueError("Duplicate months.")
    selected = frame.sort_index().loc[start:end].copy()
    expected = pd.period_range(start, end, freq="M")
    if not selected.index.equals(expected):
        raise ValueError(f"Incomplete monthly window: {start} to {end}.")
    if not np.isfinite(selected.to_numpy(dtype=float)).all():
        raise ValueError("Missing or nonfinite monthly observations.")
    return selected


def read_industry_returns(root):
    path = Path(root) / "data/raw/industry_portfolios.xlsx"
    if not path.is_file():
        raise FileNotFoundError(f"Missing canonical input: {path}")
    heading = pd.read_excel(path, sheet_name="49_Industry_Portfolios", header=None, nrows=11)
    if "Value Weighted Returns -- Monthly" not in str(heading.iloc[10, 0]):
        raise ValueError("Expected the value-weighted monthly industry block.")
    raw = pd.read_excel(path, sheet_name="49_Industry_Portfolios", header=11)
    raw = raw.rename(columns={raw.columns[0]: "month"})
    raw.columns = raw.columns.str.strip()
    codes = pd.to_numeric(raw.pop("month"), errors="raise")
    if not np.equal(codes, np.floor(codes)).all():
        raise ValueError("Industry month codes must be integral YYYYMM values.")
    result = raw.apply(pd.to_numeric, errors="raise").replace([-99.99, -999], np.nan) / 100
    result.index = pd.PeriodIndex(
        pd.to_datetime(codes.astype("int64").astype(str), format="%Y%m"),
        freq="M", name="month",
    )
    if result.shape[1] != 49 or not result.columns.is_unique:
        raise ValueError("Expected 49 uniquely named industries.")
    return monthly_window(result, "1995-01", "2023-07")


def levels_to_returns(levels, start, end):
    preceding = str(pd.Period(start, freq="M") - 1)
    levels = monthly_window(levels, preceding, end)
    if (levels <= 0).any():
        raise ValueError("Index levels must be positive.")
    return levels.pct_change(fill_method=None).iloc[1:].rename("msci_usa")


def read_msci_levels(root, start="2004-12", end="2023-07"):
    path = Path(root) / "data/raw/ff_msci_shared.xlsx"
    if not path.is_file():
        raise FileNotFoundError(f"Missing canonical input: {path}")
    sheet = "MSCI - factor totret index"
    metadata = pd.read_excel(path, sheet_name=sheet, header=None, nrows=4, usecols=[0, 1])
    if metadata.iloc[2, 1] != "Gross" or metadata.iloc[3, 1] != "USD":
        raise ValueError("Expected MSCI gross total-return index levels in USD.")
    raw = pd.read_excel(path, sheet_name=sheet, header=6, usecols=[0, 1])
    column = "USA Standard (Large+Mid Cap)"
    if list(raw.columns) != ["Date", column]:
        raise ValueError("Unexpected MSCI USA index column.")
    dates = pd.to_datetime(raw["Date"], format="%b %d, %Y", errors="coerce")
    valid = dates.notna()
    values = pd.to_numeric(
        raw.loc[valid, column].astype(str).str.replace(",", "", regex=False), errors="raise"
    )
    result = pd.Series(values.to_numpy(), index=pd.PeriodIndex(
        dates.loc[valid], freq="M", name="month"
    ), name="msci_usa_level")
    result = monthly_window(result, start, end)
    if (result <= 0).any():
        raise ValueError("MSCI index levels must be positive.")
    return result


def validate_weights(weights, long_only=()):
    if not weights.index.is_unique or not weights.columns.is_unique:
        raise ValueError("Duplicate industry or strategy labels.")
    if not np.isfinite(weights.to_numpy(dtype=float)).all():
        raise ValueError("Invalid portfolio weights.")
    if not np.allclose(weights.sum(), 1, atol=WEIGHT_TOLERANCE, rtol=0):
        raise ValueError("Portfolio weights do not sum to one.")
    if long_only and (weights.loc[:, list(long_only)] < -WEIGHT_TOLERANCE).any().any():
        raise ValueError("Long-only constraints are violated.")


def portfolio_returns(industry_returns, weights):
    validate_weights(weights)
    if not industry_returns.columns.is_unique or set(industry_returns.columns) != set(weights.index):
        raise ValueError("Industry names do not match the portfolio weights.")
    if not np.isfinite(industry_returns.to_numpy(dtype=float)).all():
        raise ValueError("Invalid industry returns.")
    return industry_returns @ weights.loc[industry_returns.columns]


def annualized_volatility(returns):
    if len(returns) < 2 or not np.isfinite(returns.to_numpy(dtype=float)).all():
        raise ValueError("Volatility requires at least two valid observations.")
    return returns.std(ddof=1) * np.sqrt(12)


def cumulative_return(returns):
    if returns.empty or not np.isfinite(returns.to_numpy(dtype=float)).all():
        raise ValueError("Cumulative returns require complete observations.")
    if (returns < -1).any().any():
        raise ValueError("Long-only returns cannot be below -100%.")
    return (1 + returns).prod() - 1


def read_weights_2004(root):
    path = Path(root) / OUTPUT_ROOT / "portfolio_optimization/industry_weights_2004.csv"
    if not path.is_file():
        raise FileNotFoundError("Run part3_portfolio_optimization before this task.")
    weights = pd.read_csv(path, index_col="industry")
    if tuple(weights.columns) != STRATEGIES or len(weights) != 49:
        raise ValueError("Unexpected December 2004 weights schema.")
    validate_weights(weights, ("min_var_long_only", "inverse_volatility"))
    return weights


def output_directory(root, section):
    path = Path(root) / OUTPUT_ROOT / section
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_csv(frame, path, index=True):
    frame.to_csv(path, index=index, float_format="%.15g", lineterminator="\n")


def save_json(payload, path):
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def source_hash(root, relative):
    return hashlib.sha256((Path(root) / relative).read_bytes()).hexdigest()


def software_versions():
    return {"python": platform.python_version(), **{
        name: version(name) for name in ("numpy", "pandas", "scipy", "matplotlib", "openpyxl", "jinja2")
    }}
