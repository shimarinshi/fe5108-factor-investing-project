"""Run every integrated task; never imply unreleased analysis is complete."""
import argparse
import sys
from pathlib import Path
from src.input_validation import run as validate_inputs

ROOT = Path(__file__).resolve().parent
TASKS = {'validate_inputs': validate_inputs}

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
    print('All registered tasks passed. Course analyses are not yet implemented.')

if __name__ == '__main__':
    main()
