"""
Test Suite for Secure Password Manager
Comprehensive tests for all security-critical components.
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCryptoUtils(unittest.TestCase):
    """Test cryptographic functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        from crypto_utils import encrypt_password, decrypt_password, generate_encryption_key
        self.encrypt_password = encrypt_password
        self.decrypt_password = decrypt_password
        self.generate_encryption_key = generate_encryption_key
    
    def test_password_encryption_decryption(self):
        """Test basic encryption and decryption"""
        password = "test_password_123!"
        master_key = "master_key_for_testing"
        
        # Encrypt password
        encrypted = self.encrypt_password(password, master_key)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, password)
        
        # Decrypt password
        decrypted = self.decrypt_password(encrypted, master_key)
        self.assertEqual(decrypted, password)
    
    def test_encryption_with_different_keys(self):
        """Test that different keys produce different ciphertexts"""
        password = "same_password"
        key1 = "key_one"
        key2 = "key_two"
        
        encrypted1 = self.encrypt_password(password, key1)
        encrypted2 = self.encrypt_password(password, key2)
        
        self.assertNotEqual(encrypted1, encrypted2)
    
    def test_encryption_randomness(self):
        """Test that encryption produces different outputs for same input"""
        password = "same_password"
        master_key = "same_key"
        
        encrypted1 = self.encrypt_password(password, master_key)
        encrypted2 = self.encrypt_password(password, master_key)
        
        # Should be different due to random IV
        self.assertNotEqual(encrypted1, encrypted2)
        
        # But both should decrypt to same password
        decrypted1 = self.decrypt_password(encrypted1, master_key)
        decrypted2 = self.decrypt_password(encrypted2, master_key)
        
        self.assertEqual(decrypted1, password)
        self.assertEqual(decrypted2, password)
    
    def test_wrong_key_decryption(self):
        """Test that wrong key fails decryption"""
        password = "test_password"
        correct_key = "correct_key"
        wrong_key = "wrong_key"
        
        encrypted = self.encrypt_password(password, correct_key)
        
        with self.assertRaises(Exception):
            self.decrypt_password(encrypted, wrong_key)
    
    def test_empty_password_encryption(self):
        """Test encryption with empty password"""
        with self.assertRaises(ValueError):
            self.encrypt_password("", "some_key")
    
    def test_empty_key_encryption(self):
        """Test encryption with empty key"""
        with self.assertRaises(ValueError):
            self.encrypt_password("password", "")
    
    def test_generate_encryption_key(self):
        """Test encryption key generation"""
        key = self.generate_encryption_key()
        
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), 64)  # 32 bytes * 2 for hex
        
        # Generate another key and ensure they're different
        key2 = self.generate_encryption_key()
        self.assertNotEqual(key, key2)


class TestAuthUtils(unittest.TestCase):
    """Test authentication functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        from auth import hash_password, verify_password, is_password_strong, validate_username, validate_email
        self.hash_password = hash_password
        self.verify_password = verify_password
        self.is_password_strong = is_password_strong
        self.validate_username = validate_username
        self.validate_email = validate_email
    
    def test_password_hashing_verification(self):
        """Test password hashing and verification"""
        password = "test_password_123!"
        
        # Hash password
        hashed = self.hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(hashed, password)
        
        # Verify correct password
        self.assertTrue(self.verify_password(password, hashed))
        
        # Verify wrong password
        self.assertFalse(self.verify_password("wrong_password", hashed))
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes"""
        password = "same_password"
        
        hash1 = self.hash_password(password)
        hash2 = self.hash_password(password)
        
        # Hashes should be different due to salt
        self.assertNotEqual(hash1, hash2)
        
        # But both should verify correctly
        self.assertTrue(self.verify_password(password, hash1))
        self.assertTrue(self.verify_password(password, hash2))
    
    def test_empty_password_hashing(self):
        """Test hashing empty password"""
        with self.assertRaises(ValueError):
            self.hash_password("")
    
    def test_short_password_hashing(self):
        """Test hashing password that's too short"""
        with self.assertRaises(ValueError):
            self.hash_password("short")
    
    def test_password_strength_validation(self):
        """Test password strength checking"""
        # Strong password
        strong_pass = "MyStr0ng!P@ssw0rd"
        is_strong, issues = self.is_password_strong(strong_pass)
        self.assertTrue(is_strong)
        self.assertEqual(len(issues), 0)
        
        # Weak password
        weak_pass = "password"
        is_strong, issues = self.is_password_strong(weak_pass)
        self.assertFalse(is_strong)
        self.assertGreater(len(issues), 0)
        
        # Common password
        common_pass = "password123"
        is_strong, issues = self.is_password_strong(common_pass)
        self.assertFalse(is_strong)
        self.assertIn("Password is too common", issues)
    
    def test_username_validation(self):
        """Test username validation"""
        # Valid username
        valid, issues = self.validate_username("valid_user123")
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)
        
        # Invalid username - too short
        valid, issues = self.validate_username("ab")
        self.assertFalse(valid)
        self.assertGreater(len(issues), 0)
        
        # Invalid username - starts with number
        valid, issues = self.validate_username("123user")
        self.assertFalse(valid)
        self.assertGreater(len(issues), 0)
    
    def test_email_validation(self):
        """Test email validation"""
        # Valid email
        valid, issues = self.validate_email("user@example.com")
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)
        
        # Invalid email
        valid, issues = self.validate_email("invalid_email")
        self.assertFalse(valid)
        self.assertGreater(len(issues), 0)


class TestModels(unittest.TestCase):
    """Test database models"""
    
    def setUp(self):
        """Set up test database"""
        from flask import Flask
        from models import db, User, Password
        
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.User = User
        self.Password = Password
        self.db = db
    
    def tearDown(self):
        """Clean up test database"""
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test user model creation"""
        from auth import hash_password
        
        username = "testuser"
        email = "test@example.com"
        password_hash = hash_password("testpassword123!")
        
        user = self.User(username=username, email=email, password_hash=password_hash)
        self.db.session.add(user)
        self.db.session.commit()
        
        # Verify user was created
        retrieved_user = self.User.query.filter_by(username=username).first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, username)
        self.assertEqual(retrieved_user.email, email)
        self.assertIsNotNone(retrieved_user.encryption_key)
        self.assertEqual(len(retrieved_user.encryption_key), 64)  # 32 bytes hex
    
    def test_password_entry_creation(self):
        """Test password entry model creation"""
        from auth import hash_password
        from crypto_utils import encrypt_password
        
        # Create user first
        user = self.User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("testpassword123!")
        )
        self.db.session.add(user)
        self.db.session.commit()
        
        # Create password entry
        service = "Gmail"
        username = "test@gmail.com"
        plain_password = "gmail_password_123!"
        encrypted_password = encrypt_password(plain_password, user.encryption_key)
        
        password_entry = self.Password(
            user_id=user.id,
            service=service,
            username=username,
            encrypted_password=encrypted_password,
            url="https://gmail.com",
            notes="Personal email account"
        )
        self.db.session.add(password_entry)
        self.db.session.commit()
        
        # Verify password entry
        retrieved_entry = self.Password.query.filter_by(service=service).first()
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry.service, service)
        self.assertEqual(retrieved_entry.username, username)
        self.assertEqual(retrieved_entry.user_id, user.id)
        
        # Verify password can be decrypted
        from crypto_utils import decrypt_password
        decrypted = decrypt_password(retrieved_entry.encrypted_password, user.encryption_key)
        self.assertEqual(decrypted, plain_password)


class TestApplicationRoutes(unittest.TestCase):
    """Test Flask application routes"""
    
    def setUp(self):
        """Set up test application"""
        import tempfile
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Import app after setting up database
        from app import app, db
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        self.app = app
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test application"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_index_route(self):
        """Test home page route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SecurePass', response.data)
    
    def test_register_route(self):
        """Test user registration"""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Should redirect to login page after successful registration
    
    def test_login_route(self):
        """Test user login"""
        # First register a user
        self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!'
        })
        
        # Then try to login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'TestPassword123!'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_protected_routes_redirect(self):
        """Test that protected routes redirect to login"""
        protected_routes = ['/dashboard', '/add_password']
        
        for route in protected_routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 302)  # Redirect to login


class TestSecurity(unittest.TestCase):
    """Test security measures"""
    
    def setUp(self):
        """Set up test application"""
        import tempfile
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Import app after setting up database
        from app import app, db
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        self.app = app
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test application"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        # This would be more comprehensive in a real security audit
        with self.app.app_context():
            from models import get_user_by_username
            
            # Try SQL injection in username
            malicious_username = "'; DROP TABLE users; --"
            user = get_user_by_username(malicious_username)
            self.assertIsNone(user)  # Should not find user or cause error
    
    def test_password_timing_attack_protection(self):
        """Test constant-time password comparison"""
        from crypto_utils import secure_compare
        
        import time
        
        # Test equal strings
        start = time.time()
        result1 = secure_compare("password123", "password123")
        end_time1 = time.time() - start
        
        # Test different strings
        start = time.time()
        result2 = secure_compare("password123", "different123")
        end_time2 = time.time() - start
        
        self.assertTrue(result1)
        self.assertFalse(result2)
        
        # Time difference should be minimal (constant time)
        time_diff = abs(end_time1 - end_time2)
        self.assertLess(time_diff, 0.01)  # Should be less than 10ms difference
        # Note: This is a basic test; real timing attack tests require more sophisticated analysis


def run_tests():
    """Run all tests"""
    print("🧪 Running Secure Password Manager Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_modules = [
        TestCryptoUtils,
        TestAuthUtils,
        TestModels,
        TestApplicationRoutes,
        TestSecurity
    ]
    
    suite = unittest.TestSuite()
    
    for test_module in test_modules:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_module)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
