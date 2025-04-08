from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from app import db
import models

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False, type=bool)
        
        user = db.session.query(models.User).filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            
            if next_page:
                return redirect(next_page)
            return redirect(url_for('admin_bp.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main_bp.index'))

@auth_bp.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    """Create first admin user (only works if no admin users exist)."""
    # Check if admin already exists
    if db.session.query(models.User).filter_by(is_admin=True).first():
        flash('Admin user already exists', 'warning')
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth_bp.create_admin'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth_bp.create_admin'))
        
        # Check if username or email already exists
        if db.session.query(models.User).filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth_bp.create_admin'))
        
        if db.session.query(models.User).filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth_bp.create_admin'))
        
        # Create new admin user
        new_admin = models.User(
            username=username,
            email=email,
            is_admin=True
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        
        try:
            db.session.commit()
            flash('Admin user created successfully! You can now log in.', 'success')
            return redirect(url_for('auth_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('auth/create_admin.html') 