"""
Authentication Utilities for Secure Password Manager
Handles password hashing and verification using bcrypt.
"""

import bcrypt
import logging
from typing import Union

# Configure logging for authentication events
logger = logging.getLogger(__name__)

# bcrypt configuration
BCRYPT_ROUNDS = 12  # Recommended salt rounds for security vs performance balance

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with salt.
    
    Args:
        password (str): Plain text password to hash
        
    Returns:
        str: Base64-encoded bcrypt hash
        
    Security Notes:
        - Uses 12 salt rounds (recommended for 2024)
        - Automatically generates random salt
        - Returns hash as string for database storage
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    try:
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string for database storage
        return hashed.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Password hashing failed: {str(e)}")
        raise RuntimeError("Password hashing failed") from e


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its bcrypt hash.
    
    Args:
        password (str): Plain text password to verify
        password_hash (str): Stored bcrypt hash from database
        
    Returns:
        bool: True if password matches, False otherwise
        
    Security Notes:
        - Constant-time comparison prevents timing attacks
        - Handles invalid hashes gracefully
        - Logs failed verification attempts
    """
    if not password or not password_hash:
        logger.warning("Password or hash is empty during verification")
        return False
    
    try:
        # Convert to bytes for bcrypt
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        
        # Verify password using bcrypt's secure comparison
        result = bcrypt.checkpw(password_bytes, hash_bytes)
        
        if not result:
            logger.warning("Password verification failed")
        
        return result
        
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Check if a password meets security requirements.
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_strong: bool, issues: list[str])
        
    Security Requirements:
        - Minimum 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains digit
        - Contains special character
        - Not in common password list
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        issues.append("Password must be less than 128 characters")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one digit")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        issues.append("Password must contain at least one special character")
    
    # Check against common passwords
    common_passwords = {
        'password', 'password123', '123456', 'qwerty', 'abc123',
        'password1', 'admin', 'letmein', 'welcome', 'monkey'
    }
    
    if password.lower() in common_passwords:
        issues.append("Password is too common")
    
    return len(issues) == 0, issues


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a cryptographically secure random password.
    
    Args:
        length (int): Desired password length (minimum 12)
        
    Returns:
        str: Randomly generated secure password
        
    Security Notes:
        - Uses secrets module for cryptographic randomness
        - Includes mix of uppercase, lowercase, digits, and symbols
        - Avoids ambiguous characters (0, O, l, 1)
    """
    import secrets
    import string
    
    if length < 12:
        raise ValueError("Password length must be at least 12 characters")
    
    # Character sets (excluding ambiguous characters)
    uppercase = 'ABCDEFGHJKLMNPQRSTUVWXYZ'  # Excludes I, O
    lowercase = 'abcdefghijkmnopqrstuvwxyz'  # Excludes l, o
    digits = '23456789'  # Excludes 0, 1
    symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    # Ensure password contains at least one character from each set
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]
    
    # Fill remaining length with random characters from all sets
    all_chars = uppercase + lowercase + digits + symbols
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password list
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def validate_username(username: str) -> tuple[bool, list[str]]:
    """
    Validate username according to security requirements.
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid: bool, issues: list[str])
    """
    issues = []
    
    if not username:
        issues.append("Username cannot be empty")
        return False, issues
    
    if len(username) < 3:
        issues.append("Username must be at least 3 characters long")
    
    if len(username) > 30:
        issues.append("Username must be less than 30 characters")
    
    # Allow alphanumeric and underscore only
    if not username.replace('_', '').isalnum():
        issues.append("Username can only contain letters, numbers, and underscores")
    
    # Must start with letter
    if not username[0].isalpha():
        issues.append("Username must start with a letter")
    
    return len(issues) == 0, issues


def validate_email(email: str) -> tuple[bool, list[str]]:
    """
    Basic email validation.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        tuple: (is_valid: bool, issues: list[str])
    """
    import re
    
    issues = []
    
    if not email:
        issues.append("Email cannot be empty")
        return False, issues
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        issues.append("Invalid email format")
    
    if len(email) > 254:
        issues.append("Email address is too long")
    
    return len(issues) == 0, issues
