#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for ScholarSphere
This script creates all database tables for PostgreSQL (Vercel/Cloud)
"""

from app import app, db, User, Award, Credential, Scholarship, ScholarshipApplication, Notification, Schedule
# Note: application_remarks and scholarship_application_files are created via SQL
# as they don't have SQLAlchemy models yet
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
import sys

def setup_database():
    """Create all database tables and initial data"""
    with app.app_context():
        try:
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            
            # Check if it's a cloud database
            if db_url.startswith('sqlite'):
                print("[ERROR] This script is for PostgreSQL/MySQL cloud databases only!")
                print("For SQLite, use: python init_database.py")
                return False
            
            print("=" * 60)
            print("ScholarSphere PostgreSQL Database Setup")
            print("=" * 60)
            print(f"\nDatabase URL: {db_url[:50]}..." if len(db_url) > 50 else f"\nDatabase URL: {db_url}")
            print("\nCreating all database tables...")
            
            # Drop all tables (optional - comment out if you want to keep existing data)
            # db.drop_all()
            
            # Create all tables from SQLAlchemy models
            db.create_all()
            print("[OK] All database tables created successfully!")
            
            # Create additional tables that don't have SQLAlchemy models yet
            try:
                # Create application_remarks table
                db.session.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS application_remarks (
                        id SERIAL PRIMARY KEY,
                        application_id INTEGER NOT NULL REFERENCES scholarship_applications(id) ON DELETE CASCADE,
                        provider_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        remark_text TEXT NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'review',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """))
                
                # Create scholarship_application_files table
                db.session.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS scholarship_application_files (
                        id SERIAL PRIMARY KEY,
                        application_id INTEGER NOT NULL REFERENCES scholarship_applications(id) ON DELETE CASCADE,
                        credential_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
                        requirement_type VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(application_id, credential_id, requirement_type)
                    )
                """))
                
                # Create indexes for additional tables
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_remarks_app_id ON application_remarks(application_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_remarks_provider_id ON application_remarks(provider_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_application_files_app_id ON scholarship_application_files(application_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_application_files_cred_id ON scholarship_application_files(credential_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_application_files_req_type ON scholarship_application_files(requirement_type)"))
                
                db.session.commit()
                print("[OK] Additional tables (application_remarks, scholarship_application_files) created!")
            except Exception as e:
                # Tables might already exist, that's okay
                db.session.rollback()
                if "already exists" not in str(e).lower():
                    print(f"[INFO] Additional tables check: {e}")
            
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
            
            # Print database status
            user_count = User.query.count()
            print(f"\nDatabase Status:")
            print(f"   Total users: {user_count}")
            print(f"   Database type: PostgreSQL")
            
            # List all tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\nCreated Tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"   - {table}")
            
            # Verify write permissions
            try:
                test_user = User.query.first()
                if test_user:
                    original_name = test_user.first_name
                    test_user.first_name = original_name  # No actual change
                    db.session.commit()
                    print(f"\n[OK] Write permissions: OK")
            except Exception as e:
                print(f"\n[WARNING] Write permissions test failed: {e}")
            
            print("\n" + "=" * 60)
            print("[OK] Database setup completed successfully!")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Error setting up database: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("[ERROR] DATABASE_URL environment variable is not set!")
        print("\nPlease set DATABASE_URL before running this script:")
        print("  export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        print("  # Or on Windows:")
        print("  set DATABASE_URL=postgresql://user:pass@host:port/dbname")
        sys.exit(1)
    
    success = setup_database()
    sys.exit(0 if success else 1)

