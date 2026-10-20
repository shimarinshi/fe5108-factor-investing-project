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

ROOT = Path(__file__).resolve().parent
TASKS = {'validate_inputs': validate_inputs, 'monthly_stock_coverage': monthly_stock_coverage,
         'return_distribution': return_distribution, 'return_coverage': return_coverage,
         'price_to_book_distribution': price_to_book_distribution,
         'valuation_sanity_check': valuation_sanity_check, 'market_portfolio': market_portfolio, 'benchmark_comparison': benchmark_comparison, 'value_returns': value_returns}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='Run all implemented tasks (default).')
    group.add_argument('--task', choices=TASKS)
    group.add_argument('--list', action='store_true')
    args = parser.parse_args()
    if sys.version_info[:3] != (3, 12, 14):
        parser.error('Use Python 3.12.14, the documented reproducibility baseline.')
    if args.list:
        print('\n'.join(TASKS))
        return
    for name in ([args.task] if args.task else TASKS):
        print(f'Running {name}')
        TASKS[name](ROOT)
    print('All registered tasks passed. Only documented tasks are implemented; remaining analyses are pending.')

if __name__ == '__main__':
    main()
