"""
Advanced Market Data Module
Handles pre-market analysis, live data, news sentiment, and options recommendations
"""

import yfinance as yf
import finnhub
import pandas as pd
import numpy as np
import requests
import pytz
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import json

class MarketDataEngine:
    def __init__(self, finnhub_api_key: str = None):
        """Initialize market data engine with API keys"""
        # Use free tier of Finnhub for now, can upgrade later
        self.finnhub_client = finnhub.Client(api_key=finnhub_api_key or "demo")
        self.eastern = pytz.timezone('US/Eastern')
        
        # Popular stock universe for scanning
        self.stock_universe = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'ORCL', 'CRM', 'ADBE', 'INTC', 'AMD', 'PYPL', 'UBER', 'LYFT',
            'ROKU', 'ZOOM', 'DOCU', 'SNOW', 'PLTR', 'BB', 'AMC', 'GME',
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'GLD', 'TLT', 'UNG',
            'BABA', 'JD', 'NIO', 'XPEV', 'LI', 'DIDI', 'PDD', 'TAL',
            'F', 'GM', 'FORD', 'RIVN', 'LCID', 'CCIV', 'SPCE', 'ARKK',
            'KO', 'PEP', 'WMT', 'TGT', 'HD', 'LOW', 'MCD', 'SBUX',
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC',
            'JNJ', 'PFE', 'MRK', 'UNH', 'CVS', 'ABBV', 'TMO', 'DHR',
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'MPC', 'VLO',
            'DIS', 'CMCSA', 'T', 'VZ', 'TMUS', 'CHTR', 'DISH', 'SIRI'
        ]
        
    def is_market_open(self) -> bool:
        """Check if market is currently open (9:30 AM - 4:00 PM ET)"""
        now = datetime.now(self.eastern)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Only weekdays
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        return market_open <= now <= market_close
    
    def is_pre_market(self) -> bool:
        """Check if it's pre-market hours (4:00 AM - 9:30 AM ET)"""
        now = datetime.now(self.eastern)
        pre_market_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # Only weekdays
        if now.weekday() >= 5:
            return False
            
        return pre_market_start <= now < market_open
    
    def get_market_status(self) -> Dict:
        """Get current market status and next session info"""
        now = datetime.now(self.eastern)
        
        status = {
            'is_open': self.is_market_open(),
            'is_pre_market': self.is_pre_market(),
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'next_session': None,
            'status_text': 'Market Closed'
        }
        
        if status['is_open']:
            status['status_text'] = 'Market Open'
            close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
            status['next_session'] = f"Closes at {close_time.strftime('%I:%M %p %Z')}"
        elif status['is_pre_market']:
            status['status_text'] = 'Pre-Market'
            open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
            status['next_session'] = f"Opens at {open_time.strftime('%I:%M %p %Z')}"
        else:
            # Calculate next market open
            next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            if now.hour >= 16 or now.weekday() >= 5:
                # Move to next weekday
                days_ahead = 1
                if now.weekday() == 4:  # Friday
                    days_ahead = 3
                elif now.weekday() == 5:  # Saturday
                    days_ahead = 2
                next_open += timedelta(days=days_ahead)
            
            status['next_session'] = f"Opens {next_open.strftime('%a %I:%M %p %Z')}"
        
        return status
    
    def get_pre_market_data(self, symbol: str) -> Dict:
        """Get pre-market data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get pre-market data (last 5 days to ensure we have data)
            hist = ticker.history(period="5d", interval="1m", prepost=True)
            
            if hist.empty:
                return {}
            
            # Get regular session close price (previous day)
            regular_hist = ticker.history(period="2d")
            prev_close = regular_hist['Close'].iloc[-2] if len(regular_hist) >= 2 else regular_hist['Close'].iloc[-1]
            
            # Current pre-market price
            current_price = hist['Close'].iloc[-1]
            
            # Calculate pre-market change
            pre_market_change = current_price - prev_close
            pre_market_change_pct = (pre_market_change / prev_close) * 100
            
            # Volume analysis
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].tail(20).mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'prev_close': round(prev_close, 2),
                'change': round(pre_market_change, 2),
                'change_percent': round(pre_market_change_pct, 2),
                'volume': int(current_volume),
                'volume_ratio': round(volume_ratio, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting pre-market data for {symbol}: {e}")
            return {}
    
    def analyze_technical_setup(self, symbol: str, timeframe: str = "1d") -> Dict:
        """Analyze technical indicators for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            period = "60d" if timeframe == "1d" else "5d"
            hist = ticker.history(period=period, interval=timeframe)
            
            if len(hist) < 26:  # Need enough data for MACD
                return {}
            
            # Calculate RSI
            def calculate_rsi(prices, period=14):
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi
            
            # Calculate MACD
            def calculate_macd(prices, fast=12, slow=26, signal=9):
                ema_fast = prices.ewm(span=fast).mean()
                ema_slow = prices.ewm(span=slow).mean()
                macd = ema_fast - ema_slow
                macd_signal = macd.ewm(span=signal).mean()
                macd_histogram = macd - macd_signal
                return macd, macd_signal, macd_histogram
            
            close_prices = hist['Close']
            rsi = calculate_rsi(close_prices)
            macd, macd_signal, macd_histogram = calculate_macd(close_prices)
            
            # EMA crossovers
            ema_20 = close_prices.ewm(span=20).mean()
            ema_50 = close_prices.ewm(span=50).mean()
            
            current_rsi = rsi.iloc[-1]
            current_macd = macd.iloc[-1]
            current_macd_signal = macd_signal.iloc[-1]
            current_price = close_prices.iloc[-1]
            current_ema_20 = ema_20.iloc[-1]
            current_ema_50 = ema_50.iloc[-1]
            
            # Determine signals
            signals = []
            
            if current_rsi < 30:
                signals.append("RSI Oversold (Bullish)")
            elif current_rsi > 70:
                signals.append("RSI Overbought (Bearish)")
            
            if current_macd > current_macd_signal and macd.iloc[-2] <= macd_signal.iloc[-2]:
                signals.append("MACD Bullish Crossover")
            elif current_macd < current_macd_signal and macd.iloc[-2] >= macd_signal.iloc[-2]:
                signals.append("MACD Bearish Crossover")
            
            if current_ema_20 > current_ema_50:
                signals.append("EMA Bullish Trend")
            else:
                signals.append("EMA Bearish Trend")
            
            # Price vs EMAs
            if current_price > current_ema_20 > current_ema_50:
                signals.append("Above All EMAs (Strong Bullish)")
            elif current_price < current_ema_20 < current_ema_50:
                signals.append("Below All EMAs (Strong Bearish)")
            
            return {
                'rsi': round(current_rsi, 2),
                'macd': round(current_macd, 4),
                'macd_signal': round(current_macd_signal, 4),
                'ema_20': round(current_ema_20, 2),
                'ema_50': round(current_ema_50, 2),
                'signals': signals,
                'current_price': round(current_price, 2)
            }
            
        except Exception as e:
            print(f"Error analyzing technical setup for {symbol}: {e}")
            return {}
    
    def get_news_sentiment(self, symbol: str) -> Dict:
        """Get news sentiment for a symbol (simplified version)"""
        try:
            # Using a simple approach - in production you'd use proper news sentiment API
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return {'sentiment': 'neutral', 'score': 0, 'news_count': 0}
            
            # Simple sentiment analysis based on news titles
            positive_words = ['up', 'rise', 'gain', 'bull', 'boost', 'strong', 'beat', 'high', 'surge']
            negative_words = ['down', 'fall', 'drop', 'bear', 'weak', 'miss', 'low', 'crash', 'decline']
            
            sentiment_score = 0
            for article in news[:10]:  # Check recent 10 articles
                title = article.get('title', '').lower()
                for word in positive_words:
                    if word in title:
                        sentiment_score += 1
                for word in negative_words:
                    if word in title:
                        sentiment_score -= 1
            
            if sentiment_score > 2:
                sentiment = 'bullish'
            elif sentiment_score < -2:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'news_count': len(news)
            }
            
        except Exception as e:
            print(f"Error getting news sentiment for {symbol}: {e}")
            return {'sentiment': 'neutral', 'score': 0, 'news_count': 0}
    
    def scan_top_movers(self, limit: int = 20) -> List[Dict]:
        """Scan for top moving stocks with comprehensive analysis"""
        results = []
        
        for symbol in self.stock_universe[:limit]:  # Limit to avoid rate limits
            try:
                # Get pre-market data
                pre_market = self.get_pre_market_data(symbol)
                if not pre_market:
                    continue
                
                # Skip if change is too small
                if abs(pre_market.get('change_percent', 0)) < 2:
                    continue
                
                # Get technical analysis
                technical = self.analyze_technical_setup(symbol)
                if not technical:
                    continue
                
                # Get news sentiment
                sentiment = self.get_news_sentiment(symbol)
                
                # Combine data
                stock_data = {
                    **pre_market,
                    'technical': technical,
                    'sentiment': sentiment,
                    'score': self._calculate_opportunity_score(pre_market, technical, sentiment)
                }
                
                results.append(stock_data)
                
                # Add delay to avoid rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by opportunity score
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:10]  # Return top 10
    
    def _calculate_opportunity_score(self, pre_market: Dict, technical: Dict, sentiment: Dict) -> float:
        """Calculate opportunity score for ranking stocks"""
        score = 0
        
        # Pre-market movement weight
        change_pct = abs(pre_market.get('change_percent', 0))
        if change_pct > 5:
            score += 3
        elif change_pct > 3:
            score += 2
        elif change_pct > 2:
            score += 1
        
        # Volume weight
        volume_ratio = pre_market.get('volume_ratio', 1)
        if volume_ratio > 2:
            score += 2
        elif volume_ratio > 1.5:
            score += 1
        
        # Technical signals weight
        signals = technical.get('signals', [])
        for signal in signals:
            if 'Bullish' in signal or 'Oversold' in signal:
                score += 1
            elif 'Bearish' in signal or 'Overbought' in signal:
                score += 0.5
        
        # Sentiment weight
        sentiment_score = sentiment.get('score', 0)
        if abs(sentiment_score) > 2:
            score += 1
        
        return score

    def generate_options_recommendation(self, symbol: str, current_price: float, 
                                      technical: Dict, budget: float = None) -> Dict:
        """Generate options trading recommendation"""
        try:
            # Determine direction based on technical signals
            signals = technical.get('signals', [])
            bullish_signals = sum(1 for s in signals if 'Bullish' in s or 'Oversold' in s)
            bearish_signals = sum(1 for s in signals if 'Bearish' in s or 'Overbought' in s)
            
            if bullish_signals > bearish_signals:
                option_type = 'CALL'
                direction = 'bullish'
                # For calls, suggest slightly OTM
                strike_multiplier = 1.02  # 2% OTM
            else:
                option_type = 'PUT'
                direction = 'bearish'
                # For puts, suggest slightly OTM
                strike_multiplier = 0.98  # 2% OTM
            
            # Calculate strike price
            suggested_strike = round(current_price * strike_multiplier, 0)
            
            # Determine expiration (usually 2-4 weeks out for momentum plays)
            now = datetime.now()
            expiration_date = now + timedelta(weeks=3)
            # Adjust to Friday if needed
            while expiration_date.weekday() != 4:  # Friday = 4
                expiration_date += timedelta(days=1)
            
            # Estimate contract price (very rough estimate)
            time_to_expiry = (expiration_date - now).days / 365
            volatility = 0.3  # Assume 30% volatility
            
            # Simple Black-Scholes approximation for rough estimate
            if option_type == 'CALL':
                intrinsic_value = max(0, current_price - suggested_strike)
                time_value = current_price * volatility * (time_to_expiry ** 0.5) * 0.4
            else:
                intrinsic_value = max(0, suggested_strike - current_price)
                time_value = current_price * volatility * (time_to_expiry ** 0.5) * 0.4
            
            estimated_premium = max(0.05, intrinsic_value + time_value)
            
            # Calculate contract estimate (per 100 shares)
            contract_cost = estimated_premium * 100
            
            # Apply budget filter
            max_contracts = 1
            if budget:
                max_contracts = int(budget * 0.1 / contract_cost)  # Risk max 10% of budget
                max_contracts = max(1, min(max_contracts, 10))  # Between 1-10 contracts
            
            # Generate reasoning
            reasoning = f"{direction.title()} setup based on: {', '.join(signals[:3])}"
            
            return {
                'option_type': option_type,
                'strike_price': suggested_strike,
                'expiration_date': expiration_date.strftime('%Y-%m-%d'),
                'estimated_premium': round(estimated_premium, 2),
                'contract_cost': round(contract_cost, 2),
                'suggested_contracts': max_contracts,
                'total_cost': round(contract_cost * max_contracts, 2),
                'entry_price': round(estimated_premium * 0.95, 2),  # Suggest limit order 5% below estimate
                'reasoning': reasoning,
                'direction': direction
            }
            
        except Exception as e:
            print(f"Error generating options recommendation for {symbol}: {e}")
            return {}