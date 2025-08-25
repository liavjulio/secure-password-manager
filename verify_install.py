#!/usr/bin/env python3
"""
Secure Password Manager - Installation Verification Script
Verifies that all components are properly installed and configured.
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'flask_login',
        'flask_wtf',
        'bcrypt',
        'cryptography',
        'python_dotenv',
        'email_validator',
        'wtforms'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_project_structure():
    """Check if all required project files exist"""
    required_files = [
        'app.py',
        'models.py', 
        'auth.py',
        'crypto_utils.py',
        'forms.py',
        'init_db.py',
        'requirements.txt',
        '.env.example',
        'templates/base.html',
        'templates/dashboard.html',
        'templates/login.html',
        'templates/register.html',
        'templates/settings.html',
        'tests/test_password_manager.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def check_environment():
    """Check environment configuration"""
    if Path('.env').exists():
        print("✅ .env file exists")
        env_configured = True
    else:
        print("⚠️ .env file not found - will be created from .env.example")
        env_configured = False
    
    if Path('.env.example').exists():
        print("✅ .env.example template exists")
    else:
        print("❌ .env.example template missing")
        return False, env_configured
    
    return True, env_configured

def check_database():
    """Check database configuration"""
    instance_dir = Path('instance')
    
    if instance_dir.exists():
        print("✅ Instance directory exists")
        
        db_file = instance_dir / 'password_manager.db'
        if db_file.exists():
            print("✅ Database file exists")
            return True, True
        else:
            print("⚠️ Database not initialized - run 'python init_db.py'")
            return True, False
    else:
        print("⚠️ Instance directory missing - will be created")
        return False, False

def main():
    """Main verification function"""
    print("🔐 Secure Password Manager - Installation Verification")
    print("=" * 55)
    
    checks_passed = 0
    total_checks = 5
    
    # Check Python version
    print("\n📍 Checking Python version...")
    if check_python_version():
        checks_passed += 1
    
    # Check dependencies
    print("\n📍 Checking dependencies...")
    deps_ok, missing_deps = check_dependencies()
    if deps_ok:
        checks_passed += 1
    else:
        print(f"\n💡 To install missing packages: pip install {' '.join(missing_deps)}")
    
    # Check project structure
    print("\n📍 Checking project structure...")
    structure_ok, missing_files = check_project_structure()
    if structure_ok:
        checks_passed += 1
    else:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
    
    # Check environment
    print("\n📍 Checking environment configuration...")
    env_ok, env_configured = check_environment()
    if env_ok:
        checks_passed += 1
        if not env_configured:
            print("💡 Copy .env.example to .env and configure as needed")
    
    # Check database
    print("\n📍 Checking database...")
    db_dir_ok, db_exists = check_database()
    if db_dir_ok:
        checks_passed += 1
        if not db_exists:
            print("💡 Run 'python init_db.py' to create the database")
    
    # Summary
    print("\n" + "=" * 55)
    print(f"📊 Verification Summary: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 Installation verification PASSED!")
        print("\n🚀 Ready to run:")
        print("   python app.py")
        print("\n🌐 Then open: http://localhost:8080")
        return True
    else:
        print("⚠️ Installation verification FAILED!")
        print("\n🔧 Please fix the issues above and run verification again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
