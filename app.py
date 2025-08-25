"""
Secure Password Manager - Main Application
A Flask-based password manager with AES encryption and secure authentication.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Use relative path that works on any system
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "instance", "password_manager.db")}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Development configuration - disable template and static file caching
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

# Initialize extensions
from models import db
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import models after db initialization
from models import User, Password
from auth import verify_password, hash_password
from crypto_utils import encrypt_password, decrypt_password
from forms import LoginForm, RegisterForm, PasswordForm

# Configure logging for security events
logging.basicConfig(
    filename='security.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with secure password hashing"""
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', form=form)
        
        # Create new user with hashed password
        try:
            hashed_password = hash_password(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Log security event
            logging.info(f"New user registered: {username} from IP: {request.remote_addr}")
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error for {username}: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with secure authentication"""
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and verify_password(password, user.password_hash):
            login_user(user, remember=remember)
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # Log successful login
            logging.info(f"Successful login: {username} from IP: {request.remote_addr}")
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            flash(f'Welcome back, {username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            # Log failed login attempt
            logging.warning(f"Failed login attempt: {username} from IP: {request.remote_addr}")
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logging.info(f"User logged out: {username}")
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing user's stored passwords"""
    passwords = Password.query.filter_by(user_id=current_user.id).all()
    
    # Decrypt passwords for display (only in memory, never stored decrypted)
    decrypted_passwords = []
    for pwd in passwords:
        try:
            decrypted_pwd = decrypt_password(pwd.encrypted_password, current_user.encryption_key)
            decrypted_passwords.append({
                'id': pwd.id,
                'service': pwd.service,
                'username': pwd.username,
                'password': decrypted_pwd,
                'url': pwd.url,
                'notes': pwd.notes,
                'created_at': pwd.created_at,
                'updated_at': pwd.updated_at
            })
        except Exception as e:
            logging.error(f"Decryption error for password ID {pwd.id}: {str(e)}")
            # Skip corrupted entries
            continue
    
    return render_template('dashboard.html', passwords=decrypted_passwords)

@app.route('/add_password', methods=['GET', 'POST'])
@login_required
def add_password():
    """Add a new password entry"""
    form = PasswordForm()
    
    if form.validate_on_submit():
        service = form.service.data
        username = form.username.data
        password = form.password.data
        url = form.url.data
        notes = form.notes.data
        
        try:
            # Encrypt the password before storing
            encrypted_password = encrypt_password(password, current_user.encryption_key)
            
            new_password = Password(
                user_id=current_user.id,
                service=service,
                username=username,
                encrypted_password=encrypted_password,
                url=url,
                notes=notes
            )
            
            db.session.add(new_password)
            db.session.commit()
            
            logging.info(f"Password added for service '{service}' by user {current_user.username}")
            flash(f'Password for {service} added successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding password for {current_user.username}: {str(e)}")
            flash('Failed to add password. Please try again.', 'error')
    
    return render_template('add_password.html', form=form)

@app.route('/edit_password/<int:password_id>', methods=['GET', 'POST'])
@login_required
def edit_password(password_id):
    """Edit an existing password entry"""
    password_entry = Password.query.filter_by(id=password_id, user_id=current_user.id).first_or_404()
    
    form = PasswordForm()
    
    if form.validate_on_submit():
        try:
            # Update the password entry
            password_entry.service = form.service.data
            password_entry.username = form.username.data
            password_entry.url = form.url.data
            password_entry.notes = form.notes.data
            password_entry.updated_at = datetime.now(timezone.utc)
            
            # Re-encrypt if password changed
            if form.password.data:
                password_entry.encrypted_password = encrypt_password(
                    form.password.data, 
                    current_user.encryption_key
                )
            
            db.session.commit()
            
            logging.info(f"Password updated for service '{password_entry.service}' by user {current_user.username}")
            flash(f'Password for {password_entry.service} updated successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating password for {current_user.username}: {str(e)}")
            flash('Failed to update password. Please try again.', 'error')
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        try:
            decrypted_password = decrypt_password(password_entry.encrypted_password, current_user.encryption_key)
            form.service.data = password_entry.service
            form.username.data = password_entry.username
            form.password.data = decrypted_password
            form.url.data = password_entry.url
            form.notes.data = password_entry.notes
        except Exception as e:
            logging.error(f"Error decrypting password for editing: {str(e)}")
            flash('Error loading password data.', 'error')
            return redirect(url_for('dashboard'))
    
    return render_template('edit_password.html', form=form, password_entry=password_entry)

@app.route('/delete_password/<int:password_id>', methods=['POST'])
@login_required
def delete_password(password_id):
    """Delete a password entry"""
    password_entry = Password.query.filter_by(id=password_id, user_id=current_user.id).first_or_404()
    
    try:
        service_name = password_entry.service
        db.session.delete(password_entry)
        db.session.commit()
        
        logging.info(f"Password deleted for service '{service_name}' by user {current_user.username}")
        flash(f'Password for {service_name} deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting password for {current_user.username}: {str(e)}")
        flash('Failed to delete password. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings and profile management"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate current password
            if not verify_password(current_password, current_user.password_hash):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('settings'))
            
            # Validate new password
            if len(new_password) < 8:
                flash('New password must be at least 8 characters long.', 'error')
                return redirect(url_for('settings'))
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('settings'))
            
            # Update password
            try:
                current_user.password_hash = hash_password(new_password)
                db.session.commit()
                flash('Password changed successfully.', 'success')
                logging.info(f"Password changed: user={current_user.username}")
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while changing password.', 'error')
                logging.error(f"Password change failed: user={current_user.username}, error={str(e)}")
        
        elif action == 'update_profile':
            username = request.form.get('username', '').strip()
            
            # Validate username
            if not username:
                flash('Username cannot be empty.', 'error')
                return redirect(url_for('settings'))
            
            if len(username) < 3:
                flash('Username must be at least 3 characters long.', 'error')
                return redirect(url_for('settings'))
            
            # Check if username is already taken (by another user)
            existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
            if existing_user:
                flash('Username is already taken.', 'error')
                return redirect(url_for('settings'))
            
            # Update username
            try:
                old_username = current_user.username
                current_user.username = username
                db.session.commit()
                flash('Profile updated successfully.', 'success')
                logging.info(f"Username changed: {old_username} -> {username}")
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while updating profile.', 'error')
                logging.error(f"Profile update failed: user={current_user.username}, error={str(e)}")
        
        elif action == 'delete_account':
            confirm_password = request.form.get('delete_confirm_password')
            
            # Validate password for account deletion
            if not verify_password(confirm_password, current_user.password_hash):
                flash('Password is incorrect. Account deletion cancelled.', 'error')
                return redirect(url_for('settings'))
            
            try:
                # Delete all user's passwords first
                Password.query.filter_by(user_id=current_user.id).delete()
                
                # Delete user account
                username = current_user.username
                db.session.delete(current_user)
                db.session.commit()
                
                # Log out the user
                logout_user()
                
                flash('Your account has been permanently deleted.', 'info')
                logging.info(f"Account deleted: user={username}")
                return redirect(url_for('register'))
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting account.', 'error')
                logging.error(f"Account deletion failed: user={current_user.username}, error={str(e)}")
    
    # Get user statistics for display
    password_count = Password.query.filter_by(user_id=current_user.id).count()
    
    return render_template('settings.html', 
                         password_count=password_count,
                         current_user=current_user)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    logging.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Run with SSL in production
    if os.getenv('FLASK_ENV') == 'production':
        app.run(
            host='0.0.0.0',
            port=443,
            ssl_context=(
                os.getenv('SSL_CERT_PATH'),
                os.getenv('SSL_KEY_PATH')
            )
        )
    else:
        app.run(debug=True, port=8080)
