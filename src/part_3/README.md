# Part 3: reproducible industry-portfolio analysis

The numerical analysis and figures for 3A–3E are integrated. See the [results overview](../../reports/part_3/README.md) for comparisons and interpretation. `industry_portfolio_analysis.ipynb` calls the Python modules below instead of maintaining a second implementation.

## Setup and execution

Use Python **3.12.14**, including for the VS Code notebook kernel. From the repository root:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pip check
python run_all.py --part 3
python -m unittest discover -s tests -v
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Notebook front-end tooling (VS Code Jupyter/IPython) is separate from the command-line runtime; the core modules do not import IPython. Select the environment containing the locked runtime packages when using the notebook.

`python run_all.py --all` reproduces integrated Parts 2–5. `python run_all.py --list` lists every task. After environment installation, the analyses run offline without API keys.

| Question | Python module | Registered task | Required upstream result |
|---|---|---|---|
| 3A | `portfolio_optimization.py` | `part3_portfolio_optimization` | None |
| 3B | `in_sample_effectiveness.py` | `part3_in_sample_effectiveness` | 3A weights |
| 3C | `out_of_sample_effectiveness.py` | `part3_out_of_sample_effectiveness` | 3A weights and 3B summary |
| 3D | `reoptimization.py` | `part3_reoptimization` | 3A weights |
| 3E | `performance_expectations.py` | `part3_performance_expectations` | 3A weights |

For example, `python run_all.py --task part3_reoptimization` reruns 3D after 3A exists. Individual tasks fail clearly if an upstream result is missing. `--part 3` runs source-integrity validation and all five tasks in order. Every analysis exports `run(root)`, where `root` is the repository root; callers do not need a particular working directory.

## Inputs and assumptions

Reuse the canonical sources from [the data registry](../../data/README.md); do not add copies:

- `data/raw/industry_portfolios.xlsx`, sheet `49_Industry_Portfolios`: 49 **value-weighted monthly total returns**, January 1995–July 2023. Strip industry-label spaces, map −99.99/−999 to missing before dividing percentage values by 100, and reject missing or duplicate analysis months. No industry-return winsorization is applied.
- `data/raw/ff_msci_shared.xlsx`, sheet `MSCI - factor totret index`: **USA Standard (Large+Mid Cap), Gross, USD** index levels. Discard non-date footer text, retain December 2004, and calculate consecutive month-end simple returns. Trading dates are matched by calendar month.

The initial covariance uses **January 1995–December 2004 (120 months)**. The shorting-allowed minimum-variance portfolio satisfies only the sum-to-one constraint. The long-only version additionally requires nonnegative weights. The heuristic weights each industry by the normalized inverse of its sample volatility, not inverse variance. Sample covariance and standard deviation use `ddof=1`.

The long-only optimization minimizes `w.T @ covariance @ w`, subject to `sum(w)=1` and `w>=0`. SLSQP uses an equal-weight starting point, an analytical gradient, `ftol=1e-12`, and `maxiter=5000`. The covariance is multiplied by 12 for the objective scale, which does not change the optimal weights. Unconstrained weights use a linear solve, not an explicit inverse. Weight-sum/nonnegativity tolerance is `1e-8`; weights are not rounded or clipped for calculation.

All evaluations maintain fixed target weights with monthly rebalancing and exclude transaction costs. Only 3D updates the target weights. The windows are:

| Use | Window | Months |
|---|---|---:|
| 3A estimation / 3B in-sample evaluation | 1995-01–2004-12 | 120 |
| 3C out-of-sample evaluation | 2005-01–2023-07 | 223 |
| 3D updated estimation | 2006-01–2015-12 | 120 |
| 3D common evaluation | 2016-01–2023-07 | 91 |
| 3E Global Financial Crisis | 2008-09–2009-02 | 6 |
| 3E COVID sell-off | 2020-02–2020-03 | 2 |

Volatility is monthly sample standard deviation times `sqrt(12)`. Crisis returns are `product(1+r)-1`. The wealth chart starts with $1 on December 31, 2004, includes January 2005–July 2023 returns, and uses a base-2 log y-axis. It uses the original 2004 long-only portfolio, not the 2015 update. Industry rankings sort cumulative returns in descending order; even negative returns may enter the top ten. Stable sorting breaks exact ties in original industry order.

## Output inventory

All paths below are under `outputs/part_3/`; the pipeline regenerates **13 CSVs and 5 presentation/metadata files**:

| Section | Files |
|---|---|
| `portfolio_optimization/` | `industry_weights_2004.csv`, `industry_weights_2004.html`, `optimization_metadata.json` |
| `in_sample_effectiveness/` | `in_sample_portfolio_returns.csv`, `in_sample_volatility.csv` |
| `out_of_sample_effectiveness/` | `out_of_sample_portfolio_returns.csv`, `in_sample_vs_out_of_sample_volatility.csv` |
| `reoptimization/` | `long_only_weights_2004_vs_2015.csv`, `reoptimization_evaluation_returns.csv`, `reoptimization_volatility.csv`, `reoptimization_metadata.json` |
| `performance_expectations/` | `strategy_and_benchmark_returns.csv`, `cumulative_wealth.csv`, `crisis_performance.csv`, `crisis_industry_rankings.csv`, `crisis_top_ten_industries.csv`, `cumulative_wealth_log2.png`, `cumulative_wealth_log2.svg` |

The HTML table highlights five highest weights per strategy in green and five lowest in red; the total row is excluded. Reference CSVs store decimal returns/weights, except columns explicitly named `*_percentage_points`. CSVs retain 15 significant digits; report formatting is separate. Dates are `YYYY-MM` realized-return months. See [interface contracts](../../docs/interfaces.md).

## Verification and version control

`tests/test_industry_portfolios.py` checks known analytical allocations, constraints, date completeness, name alignment, benchmark conversion, compounding, and all five sections against the 13 reference CSVs. Regression tolerance is `rtol=1e-7, atol=1e-9` to allow numerical platform differences. It also checks byte-stable repeated generation in the same environment. HTML UUID, SVG IDs and SVG creation metadata are fixed; figures and solver metadata can still vary across platforms. CI uses numerical regression for Part 3 rather than byte comparison across platforms.

Runtime versions are pinned, including the existing plotting/numerical packages, to the environment used for verification. Metadata records software versions and solver settings. Source hashes remain in the shared manifest; the 3A metadata additionally records the industry-workbook hash.

The 18 selected output files are intentional review/submission artifacts and must accompany their generating code. In a Git checkout, use `git add -f` with each exact result path listed above, not an entire ignored output tree. The end-to-end regression test requires all 13 reference CSVs. Keep `.DS_Store`, caches, virtual environments, raw-data duplicates, and unrelated changes out of the commit. Run `git diff --check` and request teammate review before merging. This integration does not push, publish, or change repository visibility.
