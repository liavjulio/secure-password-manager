"""
Cryptographic Utilities for Secure Password Manager
Handles AES encryption and decryption of stored passwords.
"""

import base64
import secrets
import logging
from typing import Union
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Configure logging
logger = logging.getLogger(__name__)

# Encryption constants
AES_KEY_SIZE = 32  # 256 bits
IV_SIZE = 16       # 128 bits for AES-GCM
TAG_SIZE = 16      # 128 bits for GCM authentication tag
SALT_SIZE = 32     # 256 bits for PBKDF2 salt
PBKDF2_ITERATIONS = 100000  # OWASP recommended minimum


def derive_key_from_master(master_key: str, salt: bytes) -> bytes:
    """
    Derive encryption key from master key using PBKDF2.
    
    Args:
        master_key (str): User's master encryption key
        salt (bytes): Random salt for key derivation
        
    Returns:
        bytes: Derived 256-bit encryption key
        
    Security Notes:
        - Uses PBKDF2 with SHA-256 and 100,000 iterations
        - Salt prevents rainbow table attacks
        - Key stretching increases brute force difficulty
    """
    if not master_key:
        raise ValueError("Master key cannot be empty")
    
    try:
        # Convert master key to bytes
        master_key_bytes = master_key.encode('utf-8')
        
        # Set up PBKDF2 key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=AES_KEY_SIZE,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        
        # Derive and return the key
        return kdf.derive(master_key_bytes)
        
    except Exception as e:
        logger.error(f"Key derivation failed: {str(e)}")
        raise RuntimeError("Key derivation failed") from e


def encrypt_password(plaintext_password: str, master_key: str) -> str:
    """
    Encrypt a password using AES-256-GCM.
    
    Args:
        plaintext_password (str): Password to encrypt
        master_key (str): User's master encryption key
        
    Returns:
        str: Base64-encoded encrypted data (salt + iv + tag + ciphertext)
        
    Security Features:
        - AES-256-GCM for authenticated encryption
        - Random IV for each encryption
        - PBKDF2 key derivation from master key
        - Authenticated encryption prevents tampering
    """
    if not plaintext_password:
        raise ValueError("Password cannot be empty")
    
    if not master_key:
        raise ValueError("Master key cannot be empty")
    
    try:
        # Generate random salt and IV
        salt = secrets.token_bytes(SALT_SIZE)
        iv = secrets.token_bytes(IV_SIZE)
        
        # Derive encryption key from master key
        key = derive_key_from_master(master_key, salt)
        
        # Convert password to bytes
        password_bytes = plaintext_password.encode('utf-8')
        
        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt the password
        ciphertext = encryptor.update(password_bytes) + encryptor.finalize()
        
        # Get authentication tag
        tag = encryptor.tag
        
        # Combine salt + iv + tag + ciphertext
        encrypted_data = salt + iv + tag + ciphertext
        
        # Return as base64-encoded string
        return base64.b64encode(encrypted_data).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Password encryption failed: {str(e)}")
        raise RuntimeError("Password encryption failed") from e


def decrypt_password(encrypted_password: str, master_key: str) -> str:
    """
    Decrypt a password using AES-256-GCM.
    
    Args:
        encrypted_password (str): Base64-encoded encrypted password
        master_key (str): User's master encryption key
        
    Returns:
        str: Decrypted plaintext password
        
    Raises:
        ValueError: If decryption fails or data is corrupted
        RuntimeError: If cryptographic operation fails
    """
    if not encrypted_password:
        raise ValueError("Encrypted password cannot be empty")
    
    if not master_key:
        raise ValueError("Master key cannot be empty")
    
    try:
        # Decode from base64
        encrypted_data = base64.b64decode(encrypted_password.encode('utf-8'))
        
        # Verify minimum length
        min_length = SALT_SIZE + IV_SIZE + TAG_SIZE
        if len(encrypted_data) < min_length:
            raise ValueError("Invalid encrypted data format")
        
        # Extract components
        salt = encrypted_data[:SALT_SIZE]
        iv = encrypted_data[SALT_SIZE:SALT_SIZE + IV_SIZE]
        tag = encrypted_data[SALT_SIZE + IV_SIZE:SALT_SIZE + IV_SIZE + TAG_SIZE]
        ciphertext = encrypted_data[SALT_SIZE + IV_SIZE + TAG_SIZE:]
        
        # Derive decryption key
        key = derive_key_from_master(master_key, salt)
        
        # Create AES-GCM cipher for decryption
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt and verify authentication
        plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Convert back to string
        return plaintext_bytes.decode('utf-8')
        
    except ValueError as e:
        logger.warning(f"Password decryption failed - invalid data: {str(e)}")
        raise ValueError("Invalid encrypted password data") from e
    except Exception as e:
        logger.error(f"Password decryption failed: {str(e)}")
        raise RuntimeError("Password decryption failed") from e


def change_password_encryption(old_encrypted: str, old_master_key: str, new_master_key: str) -> str:
    """
    Re-encrypt a password with a new master key.
    
    Args:
        old_encrypted (str): Password encrypted with old master key
        old_master_key (str): Current master key
        new_master_key (str): New master key
        
    Returns:
        str: Password encrypted with new master key
        
    Security Notes:
        - Used when user changes master password
        - Decrypts with old key and encrypts with new key
        - Never stores plaintext password
    """
    try:
        # Decrypt with old key
        plaintext = decrypt_password(old_encrypted, old_master_key)
        
        # Encrypt with new key
        new_encrypted = encrypt_password(plaintext, new_master_key)
        
        # Clear plaintext from memory (Python limitation)
        plaintext = None
        
        return new_encrypted
        
    except Exception as e:
        logger.error(f"Password re-encryption failed: {str(e)}")
        raise RuntimeError("Password re-encryption failed") from e


def generate_encryption_key() -> str:
    """
    Generate a cryptographically secure master encryption key.
    
    Returns:
        str: 64-character hexadecimal key
        
    Security Notes:
        - Uses secrets module for cryptographic randomness
        - 256 bits of entropy
        - Suitable for use as master encryption key
    """
    return secrets.token_hex(32)  # 32 bytes = 256 bits


def verify_encryption_integrity(encrypted_password: str, master_key: str) -> bool:
    """
    Verify that encrypted password can be decrypted without corruption.
    
    Args:
        encrypted_password (str): Encrypted password to verify
        master_key (str): Master encryption key
        
    Returns:
        bool: True if password can be decrypted successfully
        
    Note: This is useful for data integrity checks but should be used sparingly
    """
    try:
        decrypt_password(encrypted_password, master_key)
        return True
    except Exception:
        return False


def secure_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.
    
    Args:
        a (str): First string
        b (str): Second string
        
    Returns:
        bool: True if strings are equal
        
    Security Notes:
        - Prevents timing attacks on password/token comparison
        - Always compares full length regardless of differences
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    
    return result == 0


class EncryptionError(Exception):
    """Custom exception for encryption-related errors"""
    pass


class DecryptionError(Exception):
    """Custom exception for decryption-related errors"""
    pass
