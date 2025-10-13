"""
Live Trade Monitoring System
Handles real-time P/L tracking, portfolio management, and trade alerts
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import json
import uuid
from typing import Dict, List, Optional
import threading
import time
from dataclasses import dataclass, asdict
from market_data import MarketDataEngine

@dataclass
class Trade:
    """Trade data structure"""
    trade_id: str
    symbol: str
    option_type: str  # CALL, PUT, or STOCK
    entry_price: float
    strike_price: Optional[float]
    expiration_date: Optional[str]
    contracts: int
    entry_time: str
    current_price: float = 0.0
    current_value: float = 0.0
    pnl_dollar: float = 0.0
    pnl_percent: float = 0.0
    status: str = 'ACTIVE'  # ACTIVE, CLOSED, EXPIRED
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    alerts_enabled: bool = True
    user_email: Optional[str] = None

class TradeMonitor:
    def __init__(self, market_engine: MarketDataEngine = None):
        """Initialize trade monitoring system"""
        self.market_engine = market_engine or MarketDataEngine()
        self.active_trades: Dict[str, Trade] = {}
        self.trade_history: List[Trade] = []
        self.monitoring_active = False
        self.monitor_thread = None
        self.eastern = pytz.timezone('US/Eastern')
        
    def add_trade(self, symbol: str, option_type: str, entry_price: float,
                  contracts: int = 1, strike_price: float = None,
                  expiration_date: str = None, stop_loss: float = None,
                  take_profit: float = None, user_email: str = None) -> str:
        """Add a new trade to monitoring"""
        
        trade_id = str(uuid.uuid4())[:8]
        
        trade = Trade(
            trade_id=trade_id,
            symbol=symbol.upper(),
            option_type=option_type.upper(),
            entry_price=entry_price,
            strike_price=strike_price,
            expiration_date=expiration_date,
            contracts=contracts,
            entry_time=datetime.now(self.eastern).isoformat(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            user_email=user_email
        )
        
        self.active_trades[trade_id] = trade
        
        # Start monitoring if not already active
        if not self.monitoring_active:
            self.start_monitoring()
            
        return trade_id
    
    def remove_trade(self, trade_id: str, close_price: float = None) -> bool:
        """Remove a trade from active monitoring"""
        if trade_id in self.active_trades:
            trade = self.active_trades[trade_id]
            
            # Update final values if close price provided
            if close_price:
                trade.current_price = close_price
                trade.status = 'CLOSED'
                self._update_trade_pnl(trade)
            
            # Move to history
            self.trade_history.append(trade)
            del self.active_trades[trade_id]
            
            return True
        return False
    
    def get_trade_status(self, trade_id: str) -> Optional[Dict]:
        """Get current status of a specific trade"""
        if trade_id in self.active_trades:
            trade = self.active_trades[trade_id]
            return {
                **asdict(trade),
                'analysis': self._analyze_trade_signals(trade)
            }
        return None
    
    def get_all_active_trades(self) -> List[Dict]:
        """Get status of all active trades"""
        return [
            {
                **asdict(trade),
                'analysis': self._analyze_trade_signals(trade)
            }
            for trade in self.active_trades.values()
        ]
    
    def get_portfolio_summary(self) -> Dict:
        """Get overall portfolio performance summary"""
        if not self.active_trades:
            return {
                'total_trades': 0,
                'total_pnl': 0,
                'total_invested': 0,
                'best_performer': None,
                'worst_performer': None
            }
        
        trades = list(self.active_trades.values())
        total_pnl = sum(trade.pnl_dollar for trade in trades)
        total_invested = sum(trade.entry_price * trade.contracts * 
                           (100 if trade.option_type in ['CALL', 'PUT'] else 1) 
                           for trade in trades)
        
        best_trade = max(trades, key=lambda t: t.pnl_percent)
        worst_trade = min(trades, key=lambda t: t.pnl_percent)
        
        return {
            'total_trades': len(trades),
            'total_pnl': round(total_pnl, 2),
            'total_invested': round(total_invested, 2),
            'total_pnl_percent': round((total_pnl / total_invested * 100) if total_invested > 0 else 0, 2),
            'best_performer': {
                'symbol': best_trade.symbol,
                'pnl_percent': round(best_trade.pnl_percent, 2)
            },
            'worst_performer': {
                'symbol': worst_trade.symbol,
                'pnl_percent': round(worst_trade.pnl_percent, 2)
            }
        }
    
    def start_monitoring(self):
        """Start the background monitoring thread"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the background monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Main monitoring loop - runs every 30 seconds during market hours"""
        while self.monitoring_active:
            try:
                if self.market_engine.is_market_open() and self.active_trades:
                    self._update_all_trades()
                    self._check_alerts()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Continue monitoring even if there's an error
    
    def _update_all_trades(self):
        """Update prices and P/L for all active trades"""
        symbols_to_update = list(set(trade.symbol for trade in self.active_trades.values()))
        
        # Batch fetch current prices
        price_data = self._get_batch_prices(symbols_to_update)
        
        for trade in self.active_trades.values():
            if trade.symbol in price_data:
                trade.current_price = price_data[trade.symbol]
                self._update_trade_pnl(trade)
    
    def _get_batch_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols"""
        prices = {}
        
        try:
            # Use yfinance to get real-time prices
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = getattr(tickers.tickers, symbol, None)
                    if ticker:
                        hist = ticker.history(period='1d', interval='1m')
                        if not hist.empty:
                            prices[symbol] = hist['Close'].iloc[-1]
                except:
                    # Fallback to individual ticker if batch fails
                    try:
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period='1d', interval='1m')
                        if not hist.empty:
                            prices[symbol] = hist['Close'].iloc[-1]
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error fetching batch prices: {e}")
        
        return prices
    
    def _update_trade_pnl(self, trade: Trade):
        """Update P&L calculations for a trade"""
        if trade.current_price <= 0:
            return
            
        if trade.option_type == 'STOCK':
            # Stock trade
            current_value = trade.current_price * trade.contracts
            entry_value = trade.entry_price * trade.contracts
            trade.current_value = current_value
            trade.pnl_dollar = current_value - entry_value
            trade.pnl_percent = (trade.pnl_dollar / entry_value) * 100
            
        else:
            # Options trade (simplified - in reality would need options pricing model)
            # Using intrinsic value approximation
            if trade.option_type == 'CALL':
                intrinsic_value = max(0, trade.current_price - trade.strike_price)
                # Add some time value estimate
                time_value = max(0.05, (trade.entry_price - max(0, trade.entry_price - trade.strike_price)) * 0.5)
                estimated_premium = intrinsic_value + time_value
            else:  # PUT
                intrinsic_value = max(0, trade.strike_price - trade.current_price)
                time_value = max(0.05, (trade.entry_price - max(0, trade.strike_price - trade.entry_price)) * 0.5)
                estimated_premium = intrinsic_value + time_value
            
            current_value = estimated_premium * trade.contracts * 100
            entry_value = trade.entry_price * trade.contracts * 100
            trade.current_value = current_value
            trade.pnl_dollar = current_value - entry_value
            trade.pnl_percent = (trade.pnl_dollar / entry_value) * 100 if entry_value > 0 else 0
    
    def _analyze_trade_signals(self, trade: Trade) -> Dict:
        """Analyze current trade for exit signals"""
        try:
            # Get technical analysis for the underlying stock
            technical = self.market_engine.analyze_technical_setup(trade.symbol)
            if not technical:
                return {'action': 'HOLD', 'reason': 'No technical data available'}
            
            signals = technical.get('signals', [])
            rsi = technical.get('rsi', 50)
            
            # Determine if we should exit based on technical signals
            exit_signals = []
            alert_level = 'LOW'
            
            # Check stop loss and take profit
            if trade.stop_loss and trade.current_price <= trade.stop_loss:
                exit_signals.append('Stop loss triggered')
                alert_level = 'HIGH'
                
            if trade.take_profit and trade.current_price >= trade.take_profit:
                exit_signals.append('Take profit triggered')
                alert_level = 'HIGH'
            
            # Check P/L thresholds
            if trade.pnl_percent <= -20:
                exit_signals.append('Large loss (-20%+)')
                alert_level = 'HIGH'
            elif trade.pnl_percent >= 50:
                exit_signals.append('Large gain (+50%)')
                alert_level = 'MEDIUM'
            
            # Technical signal analysis for options
            if trade.option_type == 'CALL':
                bearish_signals = [s for s in signals if 'Bearish' in s or 'Overbought' in s]
                if len(bearish_signals) >= 2:
                    exit_signals.append('Multiple bearish technical signals')
                    alert_level = 'MEDIUM'
                elif rsi > 75:
                    exit_signals.append('RSI extremely overbought')
                    alert_level = 'MEDIUM'
                    
            elif trade.option_type == 'PUT':
                bullish_signals = [s for s in signals if 'Bullish' in s or 'Oversold' in s]
                if len(bullish_signals) >= 2:
                    exit_signals.append('Multiple bullish technical signals')
                    alert_level = 'MEDIUM'
                elif rsi < 25:
                    exit_signals.append('RSI extremely oversold')
                    alert_level = 'MEDIUM'
            
            # Check expiration (for options)
            if trade.expiration_date:
                try:
                    exp_date = datetime.strptime(trade.expiration_date, '%Y-%m-%d')
                    days_to_exp = (exp_date - datetime.now()).days
                    
                    if days_to_exp <= 1:
                        exit_signals.append('Expiration in 1 day')
                        alert_level = 'HIGH'
                    elif days_to_exp <= 7:
                        exit_signals.append('Expiration within 1 week')
                        alert_level = 'MEDIUM'
                except:
                    pass
            
            # Determine action
            if alert_level == 'HIGH':
                action = 'SELL NOW'
                color = '#ff4757'
            elif alert_level == 'MEDIUM':
                action = 'CONSIDER SELLING'
                color = '#ffaa00'
            else:
                action = 'HOLD'
                color = '#00ff88'
            
            alert_message = '; '.join(exit_signals) if exit_signals else 'Position looks good'
            
            return {
                'action': action,
                'alert_level': alert_level,
                'alert_message': alert_message,
                'color': color,
                'technical_signals': signals,
                'rsi': rsi
            }
            
        except Exception as e:
            print(f"Error analyzing trade signals: {e}")
            return {
                'action': 'HOLD',
                'alert_level': 'LOW',
                'alert_message': 'Analysis unavailable',
                'color': '#888888'
            }
    
    def _check_alerts(self):
        """Check for alert conditions and potentially send notifications"""
        for trade in self.active_trades.values():
            if not trade.alerts_enabled:
                continue
                
            analysis = self._analyze_trade_signals(trade)
            
            if analysis['alert_level'] == 'HIGH':
                self._send_alert(trade, analysis)
    
    def _send_alert(self, trade: Trade, analysis: Dict):
        """Send alert notification (placeholder for email/SMS integration)"""
        # In a real implementation, this would send email/SMS alerts
        print(f"🚨 ALERT for {trade.symbol}: {analysis['alert_message']}")
        print(f"   P/L: {trade.pnl_percent:.2f}% (${trade.pnl_dollar:.2f})")
        print(f"   Action: {analysis['action']}")
        
        # TODO: Implement email/SMS notifications
        # if trade.user_email:
        #     send_email_alert(trade.user_email, trade, analysis)