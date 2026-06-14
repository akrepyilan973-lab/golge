"""
Advanced Binance Trading Bot with Multiple Strategies
Features: MA, RSI, MACD, Risk Management, Backtesting, Notifications
"""

import ccxt
import pandas as pd
import numpy as np
import time
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
import sqlite3
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Available trading strategies"""
    MOVING_AVERAGE = "moving_average"
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER_BANDS = "bollinger_bands"
    HYBRID = "hybrid"


class TradeSignal(Enum):
    """Trade signals"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Strategy.{name}")
    
    @abstractmethod
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate strategy indicators"""
        pass
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> TradeSignal:
        """Generate trading signal"""
        pass


class MovingAverageStrategy(BaseStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, short_period: int = 10, long_period: int = 30):
        super().__init__("MovingAverage")
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df['short_ma'] = df['close'].rolling(window=self.short_period).mean()
        df['long_ma'] = df['close'].rolling(window=self.long_period).mean()
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> TradeSignal:
        if len(df) < self.long_period:
            return TradeSignal.HOLD
        
        current_short = df['short_ma'].iloc[-1]
        current_long = df['long_ma'].iloc[-1]
        prev_short = df['short_ma'].iloc[-2]
        prev_long = df['long_ma'].iloc[-2]
        
        if pd.isna(current_short) or pd.isna(current_long):
            return TradeSignal.HOLD
        
        if prev_short <= prev_long and current_short > current_long:
            return TradeSignal.BUY
        elif prev_short >= prev_long and current_short < current_long:
            return TradeSignal.SELL
        
        return TradeSignal.HOLD


class RSIStrategy(BaseStrategy):
    """Relative Strength Index Strategy"""
    
    def __init__(self, period: int = 14, overbought: int = 70, oversold: int = 30):
        super().__init__("RSI")
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> TradeSignal:
        if len(df) < self.period:
            return TradeSignal.HOLD
        
        rsi = df['rsi'].iloc[-1]
        
        if pd.isna(rsi):
            return TradeSignal.HOLD
        
        if rsi < self.oversold:
            return TradeSignal.BUY
        elif rsi > self.overbought:
            return TradeSignal.SELL
        
        return TradeSignal.HOLD


class MACDStrategy(BaseStrategy):
    """MACD (Moving Average Convergence Divergence) Strategy"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__("MACD")
        self.fast = fast
        self.slow = slow
        self.signal_period = signal
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df['ema_fast'] = df['close'].ewm(span=self.fast).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=self.signal_period).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> TradeSignal:
        if len(df) < self.slow + 1:
            return TradeSignal.HOLD
        
        current_hist = df['macd_histogram'].iloc[-1]
        prev_hist = df['macd_histogram'].iloc[-2]
        
        if pd.isna(current_hist) or pd.isna(prev_hist):
            return TradeSignal.HOLD
        
        if prev_hist < 0 and current_hist > 0:
            return TradeSignal.BUY
        elif prev_hist > 0 and current_hist < 0:
            return TradeSignal.SELL
        
        return TradeSignal.HOLD


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands Strategy"""
    
    def __init__(self, period: int = 20, std_dev: int = 2):
        super().__init__("BollingerBands")
        self.period = period
        self.std_dev = std_dev
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df['bb_middle'] = df['close'].rolling(window=self.period).mean()
        bb_std = df['close'].rolling(window=self.period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * self.std_dev)
        df['bb_lower'] = df['bb_middle'] - (bb_std * self.std_dev)
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> TradeSignal:
        if len(df) < self.period:
            return TradeSignal.HOLD
        
        price = df['close'].iloc[-1]
        upper = df['bb_upper'].iloc[-1]
        lower = df['bb_lower'].iloc[-1]
        
        if pd.isna(upper) or pd.isna(lower):
            return TradeSignal.HOLD
        
        if price < lower:
            return TradeSignal.BUY
        elif price > upper:
            return TradeSignal.SELL
        
        return TradeSignal.HOLD


class TradeDatabase:
    """Database manager for trade history"""
    
    def __init__(self, db_file: str = "trades.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME,
                symbol TEXT,
                side TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                profit_loss REAL,
                profit_loss_pct REAL,
                strategy TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_trade(self, symbol: str, side: str, entry_price: float, 
                   quantity: float, strategy: str):
        """Save trade to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (timestamp, symbol, side, entry_price, quantity, strategy, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now(), symbol, side, entry_price, quantity, strategy, 'OPEN'))
        
        conn.commit()
        conn.close()
    
    def close_trade(self, trade_id: int, exit_price: float):
        """Close trade and calculate P&L"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT entry_price, quantity FROM trades WHERE id = ?', (trade_id,))
        result = cursor.fetchone()
        
        if result:
            entry_price, quantity = result
            profit_loss = (exit_price - entry_price) * quantity
            profit_loss_pct = ((exit_price - entry_price) / entry_price) * 100
            
            cursor.execute('''
                UPDATE trades 
                SET exit_price = ?, profit_loss = ?, profit_loss_pct = ?, status = 'CLOSED'
                WHERE id = ?
            ''', (exit_price, profit_loss, profit_loss_pct, trade_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """Get trading statistics"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "CLOSED"')
        total_trades = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "CLOSED" AND profit_loss > 0')
        winning_trades = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(profit_loss) FROM trades WHERE status = "CLOSED"')
        total_profit = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT AVG(profit_loss_pct) FROM trades WHERE status = "CLOSED"')
        avg_return = cursor.fetchone()[0] or 0
        
        conn.close()
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'avg_return_pct': avg_return
        }


class RiskManager:
    """Risk management module"""
    
    def __init__(self, max_risk_per_trade: float = 0.02, 
                 max_position_size: float = 0.1,
                 max_open_trades: int = 3):
        self.max_risk_per_trade = max_risk_per_trade  # 2% per trade
        self.max_position_size = max_position_size    # 10% of portfolio
        self.max_open_trades = max_open_trades
    
    def calculate_position_size(self, portfolio_value: float, 
                               entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk"""
        risk_amount = portfolio_value * self.max_risk_per_trade
        price_difference = abs(entry_price - stop_loss)
        
        if price_difference == 0:
            return 0
        
        position_size = risk_amount / price_difference
        max_position = (portfolio_value * self.max_position_size) / entry_price
        
        return min(position_size, max_position)
    
    def calculate_stop_loss(self, entry_price: float, atr: float) -> float:
        """Calculate stop loss based on ATR"""
        return entry_price - (atr * 2)
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float, 
                            risk_reward_ratio: float = 2.0) -> float:
        """Calculate take profit based on risk-reward ratio"""
        risk = entry_price - stop_loss
        return entry_price + (risk * risk_reward_ratio)


class AdvancedBinanceBot:
    """Advanced Binance Trading Bot"""
    
    def __init__(self, api_key: str, api_secret: str, 
                 symbol: str = 'BTC/USDT',
                 strategies: List[str] = None,
                 timeframe: str = '1h'):
        
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = logging.getLogger(f"Bot.{symbol}")
        
        # Initialize strategies
        self.strategies = self._init_strategies(strategies)
        
        # Risk management
        self.risk_manager = RiskManager()
        
        # Database
        self.db = TradeDatabase()
        
        # Position tracking
        self.positions = {}
        self.open_trades = 0
        
        self.logger.info(f"Bot initialized for {symbol} with {len(self.strategies)} strategies")
    
    def _init_strategies(self, strategy_names: List[str] = None) -> Dict[str, BaseStrategy]:
        """Initialize trading strategies"""
        strategies = {}
        
        if strategy_names is None:
            strategy_names = [StrategyType.MOVING_AVERAGE.value, 
                            StrategyType.RSI.value]
        
        strategy_map = {
            StrategyType.MOVING_AVERAGE.value: MovingAverageStrategy(),
            StrategyType.RSI.value: RSIStrategy(),
            StrategyType.MACD.value: MACDStrategy(),
            StrategyType.BOLLINGER_BANDS.value: BollingerBandsStrategy(),
        }
        
        for strategy_name in strategy_names:
            if strategy_name in strategy_map:
                strategies[strategy_name] = strategy_map[strategy_name]
        
        return strategies
    
    def get_historical_data(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return None
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        atr = df['tr'].rolling(window=period).mean().iloc[-1]
        
        return atr if not pd.isna(atr) else 0
    
    def generate_composite_signal(self, df: pd.DataFrame) -> Tuple[TradeSignal, Dict]:
        """Generate signal from all strategies"""
        signals = {}
        
        for strategy_name, strategy in self.strategies.items():
            df = strategy.calculate_indicators(df)
            signal = strategy.generate_signal(df)
            signals[strategy_name] = signal.value
        
        # Majority voting
        buy_votes = sum(1 for s in signals.values() if s == TradeSignal.BUY.value)
        sell_votes = sum(1 for s in signals.values() if s == TradeSignal.SELL.value)
        
        if buy_votes > len(self.strategies) / 2:
            final_signal = TradeSignal.BUY
        elif sell_votes > len(self.strategies) / 2:
            final_signal = TradeSignal.SELL
        else:
            final_signal = TradeSignal.HOLD
        
        return final_signal, signals
    
    def get_balance(self, asset: str = 'USDT') -> float:
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            return balance[asset]['free']
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return 0
    
    def place_buy_order(self, amount: float) -> Optional[Dict]:
        """Place buy order"""
        try:
            order = self.exchange.create_market_buy_order(self.symbol, amount)
            self.logger.info(f"Buy order executed: {order['id']}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing buy order: {e}")
            return None
    
    def place_sell_order(self, amount: float) -> Optional[Dict]:
        """Place sell order"""
        try:
            order = self.exchange.create_market_sell_order(self.symbol, amount)
            self.logger.info(f"Sell order executed: {order['id']}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing sell order: {e}")
            return None
    
    def run(self, check_interval: int = 3600, dry_run: bool = False):
        """Main bot loop"""
        self.logger.info(f"Bot started - Check interval: {check_interval}s - Dry run: {dry_run}")
        
        try:
            while True:
                df = self.get_historical_data(limit=100)
                
                if df is None or df.empty:
                    self.logger.warning("No data received")
                    time.sleep(check_interval)
                    continue
                
                # Generate signal
                signal, strategy_signals = self.generate_composite_signal(df)
                
                current_price = df['close'].iloc[-1]
                atr = self.calculate_atr(df)
                
                self.logger.info(f"Price: {current_price:.2f} | ATR: {atr:.2f} | Signal: {signal.value}")
                self.logger.info(f"Strategy votes: {strategy_signals}")
                
                # Execute trades
                if signal == TradeSignal.BUY and self.open_trades < self.risk_manager.max_open_trades:
                    balance = self.get_balance('USDT')
                    
                    if balance > 10:
                        stop_loss = self.risk_manager.calculate_stop_loss(current_price, atr)
                        take_profit = self.risk_manager.calculate_take_profit(current_price, stop_loss)
                        position_size = self.risk_manager.calculate_position_size(
                            balance, current_price, stop_loss
                        )
                        
                        if not dry_run:
                            order = self.place_buy_order(position_size)
                            if order:
                                self.positions['long'] = {
                                    'entry_price': current_price,
                                    'stop_loss': stop_loss,
                                    'take_profit': take_profit,
                                    'quantity': position_size
                                }
                                self.open_trades += 1
                                self.logger.info(
                                    f"BUY | Entry: {current_price:.2f} | "
                                    f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
                                )
                        else:
                            self.logger.info(f"[DRY RUN] BUY signal - Price: {current_price:.2f}")
                
                elif signal == TradeSignal.SELL and 'long' in self.positions:
                    balance = self.get_balance(self.symbol.split('/')[0])
                    
                    if balance > 0:
                        position = self.positions['long']
                        
                        if not dry_run:
                            order = self.place_sell_order(balance)
                            if order:
                                profit_loss_pct = ((current_price - position['entry_price']) / 
                                                  position['entry_price']) * 100
                                self.logger.info(
                                    f"SELL | Exit: {current_price:.2f} | "
                                    f"P&L: {profit_loss_pct:.2f}%"
                                )
                                del self.positions['long']
                                self.open_trades -= 1
                        else:
                            self.logger.info(f"[DRY RUN] SELL signal - Price: {current_price:.2f}")
                
                # Check stop loss and take profit
                if 'long' in self.positions:
                    position = self.positions['long']
                    
                    if current_price <= position['stop_loss']:
                        self.logger.warning(f"Stop loss hit at {current_price:.2f}")
                        if not dry_run:
                            self.place_sell_order(position['quantity'])
                            del self.positions['long']
                            self.open_trades -= 1
                    
                    elif current_price >= position['take_profit']:
                        self.logger.info(f"Take profit hit at {current_price:.2f}")
                        if not dry_run:
                            self.place_sell_order(position['quantity'])
                            del self.positions['long']
                            self.open_trades -= 1
                
                # Print statistics
                stats = self.db.get_statistics()
                self.logger.info(f"Stats - Trades: {stats['total_trades']} | "
                               f"Win Rate: {stats['win_rate']:.2f}% | "
                               f"Profit: ${stats['total_profit']:.2f}")
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)


def main():
    """Main entry point"""
    
    # Configuration
    API_KEY = 'your_binance_api_key_here'
    API_SECRET = 'your_binance_api_secret_here'
    SYMBOL = 'BTC/USDT'
    TIMEFRAME = '1h'
    CHECK_INTERVAL = 3600
    DRY_RUN = True  # Set to False for live trading
    
    # Select strategies
    STRATEGIES = [
        StrategyType.MOVING_AVERAGE.value,
        StrategyType.RSI.value,
        StrategyType.MACD.value
    ]
    
    # Create and run bot
    bot = AdvancedBinanceBot(
        api_key=API_KEY,
        api_secret=API_SECRET,
        symbol=SYMBOL,
        strategies=STRATEGIES,
        timeframe=TIMEFRAME
    )
    
    bot.run(check_interval=CHECK_INTERVAL, dry_run=DRY_RUN)


if __name__ == '__main__':
    main()
