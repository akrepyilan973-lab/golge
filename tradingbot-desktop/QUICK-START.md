# ⚡ TradingBot Quick Start

## 🎯 3 Steps to Get Running

### 1️⃣ Download & Install
```bash
# Download: TradingBot-Setup-1.0.0.exe from GitHub
# Double-click and follow the installer
```

### 2️⃣ Setup Backend (One time only)
```bash
cd C:\Users\[YourUsername]\Desktop\TradingBot\backend
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with Notepad
```

### 3️⃣ Run & Trade!
```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload

# Terminal 2: App (or double-click desktop shortcut)
C:\Users\[YourUsername]\Desktop\TradingBot\TradingBot.exe
```

✅ **Done!** Open http://localhost:5173 and start trading!

---

## 🆘 Stuck?

1. Check `WIN-INSTALLER-GUIDE.md` for detailed help
2. Check `trading_bot.log` for error details
3. Visit: https://github.com/akrepyilan973-lab/golge
