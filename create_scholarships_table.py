#!/usr/bin/env python3
"""
Create a minimal scholarships table if it doesn't exist.
"""
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'scholarsphere.db')

def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Create table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            title TEXT NOT NULL,
            provider_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'approved',
            applications_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(provider_id) REFERENCES users(id)
        )
        """
    )

    # Do not seed mock scholarship data here to avoid polluting production database
    conn.commit()
    conn.close()
    print('Scholarships table ensured')

if __name__ == '__main__':
    main()





