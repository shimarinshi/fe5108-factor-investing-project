"""Run every integrated task; never imply unreleased analysis is complete."""
import argparse
import sys
from pathlib import Path
from src.input_validation import run as validate_inputs
from src.part_2.data_validation.monthly_stock_coverage import run as monthly_stock_coverage
from src.part_2.data_validation.return_distribution import run as return_distribution
from src.part_2.data_validation.return_coverage import run as return_coverage
from src.part_2.data_validation.price_to_book_distribution import run as price_to_book_distribution
from src.part_2.data_validation.valuation_sanity_check import run as valuation_sanity_check

from src.part_2.broad_market.market_portfolio import run as market_portfolio

from src.part_2.broad_market.benchmark_comparison import run as benchmark_comparison

from src.part_2.value_portfolios.value_returns import run as value_returns

from src.part_2.active_returns.tracking_error import run as tracking_error

from src.part_2.active_returns.factor_correlations import run as factor_correlations
from src.part_3.portfolio_optimization import run as part3_portfolio_optimization
from src.part_3.in_sample_effectiveness import run as part3_in_sample_effectiveness
from src.part_3.out_of_sample_effectiveness import run as part3_out_of_sample_effectiveness
from src.part_3.reoptimization import run as part3_reoptimization
from src.part_3.performance_expectations import run as part3_performance_expectations
from src.part4.part4_analysis import run as part4_analyze
from src.part4.part4_figures import run as part4_plot

def part4_analysis(root):
    part4_analyze(root / 'data/raw/product_innovation.xlsx', root / 'outputs/part4')

def part4_figures(root):
    part4_plot(root / 'outputs/part4')

ROOT = Path(__file__).resolve().parent
TASKS = {'validate_inputs': validate_inputs, 'monthly_stock_coverage': monthly_stock_coverage,
         'return_distribution': return_distribution, 'return_coverage': return_coverage,
         'price_to_book_distribution': price_to_book_distribution,
         'valuation_sanity_check': valuation_sanity_check, 'market_portfolio': market_portfolio, 'benchmark_comparison': benchmark_comparison, 'value_returns': value_returns, 'tracking_error': tracking_error, 'factor_correlations': factor_correlations,
         'part3_portfolio_optimization': part3_portfolio_optimization,
         'part3_in_sample_effectiveness': part3_in_sample_effectiveness,
         'part3_out_of_sample_effectiveness': part3_out_of_sample_effectiveness,
         'part3_reoptimization': part3_reoptimization,
         'part3_performance_expectations': part3_performance_expectations,
         'part4_analysis': part4_analysis,
         'part4_figures': part4_figures}

PART_TASKS = {
    '2': tuple(name for name in TASKS if not name.startswith(('part3_', 'part4_'))),
    '3': ('validate_inputs',) + tuple(name for name in TASKS if name.startswith('part3_')),
    '4': ('validate_inputs', 'part4_analysis', 'part4_figures'),
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='Run all implemented tasks (default).')
    group.add_argument('--task', choices=TASKS)
    group.add_argument('--part', choices=PART_TASKS, help='Run one implemented part with its input checks.')
    group.add_argument('--list', action='store_true')
    args = parser.parse_args()
    if sys.version_info[:3] != (3, 12, 14):
        parser.error('Use Python 3.12.14, the documented reproducibility baseline.')
    if args.list:
        print('\n'.join(TASKS))
        return
    selected = [args.task] if args.task else PART_TASKS[args.part] if args.part else TASKS
    for name in selected:
        print(f'Running {name}')
        TASKS[name](ROOT)
    print('All registered tasks passed. Only documented tasks are implemented; remaining analyses are pending.')

if __name__ == '__main__':
    main()
