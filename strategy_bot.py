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

def get_trading_recommendation(rsi_value):
    """
    Get trading recommendation based on RSI value
    
    Args:
        rsi_value: Current RSI value
    
    Returns:
        dict with recommendation details
    """
    if rsi_value < 30:
        return {
            'action': 'BUY CALL',
            'signal': 'BULLISH',
            'reason': 'RSI indicates oversold conditions - potential upward movement',
            'strength': 'STRONG' if rsi_value < 20 else 'MODERATE',
            'color': '#00ff88'  # Green
        }
    elif rsi_value > 70:
        return {
            'action': 'BUY PUT',
            'signal': 'BEARISH', 
            'reason': 'RSI indicates overbought conditions - potential downward movement',
            'strength': 'STRONG' if rsi_value > 80 else 'MODERATE',
            'color': '#ff4757'  # Red
        }
    else:
        return {
            'action': 'HOLD',
            'signal': 'NEUTRAL',
            'reason': 'RSI in neutral range - no strong directional signal',
            'strength': 'WEAK',
            'color': '#ffa502'  # Orange
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
        # Get current prices for popular stocks
        for stock_info in popular_stocks:
            try:
                ticker = yf.Ticker(stock_info['ticker'])
                hist = ticker.history(period='1d')
                
                if not hist.empty:
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
                continue  # Skip stocks that fail to fetch
                
    except Exception as e:
        # Fallback suggestions if API fails
        suitable_stocks = [
            {'ticker': 'SPY', 'name': 'SPDR S&P 500 ETF', 'price': 'N/A', 'note': 'Popular ETF - check current price'},
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'price': 'N/A', 'note': 'Large cap tech stock'},
            {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'price': 'N/A', 'note': 'Large cap tech stock'}
        ]
    
    return suitable_stocks[:8]  # Return top 8 suggestions

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