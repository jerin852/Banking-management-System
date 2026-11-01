
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from bank_account import SavingsAccount

load_dotenv()


# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

@contextmanager
def get_connection():

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "jerin_banking"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ==========================================
# 2. INITIALIZE DATABASE TABLES
# ==========================================

def init_db():

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    balance NUMERIC(12, 2) NOT NULL
                        CHECK (balance >= 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    account_id BIGINT NOT NULL
                        REFERENCES accounts(id),
                    transaction_type VARCHAR(20) NOT NULL,
                    amount NUMERIC(12, 2) NOT NULL
                        CHECK (amount > 0),
                    balance_after NUMERIC(12, 2) NOT NULL
                        CHECK (balance_after >= 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


# ==========================================
# 3. CREATE ACCOUNT
# ==========================================

def create_account(name, balance):

    name = name.strip()
    balance = float(balance)

    if not name:
        raise ValueError("Account holder name is required")

    account = SavingsAccount(name, balance)

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                INSERT INTO accounts (name, balance)
                VALUES (%s, %s)
                RETURNING id
            """, (name, account.get_balance()))

            account_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO transactions
                (account_id, transaction_type, amount, balance_after)
                VALUES (%s, %s, %s, %s)
            """, (
                account_id,
                "OPENING",
                account.get_balance(),
                account.get_balance()
            ))

    return 1000 + account_id


# ==========================================
# 4. GET ACCOUNT
# ==========================================

def get_account(account_number):

    try:
        account_id = int(account_number) - 1000
    except (ValueError, TypeError):
        raise ValueError("Invalid account number")

    if account_id <= 0:
        raise ValueError("Invalid account number")

    with get_connection() as conn:

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""
                SELECT * FROM accounts
                WHERE id = %s
            """, (account_id,))

            row = cursor.fetchone()

    if row is None:
        raise ValueError("Account not found")

    account = dict(row)
    account["balance"] = float(account["balance"])

    return account


# ==========================================
# 5. DEPOSIT MONEY
# ==========================================

def deposit_money(account_number, amount):

    amount = float(amount)

    account = get_account(account_number)

    bank_account = SavingsAccount(
        account["name"],
        account["balance"]
    )

    new_balance = bank_account.deposit(amount)

    account_id = account["id"]

    with get_connection() as conn:

        with conn.cursor() as cursor:

            # Lock the account row during the update.
            cursor.execute("""
                SELECT balance FROM accounts
                WHERE id = %s
                FOR UPDATE
            """, (account_id,))

            row = cursor.fetchone()

            if row is None:
                raise ValueError("Account not found")

            bank_account = SavingsAccount(
                account["name"],
                float(row[0])
            )

            new_balance = bank_account.deposit(amount)

            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
            """, (new_balance, account_id))

            cursor.execute("""
                INSERT INTO transactions
                (account_id, transaction_type, amount, balance_after)
                VALUES (%s, %s, %s, %s)
            """, (account_id, "DEPOSIT", amount, new_balance))

    return new_balance


# ==========================================
# 6. WITHDRAW MONEY
# ==========================================

def withdraw_money(account_number, amount):

    amount = float(amount)

    account = get_account(account_number)

    account_id = account["id"]

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT balance FROM accounts
                WHERE id = %s
                FOR UPDATE
            """, (account_id,))

            row = cursor.fetchone()

            if row is None:
                raise ValueError("Account not found")

            bank_account = SavingsAccount(
                account["name"],
                float(row[0])
            )

            new_balance = bank_account.withdraw(amount)

            cursor.execute("""
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
            """, (new_balance, account_id))

            cursor.execute("""
                INSERT INTO transactions
                (account_id, transaction_type, amount, balance_after)
                VALUES (%s, %s, %s, %s)
            """, (account_id, "WITHDRAWAL", amount, new_balance))

    return new_balance


# ==========================================
# 7. LIST ALL ACCOUNTS
# ==========================================

def list_accounts():

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT id, name, balance, created_at
                FROM accounts
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

    return [
        {
            "Account Number": 1000 + row[0],
            "Account Holder": row[1],
            "Balance": float(row[2]),
            "Created At": row[3]
        }
        for row in rows
    ]


# ==========================================
# 8. GET TRANSACTION HISTORY
# ==========================================

def get_transactions(account_number):

    account = get_account(account_number)

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT transaction_type, amount,
                       balance_after, created_at
                FROM transactions
                WHERE account_id = %s
                ORDER BY id DESC
            """, (account["id"],))

            rows = cursor.fetchall()

    return [
        {
            "Transaction": row[0],
            "Amount": float(row[1]),
            "Balance After": float(row[2]),
            "Date": row[3]
        }
        for row in rows
    ]
