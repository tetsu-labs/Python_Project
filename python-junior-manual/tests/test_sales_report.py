import pandas as pd
import pytest
from exercises.sales_report import analyze_sales


def csv(tmp_path, content):
    p = tmp_path / 'sales.csv'
    p.write_text(content, encoding='utf-8')
    return p


def test_revenue_and_profit(tmp_path):
    path = csv(tmp_path, 'category,quantity,unit_price,unit_cost\nBook,2,1000,600\nGame,1,2000,1200\nBook,-1,1000,600\n')
    result = analyze_sales(path)
    assert result.to_dict('records') == [
        {'category': 'Book', 'revenue': 1000, 'profit': 400},
        {'category': 'Game', 'revenue': 2000, 'profit': 800},
    ]


@pytest.mark.parametrize('content', [
    'category,quantity,unit_price,unit_cost\n',
    'category,quantity,unit_price,unit_cost\n,1,2,1\n',
    'category,quantity,unit_price,unit_cost\nBook,x,2,1\n',
    'category,quantity,unit_price,unit_cost\nBook,1.5,2,1\n',
    'category,quantity,unit_price,unit_cost\nBook,1,-2,1\n',
    'category,quantity,unit_price\nBook,1,2\n',
])
def test_bad_input(tmp_path, content):
    with pytest.raises(ValueError):
        analyze_sales(csv(tmp_path, content))


def test_japanese_category(tmp_path):
    result = analyze_sales(csv(tmp_path, 'category,quantity,unit_price,unit_cost\n書籍,1,100,60\n'))
    assert result.iloc[0]['category'] == '書籍'
