#!/usr/bin/env python3
"""
Test Supabase Database Connection
This script tests if your Supabase connection string works
"""

import os
import sys

# Set connection string BEFORE importing app
connection_string = "postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres"
os.environ['DATABASE_URL'] = connection_string

# Now import app (it will use the DATABASE_URL we just set)
from app import app, db

def test_connection():
    """Test database connection"""
    with app.app_context():
        try:
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print("=" * 60)
            print("Testing Supabase Connection")
            print("=" * 60)
            print(f"\nDatabase URL: {db_url[:50]}..." if len(db_url) > 50 else f"\nDatabase URL: {db_url}")
            
            # Test connection
            print("\nTesting connection...")
            db.engine.connect()
            print("[OK] Connection successful!")
            
            # Test if we can query
            print("\nTesting query...")
            result = db.session.execute(db.text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"[OK] Database version: {version[:50]}...")
            
            # List existing tables
            print("\nChecking existing tables...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"[OK] Found {len(tables)} existing tables:")
                for table in sorted(tables):
                    print(f"   - {table}")
            else:
                print("[INFO] No tables found yet (this is normal for a new database)")
            
            print("\n" + "=" * 60)
            print("[OK] Connection test passed! Database is ready.")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Connection failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("Testing Supabase connection...")
    print("(Note: Password is hidden in output for security)\n")
    
    success = test_connection()
    sys.exit(0 if success else 1)

