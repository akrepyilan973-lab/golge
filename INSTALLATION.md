# Installation Guide - Advanced Trading Bot

## 🔧 System Requirements

- **OS**: Windows 10+, macOS 10.13+, Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

---

## 📦 Installation Methods

### Method 1: Automated Setup (Recommended)

#### Windows
```cmd
# Clone repository
git clone https://github.com/akrepyilan973-lab/golge.git
cd golge

# Run setup script
bash setup.sh
```

#### macOS/Linux
```bash
# Clone repository
git clone https://github.com/akrepyilan973-lab/golge.git
cd golge

# Make script executable
chmod +x setup.sh

# Run setup script
./setup.sh
```

### Method 2: Docker Compose (Easiest)

```bash
# Clone repository
git clone https://github.com/akrepyilan973-lab/golge.git
cd golge

# Start all services
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Database: localhost:5432
```

### Method 3: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations (if using PostgreSQL)
alembic upgrade head

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:5173
```

#### Desktop App Setup
```bash
cd desktop

# Install dependencies
npm install

# Start development
npm run dev

# Build for distribution
npm run build
```

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Database
DATABASE_URL=sqlite:///./trading_bot.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/tradingbot

# JWT Security
SECRET_KEY=your-very-secure-random-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Binance API Keys
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Email Configuration (optional)
EMAIL_FROM=noreply@tradingbot.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Discord Webhook (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Frontend Configuration

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 🧪 Verification

### Test Backend
```bash
# Backend should be running on port 8000
curl http://localhost:8000/

# Should return:
# {"name":"Advanced Trading Bot API","version":"1.0.0","status":"running"}
```

### Test Frontend
```bash
# Open browser
# http://localhost:5173  (for development)
# http://localhost:3000  (for production build)
```

### Test Database
```bash
# SQLite (if using SQLite)
ls -la trading_bot.db

# PostgreSQL (if using PostgreSQL)
psql -U trader -d tradingbot -c "\dt"
```

---

## 🔑 Binance API Setup

1. Go to https://www.binance.com/en/account/api-management
2. Create new API key
3. Enable Spot Trading
4. Set IP whitelist (your server IP)
5. Copy API Key and Secret
6. Paste in `.env` file

---

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Desktop (optional):**
```bash
cd desktop
npm run dev
```

### Production Mode

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend
npm run build
npm run preview

# Or use Docker
docker-compose up -d
```

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Python Module Not Found
```bash
# Reinstall packages
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Node Modules Issues
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Database Connection Error
```bash
# Check database URL in .env
# Ensure PostgreSQL is running (if using PostgreSQL)
# Test connection:
psql postgresql://user:password@localhost/dbname
```

### CORS Errors
- Ensure backend is running
- Check frontend API URL configuration
- Verify CORS settings in `backend/main.py`

---

## 📱 First Login

1. Open http://localhost:5173 (or :3000 for production)
2. Register new account
3. Fill in email and password
4. Login with credentials
5. Configure bot settings
6. Start trading!

---

## 🔐 Security Best Practices

✅ Change SECRET_KEY in production
✅ Use PostgreSQL for production (not SQLite)
✅ Enable HTTPS
✅ Keep API keys secure
✅ Regular backups
✅ Monitor for suspicious activities
✅ Use environment variables for sensitive data
✅ Keep dependencies updated

---

## 📞 Need Help?

- Check logs: `trading_bot.log`
- API docs: `http://localhost:8000/docs`
- GitHub Issues: [Link to issues]
- Email: support@tradingbot.com

---

**Happy Trading! 🚀📈**