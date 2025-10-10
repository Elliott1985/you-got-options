from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from strategy_bot import calculate_rsi, get_trading_recommendation, get_popular_tickers_by_budget

app = Flask(__name__)

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
        
        # Fetch stock data (6 months)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        stock = yf.Ticker(ticker)
        hist_data = stock.history(start=start_date, end=end_date)
        
        if hist_data.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for ticker {ticker}. Please check the symbol.'
            })
        
        # Get current price
        current_price = hist_data['Close'].iloc[-1]
        
        # Calculate RSI
        rsi_values = calculate_rsi(hist_data['Close'])
        current_rsi = rsi_values.iloc[-1]
        
        # Get trading recommendation
        recommendation = get_trading_recommendation(current_rsi)
        
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
                'rsi': round(row['RSI'], 2) if pd.notna(row['RSI']) else None
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)