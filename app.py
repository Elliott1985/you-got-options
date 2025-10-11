from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from strategy_bot import (
    calculate_rsi, calculate_macd, get_trading_recommendation, 
    get_popular_tickers_by_budget, get_market_status, analyze_for_exit_signal
)
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# In-memory storage for active trades (in production, use a database)
active_trades = {}

def get_demo_analysis(ticker, budget):
    """Return demo analysis data for testing when Yahoo Finance is unavailable"""
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate fake but realistic data
    current_price = 150.25
    current_rsi = 65.8
    
    # Create fake chart data
    dates = [(datetime.now() - timedelta(days=x)) for x in range(90, 0, -1)]
    prices = []
    base_price = 140
    
    # Generate realistic price movements
    for i in range(90):
        # Add some random walk with trend
        change = np.random.normal(0, 2)  # Random change with std dev of 2
        base_price += change
        base_price = max(base_price, 100)  # Floor price at 100
        prices.append(base_price)
    
    # Calculate RSI and MACD on fake data
    price_series = pd.Series(prices)
    rsi_values = calculate_rsi(price_series)
    macd_data = calculate_macd(price_series)
    
    # Format chart data
    chart_formatted = []
    for i, date in enumerate(dates):
        price = prices[i]
        chart_formatted.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(price * 0.999, 2),
            'high': round(price * 1.005, 2),
            'low': round(price * 0.995, 2),
            'close': round(price, 2),
            'volume': int(np.random.normal(1000000, 200000)),
            'rsi': round(rsi_values.iloc[i], 2) if pd.notna(rsi_values.iloc[i]) else None,
            'macd': round(macd_data['macd'].iloc[i], 4) if i < len(macd_data['macd']) and pd.notna(macd_data['macd'].iloc[i]) else None,
            'macd_signal': round(macd_data['signal'].iloc[i], 4) if i < len(macd_data['signal']) and pd.notna(macd_data['signal'].iloc[i]) else None,
            'macd_histogram': round(macd_data['histogram'].iloc[i], 4) if i < len(macd_data['histogram']) and pd.notna(macd_data['histogram'].iloc[i]) else None
        })
    
    # Get trading recommendation with MACD
    recommendation = get_trading_recommendation(current_rsi, macd_data)
    
    # Calculate shares info if budget provided
    shares_info = {}
    if budget:
        max_shares = int(budget // current_price)
        shares_info = {
            'max_shares': max_shares,
            'cost_per_share': current_price,
            'total_cost': max_shares * current_price,
            'remaining_budget': budget - (max_shares * current_price)
        }
    
    response = {
        'success': True,
        'ticker': ticker.upper(),
        'company_name': 'Demo Company Inc. (Testing Data)',
        'current_price': round(current_price, 2),
        'current_rsi': round(current_rsi, 2),
        'recommendation': recommendation,
        'chart_data': chart_formatted,
        'shares_info': shares_info,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'demo_note': '⚠️ This is demo data for testing purposes'
    }
    
    return jsonify(response)

def get_demo_analysis_for_ticker(ticker, budget):
    """Return demo analysis data for specific ticker when Yahoo Finance is unavailable"""
    import numpy as np
    from datetime import datetime, timedelta
    
    # Realistic price ranges for popular stocks
    ticker_data = {
        'AAPL': {'price': 175.25, 'name': 'Apple Inc.'},
        'MSFT': {'price': 338.50, 'name': 'Microsoft Corporation'},
        'GOOGL': {'price': 138.75, 'name': 'Alphabet Inc.'},
        'TSLA': {'price': 248.50, 'name': 'Tesla, Inc.'},
        'META': {'price': 312.75, 'name': 'Meta Platforms, Inc.'},
        'NVDA': {'price': 445.80, 'name': 'NVIDIA Corporation'},
        'AMZN': {'price': 145.25, 'name': 'Amazon.com, Inc.'},
        'SPY': {'price': 428.75, 'name': 'SPDR S&P 500 ETF'},
        'DEMO': {'price': 150.25, 'name': 'Demo Company Inc.'},
        'TEST': {'price': 150.25, 'name': 'Test Company Inc.'}
    }
    
    # Get ticker info or use default
    info = ticker_data.get(ticker.upper(), {'price': 150.25, 'name': f'{ticker} Corporation'})
    current_price = info['price']
    company_name = f"{info['name']} (Demo Data)"
    
    # Generate realistic RSI (vary by ticker)
    rsi_base = {'AAPL': 65.8, 'MSFT': 58.2, 'GOOGL': 72.1, 'TSLA': 45.5, 
                'META': 55.9, 'NVDA': 68.3, 'AMZN': 62.7, 'SPY': 52.4}.get(ticker.upper(), 65.8)
    current_rsi = rsi_base + np.random.normal(0, 3)  # Add some variation
    current_rsi = max(10, min(90, current_rsi))  # Keep in realistic range
    
    # Generate fake but realistic data
    dates = [(datetime.now() - timedelta(days=x)) for x in range(90, 0, -1)]
    prices = []
    base_price = current_price * 0.95  # Start slightly lower
    
    # Generate realistic price movements
    for i in range(90):
        # Add some random walk with slight upward trend
        change = np.random.normal(0.5, 2)  # Slight bullish bias
        base_price += change
        base_price = max(base_price, current_price * 0.8)  # Floor
        prices.append(base_price)
    
    # Ensure last price matches current price
    prices[-1] = current_price
    
    # Calculate RSI and MACD on fake data
    price_series = pd.Series(prices)
    rsi_values = calculate_rsi(price_series)
    macd_data = calculate_macd(price_series)
    
    # Override the last RSI value with our realistic one
    rsi_values.iloc[-1] = current_rsi
    
    # Format chart data
    chart_formatted = []
    for i, date in enumerate(dates):
        price = prices[i]
        chart_formatted.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(price * 0.999, 2),
            'high': round(price * 1.005, 2),
            'low': round(price * 0.995, 2),
            'close': round(price, 2),
            'volume': int(np.random.normal(1000000, 200000)),
            'rsi': round(rsi_values.iloc[i], 2) if pd.notna(rsi_values.iloc[i]) else None,
            'macd': round(macd_data['macd'].iloc[i], 4) if i < len(macd_data['macd']) and pd.notna(macd_data['macd'].iloc[i]) else None,
            'macd_signal': round(macd_data['signal'].iloc[i], 4) if i < len(macd_data['signal']) and pd.notna(macd_data['signal'].iloc[i]) else None,
            'macd_histogram': round(macd_data['histogram'].iloc[i], 4) if i < len(macd_data['histogram']) and pd.notna(macd_data['histogram'].iloc[i]) else None
        })
    
    # Get trading recommendation with MACD
    recommendation = get_trading_recommendation(current_rsi, macd_data)
    
    # Calculate shares info if budget provided
    shares_info = {}
    if budget:
        max_shares = int(budget // current_price)
        shares_info = {
            'max_shares': max_shares,
            'cost_per_share': current_price,
            'total_cost': max_shares * current_price,
            'remaining_budget': budget - (max_shares * current_price)
        }
    
    response = {
        'success': True,
        'ticker': ticker.upper(),
        'company_name': company_name,
        'current_price': round(current_price, 2),
        'current_rsi': round(current_rsi, 2),
        'recommendation': recommendation,
        'chart_data': chart_formatted,
        'shares_info': shares_info,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'demo_note': f'⚠️ Demo data for {ticker} - Real data available on live deployment'
    }
    
    return jsonify(response)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        budget = data.get('budget')
        
        # Convert budget to float if provided
        if budget:
            try:
                budget = float(budget)
            except (ValueError, TypeError):
                budget = None
        
        # If no ticker provided but budget is, suggest popular tickers
        if not ticker and budget:
            suggestions = get_popular_tickers_by_budget(budget)
            return jsonify({
                'success': True,
                'suggestions': suggestions,
                'message': f'Here are some popular stocks that fit your ${budget:.2f} budget:'
            })
        
        # If no ticker provided and no budget, return error
        if not ticker:
            return jsonify({
                'success': False,
                'error': 'Please provide a stock ticker symbol'
            })
        
        # Fetch stock data (6 months with retry logic)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        hist_data = None
        error_msg = None
        
        # Try different time periods if the longer period fails
        periods_to_try = [
            (start_date, end_date, '6 months'),
            (end_date - timedelta(days=90), end_date, '3 months'), 
            (end_date - timedelta(days=30), end_date, '1 month'),
            (end_date - timedelta(days=14), end_date, '2 weeks')
        ]
        
        for start, end, period_name in periods_to_try:
            try:
                stock = yf.Ticker(ticker)
                hist_data = stock.history(start=start, end=end)
                
                if not hist_data.empty and len(hist_data) >= 14:  # Need at least 14 days for RSI
                    print(f"Successfully fetched {len(hist_data)} days of data for {ticker} ({period_name})")
                    break
                elif not hist_data.empty:
                    print(f"Fetched {len(hist_data)} days of data for {ticker} ({period_name}) - insufficient for RSI")
                    continue
                else:
                    print(f"No data returned for {ticker} ({period_name})")
                    continue
                    
            except Exception as e:
                print(f"Error fetching {period_name} data for {ticker}: {e}")
                error_msg = str(e)
                continue
        
        if hist_data is None or hist_data.empty or len(hist_data) < 14:
            # Check if this is a demo request (for testing when Yahoo Finance is down)
            if ticker.upper() in ['DEMO', 'TEST'] or '-DEMO' in ticker.upper():
                # Extract the base ticker if it's in format like "AAPL-DEMO"
                base_ticker = ticker.upper().replace('-DEMO', '') if '-DEMO' in ticker.upper() else ticker
                return get_demo_analysis_for_ticker(base_ticker, budget)
            
            # For popular tickers, offer demo analysis as fallback
            popular_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA', 'AMZN', 'SPY']
            if ticker.upper() in popular_tickers:
                if "Too Many Requests" in str(error_msg) or "rate limit" in str(error_msg).lower() or "429" in str(error_msg):
                    return jsonify({
                        'success': False,
                        'error': f'🚫 Yahoo Finance is rate-limited right now.\n\n🎯 QUICK FIX:\n• Try "{ticker}-DEMO" to see how {ticker} analysis would look\n• Or use "DEMO" for full testing\n\n⚡ Real {ticker} data works great on the live deployment!',
                        'suggested_demo': f'{ticker}-DEMO'
                    })
            
            if "Too Many Requests" in str(error_msg) or "rate limit" in str(error_msg).lower() or "429" in str(error_msg):
                return jsonify({
                    'success': False,
                    'error': f'🚫 Yahoo Finance is temporarily busy (rate limited). Try these options:\n\n✅ Use "DEMO" ticker for full testing\n✅ Try again in 1-2 minutes\n✅ Use budget-only mode for stock suggestions\n\nThe live deployment won\'t have this issue!'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'📊 Market data temporarily unavailable for {ticker}.\n\n🎯 Try these instead:\n• "DEMO" - Full featured testing\n• "TEST" - Alternative demo mode\n• Leave ticker empty and use budget for suggestions\n\nReal tickers work better on the live deployment!'
                })
        
        # Get current price
        current_price = hist_data['Close'].iloc[-1]
        
        # Calculate RSI and MACD
        rsi_values = calculate_rsi(hist_data['Close'])
        macd_data = calculate_macd(hist_data['Close'])
        current_rsi = rsi_values.iloc[-1]
        
        # Get trading recommendation with MACD analysis
        recommendation = get_trading_recommendation(current_rsi, macd_data)
        
        # Calculate approximate shares if budget provided
        shares_info = {}
        if budget:
            max_shares = int(budget // current_price)
            shares_info = {
                'max_shares': max_shares,
                'cost_per_share': current_price,
                'total_cost': max_shares * current_price,
                'remaining_budget': budget - (max_shares * current_price)
            }
        
        # Prepare chart data (last 90 days for better visualization)
        chart_data = hist_data.tail(90).copy()
        chart_data['RSI'] = rsi_values.tail(90)
        chart_data['MACD'] = macd_data['macd'].tail(90)
        chart_data['MACD_Signal'] = macd_data['signal'].tail(90)
        chart_data['MACD_Histogram'] = macd_data['histogram'].tail(90)
        
        # Format data for frontend
        chart_formatted = []
        for date, row in chart_data.iterrows():
            chart_formatted.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'close': round(row['Close'], 2),
                'volume': int(row['Volume']),
                'rsi': round(row['RSI'], 2) if pd.notna(row['RSI']) else None,
                'macd': round(row['MACD'], 4) if pd.notna(row['MACD']) else None,
                'macd_signal': round(row['MACD_Signal'], 4) if pd.notna(row['MACD_Signal']) else None,
                'macd_histogram': round(row['MACD_Histogram'], 4) if pd.notna(row['MACD_Histogram']) else None
            })
        
        # Get company info
        try:
            info = stock.info
            company_name = info.get('longName', ticker)
        except:
            company_name = ticker
        
        response = {
            'success': True,
            'ticker': ticker,
            'company_name': company_name,
            'current_price': round(current_price, 2),
            'current_rsi': round(current_rsi, 2),
            'recommendation': recommendation,
            'chart_data': chart_formatted,
            'shares_info': shares_info,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Simple test endpoint for debugging"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'method': request.method,
        'timestamp': datetime.now().isoformat(),
        'environment': 'production' if os.environ.get('FLASK_ENV') == 'production' else 'development'
    })

@app.route('/api/market-status')
def market_status():
    """Get current market status"""
    try:
        status = get_market_status()
        return jsonify({'success': True, **status})
    except Exception as e:
        # Fallback if timezone library not available
        return jsonify({
            'success': True,
            'status': 'UNKNOWN',
            'message': 'Market status unavailable',
            'is_trading_hours': True  # Assume trading hours for functionality
        })

@app.route('/api/enter-trade', methods=['POST'])
def enter_trade():
    """Enter a new trade for tracking"""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        entry_price = float(data.get('entry_price', 0))
        email = data.get('email', '').strip()
        
        if not ticker or entry_price <= 0:
            return jsonify({
                'success': False,
                'error': 'Valid ticker and entry price required'
            })
        
        # Generate unique trade ID
        trade_id = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store trade information
        active_trades[trade_id] = {
            'ticker': ticker,
            'entry_price': entry_price,
            'entry_time': datetime.now().isoformat(),
            'email': email,
            'status': 'ACTIVE',
            'last_check': None
        }
        
        # Store trade ID in session for user
        if 'user_trades' not in session:
            session['user_trades'] = []
        session['user_trades'].append(trade_id)
        session.modified = True
        
        return jsonify({
            'success': True,
            'trade_id': trade_id,
            'message': f'Now tracking {ticker} position entered at ${entry_price:.2f}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error entering trade: {str(e)}'
        })

@app.route('/api/track-trade/<trade_id>')
def track_trade(trade_id):
    """Get current tracking status for a trade"""
    try:
        if trade_id not in active_trades:
            return jsonify({
                'success': False,
                'error': 'Trade not found'
            })
        
        trade = active_trades[trade_id]
        ticker = trade['ticker']
        entry_price = trade['entry_price']
        
        # Get current data
        current_data = get_current_stock_data(ticker)
        if not current_data['success']:
            return jsonify(current_data)
        
        current_price = current_data['current_price']
        rsi_values = current_data['rsi_values']
        macd_data = current_data['macd_data']
        current_rsi = rsi_values.iloc[-1] if len(rsi_values) > 0 else 50
        
        # Analyze for exit signal
        analysis = analyze_for_exit_signal(
            current_rsi, macd_data, entry_price, current_price
        )
        
        # Update trade status
        trade['last_check'] = datetime.now().isoformat()
        trade['current_price'] = current_price
        trade['current_rsi'] = current_rsi
        
        # Prepare response
        response = {
            'success': True,
            'trade_id': trade_id,
            'ticker': ticker,
            'entry_price': entry_price,
            'current_price': current_price,
            'pnl': analysis['pnl'],
            'rsi': current_rsi,
            'analysis': analysis,
            'last_updated': trade['last_check'],
            'market_status': get_market_status() if 'pytz' in globals() else {'status': 'UNKNOWN'}
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error tracking trade: {str(e)}'
        })

@app.route('/api/stop-tracking/<trade_id>', methods=['POST'])
def stop_tracking(trade_id):
    """Stop tracking a trade"""
    try:
        if trade_id not in active_trades:
            return jsonify({
                'success': False,
                'error': 'Trade not found'
            })
        
        # Update trade status
        active_trades[trade_id]['status'] = 'STOPPED'
        active_trades[trade_id]['stop_time'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Trade tracking stopped'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error stopping trade: {str(e)}'
        })

@app.route('/api/user-trades')
def get_user_trades():
    """Get all trades for current user session"""
    try:
        user_trade_ids = session.get('user_trades', [])
        user_trades = []
        
        for trade_id in user_trade_ids:
            if trade_id in active_trades:
                trade = active_trades[trade_id].copy()
                trade['trade_id'] = trade_id
                user_trades.append(trade)
        
        return jsonify({
            'success': True,
            'trades': user_trades
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting trades: {str(e)}'
        })

def get_current_stock_data(ticker):
    """Helper function to get current stock data with RSI and MACD"""
    try:
        # Handle demo tickers
        if ticker.upper() in ['DEMO', 'TEST']:
            return get_demo_stock_data()
        
        # Get recent data (30 days should be enough for indicators)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        stock = yf.Ticker(ticker)
        hist_data = stock.history(start=start_date, end=end_date)
        
        if hist_data.empty or len(hist_data) < 26:  # Need at least 26 days for MACD
            return {
                'success': False,
                'error': f'Insufficient data for {ticker}'
            }
        
        current_price = hist_data['Close'].iloc[-1]
        
        # Calculate indicators
        rsi_values = calculate_rsi(hist_data['Close'])
        macd_data = calculate_macd(hist_data['Close'])
        
        return {
            'success': True,
            'current_price': current_price,
            'rsi_values': rsi_values,
            'macd_data': macd_data,
            'hist_data': hist_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error fetching data for {ticker}: {str(e)}'
        }

def get_demo_stock_data():
    """Generate demo stock data for trade tracking"""
    import numpy as np
    
    # Generate realistic price movements for tracking
    base_price = 150.0
    prices = []
    
    for i in range(30):  # 30 days of data
        # Add some random walk
        change = np.random.normal(0, 1.5)  # Random change
        base_price += change
        base_price = max(base_price, 100)  # Floor price
        prices.append(base_price)
    
    price_series = pd.Series(prices)
    current_price = prices[-1]
    
    # Calculate indicators
    rsi_values = calculate_rsi(price_series)
    macd_data = calculate_macd(price_series)
    
    return {
        'success': True,
        'current_price': current_price,
        'rsi_values': rsi_values,
        'macd_data': macd_data,
        'hist_data': pd.DataFrame({'Close': prices})
    }

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
