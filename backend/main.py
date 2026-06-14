"""
Advanced Trading Bot Backend API
FastAPI + SQLAlchemy + PostgreSQL
"""

from fastapi import FastAPI, WebSocket, HTTPException, Depends, status
from fastapi.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv
import logging
import asyncio
from enum import Enum

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_bot.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# FastAPI app
app = FastAPI(
    title="Advanced Trading Bot API",
    description="Professional Trading Bot with Multiple Strategies",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


# ==================== Models ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BotConfig(Base):
    __tablename__ = "bot_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    symbol = Column(String, default="BTC/USDT")
    timeframe = Column(String, default="1h")
    strategies = Column(String)  # JSON string
    max_risk_per_trade = Column(Float, default=0.02)
    max_position_size = Column(Float, default=0.1)
    max_open_trades = Column(Integer, default=3)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    symbol = Column(String)
    side = Column(String)  # buy/sell
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float)
    profit_loss = Column(Float, nullable=True)
    profit_loss_pct = Column(Float, nullable=True)
    strategy = Column(String)
    status = Column(String, default="OPEN")  # OPEN/CLOSED
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    symbol = Column(String)
    alert_type = Column(String)  # price_target, volume, rsi, etc
    condition = Column(String)
    value = Column(Float)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# ==================== Pydantic Models ====================

class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class BotConfigBase(BaseModel):
    symbol: str
    timeframe: str
    strategies: List[str]
    max_risk_per_trade: float = 0.02
    max_position_size: float = 0.1
    max_open_trades: int = 3


class BotConfigCreate(BotConfigBase):
    pass


class BotConfigUpdate(BaseModel):
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    strategies: Optional[List[str]] = None
    max_risk_per_trade: Optional[float] = None
    max_position_size: Optional[float] = None
    max_open_trades: Optional[int] = None
    is_active: Optional[bool] = None


class BotConfigResponse(BotConfigBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TradeBase(BaseModel):
    symbol: str
    side: str
    entry_price: float
    quantity: float
    strategy: str


class TradeResponse(TradeBase):
    id: int
    exit_price: Optional[float]
    profit_loss: Optional[float]
    profit_loss_pct: Optional[float]
    status: str
    entry_time: datetime
    exit_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    symbol: str
    alert_type: str
    condition: str
    value: float


class AlertResponse(AlertBase):
    id: int
    is_triggered: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PortfolioStats(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    avg_return_pct: float
    current_open_trades: int
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int


class StrategyStats(BaseModel):
    strategy_name: str
    total_trades: int
    win_rate: float
    avg_return: float
    total_profit: float


# ==================== Dependencies ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ==================== Routes ====================

@app.get("/")
def read_root():
    return {
        "name": "Advanced Trading Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# User Routes
@app.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # In production, use proper password hashing
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=user.password  # HASH THIS IN PRODUCTION
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/api/auth/login", response_model=TokenResponse)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.hashed_password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.get("/api/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


# Bot Config Routes
@app.post("/api/bot-config", response_model=BotConfigResponse)
def create_bot_config(
    config: BotConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_config = BotConfig(
        user_id=current_user.id,
        symbol=config.symbol,
        timeframe=config.timeframe,
        strategies=",".join(config.strategies),
        max_risk_per_trade=config.max_risk_per_trade,
        max_position_size=config.max_position_size,
        max_open_trades=config.max_open_trades
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@app.get("/api/bot-config", response_model=List[BotConfigResponse])
def get_bot_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    configs = db.query(BotConfig).filter(BotConfig.user_id == current_user.id).all()
    return configs


@app.put("/api/bot-config/{config_id}", response_model=BotConfigResponse)
def update_bot_config(
    config_id: int,
    config: BotConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_config = db.query(BotConfig).filter(
        BotConfig.id == config_id,
        BotConfig.user_id == current_user.id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    update_data = config.dict(exclude_unset=True)
    if "strategies" in update_data:
        update_data["strategies"] = ",".join(update_data["strategies"])
    
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


# Trade Routes
@app.get("/api/trades", response_model=List[TradeResponse])
def get_trades(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    if status:
        query = query.filter(Trade.status == status)
    
    return query.order_by(Trade.entry_time.desc()).all()


@app.post("/api/trades", response_model=TradeResponse)
def create_trade(
    trade: TradeBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_trade = Trade(
        user_id=current_user.id,
        symbol=trade.symbol,
        side=trade.side,
        entry_price=trade.entry_price,
        quantity=trade.quantity,
        strategy=trade.strategy
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


@app.put("/api/trades/{trade_id}")
def close_trade(
    trade_id: int,
    exit_price: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == current_user.id
    ).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    profit_loss = (exit_price - trade.entry_price) * trade.quantity
    profit_loss_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100
    
    trade.exit_price = exit_price
    trade.profit_loss = profit_loss
    trade.profit_loss_pct = profit_loss_pct
    trade.status = "CLOSED"
    trade.exit_time = datetime.utcnow()
    
    db.commit()
    db.refresh(trade)
    return trade


# Statistics Routes
@app.get("/api/statistics/portfolio", response_model=PortfolioStats)
def get_portfolio_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trades = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "CLOSED"
    ).all()
    
    if not trades:
        return PortfolioStats(
            total_trades=0, winning_trades=0, losing_trades=0,
            win_rate=0, total_profit=0, avg_return_pct=0,
            current_open_trades=0, largest_win=0, largest_loss=0,
            consecutive_wins=0, consecutive_losses=0
        )
    
    winning = [t for t in trades if t.profit_loss > 0]
    losing = [t for t in trades if t.profit_loss < 0]
    
    total_profit = sum(t.profit_loss for t in trades)
    avg_return = sum(t.profit_loss_pct for t in trades) / len(trades)
    
    open_trades = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "OPEN"
    ).count()
    
    largest_win = max([t.profit_loss for t in winning], default=0)
    largest_loss = min([t.profit_loss for t in losing], default=0)
    
    return PortfolioStats(
        total_trades=len(trades),
        winning_trades=len(winning),
        losing_trades=len(losing),
        win_rate=(len(winning) / len(trades) * 100) if trades else 0,
        total_profit=total_profit,
        avg_return_pct=avg_return,
        current_open_trades=open_trades,
        largest_win=largest_win,
        largest_loss=largest_loss,
        consecutive_wins=0,
        consecutive_losses=0
    )


@app.get("/api/statistics/strategies", response_model=List[StrategyStats])
def get_strategy_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trades = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "CLOSED"
    ).all()
    
    strategies = {}
    for trade in trades:
        if trade.strategy not in strategies:
            strategies[trade.strategy] = {
                "trades": [],
                "total_profit": 0,
                "winning": 0
            }
        strategies[trade.strategy]["trades"].append(trade)
        strategies[trade.strategy]["total_profit"] += trade.profit_loss or 0
        if (trade.profit_loss or 0) > 0:
            strategies[trade.strategy]["winning"] += 1
    
    result = []
    for strategy_name, data in strategies.items():
        trades_list = data["trades"]
        win_rate = (data["winning"] / len(trades_list) * 100) if trades_list else 0
        avg_return = (sum(t.profit_loss_pct or 0 for t in trades_list) / len(trades_list)) if trades_list else 0
        
        result.append(StrategyStats(
            strategy_name=strategy_name,
            total_trades=len(trades_list),
            win_rate=win_rate,
            avg_return=avg_return,
            total_profit=data["total_profit"]
        ))
    
    return result


# Alert Routes
@app.post("/api/alerts", response_model=AlertResponse)
def create_alert(
    alert: AlertBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_alert = Alert(
        user_id=current_user.id,
        symbol=alert.symbol,
        alert_type=alert.alert_type,
        condition=alert.condition,
        value=alert.value
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@app.get("/api/alerts", response_model=List[AlertResponse])
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
    return alerts


@app.delete("/api/alerts/{alert_id}")
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted"}


# WebSocket for real-time updates
@app.websocket("/ws/market-data/{symbol}")
async def websocket_market_data(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        while True:
            # In production, connect to real market data source
            data = {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "price": 45000,  # Mock data
                "volume": 1000
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
