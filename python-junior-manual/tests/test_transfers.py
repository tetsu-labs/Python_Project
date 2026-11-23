"""Atomicity, validation, and ledger tests for transactions."""
import sqlite3

import pytest

from exercises.transfers import InsufficientFunds, balance, initialize, transfer


@pytest.fixture
def db(tmp_path):
    path = tmp_path / 'accounts.db'
    initialize(path)
    with sqlite3.connect(path) as conn:
        conn.executemany('INSERT INTO accounts(id, balance) VALUES(?, ?)', [(1, 100), (2, 40)])
    return path


def ledger(db):
    with sqlite3.connect(db) as conn:
        return conn.execute('SELECT sender_id, recipient_id, amount FROM transfers').fetchall()


def test_success_and_ledger(db):
    assert transfer(db, 1, 2, 30) == 1
    assert (balance(db, 1), balance(db, 2)) == (70, 70)
    assert ledger(db) == [(1, 2, 30)]


def test_insufficient_funds_rolls_back(db):
    with pytest.raises(InsufficientFunds):
        transfer(db, 1, 2, 101)
    assert (balance(db, 1), balance(db, 2)) == (100, 40)
    assert ledger(db) == []


def test_missing_recipient_rolls_back_debit(db):
    with pytest.raises(LookupError, match='recipient'):
        transfer(db, 1, 999, 50)
    assert balance(db, 1) == 100
    assert ledger(db) == []


def test_missing_sender(db):
    with pytest.raises(LookupError, match='sender'):
        transfer(db, 999, 2, 10)
    assert balance(db, 2) == 40


@pytest.mark.parametrize('amount', [0, -1, 0.5, True, '10'])
def test_invalid_amount(db, amount):
    with pytest.raises(ValueError):
        transfer(db, 1, 2, amount)
    assert (balance(db, 1), balance(db, 2)) == (100, 40)


def test_same_account(db):
    with pytest.raises(ValueError):
        transfer(db, 1, 1, 1)


def test_initialize_idempotent(db):
    initialize(db)
    assert balance(db, 1) == 100


def test_conserves_total_across_many_transfers(db):
    for _ in range(5):
        transfer(db, 1, 2, 10)
        transfer(db, 2, 1, 5)
    assert balance(db, 1) + balance(db, 2) == 140
    assert len(ledger(db)) == 10
