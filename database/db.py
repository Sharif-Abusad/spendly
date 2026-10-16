import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = 'spendly.db'

def get_db():
    """
    Opens connection to spendly.db in project root.
    Sets row_factory to sqlite3.Row and enables foreign key constraints.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Creates users and expenses tables using CREATE TABLE IF NOT EXISTS.
    Ensures schema is ready before app usage.
    """
    conn = get_db()
    try:
        with conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

            # Expenses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
    finally:
        conn.close()

def seed_db():
    """
    Seeds the database with one demo user and 8 sample expenses.
    Prevents duplicate inserts by checking if users already exist.
    """
    conn = get_db()
    try:
        # Check if users table already contains data
        cursor = conn.execute("SELECT 1 FROM users LIMIT 1")
        if cursor.fetchone():
            return

        with conn:
            # 1. Insert demo user
            # Name: Demo User, Email: demo@spendly.com, Password: demo123
            hashed_password = generate_password_hash("demo123")
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo User", "demo@spendly.com", hashed_password)
            )
            user_id = cursor.lastrowid

            # 2. Insert 8 sample expenses
            # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
            # Ensure all 7 categories are covered
            sample_expenses = [
                (user_id, 15.50, "Food", "2023-10-01", "Lunch at cafe"),
                (user_id, 25.00, "Transport", "2023-10-02", "Taxi to airport"),
                (user_id, 120.00, "Bills", "2023-10-03", "Electricity bill"),
                (user_id, 45.00, "Health", "2023-10-04", "Pharmacy"),
                (user_id, 20.00, "Entertainment", "2023-10-05", "Movie ticket"),
                (user_id, 60.00, "Shopping", "2023-10-06", "New shirt"),
                (user_id, 10.00, "Other", "2023-10-07", "Miscellaneous"),
                (user_id, 30.00, "Food", "2023-10-08", "Dinner out"),
            ]

            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                sample_expenses
            )
    finally:
        conn.close()
