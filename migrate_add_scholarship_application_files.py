#!/usr/bin/env python3
"""
Migration: Add scholarship_application_files table
This table will link scholarship applications with credential files
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
        
        # Create scholarship_application_files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scholarship_application_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                credential_id INTEGER NOT NULL,
                requirement_type VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES scholarship_applications (id) ON DELETE CASCADE,
                FOREIGN KEY (credential_id) REFERENCES credentials (id) ON DELETE CASCADE,
                UNIQUE(application_id, credential_id, requirement_type)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_application_files_app_id 
            ON scholarship_application_files (application_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_application_files_cred_id 
            ON scholarship_application_files (credential_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_application_files_req_type 
            ON scholarship_application_files (requirement_type)
        """)
        
        conn.commit()
        print("✅ Successfully created scholarship_application_files table")
        
        # Verify table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scholarship_application_files'")
        if cursor.fetchone():
            print("✅ Table verification successful")
        else:
            print("❌ Table verification failed")
            return False
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("Starting migration: Add scholarship_application_files table")
    print("=" * 60)
    
    success = migrate()
    
    if success:
        print("=" * 60)
        print("✅ Migration completed successfully!")
    else:
        print("=" * 60)
        print("❌ Migration failed!")
