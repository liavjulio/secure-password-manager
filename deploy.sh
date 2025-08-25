#!/bin/bash

# Secure Password Manager - Setup and Deployment Script
# This script automates the setup process for the secure password manager

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    if [ ! -f "instance/password_manager.db" ]; then
        python init_db.py
        print_success "Database initialized"
    else
        print_warning "Database already exists"
    fi
}

# Generate encryption key if not exists
setup_encryption() {
    print_status "Setting up encryption..."
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    fi
    
    # Check if encryption key exists
    if ! grep -q "ENCRYPTION_KEY=" .env || [ -z "$(grep 'ENCRYPTION_KEY=' .env | cut -d'=' -f2)" ]; then
        print_status "Generating encryption key..."
        ENCRYPTION_KEY=$(python -c "from crypto_utils import generate_encryption_key; import base64; print(base64.b64encode(generate_encryption_key()).decode())")
        
        # Update .env file
        if grep -q "ENCRYPTION_KEY=" .env; then
            sed -i '' "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
        else
            echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> .env
        fi
        
        print_success "Encryption key generated and saved to .env"
    else
        print_success "Encryption key already configured"
    fi
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    python -m pytest tests/ -v
    
    if [ $? -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed. Please check the output above."
        exit 1
    fi
}

# Start the application
start_app() {
    print_status "Starting the application..."
    
    # Find available port
    PORT=5000
    while netstat -an | grep -q ":$PORT "; do
        PORT=$((PORT + 1))
    done
    
    print_success "Starting application on port $PORT"
    print_status "Access the application at: http://localhost:$PORT"
    print_status "Press Ctrl+C to stop the application"
    
    export FLASK_ENV=development
    python -c "from app import app; app.run(debug=True, port=$PORT)"
}

# Main deployment function
main() {
    echo "============================================"
    echo "  Secure Password Manager Setup Script"
    echo "============================================"
    echo ""
    
    # Parse command line arguments
    case "$1" in
        "setup")
            check_python
            setup_venv
            install_dependencies
            setup_encryption
            init_database
            print_success "Setup completed successfully!"
            print_status "Run './deploy.sh start' to start the application"
            ;;
        "test")
            source .venv/bin/activate
            run_tests
            ;;
        "start")
            source .venv/bin/activate
            start_app
            ;;
        "clean")
            print_status "Cleaning up..."
            rm -rf .venv
            rm -rf __pycache__
            rm -rf instance/password_manager.db
            rm -rf .pytest_cache
            print_success "Cleanup completed"
            ;;
        *)
            echo "Usage: $0 {setup|test|start|clean}"
            echo ""
            echo "Commands:"
            echo "  setup  - Set up the project (install dependencies, create database, etc.)"
            echo "  test   - Run all unit tests"
            echo "  start  - Start the application"
            echo "  clean  - Clean up all generated files and virtual environment"
            echo ""
            echo "First time setup:"
            echo "  1. Copy .env.example to .env and configure settings"
            echo "  2. Run './deploy.sh setup'"
            echo "  3. Run './deploy.sh start'"
            exit 1
            ;;
    esac
}

# Check if script is being run from the correct directory
if [ ! -f "app.py" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Run main function with all arguments
main "$@"
