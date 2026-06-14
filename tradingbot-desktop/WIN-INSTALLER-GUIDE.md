# 🖥️ TradingBot Windows Installer - Setup Guide

**Personal Edition for Akrepyilan973**

---

## 📥 Installation Instructions

### Step 1: Download the Installer

1. Go to GitHub: https://github.com/akrepyilan973-lab/golge
2. Go to **Releases** section
3. Download `TradingBot-Setup-1.0.0.exe`
4. Save to your Downloads folder

---

### Step 2: Run the Installer

1. **Double-click** `TradingBot-Setup-1.0.0.exe`
2. Windows SmartScreen may warn you - click **"More info" → "Run anyway"**
3. **Next** → Follow the wizard
4. **Install**
5. Wait for installation to complete

---

### Step 3: Launch TradingBot

After installation, TradingBot will be installed to:
```
C:\Users\[YourUsername]\Desktop\TradingBot
```

**Two ways to launch:**

1. **Desktop Shortcut** - Double-click the TradingBot icon on your desktop
2. **Start Menu** - Search for "TradingBot" in Windows Start Menu

---

## ⚙️ First Time Setup

### 1. Configure Backend

The first time you launch, you need to:

```bash
# Open Command Prompt (Windows + R, type: cmd, press Enter)

# Navigate to the installation directory
cd C:\Users\[YourUsername]\Desktop\TradingBot\backend

# Setup virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

### 2. Configure .env File

Edit `C:\Users\[YourUsername]\Desktop\TradingBot\backend\.env`:

```env
# Database (keep as is)
DATABASE_URL=sqlite:///./trading_bot.db

# Security (change this!)
SECRET_KEY=change-this-to-random-secure-key

# Binance API (optional for now, can add later)
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

---

## 🚀 Running TradingBot

### Option 1: One-Click Start (Easiest)

After first setup, double-click `TradingBot.exe` on your desktop.

It will:
- ✅ Start the backend API
- ✅ Open the desktop app
- ✅ Everything works automatically

---

### Option 2: Manual Start (For Development)

**Terminal 1 - Backend:**
```bash
cd C:\Users\[YourUsername]\Desktop\TradingBot\backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Desktop App:**
```bash
C:\Users\[YourUsername]\Desktop\TradingBot\TradingBot.exe
```

---

## 🌐 Access Points

| Component | URL/Location |
|-----------|-------------|
| **Desktop App** | Open from Start Menu or desktop shortcut |
| **API Docs** | http://localhost:8000/docs |
| **Data Folder** | `C:\Users\[YourUsername]\Desktop\TradingBot\data` |
| **Logs** | `C:\Users\[YourUsername]\Desktop\TradingBot\logs` |

---

## 🔧 Troubleshooting

### "Python not found" error

1. Download Python from https://www.python.org
2. **Important**: Check "Add Python to PATH" during installation
3. Restart computer
4. Try again

### "Port 8000 already in use"

```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the number)
taskkill /PID [PID] /F
```

### App crashes on startup

1. Check `trading_bot.log` in the installation folder
2. Ensure backend is running on port 8000
3. Try reinstalling

### "Cannot find module" error

```bash
cd backend
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## 🔐 Security & Privacy

✅ **This is YOUR personal app**
- Runs locally on your computer
- Your data stays on your machine
- No cloud sync
- No tracking
- Completely private

✅ **API Keys are safe**
- Stored locally in `.env` file
- Never transmitted anywhere
- Password protected

---

## 📊 Dashboard Features

Once running, you can:

- 📈 View trading statistics
- 💹 Monitor profit/loss
- 🎯 See win rate
- 📊 View performance charts
- ⚙️ Configure bot settings
- ▶️ Start/Stop trading
- 🔔 Set up alerts

---

## 🎯 Next Steps

1. ✅ Install the app
2. ✅ Set up backend and API keys
3. ✅ Configure trading strategies in Settings
4. ✅ Click "Start Bot"
5. ✅ Monitor trades on dashboard

---

## 💪 You're All Set!

Your personal TradingBot is ready to use!

Enjoy! 🚀📈

---

**Questions?** Check GitHub: https://github.com/akrepyilan973-lab/golge
