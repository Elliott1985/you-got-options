# You Got Options - RSI Trading Bot

A full-stack Python web application using Flask that functions as an RSI-based options trading bot with a stylish dark mode UI inspired by graffiti and hip-hop aesthetics.

## Features

### Frontend
- **Stylish UI**: Dark mode with graffiti/hip-hop inspired design
- **Interactive Interface**: Clean inputs for stock ticker and budget
- **Responsive Charts**: Real-time RSI indicator and candlestick visualization
- **Dynamic Analysis**: Live display of current price, RSI value, and trading recommendations
- **Budget Suggestions**: Get stock recommendations based on available budget
- **Hover Animations**: Smooth card and button interactions

### Backend
- **Real-time Data**: Uses `yfinance` to fetch 6 months of stock data
- **RSI Calculation**: 14-period RSI with proper technical analysis
- **Smart Recommendations**:
  - RSI < 30 → **BUY CALL** (Bullish signal)
  - RSI > 70 → **BUY PUT** (Bearish signal)  
  - Else → **HOLD** (Neutral)
- **Budget Analysis**: Calculate max shares and costs based on available budget
- **Popular Stock Suggestions**: Recommend stocks that fit within budget constraints

## Project Structure

```
you-got-options/
├── app.py                 # Main Flask application
├── strategy_bot.py        # RSI calculation and trading logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML template
├── static/
│   └── styles.css        # Dark mode CSS with hip-hop styling
└── README.md             # This file
```

## Installation

1. **Clone or navigate to the project**:
```bash
cd you-got-options
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

1. **Start the Flask application**:
```bash
python app.py
```

2. **Open your browser** and navigate to:
```
http://localhost:5000
```

3. **Use the application**:
   - Enter a stock ticker (e.g., AAPL, TSLA) and/or budget amount
   - Click **ANALYZE** to get RSI-based trading recommendations
   - View the interactive chart showing price and RSI over the last 90 days
   - If you only enter a budget, get stock suggestions that fit your budget

## API Endpoints

- `GET /` - Main application interface
- `POST /api/analyze` - Analyze stock with ticker and/or budget
- `GET /api/health` - Health check endpoint

## Trading Logic

The bot uses a simple but effective RSI-based strategy:

1. **Oversold Condition (RSI < 30)**: Recommends **BUY CALL**
   - Theory: Stock may be undervalued and due for upward movement
   
2. **Overbought Condition (RSI > 70)**: Recommends **BUY PUT**  
   - Theory: Stock may be overvalued and due for downward correction
   
3. **Neutral Range (30 ≤ RSI ≤ 70)**: Recommends **HOLD**
   - Theory: No strong directional signal, wait for better entry

## Technical Details

- **RSI Calculation**: 14-period using exponential moving average
- **Data Source**: Yahoo Finance via `yfinance` library
- **Chart Library**: Chart.js for responsive visualization
- **Styling**: CSS Grid, Flexbox, and custom animations
- **Responsive**: Mobile-friendly design with breakpoints

## Future Features

- 🚀 Live trade tracking integration
- 📈 Multiple technical indicators (MACD, Bollinger Bands)
- 📊 Portfolio management
- 🔔 Price alerts and notifications
- 📱 Mobile app version

## Disclaimer

⚠️ **Important**: This application is for educational purposes only and should not be considered as financial advice. Options trading involves significant risk and can result in substantial losses. Always do your own research and consult with a qualified financial advisor before making trading decisions.

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Happy Trading! 🚀📈**