"""Summarize sales CSV using only the Python standard library.

CSV columns: category,amount (JPY integer). Negative amounts represent refunds.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def summarize(path: Path) -> dict[str, int]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    totals: dict[str, int] = defaultdict(int)
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or set(reader.fieldnames) != {'category', 'amount'}:
            raise ValueError('CSV must contain exactly category,amount columns')
        for line, row in enumerate(reader, start=2):
            category = (row.get('category') or '').strip()
            amount = (row.get('amount') or '').strip()
            if not category or not amount or not amount.lstrip('-').isdigit():
                raise ValueError(f'invalid row at line {line}')
            totals[category] += int(amount)
    return dict(sorted(totals.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize integer JPY sales by category')
    parser.add_argument('csv_file', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(summarize(args.csv_file), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    main()
