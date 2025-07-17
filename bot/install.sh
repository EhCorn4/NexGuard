#!/bin/bash
# NexGuard Bot Installation Script

echo "Setting up NexGuard Discord Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your Discord bot token and other settings."
fi

# Create database directory
mkdir -p nexguard/database

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit .env file with your bot token"
echo "2. Run: python main.py"
echo "3. Access dashboard at: http://localhost:8080"
