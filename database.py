
import sqlite3
from bank_account import SavingsAccount

DB_NAME = "banking.db"


# Connect to database
def get_connection():
    return sqlite3.connect(DB_NAME)


# Initialize database tables
def init_db():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)


# Create new account
def create_account(name, balance):

    name = name.strip()
    balance = float(balance)

    if not name:
        raise ValueError("Account holder name is required")

    account = SavingsAccount(name, balance)

    with get_connection() as conn:

        cursor = conn.execute(
            "INSERT INTO accounts (name, balance) VALUES (?, ?)",
            (name, account.get_balance())
        )

        account_id = cursor.lastrowid

        conn.execute("""
            INSERT INTO transactions
            (account_id, transaction_type, amount, balance_after)
            VALUES (?, ?, ?, ?)
        """, (account_id, "OPENING", balance, balance))

    return 1000 + account_id


# Get account details
def get_account(account_number):

    try:
        account_id = int(account_number) - 1000
    except (ValueError, TypeError):
        raise ValueError("Invalid account number")

    if account_id <= 0:
        raise ValueError("Invalid account number")

    with get_connection() as conn:

        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,)
        ).fetchone()

    if row is None:
        raise ValueError("Account not found")

    return dict(row)


# Deposit money
def deposit_money(account_number, amount):

    account = get_account(account_number)
    amount = float(amount)

    bank_account = SavingsAccount(
        account["name"],
        account["balance"]
    )

    new_balance = bank_account.deposit(amount)
    account_id = account["id"]

    with get_connection() as conn:

        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?",
            (new_balance, account_id)
        )

        conn.execute("""
            INSERT INTO transactions
            (account_id, transaction_type, amount, balance_after)
            VALUES (?, ?, ?, ?)
        """, (account_id, "DEPOSIT", amount, new_balance))

    return new_balance


# Withdraw money
def withdraw_money(account_number, amount):

    account = get_account(account_number)
    amount = float(amount)

    bank_account = SavingsAccount(
        account["name"],
        account["balance"]
    )

    new_balance = bank_account.withdraw(amount)
    account_id = account["id"]

    with get_connection() as conn:

        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?",
            (new_balance, account_id)
        )

        conn.execute("""
            INSERT INTO transactions
            (account_id, transaction_type, amount, balance_after)
            VALUES (?, ?, ?, ?)
        """, (account_id, "WITHDRAWAL", amount, new_balance))

    return new_balance


# Display all accounts
def list_accounts():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT id, name, balance, created_at
            FROM accounts
            ORDER BY id DESC
        """).fetchall()

    return [
        {
            "Account Number": 1000 + row[0],
            "Account Holder": row[1],
            "Balance": row[2],
            "Created At": row[3]
        }
        for row in rows
    ]


# Display transaction history
def get_transactions(account_number):

    account = get_account(account_number)
    account_id = account["id"]

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT transaction_type, amount,
                   balance_after, created_at
            FROM transactions
            WHERE account_id = ?
            ORDER BY id DESC
        """, (account_id,)).fetchall()

    return [
        {
            "Transaction": row[0],
            "Amount": row[1],
            "Balance After": row[2],
            "Date": row[3]
        }
        for row in rows
    ]
