#!/usr/bin/env python3
"""
Database Initialization Script for Secure Password Manager
Run this script to create the database tables.
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database with all required tables"""
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Use relative path that works on any system
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "instance", "password_manager.db")}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure instance directory exists
    instance_dir = os.path.join(basedir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    # Initialize database
    db = SQLAlchemy(app)
    
    # Define models here to avoid import issues
    from flask_login import UserMixin
    from datetime import datetime, timezone
    import secrets
    
    class User(UserMixin, db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(128), nullable=False)
        encryption_key = db.Column(db.String(64), nullable=False, default=lambda: secrets.token_hex(32))
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
        last_login = db.Column(db.DateTime)
        passwords = db.relationship('Password', backref='user', lazy=True, cascade='all, delete-orphan')
    
    class Password(db.Model):
        __tablename__ = 'passwords'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        service = db.Column(db.String(100), nullable=False)
        username = db.Column(db.String(100), nullable=False)
        url = db.Column(db.String(200))
        notes = db.Column(db.Text)
        encrypted_password = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
        updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            print("✅ Database initialized successfully!")
            print(f"📍 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("📋 Tables created:")
            print("   - users (for user authentication)")
            print("   - passwords (for encrypted password storage)")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def check_database():
    """Check if database exists and is properly configured"""
    
    # Use relative path that works on any system
    basedir = os.path.abspath(os.path.dirname(__file__))
    default_db_path = f'sqlite:///{os.path.join(basedir, "instance", "password_manager.db")}'
    db_path = os.getenv('DATABASE_URL', default_db_path)
    
    if db_path.startswith('sqlite:///'):
        file_path = db_path.replace('sqlite:///', '')
        if os.path.exists(file_path):
            print(f"✅ Database file exists: {file_path}")
            
            # Try to connect and check tables
            app = Flask(__name__)
            app.config['SQLALCHEMY_DATABASE_URI'] = db_path
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
            from models import db
            db.init_app(app)
            
            with app.app_context():
                if db.engine.has_table('users') and db.engine.has_table('passwords'):
                    print("✅ Database tables are properly configured")
                    return True
                else:
                    print("❌ Database tables are missing")
                    return False
        else:
            print(f"❌ Database file does not exist: {file_path}")
            return False
    else:
        print("⚠️  Using non-SQLite database, cannot check file existence")
        return True

def main():
    """Main function"""
    print("🔐 Secure Password Manager - Database Initialization")
    print("=" * 50)
    
    # Check if database already exists
    if check_database():
        print("\n📋 Database already exists and is properly configured.")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        
        if response != 'y':
            print("✅ Database check complete. No changes made.")
            return
        else:
            print("🔄 Recreating database...")
    
    # Initialize database
    if init_database():
        print("\n🎉 Database initialization complete!")
        print("\n📝 Next steps:")
        print("1. Run 'python app.py' to start the application")
        print("2. Open your browser to http://localhost:5000")
        print("3. Register a new account to get started")
        print("\n🔒 Security Notes:")
        print("- Change the SECRET_KEY in .env for production")
        print("- Use HTTPS in production environment")
        print("- Regular backups are recommended")
        
    else:
        print("\n❌ Database initialization failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
