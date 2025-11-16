"""
Authentication routes for Scholarsphere
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.role == 'student':
            return redirect(url_for('students.dashboard'))
        elif current_user.role == 'provider':
            return redirect(url_for('provider.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        
        if not identifier or not password:
            flash('Please provide your ID/email and password.', 'error')
            return render_template('auth/login.html')
        
        # Check if identifier is student ID (8 digits) or email
        is_student_id = re.match(r'^\d{8}$', identifier)
        
        # Use SQLAlchemy ORM - import from app
        try:
            from app import db, User
            
            # Query user using ORM
            if is_student_id:
                user = User.query.filter_by(student_id=identifier).first()
            else:
                # Case-insensitive email lookup
                user = User.query.filter(User.email.ilike(identifier)).first()
                
        except Exception as e:
            # If ORM fails, log error and return
            import traceback
            print(f"Database query error: {e}")
            traceback.print_exc()
            flash('Database connection error. Please try again later.', 'error')
            return render_template('auth/login.html')
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            
            # Redirect based on role
            if user.role == 'student':
                return redirect(url_for('students.dashboard'))
            elif user.role == 'provider':
                return redirect(url_for('provider.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        email = request.form.get('email', '').strip()
        student_id = request.form.get('studentId', '').strip()
        birthday = request.form.get('birthday', '')
        password = request.form.get('password', '')
        repeat_password = request.form.get('repeatPassword', '')
        
        # Validation
        if not all([first_name, last_name, email, student_id, birthday, password, repeat_password]):
            flash('Please complete all fields.', 'error')
            return render_template('auth/signup.html')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Invalid email address.', 'error')
            return render_template('auth/signup.html')
        
        if not re.match(r'^\d{8}$', student_id):
            flash('Student ID must be exactly 8 digits.', 'error')
            return render_template('auth/signup.html')
        
        if password != repeat_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/signup.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/signup.html')
        
        # Check for existing user using SQLAlchemy ORM
        try:
            from app import db, User
            
            existing_user = User.query.filter(
                (User.email.ilike(email)) | (User.student_id == student_id)
            ).first()
            
            if existing_user:
                flash('An account with this email or student ID already exists.', 'error')
                return render_template('auth/signup.html')
            
            # Create new user using ORM
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email.lower(),
                student_id=student_id,
                birthday=datetime.strptime(birthday, '%Y-%m-%d').date(),
                role='student',
                is_active=True
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully. Please sign in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            # Rollback on error
            try:
                db.session.rollback()
            except:
                pass
            
            # Log error for debugging
            import traceback
            print(f"Error creating user: {e}")
            traceback.print_exc()
            
            flash(f'Failed to create account: {str(e)}. Please try again.', 'error')
            return render_template('auth/signup.html')
    
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
