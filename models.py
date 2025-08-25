"""
Database Models for Secure Password Manager
Defines User and Password models with appropriate security considerations.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import secrets

# Database instance - will be set by Flask-SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model for authentication and password management.
    
    Security Features:
    - Password hashes stored using bcrypt
    - Unique encryption key per user for password encryption
    - Session tracking for security auditing
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Unique encryption key for each user's passwords
    encryption_key = db.Column(db.String(64), nullable=False, default=lambda: secrets.token_hex(32))
    
    # Timestamps for security auditing
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationship to passwords (one-to-many)
    passwords = db.relationship('Password', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password_hash):
        """Initialize user with secure defaults"""
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.encryption_key = secrets.token_hex(32)  # Generate unique encryption key
        self.created_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)


class Password(db.Model):
    """
    Password storage model with AES encryption.
    
    Security Features:
    - Passwords encrypted using AES with user-specific keys
    - Metadata stored in plaintext for searchability
    - Audit trail with creation and modification timestamps
    """
    
    __tablename__ = 'passwords'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Service information (stored in plaintext for searchability)
    service = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Encrypted password (stored as base64-encoded ciphertext)
    encrypted_password = db.Column(db.Text, nullable=False)
    
    # Timestamps for audit trail
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __init__(self, user_id, service, username, encrypted_password, url=None, notes=None):
        """Initialize password entry with audit timestamps"""
        self.user_id = user_id
        self.service = service
        self.username = username
        self.encrypted_password = encrypted_password
        self.url = url
        self.notes = notes
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<Password {self.service} for {self.username}>'


# Database initialization function
def init_database(app):
    """
    Initialize the database with proper configuration.
    Should be called once during application setup.
    """
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Verify tables were created
        if not db.engine.has_table('users'):
            raise Exception("Failed to create users table")
        if not db.engine.has_table('passwords'):
            raise Exception("Failed to create passwords table")
        
        print("Database initialized successfully")


# Database utility functions
def get_user_password_count(user_id):
    """Get the number of passwords stored for a user"""
    return Password.query.filter_by(user_id=user_id).count()


def search_passwords(user_id, search_term):
    """Search passwords by service name or username"""
    return Password.query.filter_by(user_id=user_id).filter(
        db.or_(
            Password.service.ilike(f'%{search_term}%'),
            Password.username.ilike(f'%{search_term}%'),
            Password.url.ilike(f'%{search_term}%')
        )
    ).all()


def get_user_by_email(email):
    """Get user by email address"""
    return User.query.filter_by(email=email).first()


def get_user_by_username(username):
    """Get user by username"""
    return User.query.filter_by(username=username).first()
