from pathlib import Path

import pytest

from exercises.sales_summary import summarize


def write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / 'sales.csv'
    path.write_text(text, encoding='utf-8')
    return path


def test_grouped_totals(tmp_path):
    path = write_csv(tmp_path, 'category,amount\nBook,1200\nGame,500\nBook,-200\n')
    assert summarize(path) == {'Book': 1000, 'Game': 500}


def test_japanese_and_utf8_bom(tmp_path):
    path = tmp_path / 'bom.csv'
    path.write_text('\ufeffcategory,amount\n書籍,1000\n', encoding='utf-8')
    assert summarize(path) == {'書籍': 1000}


@pytest.mark.parametrize('csv_data', [
    'category,amount\nBook,abc\n',
    'category,amount\n,100\n',
    'category,amount\nBook,\n',
    'category,amount\nBook,1.5\n',
    'category,price\nBook,100\n',
])
def test_invalid_input(tmp_path, csv_data):
    with pytest.raises(ValueError):
        summarize(write_csv(tmp_path, csv_data))


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        summarize(tmp_path / 'missing.csv')
