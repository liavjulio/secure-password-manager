#!/usr/bin/env python3
"""
Test script to verify password manager functionality
"""

import requests
import sys
import json

def test_app_functionality():
    """Test the web application functionality"""
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("🧪 Testing Secure Password Manager Functionality")
    print("=" * 60)
    
    # Test 1: Home page
    print("\n1. Testing home page...")
    try:
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Home page loads successfully")
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return False
    
    # Test 2: Register new user
    print("\n2. Testing user registration...")
    test_user = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!'
    }
    
    try:
        response = session.post(f"{base_url}/register", data=test_user)
        if response.status_code in [200, 302]:  # Success or redirect
            print("✅ User registration successful")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            # Try login instead if user already exists
            print("   Attempting to login with existing user...")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 3: Login
    print("\n3. Testing user login...")
    login_data = {
        'username': test_user['username'],
        'password': test_user['password']
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code in [200, 302]:
            print("✅ User login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 4: Dashboard access
    print("\n4. Testing dashboard access...")
    try:
        response = session.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard accessible")
            if 'password-item' in response.text:
                print("✅ Dashboard contains password items")
            else:
                print("ℹ️  Dashboard is empty (no passwords yet)")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False
    
    # Test 5: Add password
    print("\n5. Testing add password...")
    password_data = {
        'service': 'Test Gmail',
        'username': 'testuser@gmail.com',
        'password': 'MySecurePassword123!',
        'url': 'https://gmail.com',
        'notes': 'Test email account'
    }
    
    try:
        response = session.post(f"{base_url}/add_password", data=password_data)
        if response.status_code in [200, 302]:
            print("✅ Password addition successful")
        else:
            print(f"❌ Add password failed: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Add password error: {e}")
    
    # Test 6: Dashboard with password
    print("\n6. Testing dashboard with added password...")
    try:
        response = session.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            if 'Test Gmail' in response.text:
                print("✅ Added password appears in dashboard")
                
                # Check for JavaScript functions
                if 'togglePasswordVisibility' in response.text:
                    print("✅ Password visibility toggle function present")
                else:
                    print("❌ Password visibility toggle function missing")
                
                if 'copyToClipboard' in response.text:
                    print("✅ Copy to clipboard function present")
                else:
                    print("❌ Copy to clipboard function missing")
                
                if 'confirmDelete' in response.text:
                    print("✅ Delete confirmation function present")
                else:
                    print("❌ Delete confirmation function missing")
                    
            else:
                print("❌ Added password does not appear in dashboard")
        else:
            print(f"❌ Dashboard access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Functionality test completed!")
    print("\nTo test the buttons manually:")
    print("1. Open http://localhost:5001 in your browser")
    print("2. Register/login with the test account")
    print("3. Go to dashboard and test:")
    print("   - Click the eye icon to show/hide passwords")
    print("   - Click the clipboard icon to copy passwords")
    print("   - Click the trash icon to delete passwords")
    print("   - Use the search functionality")
    
    return True

if __name__ == "__main__":
    success = test_app_functionality()
    sys.exit(0 if success else 1)
