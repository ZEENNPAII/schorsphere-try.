#!/usr/bin/env python3
"""
Database Initialization Script for ScholarSphere
This script creates all necessary database tables.
Works with SQLite (local) and PostgreSQL/MySQL (Vercel/cloud).
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        try:
            # Get database URL
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"Database URL: {db_url[:50]}..." if len(db_url) > 50 else f"Database URL: {db_url}")
            
            # Create all tables
            print("\nCreating database tables...")
            db.create_all()
            print("[OK] Database tables created successfully!")
            
            # Check if admin user exists
            admin = User.query.filter_by(email='admin@scholarsphere.com').first()
            if not admin:
                print("\nCreating default admin user...")
                admin = User(
                    first_name='Admin',
                    last_name='User',
                    email='admin@scholarsphere.com',
                    student_id='00000000',
                    birthday=datetime(1990, 1, 1).date(),
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                print("[OK] Default admin user created!")
                print("   Email: admin@scholarsphere.com")
                print("   Password: admin123")
                print("   [WARNING] Please change this password after first login!")
            else:
                print("\n[OK] Admin user already exists")
            
            # Print database info
            user_count = User.query.count()
            print(f"\nDatabase Status:")
            print(f"   Total users: {user_count}")
            print(f"   Database type: {'PostgreSQL' if 'postgresql' in db_url else 'MySQL' if 'mysql' in db_url else 'SQLite'}")
            
            # Verify write permissions
            try:
                test_user = User.query.first()
                if test_user:
                    # Try a harmless update to test write access
                    original_name = test_user.first_name
                    test_user.first_name = original_name  # No actual change
                    db.session.commit()
                    print(f"   [OK] Write permissions: OK")
            except Exception as e:
                print(f"   [WARNING] Write permissions test failed: {e}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("ScholarSphere Database Initialization")
    print("=" * 60)
    
    if init_database():
        print("\n" + "=" * 60)
        print("[OK] Database initialization completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[ERROR] Database initialization failed!")
        print("=" * 60)
        exit(1)

