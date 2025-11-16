#!/usr/bin/env python3
"""
Setup Supabase Database with Your Connection String
This will create all tables and admin user
"""

import os
import sys

# Set your Supabase connection string
connection_string = "postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres"
os.environ['DATABASE_URL'] = connection_string

# Now import app
from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_database():
    """Create all database tables and initial data"""
    with app.app_context():
        try:
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print("=" * 60)
            print("Setting Up Supabase Database")
            print("=" * 60)
            print(f"\nDatabase: Supabase PostgreSQL")
            print(f"Host: db.hnlypdmzvmdehrzunqke.supabase.co")
            print("\nCreating all database tables...")
            
            # Create all tables from SQLAlchemy models
            db.create_all()
            print("[OK] All database tables created successfully!")
            
            # Create additional tables
            try:
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
                
                # Create indexes
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_remarks_app_id ON application_remarks(application_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_remarks_provider_id ON application_remarks(provider_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_application_files_app_id ON scholarship_application_files(application_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_application_files_cred_id ON scholarship_application_files(credential_id)"))
                db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_application_files_req_type ON scholarship_application_files(requirement_type)"))
                
                db.session.commit()
                print("[OK] Additional tables created!")
            except Exception as e:
                db.session.rollback()
                if "already exists" not in str(e).lower():
                    print(f"[INFO] Additional tables: {e}")
            
            # Create admin user
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
                print("[OK] Admin user created!")
                print("   Email: admin@scholarsphere.com")
                print("   Password: admin123")
            else:
                print("\n[OK] Admin user already exists")
            
            # List tables
            try:
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"\nDatabase Tables ({len(tables)}):")
                for table in sorted(tables):
                    print(f"   - {table}")
            except:
                pass
            
            user_count = User.query.count()
            print(f"\nTotal users: {user_count}")
            
            print("\n" + "=" * 60)
            print("[OK] Database setup completed successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Add DATABASE_URL to Vercel environment variables")
            print("2. Deploy your app to Vercel")
            print("3. Test account creation and login")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)

