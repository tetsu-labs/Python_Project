"""Reproducible sales analysis with pandas; no external services needed."""
from pathlib import Path
import pandas as pd

REQUIRED = {'category', 'quantity', 'unit_price', 'unit_cost'}


def analyze_sales(path: Path) -> pd.DataFrame:
    """Return category summary; currency is integer JPY and refunds are negative quantities."""
    df = pd.read_csv(path, encoding='utf-8-sig')
    if set(df.columns) != REQUIRED:
        raise ValueError('CSV columns must be category,quantity,unit_price,unit_cost')
    if df.empty:
        raise ValueError('sales CSV is empty')
    if df['category'].isna().any() or df['category'].astype(str).str.strip().eq('').any():
        raise ValueError('category cannot be empty')
    for col in ('quantity', 'unit_price', 'unit_cost'):
        values = pd.to_numeric(df[col], errors='coerce')
        if values.isna().any() or (values % 1 != 0).any():
            raise ValueError(f'{col} must contain integer values')
        df[col] = values.astype('int64')
    if (df[['unit_price', 'unit_cost']] < 0).any().any():
        raise ValueError('unit price/cost must be nonnegative')
    df['revenue'] = df['quantity'] * df['unit_price']
    df['profit'] = df['quantity'] * (df['unit_price'] - df['unit_cost'])
    return (df.groupby('category', as_index=False)[['revenue', 'profit']]
            .sum().sort_values('category').reset_index(drop=True))
