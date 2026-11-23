"""SQLite transactions exercise: atomic transfer between accounts.

Educational example; not suitable for real money without further controls.
"""
import sqlite3
from pathlib import Path


class InsufficientFunds(ValueError):
    """There is not enough balance to transfer."""


def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('''CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL CHECK(balance >= 0)
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL REFERENCES accounts(id),
            recipient_id INTEGER NOT NULL REFERENCES accounts(id),
            amount INTEGER NOT NULL CHECK(amount > 0)
        )''')


def balance(path: Path, account_id: int) -> int | None:
    with sqlite3.connect(path) as conn:
        row = conn.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,)).fetchone()
        return row[0] if row else None


def transfer(path: Path, sender_id: int, recipient_id: int, amount: int) -> int:
    """Atomically debit, credit, and record a transfer; return ledger id."""
    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        raise ValueError('amount must be a positive integer')
    if sender_id == recipient_id:
        raise ValueError('sender and recipient must be different')
    conn = sqlite3.connect(path, timeout=5, isolation_level=None)
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('BEGIN IMMEDIATE')
        result = conn.execute('''UPDATE accounts SET balance = balance - ?
            WHERE id = ? AND balance >= ?''', (amount, sender_id, amount))
        if result.rowcount != 1:
            exists = conn.execute('SELECT 1 FROM accounts WHERE id = ?', (sender_id,)).fetchone()
            if not exists:
                raise LookupError('sender not found')
            raise InsufficientFunds('insufficient balance')
        result = conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, recipient_id))
        if result.rowcount != 1:
            raise LookupError('recipient not found')
        cursor = conn.execute('''INSERT INTO transfers(sender_id, recipient_id, amount)
            VALUES (?, ?, ?)''', (sender_id, recipient_id, amount))
        conn.execute('COMMIT')
        return cursor.lastrowid
    except BaseException:
        if conn.in_transaction:
            conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()
