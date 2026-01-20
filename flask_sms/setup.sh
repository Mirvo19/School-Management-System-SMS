#!/bin/bash

echo "================================"
echo "Flask SMS - Setup Script"
echo "================================"
echo ""

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"

echo ""
echo "[2/5] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

echo ""
echo "[4/5] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
    echo "⚠ Please edit .env file with your configuration"
else
    echo "! .env file already exists, skipping..."
fi

echo ""
echo "[5/5] Creating database and seeding data..."
python run.py &
PID=$!
sleep 3
kill $PID 2>/dev/null

python seed.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to seed database"
    exit 1
fi

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python app.py"
echo "  3. Open browser: http://localhost:5000"
echo ""
echo "Default login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "⚠ Remember to change the default password!"
echo ""
