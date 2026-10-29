# Part 4: Product innovation — evaluating NVDL

## Data and objective

This section evaluates whether the GraniteShares 2x Long NVDA Daily ETF (NVDL) delivers approximately twice the daily return of NVIDIA (NVDA), and how daily leverage changes risk and returns over longer holding periods. We use the instructor-provided daily total returns for both securities from February 1 through August 30, 2024: 147 paired trading-day observations. Returns are expressed as decimal fractions in the data; reported percentages are converted accordingly. The source describes these as total returns; we have not independently reconstructed its adjustments or established the ETF return's NAV-versus-market-price convention.

The fund's objective concerns the daily percentage change before fees and expenses. It should therefore be evaluated day by day; twice the stock's cumulative return over several days is not its stated target.

## 4A. Daily risk

| Daily risk measure | NVDA | NVDL |
|---|---:|---:|
| Standard deviation | 3.746% | 7.479% |
| Historical 95% VaR | 6.121% | 12.029% |
| Historical 95% CVaR | 7.073% | 14.162% |

We calculate sample standard deviations with 146 degrees of freedom. Historical VaR is the negative of the linearly interpolated 5th percentile of daily returns. CVaR is the negative average of the eight observations at or below that percentile. Both are displayed as positive loss magnitudes. These are daily, unannualized estimates; other finite-sample expected-shortfall conventions can produce slightly different values.

In this sample, NVDL's daily volatility is almost twice NVDA's. Its 95% VaR of 12.029% is the estimated one-day loss threshold at the 5th percentile, and its CVaR of 14.162% describes the average loss among the observed days in that tail. The corresponding values for NVDA are 6.121% and 7.073%. All three measures indicate substantially higher daily risk for NVDL, consistent with leveraged exposure. The estimates describe this particular sample, however, and should not be treated as guaranteed limits on future losses.

![Daily risk comparison](../../outputs/part4/daily_risk_comparison.png)

## 4B. Does NVDL deliver approximately twice the daily return?

We estimate an ordinary least squares regression with an intercept:

`NVDL daily return = α + β × NVDA daily return + error`

| Coefficient | Estimate | 95% confidence interval |
|---|---:|---:|
| Intercept α | -0.000612 | [-0.000935, -0.000289] |
| NVDA slope β | 1.995975 | [1.987407, 2.004543] |

The slope implies that a one-percentage-point increase in NVDA's daily return is associated with approximately a 1.996-percentage-point increase in NVDL's daily return. The 95% interval includes 2, so the estimated average relationship is consistent with the fund's 2× daily target. The intercept corresponds to about -0.061 percentage points per day when NVDA's return is zero. The regression has 145 residual degrees of freedom and uses conventional OLS standard errors.

This evidence does not establish that the fund achieved exactly twice the stock return on every day. The target is stated before fees and expenses, while the provided realized ETF returns reflect the fund's actual performance. Differences can also arise from tracking and data conventions. The confidence intervals rely on the standard OLS error assumptions and quantify uncertainty in the fitted coefficients, not a bound on every individual day's tracking difference.

![Daily return regression](../../outputs/part4/daily_return_regression.png)

## 4C. Performance drag and expenses

The estimated intercept provides a crude measure of daily return not explained by the fitted NVDA component. Following the assignment's convention, multiplying by 252 trading days gives:

`−0.00061164 × 252 = −0.1541`, or approximately **−15.41% per year**.

This is much larger in magnitude than the 1.15% annual net operating expense ratio stated in the assignment. The figures therefore do not roughly align in this sample. The intercept is a statistical estimate conditional on the fitted slope, and its annualization is an arithmetic approximation. It should not be interpreted as a direct measurement of the fund's annual fee, a forecast, or proof that the unexplained difference consists entirely of costs.

Two additional costs that could contribute to performance drag are financing or swap-related costs associated with maintaining leveraged exposure, and trading costs such as bid–ask spreads or market impact when exposure is adjusted. Tracking differences, sample uncertainty, and differences in the provided data's return conventions may also affect the fitted intercept. This regression cannot separately identify the contribution of each source. The 1.15% figure is the historical figure specified in the assignment, not a statement of the current fee.

## 4D. Daily leverage and cumulative performance

We compound daily total returns within each calendar month and across the full sample:

`Cumulative return = product of (1 + daily return) − 1`

| Period, 2024 | NVDA | NVDL | Twice NVDA's cumulative return |
|---|---:|---:|---:|
| February | 28.60% | 59.11% | 57.19% |
| March | 14.21% | 25.76% | 28.42% |
| April | -4.37% | -12.22% | -8.74% |
| May | 26.88% | 55.72% | 53.76% |
| June | 12.70% | 22.60% | 25.40% |
| July | -5.28% | -14.68% | -10.56% |
| August | 2.01% | -1.60% | 4.02% |
| February–August | 94.05% | 181.53% | 188.10% |

The last column is twice the stock's cumulative return for comparison, not a target return for a multi-day holding period. Over the full period, the difference between NVDL and twice NVDA's cumulative return is approximately −6.57 percentage points. The monthly results show that the difference can go in either direction: NVDL exceeded twice NVDA's return in February and May but fell below it in the other displayed months.

August illustrates the effect particularly clearly: NVDA gained 2.01%, whereas NVDL lost 1.60%. These observations support the factsheet's warning that a daily leverage objective does not imply two times the underlying stock's cumulative performance. Daily compounding, the return path, costs, and tracking can all contribute; the table by itself does not isolate their individual effects.

![Monthly return comparison](../../outputs/part4/monthly_return_comparison.png)

![Growth of one dollar](../../outputs/part4/cumulative_growth.png)

## 4E. Two-day illustration

Assume NVDA rises 10% on day one and falls 9% on day two. Starting from $100, its value becomes $110 and then $100.10. Its cumulative return is:

`1.10 × 0.91 − 1 = +0.10%`

Assuming an idealized NVDL return of exactly twice the stock's return each day, with no fees or other drag, its returns are +20% and −18%. Starting from $100, its value becomes $120 and then $98.40:

`1.20 × 0.82 − 1 = −1.60%`

The stock ends slightly higher while the hypothetical leveraged ETF loses money. The second day's loss is applied to a different capital base after the first day's gain. The example supports the warning about path dependence; it does not mean that every volatile price path necessarily produces an ETF loss.

## 4F. Which product fits each investor?

For a trader who is bullish specifically on the day of a product announcement, NVDL provides exposure aligned with an approximately 2× daily objective. It may therefore be appropriate if the trader deliberately wants that larger exposure and can absorb a correspondingly larger loss if the announcement disappoints. The choice also requires attention to spreads, execution costs and tracking differences. A bullish view is not a guarantee of a positive daily return.

For an investor who expects NVDA to perform well over a year but also expects substantial volatility, NVDA is the more straightforward choice. NVDL resets its exposure daily, so its one-year outcome depends on the sequence of returns and can differ substantially from twice NVDA's one-year gain or loss. Financing and other fund expenses can further affect the result. An investor considering NVDL over a longer period would need to evaluate those effects and their own risk tolerance rather than relying on a simple 2× annual-return expectation.

## Methods and reproducibility

The underlying tables and four figures are in `outputs/part4/`; run `python run_all.py --part 4` from the repository root to regenerate them. This report uses the instructor-provided sample and the historical fee stated in the assignment. The 2024 factsheet itself has not been independently checked in preparing this draft; its precise wording and expense figure should be verified against the course copy before submission.

