"""Inspect supplied sources without cleaning or computing portfolio performance."""
import calendar
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

COLUMNS = ['stock_id', 'date', 'Pb', 'Bv', 'R1M_Usd', 'Vol3Y_Usd', 'Mkt_Cap_3M_Usd']

def inspect_csv(path):
    dates, missing, ids, seen = Counter(), Counter(), set(), set()
    ranges = {c: [math.inf, -math.inf] for c in COLUMNS[2:]}
    count = 0
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != COLUMNS:
            raise ValueError('Unexpected raw columns; review the data contract.')
        for row in reader:
            day = datetime.strptime(row['date'], '%m/%d/%Y').date()
            if day.day != calendar.monthrange(day.year, day.month)[1]:
                raise ValueError('Formation date is not month end.')
            sid = row['stock_id'].strip()
            if not sid or (sid, day) in seen:
                raise ValueError('Empty identifier or duplicate stock-date key.')
            seen.add((sid, day)); ids.add(sid); dates[day.isoformat()] += 1; count += 1
            for col in COLUMNS[2:]:
                if row[col].strip().lower() in {'', 'na', 'nan', 'null'}:
                    missing[col] += 1
                    continue
                value = float(row[col])
                if not math.isfinite(value):
                    missing[col] += 1
                    continue
                ranges[col] = [min(ranges[col][0], value), max(ranges[col][1], value)]
    if not count:
        raise ValueError('Empty input.')
    return {'rows': count, 'securities': len(ids), 'formation_start': min(dates),
            'formation_end': max(dates), 'months': len(dates),
            'rows_by_formation_date': dict(sorted(dates.items())),
            'missing_by_field': {c: missing[c] for c in COLUMNS[2:]},
            'ranges': {c: [v if math.isfinite(v) else None for v in vals] for c, vals in ranges.items()},
            'scope': 'Raw inventory only; no winsorization or portfolio analysis.'}

def run(root):
    root = Path(root)
    manifest = json.loads((root / 'data/raw/source_manifest.json').read_text())
    for source in manifest['sources']:
        path = root / source['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f"Missing or modified source: {source['path']}")
    report = inspect_csv(root / 'data/raw/security_characteristics.csv')
    output = root / 'outputs/input_validation'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'summary.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(f"Validated {report['rows']:,} raw rows; analysis remains unimplemented.")
