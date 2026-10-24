"""Part 3E: cumulative wealth, two crisis windows, and industry rankings."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from .data_loading import (
    CRISIS_WINDOWS, cumulative_return, levels_to_returns, monthly_window,
    output_directory, portfolio_returns, read_industry_returns,
    read_msci_levels, read_weights_2004, save_csv,
)


def wealth_from_returns(returns, initial_month="2004-12"):
    if not np.isfinite(returns.to_numpy()).all() or not (returns > -1).all().all():
        raise ValueError("Log-scale wealth requires finite returns above -100%.")
    if returns.index[0] != pd.Period(initial_month, freq="M") + 1:
        raise ValueError("Initial wealth must immediately precede the first return month.")
    initial = pd.DataFrame(1.0, index=pd.PeriodIndex([initial_month], freq="M", name="month"), columns=returns.columns)
    return pd.concat([initial, (1 + returns).cumprod()])


def plot_wealth(wealth, out):
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.hashsalt": "fe5108_part3_wealth"}):
        fig, ax = plt.subplots(figsize=(12, 6), facecolor="white")
        dates = wealth.index.to_timestamp(how="end").normalize()
        ax.plot(dates, wealth["min_var_2004"], color="#246B83", linewidth=2,
                label="Minimum variance (December 2004, long only)")
        ax.plot(dates, wealth["msci_usa"], color="#87949E", linewidth=1.8,
                linestyle="--", label="MSCI USA (gross total return, USD)")
        for start, end, _ in CRISIS_WINDOWS.values():
            ax.axvspan(pd.Period(start, freq="M").start_time, pd.Period(end, freq="M").end_time,
                       color="#DFE5E9", alpha=0.7, zorder=0)
        ax.set_yscale("log", base=2)
        ax.yaxis.set_major_locator(LogLocator(base=2))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, position: f"${value:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_xlim(dates[0], dates[-1])
        ax.set_title("Growth of $1: Minimum Variance vs. MSCI USA", color="#213444")
        ax.set_xlabel("Month", color="#213444")
        ax.set_ylabel("Portfolio value (USD, log2 scale)", color="#213444")
        ax.tick_params(colors="#546471")
        ax.legend(frameon=False, loc="upper left")
        ax.grid(axis="y", which="major", color="#DFE5E9", linewidth=0.7)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.text(0.08, 0.04,
                 "Source: supplied FF industry returns and MSCI USA Gross USD index. "
                 "Start: Dec 31, 2004; end: Jul 31, 2023.\n"
                 "Shaded periods: Sep 2008–Feb 2009 and Feb–Mar 2020. "
                 "Fixed target weights; monthly rebalancing; no transaction costs.",
                 fontsize=8, color="#65727C")
        fig.tight_layout(rect=(0, 0.13, 1, 1))
        fig.savefig(out / "cumulative_wealth_log2.png", dpi=220, facecolor="white",
                    bbox_inches="tight", metadata={"Software": "FE5108 Part 3"})
        fig.savefig(out / "cumulative_wealth_log2.svg", facecolor="white",
                    bbox_inches="tight", metadata={"Date": None, "Creator": "FE5108 Part 3"})
        svg_path = out / "cumulative_wealth_log2.svg"
        svg_text = svg_path.read_text(encoding="utf-8")
        svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")
        plt.close(fig)


def run(root):
    industry = read_industry_returns(root)
    evaluation = monthly_window(industry, "2005-01", "2023-07")
    weights = read_weights_2004(root)[["min_var_long_only"]]
    strategy = portfolio_returns(evaluation, weights)["min_var_long_only"].rename("min_var_2004")
    levels = read_msci_levels(root)
    market = levels_to_returns(levels, "2005-01", "2023-07")
    returns = monthly_window(pd.concat([strategy, market], axis=1), "2005-01", "2023-07")
    wealth = wealth_from_returns(returns)
    np.testing.assert_allclose(wealth["msci_usa"], levels / levels.iloc[0], rtol=1e-10, atol=1e-12)
    crises, ranks = [], []
    for label, (start, end, months) in CRISIS_WINDOWS.items():
        window = monthly_window(returns, start, end)
        if len(window) != months:
            raise ValueError(f"Unexpected crisis length: {label}.")
        cumulative = cumulative_return(window)
        crises.append({
            "crisis": label, "period": f"{start} to {end}", "months": months,
            "minimum_variance_return": cumulative["min_var_2004"],
            "msci_usa_return": cumulative["msci_usa"],
            "difference_percentage_points": 100 * (cumulative["min_var_2004"] - cumulative["msci_usa"]),
        })
        ranked = cumulative_return(monthly_window(industry, start, end)).sort_values(
            ascending=False, kind="stable"
        ).rename("cumulative_return").rename_axis("industry").reset_index()
        ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
        ranked.insert(0, "crisis", label)
        ranks.append(ranked)
    crisis_summary = pd.DataFrame(crises)
    rankings = pd.concat(ranks, ignore_index=True)
    out = output_directory(root, "performance_expectations")
    save_csv(returns, out / "strategy_and_benchmark_returns.csv")
    save_csv(wealth, out / "cumulative_wealth.csv")
    save_csv(crisis_summary, out / "crisis_performance.csv", index=False)
    save_csv(rankings, out / "crisis_industry_rankings.csv", index=False)
    save_csv(rankings.groupby("crisis", sort=False).head(10), out / "crisis_top_ten_industries.csv", index=False)
    plot_wealth(wealth, out)
    print("Part 3E: 224 wealth dates; two crisis windows; two top-ten industry lists.")
    return crisis_summary
