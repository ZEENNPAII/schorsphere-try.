#!/usr/bin/env python3
"""
Migration: Add application_remarks table
This table stores provider remarks/reviews for scholarship applications
"""

import sqlite3
import os
from datetime import datetime

def migrate():
    # Get database path
    db_path = os.path.join('instance', 'scholarsphere.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the application first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create application_remarks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_remarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                provider_id INTEGER NOT NULL,
                remark_text TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'review',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                FOREIGN KEY (application_id) REFERENCES scholarship_applications (id) ON DELETE CASCADE,
                FOREIGN KEY (provider_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_remarks_app_id 
            ON application_remarks (application_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_remarks_provider_id 
            ON application_remarks (provider_id)
        """)
        
        conn.commit()
        print("Successfully created application_remarks table")
        
        # Verify table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='application_remarks'")
        if cursor.fetchone():
            print("Table verification successful")
        else:
            print("Table verification failed")
            return False
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("Starting migration: Add application_remarks table")
    print("=" * 60)
    
    success = migrate()
    
    if success:
        print("=" * 60)
        print("Migration completed successfully!")
    else:
        print("=" * 60)
        print("Migration failed!")


