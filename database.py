"""
database.py
-----------
Handles SQLite database connection and table creation.

This file is responsible for:
1. Creating the crm.db database file
2. Creating the tickets and notes tables
3. Providing a get_db_connection() function for other files to use
"""

import sqlite3
from pathlib import Path

# Path to the SQLite database file
DB_PATH = Path(__file__).parent / "crm.db"


def get_db_connection():
    """
    Returns a connection to the SQLite database.

    In data engineering terms: this is like getting a Spark session
    or a boto3 redshift client. You call this function whenever you
    need to run a SQL query.

    The 'row_factory = sqlite3.Row' line makes query results return
    as dictionaries instead of tuples, so you can do result['ticket_id']
    instead of result[0].
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return conn


def init_db():
    """
    Creates the database tables if they don't exist.

    This function runs once when the app starts (called from main.py).
    It's idempotent: running it multiple times is safe because of
    'CREATE TABLE IF NOT EXISTS'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            ai_summary TEXT,
            ai_priority TEXT,
            ai_priority_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            note_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


# If you run this file directly (python database.py), it will create the tables
if __name__ == "__main__":
    init_db()
    print(f"📁 Database file created at: {DB_PATH.absolute()}")
