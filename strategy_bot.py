import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def calculate_rsi(prices, period=14):
    """
    Calculate RSI (Relative Strength Index) for given prices
    
    Args:
        prices: pandas Series of closing prices
        period: RSI period (default 14)
    
    Returns:
        pandas Series with RSI values
    """
    # Calculate price changes
    delta = prices.diff()
    
    # Calculate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    
    # Calculate average gains and losses using exponential moving average
    avg_gains = gains.ewm(span=period, adjust=False).mean()
    avg_losses = losses.ewm(span=period, adjust=False).mean()
    
    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate MACD (Moving Average Convergence Divergence) for given prices
    
    Args:
        prices: pandas Series of closing prices
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line EMA period (default 9)
    
    Returns:
        dict with MACD line, signal line, and histogram
    """
    # Calculate EMAs
    ema_fast = prices.ewm(span=fast_period).mean()
    ema_slow = prices.ewm(span=slow_period).mean()
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period).mean()
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }

def get_trading_recommendation(rsi_value, macd_data=None):
    """
    Get trading recommendation based on RSI value and optional MACD data
    
    Args:
        rsi_value: Current RSI value
        macd_data: Optional dict with MACD values {macd, signal, histogram}
    
    Returns:
        dict with recommendation details
    """
    # RSI-only analysis (backwards compatibility)
    if macd_data is None:
        if rsi_value < 30:
            return {
                'action': 'BUY CALL',
                'signal': 'BULLISH',
                'reason': 'RSI indicates oversold conditions - potential upward movement',
                'strength': 'STRONG' if rsi_value < 20 else 'MODERATE',
                'color': '#00c851'  # Green
            }
        elif rsi_value > 70:
            return {
                'action': 'BUY PUT',
                'signal': 'BEARISH', 
                'reason': 'RSI indicates overbought conditions - potential downward movement',
                'strength': 'STRONG' if rsi_value > 80 else 'MODERATE',
                'color': '#ff4444'  # Red
            }
        else:
            return {
                'action': 'HOLD',
                'signal': 'NEUTRAL',
                'reason': 'RSI in neutral range - no strong directional signal',
                'strength': 'WEAK',
                'color': '#ffbb33'  # Orange
            }
    
    # Combined RSI and MACD analysis
    current_macd = macd_data['macd'].iloc[-1] if len(macd_data['macd']) > 0 else 0
    current_signal = macd_data['signal'].iloc[-1] if len(macd_data['signal']) > 0 else 0
    current_histogram = macd_data['histogram'].iloc[-1] if len(macd_data['histogram']) > 0 else 0
    
    # Check for MACD crossovers (look at last 2 values)
    macd_bullish_crossover = False
    macd_bearish_crossover = False
    
    if len(macd_data['macd']) >= 2 and len(macd_data['signal']) >= 2:
        prev_macd = macd_data['macd'].iloc[-2]
        prev_signal = macd_data['signal'].iloc[-2]
        
        # Bullish crossover: MACD crosses above signal line
        macd_bullish_crossover = (prev_macd <= prev_signal) and (current_macd > current_signal)
        
        # Bearish crossover: MACD crosses below signal line
        macd_bearish_crossover = (prev_macd >= prev_signal) and (current_macd < current_signal)
    
    # Strong exit signals (combination of RSI and MACD)
    if rsi_value > 70 and macd_bearish_crossover:
        return {
            'action': 'SELL NOW',
            'signal': 'STRONG BEARISH',
            'reason': f'RSI overbought ({rsi_value:.1f}) + MACD bearish crossover - Strong sell signal',
            'strength': 'STRONG',
            'color': '#ff4444',
            'exit_signal': True
        }
    
    if rsi_value < 30 and macd_bullish_crossover:
        return {
            'action': 'BUY STRONG',
            'signal': 'STRONG BULLISH',
            'reason': f'RSI oversold ({rsi_value:.1f}) + MACD bullish crossover - Strong buy signal',
            'strength': 'STRONG',
            'color': '#00c851',
            'entry_signal': True
        }
    
    # Moderate signals
    if rsi_value > 70:
        return {
            'action': 'REVIEW POSITION',
            'signal': 'BEARISH',
            'reason': f'RSI overbought ({rsi_value:.1f}) - Consider reducing position',
            'strength': 'MODERATE',
            'color': '#ff8800',
            'macd_trend': 'Bearish' if current_macd < current_signal else 'Bullish'
        }
    
    if rsi_value < 30:
        return {
            'action': 'BUY OPPORTUNITY',
            'signal': 'BULLISH',
            'reason': f'RSI oversold ({rsi_value:.1f}) - Consider accumulating',
            'strength': 'MODERATE',
            'color': '#00c851',
            'macd_trend': 'Bullish' if current_macd > current_signal else 'Bearish'
        }
    
    # Neutral with MACD context
    macd_trend = 'Bullish' if current_macd > current_signal else 'Bearish'
    momentum = 'Increasing' if current_histogram > 0 else 'Decreasing'
    
    return {
        'action': 'HOLD',
        'signal': 'NEUTRAL',
        'reason': f'RSI neutral ({rsi_value:.1f}) - {macd_trend} MACD trend, {momentum} momentum',
        'strength': 'WEAK',
        'color': '#ffbb33',
        'macd_trend': macd_trend
    }

def get_popular_tickers_by_budget(budget):
    """
    Get popular stock suggestions based on budget
    
    Args:
        budget: Available budget amount
    
    Returns:
        list of suggested ticker dictionaries
    """
    # Popular tickers with different price ranges
    popular_stocks = [
        # Lower priced stocks (under $50)
        {'ticker': 'F', 'name': 'Ford Motor Company'},
        {'ticker': 'BAC', 'name': 'Bank of America'},
        {'ticker': 'T', 'name': 'AT&T Inc.'},
        {'ticker': 'PFE', 'name': 'Pfizer Inc.'},
        {'ticker': 'WFC', 'name': 'Wells Fargo'},
        {'ticker': 'KO', 'name': 'Coca-Cola'},
        
        # Mid-priced stocks ($50-$200)
        {'ticker': 'AAPL', 'name': 'Apple Inc.'},
        {'ticker': 'MSFT', 'name': 'Microsoft Corporation'},
        {'ticker': 'GOOGL', 'name': 'Alphabet Inc.'},
        {'ticker': 'TSLA', 'name': 'Tesla, Inc.'},
        {'ticker': 'META', 'name': 'Meta Platforms'},
        {'ticker': 'NVDA', 'name': 'NVIDIA Corporation'},
        
        # Higher priced stocks ($200+)
        {'ticker': 'AMZN', 'name': 'Amazon.com Inc.'},
        {'ticker': 'BRK-B', 'name': 'Berkshire Hathaway'},
        {'ticker': 'UNH', 'name': 'UnitedHealth Group'},
        {'ticker': 'V', 'name': 'Visa Inc.'}
    ]
    
    suitable_stocks = []
    
    try:
        import time
        # Get current prices for popular stocks with retry and delay
        for i, stock_info in enumerate(popular_stocks):
            try:
                # Add a small delay between requests to avoid rate limiting
                if i > 0:
                    time.sleep(0.5)  # 500ms delay between requests
                
                ticker = yf.Ticker(stock_info['ticker'])
                
                # Try different approaches to get current price
                hist = None
                for period in ['1d', '5d', '1mo']:
                    try:
                        hist = ticker.history(period=period)
                        if not hist.empty:
                            break
                    except:
                        continue
                
                if hist is not None and not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    max_shares = int(budget // current_price)
                    
                    if max_shares > 0:  # Can afford at least 1 share
                        suitable_stocks.append({
                            'ticker': stock_info['ticker'],
                            'name': stock_info['name'],
                            'price': round(current_price, 2),
                            'max_shares': max_shares,
                            'total_cost': round(max_shares * current_price, 2),
                            'remaining_budget': round(budget - (max_shares * current_price), 2)
                        })
                
                # Limit to top 8 suggestions
                if len(suitable_stocks) >= 8:
                    break
                    
            except Exception as e:
                print(f"Error fetching data for {stock_info['ticker']}: {e}")
                continue  # Skip stocks that fail to fetch
                
    except Exception as e:
        print(f"Error in budget suggestions: {e}")
    
    # If no suitable stocks found or API failed, provide fallback suggestions
    if len(suitable_stocks) == 0:
        # Create realistic fallback suggestions with estimated prices
        fallback_suggestions = [
            {'ticker': 'F', 'name': 'Ford Motor Company', 'price': 12.50, 'estimated': True},
            {'ticker': 'T', 'name': 'AT&T Inc.', 'price': 16.25, 'estimated': True},
            {'ticker': 'BAC', 'name': 'Bank of America', 'price': 32.75, 'estimated': True},
            {'ticker': 'KO', 'name': 'Coca-Cola', 'price': 58.50, 'estimated': True},
            {'ticker': 'PFE', 'name': 'Pfizer Inc.', 'price': 28.90, 'estimated': True},
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'price': 175.25, 'estimated': True},
            {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'price': 338.50, 'estimated': True},
            {'ticker': 'SPY', 'name': 'SPDR S&P 500 ETF', 'price': 425.75, 'estimated': True}
        ]
        
        for stock_info in fallback_suggestions:
            current_price = stock_info['price']
            max_shares = int(budget // current_price)
            
            if max_shares > 0:  # Can afford at least 1 share
                suitable_stocks.append({
                    'ticker': stock_info['ticker'],
                    'name': stock_info['name'] + ' (Estimated Price)',
                    'price': round(current_price, 2),
                    'max_shares': max_shares,
                    'total_cost': round(max_shares * current_price, 2),
                    'remaining_budget': round(budget - (max_shares * current_price), 2),
                    'note': '⚠️ Price estimated - Yahoo Finance unavailable'
                })
            
            # Limit to top 6 suggestions
            if len(suitable_stocks) >= 6:
                break
    
    return suitable_stocks[:8]  # Return top 8 suggestions

def get_market_status():
    """
    Determine if the market is currently open, closed, or in extended hours
    
    Returns:
        dict with market status and next session info
    """
    import pytz
    from datetime import time
    
    # Get current time in EST (market timezone)
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est)
    current_weekday = current_time.weekday()  # 0=Monday, 6=Sunday
    current_time_only = current_time.time()
    
    # Market hours (EST)
    pre_market_start = time(4, 0)   # 4:00 AM EST
    market_open = time(9, 30)       # 9:30 AM EST
    market_close = time(16, 0)      # 4:00 PM EST
    after_hours_end = time(20, 0)   # 8:00 PM EST
    
    # Check if it's a weekend
    if current_weekday >= 5:  # Saturday or Sunday
        next_open = "Monday 9:30 AM EST"
        return {
            'status': 'CLOSED',
            'message': 'Market is closed for the weekend',
            'next_session': next_open,
            'is_trading_hours': False
        }
    
    # Check market status on weekdays
    if current_time_only < pre_market_start:
        return {
            'status': 'CLOSED',
            'message': 'Market is closed - opens at 4:00 AM EST for pre-market',
            'next_session': 'Today 4:00 AM EST',
            'is_trading_hours': False
        }
    elif pre_market_start <= current_time_only < market_open:
        return {
            'status': 'PRE_MARKET',
            'message': 'Pre-market trading session',
            'next_session': 'Today 9:30 AM EST (Regular Hours)',
            'is_trading_hours': True
        }
    elif market_open <= current_time_only < market_close:
        return {
            'status': 'OPEN',
            'message': 'Market is open for regular trading',
            'next_session': 'Today 4:00 PM EST (Market Close)',
            'is_trading_hours': True
        }
    elif market_close <= current_time_only < after_hours_end:
        return {
            'status': 'AFTER_HOURS',
            'message': 'After-hours trading session',
            'next_session': 'Tomorrow 4:00 AM EST',
            'is_trading_hours': True
        }
    else:
        return {
            'status': 'CLOSED',
            'message': 'Market is closed until tomorrow',
            'next_session': 'Tomorrow 4:00 AM EST',
            'is_trading_hours': False
        }

def analyze_for_exit_signal(rsi_value, macd_data, entry_price, current_price):
    """
    Specialized analysis for exit signals when tracking a trade
    
    Args:
        rsi_value: Current RSI value
        macd_data: MACD data dict
        entry_price: Price at which position was entered
        current_price: Current market price
    
    Returns:
        dict with exit recommendation and P&L info
    """
    recommendation = get_trading_recommendation(rsi_value, macd_data)
    
    # Calculate P&L
    pnl_dollar = current_price - entry_price
    pnl_percent = ((current_price - entry_price) / entry_price) * 100
    
    # Enhance recommendation with P&L context
    recommendation['pnl'] = {
        'dollar': pnl_dollar,
        'percent': pnl_percent,
        'entry_price': entry_price,
        'current_price': current_price
    }
    
    # Determine if this is a strong exit signal
    is_exit_signal = recommendation.get('exit_signal', False)
    
    if is_exit_signal:
        recommendation['alert_level'] = 'HIGH'
        recommendation['alert_message'] = f'SELL SIGNAL: {recommendation["reason"]}. Current P&L: {pnl_percent:+.1f}%'
    elif recommendation['action'] in ['REVIEW POSITION'] and pnl_percent > 10:
        recommendation['alert_level'] = 'MEDIUM'
        recommendation['alert_message'] = f'Consider taking profits. Current gain: +{pnl_percent:.1f}%'
    elif pnl_percent < -10 and rsi_value < 40:
        recommendation['alert_level'] = 'MEDIUM'
        recommendation['alert_message'] = f'Position down {pnl_percent:.1f}%. Consider stop loss.'
    else:
        recommendation['alert_level'] = 'LOW'
    
    return recommendation

def calculate_options_estimate(stock_price, budget, option_type='call'):
    """
    Rough estimate for options pricing (simplified)
    
    Args:
        stock_price: Current stock price
        budget: Available budget
        option_type: 'call' or 'put'
    
    Returns:
        dict with options estimate
    """
    # Very rough estimation - real options pricing is much more complex
    # This is for demonstration purposes only
    
    # Typical option premium might be 2-5% of stock price
    estimated_premium = stock_price * 0.03  # 3% estimate
    
    max_contracts = int(budget // (estimated_premium * 100))  # Options are sold in lots of 100
    
    return {
        'estimated_premium_per_share': round(estimated_premium, 2),
        'estimated_premium_per_contract': round(estimated_premium * 100, 2),
        'max_contracts': max_contracts,
        'total_cost': round(max_contracts * estimated_premium * 100, 2),
        'remaining_budget': round(budget - (max_contracts * estimated_premium * 100), 2),
        'note': 'This is a rough estimate. Actual option prices vary significantly.'
    }