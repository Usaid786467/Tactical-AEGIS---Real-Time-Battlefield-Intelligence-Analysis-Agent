#!/bin/bash

# Tactical AEGIS Setup Script
# Sets up both backend and frontend for development

echo "========================================="
echo "Tactical AEGIS - Setup Script"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Setup Backend
echo ""
echo "Setting up backend..."
cd backend || exit 1

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit backend/.env and add your API keys"
else
    echo ".env file already exists"
fi

# Initialize database
echo "Initializing database..."
python3 -c "from app.database.database import init_db; init_db()"

echo ""
echo "Backend setup complete!"
echo ""

# Setup Frontend (if needed in future)
cd ..
# Uncomment when frontend is ready:
# echo "Setting up frontend..."
# cd frontend || exit 1
# npm install
# cd ..

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the backend server:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m app.main"
echo ""
echo "Or use the start script:"
echo "  ./scripts/start_dev.sh"
echo ""
