#!/bin/bash

echo "🚀 Trading Bot Setup Script"
echo "============================="

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# Check Node.js
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi
echo "✅ Node.js $(node --version)"

# Backend setup
echo ""
echo "Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
echo "✅ Backend ready"

# Frontend setup
echo ""
echo "Setting up Frontend..."
cd ../frontend
npm install
echo "✅ Frontend ready"

# Desktop setup
echo ""
echo "Setting up Desktop App..."
cd ../desktop
npm install
echo "✅ Desktop app ready"

echo ""
echo "============================="
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Backend:  cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo "3. Desktop:  cd desktop && npm run dev"
echo ""
echo "Access at: http://localhost:3000"
echo "API docs: http://localhost:8000/docs"