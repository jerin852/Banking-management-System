
import os
import sqlite3

import psycopg2
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = "banking.db"


def migrate_data():
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = None

    try:
        # Read SQLite data
        accounts = sqlite_conn.execute("""
            SELECT id, name, balance, created_at
            FROM accounts
            ORDER BY id
        """).fetchall()

        transactions = sqlite_conn.execute("""
            SELECT id, account_id, transaction_type,
                   amount, balance_after, created_at
            FROM transactions
            ORDER BY id
        """).fetchall()

        print("SQLite records found:")
        print("Accounts:", len(accounts))
        print("Transactions:", len(transactions))

        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "jerin_banking"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )

        # PostgreSQL transaction
        with pg_conn:
            with pg_conn.cursor() as cursor:

                # Prevent duplicate migration
                cursor.execute("SELECT COUNT(*) FROM accounts")
                if cursor.fetchone()[0] != 0:
                    raise RuntimeError(
                        "PostgreSQL accounts table is not empty."
                    )

                cursor.execute("SELECT COUNT(*) FROM transactions")
                if cursor.fetchone()[0] != 0:
                    raise RuntimeError(
                        "PostgreSQL transactions table is not empty."
                    )

                # Migrate accounts
                for account in accounts:
                    cursor.execute("""
                        INSERT INTO accounts
                            (id, name, balance, created_at)
                        OVERRIDING SYSTEM VALUE
                        VALUES (%s, %s, %s, %s)
                    """, (
                        account["id"],
                        account["name"],
                        account["balance"],
                        account["created_at"]
                    ))

                # Migrate transactions
                for transaction in transactions:
                    cursor.execute("""
                        INSERT INTO transactions
                            (id, account_id, transaction_type,
                             amount, balance_after, created_at)
                        OVERRIDING SYSTEM VALUE
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        transaction["id"],
                        transaction["account_id"],
                        transaction["transaction_type"],
                        transaction["amount"],
                        transaction["balance_after"],
                        transaction["created_at"]
                    ))

                # Reset account identity sequence
                cursor.execute("""
                    SELECT setval(
                        pg_get_serial_sequence(
                            'public.accounts', 'id'
                        ),
                        COALESCE(MAX(id), 1),
                        MAX(id) IS NOT NULL
                    )
                    FROM public.accounts
                """)

                # Reset transaction identity sequence
                cursor.execute("""
                    SELECT setval(
                        pg_get_serial_sequence(
                            'public.transactions', 'id'
                        ),
                        COALESCE(MAX(id), 1),
                        MAX(id) IS NOT NULL
                    )
                    FROM public.transactions
                """)

        print("\nMigration completed successfully!")

        # Verify migrated records
        with pg_conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM accounts")
            print("PostgreSQL Accounts:", cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM transactions")
            print("PostgreSQL Transactions:", cursor.fetchone()[0])

    finally:
        if pg_conn is not None:
            pg_conn.close()

        sqlite_conn.close()


if __name__ == "__main__":
    try:
        migrate_data()
    except Exception as error:
        print("\nMigration failed:", error)
        print("Check the error before retrying.")
