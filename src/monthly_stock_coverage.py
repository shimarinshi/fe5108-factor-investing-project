"""Part 2A, first bullet: count unique securities by raw formation month."""
import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, StrMethodFormatter


def monthly_counts(source):
    """Retain all observations, including stocks with missing characteristics."""
    stocks = defaultdict(set)
    with Path(source).open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            month = datetime.strptime(row["date"], "%m/%d/%Y").replace(day=1)
            stocks[month].add(row["stock_id"])
    if not stocks:
        raise ValueError("No stock observations found.")
    observed = sorted(stocks)
    # An absent month must break the line, not be silently bridged or called zero.
    result = []
    month = observed[0]
    previous = None
    while month <= observed[-1]:
        count = len(stocks[month]) if month in stocks else None
        change = count - previous if count is not None and previous is not None else None
        result.append((month, count, change))
        previous = count
        month = datetime(month.year + month.month // 12, month.month % 12 + 1, 1)
    return result


def create_outputs(source, output):
    rows = monthly_counts(source)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "monthly_stock_counts.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["formation_month", "stock_count", "change_from_previous_month"])
        writer.writerows((date.strftime("%Y-%m"), count, change) for date, count, change in rows)

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.spines.left": False, "axes.spines.bottom": False,
        "svg.fonttype": "none",
    })
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor="white")
    fig.subplots_adjust(left=.085, right=.965, top=.78, bottom=.23)
    dates = [r[0] for r in rows]
    counts = [r[1] if r[1] is not None else float("nan") for r in rows]
    blue, red, ink = "#246B83", "#BD503B", "#213444"
    ax.fill_between(dates, counts, color=blue, alpha=.07)
    ax.plot(dates, counts, color=blue, linewidth=2.3)
    ax.set_ylim(0, max(c for c in counts if c == c) * 1.12)
    ax.set_xlim(datetime(1998, 5, 1), datetime(2020, 2, 1))
    ax.yaxis.set_major_locator(MultipleLocator(200))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color="#DFE5E9", linewidth=.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0, pad=9, labelcolor="#546471")
    ax.set_xlabel("Formation month", labelpad=14, color=ink)
    ax.set_ylabel("Number of stocks", labelpad=16, color=ink)

    # Mark the two largest month-to-month declines, selected from the data.
    declines = sorted((r for r in rows if r[2] is not None and r[2] < 0),
                      key=lambda r: r[2])[:2]
    declines.sort(key=lambda r: r[0])
    for row, position in zip(declines, [(0.69, .55), (.69, .15)]):
        date, count, change = row
        previous = count - change
        ax.scatter(date, count, s=42, color=red, edgecolor="white", zorder=4)
        label = (f"{date:%b %Y}  |  {count:,} stocks\n"
                 f"{change:,} from previous month ({change / previous:.1%})")
        ax.annotate(label, xy=(date, count), xytext=position,
                    textcoords="axes fraction", fontsize=10.5, color=red,
                    va="center", linespacing=1.6,
                    arrowprops={"arrowstyle": "-", "color": red, "lw": 1,
                                "connectionstyle": "angle3,angleA=0,angleB=90"},
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 5})
    ax.scatter(dates[0], counts[0], color=blue, s=25, zorder=4)
    ax.annotate(f"{counts[0]:,}", (dates[0], counts[0]),
                xytext=(7, -22), textcoords="offset points", color=blue, fontsize=10)

    fig.text(.085, .93, "Monthly stock coverage", fontsize=23, weight="bold", color=ink)
    fig.text(.085, .875,
             f"Unique securities in the supplied sample  |  {dates[0]:%b %Y}–{dates[-1]:%b %Y}",
             fontsize=12, color="#546471")
    fig.text(.085, .115,
             "Source: Instructor-provided security_characteristics.csv (ML for Factor Investing extract).",
             fontsize=9, color="#65727C")
    fig.text(.085, .08,
             "Universe: All stock IDs observed each month; no screening or return-based exclusions. "
             "Dates are formation months.",
             fontsize=9, color="#65727C")
    fig.text(.085, .045,
             "Highlighted: the two largest monthly declines. Counts alone do not establish "
             "whether universe selection rules changed.",
             fontsize=9, color="#65727C")
    for extension in ("png", "svg"):
        fig.savefig(output / f"monthly_stock_coverage.{extension}", dpi=220, facecolor="white")
    plt.close(fig)
    print(f"Saved monthly coverage chart and counts for {len(rows)} months to {output}")


def run(root):
    root = Path(root)
    create_outputs(root / "data/raw/security_characteristics.csv",
                   root / "outputs/monthly_stock_coverage")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    create_outputs(args.input, args.output)
