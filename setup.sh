#!/bin/bash

# Secure Password Manager - Installation Script
# This script sets up the password manager for GitHub deployment

set -e  # Exit on any error

echo "� Setting up Secure Password Manager..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_status "Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    print_status "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        
        # Generate a random secret key
        SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
        
        # Update .env with generated secret key
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
        fi
        
        print_status ".env file created with generated secret key"
    else
        print_warning ".env.example not found, creating basic .env file"
        SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
        cat > .env << EOF
# Flask Configuration
SECRET_KEY=$SECRET_KEY
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///instance/password_manager.db

# Security Configuration
BCRYPT_LOG_ROUNDS=12
AES_KEY_LENGTH=32

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=security.log
EOF
        print_status "Basic .env file created"
    fi
else
    print_status ".env file already exists"
fi

# Create instance directory
print_info "Creating instance directory..."
mkdir -p instance
print_status "Instance directory created"

# Initialize database
print_info "Initializing database..."
python3 init_db.py
if [ $? -eq 0 ]; then
    print_status "Database initialized successfully"
else
    print_error "Database initialization failed"
    exit 1
fi

# Run tests if available
if [ -d "tests" ] && [ -f "tests/test_password_manager.py" ]; then
    print_info "Running tests..."
    python3 -m pytest tests/ -v --tb=short
    if [ $? -eq 0 ]; then
        print_status "All tests passed"
    else
        print_warning "Some tests failed, but installation can continue"
    fi
fi

# Check if everything is working
print_info "Verifying installation..."
python3 -c "
import sys
sys.path.append('.')
try:
    from app import app
    from models import User, Password
    print('✅ Application imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo ""
echo "🎉 Installation completed successfully!"
echo "======================================"
echo ""
print_info "To start the application:"
echo "  1. Activate virtual environment: source .venv/bin/activate"
echo "  2. Run the application: python3 app.py"
echo "  3. Open browser to: http://localhost:8080"
echo ""
print_info "To run tests:"
echo "  python3 -m pytest tests/ -v"
echo ""
print_info "For more information, see README.md"
echo ""
print_warning "Note: Make sure to change the SECRET_KEY in .env for production!"
