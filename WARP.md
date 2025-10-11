# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

You Got Options is a full-stack Python web application using Flask that functions as an RSI-based options trading bot. It features a stylish dark mode UI inspired by graffiti and hip-hop aesthetics.

**Key Features:**
- Real-time RSI analysis using yfinance data
- Options trading recommendations (BUY CALL/PUT/HOLD) with hip-hop quotes
- Budget-based stock suggestions
- Interactive price and RSI charts
- **Hip-hop inspired theme** with iconic album covers and Wu-Tang watermark
- Rotating vinyl album showcase with graffiti-style fonts
- Responsive dark mode UI with neon accents and vinyl scratch effects

**⚠️ Important:** This is an educational trading tool, not financial advice.

## Common Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start Flask development server
python3 app.py
# OR
flask run

# Application runs on http://localhost:5001
```

### Development Commands
```bash
# Check Python version (requires 3.7+)
python3 --version

# Install single dependency
pip install package_name

# Update requirements after adding dependencies
pip freeze > requirements.txt

# Test specific functionality (manual testing via web interface)
python3 -c "from strategy_bot import calculate_rsi; print('RSI module working')"
```

## Architecture Overview

### Backend Structure
The application follows a simple Flask MVC pattern:

- **`app.py`** - Main Flask application with three endpoints:
  - `/` - Serves the main interface
  - `POST /api/analyze` - Core analysis endpoint handling both stock analysis and budget suggestions
  - `GET /api/health` - Health check endpoint

- **`strategy_bot.py`** - Trading logic module containing:
  - RSI calculation using exponential moving averages (14-period)
  - Trading recommendations based on RSI thresholds (<30=BULLISH, >70=BEARISH)
  - Popular stock suggestions filtered by budget constraints
  - Options pricing estimates (simplified)

### Frontend Structure
Single-page application using vanilla JavaScript:

- **`templates/index.html`** - Complete SPA with embedded JavaScript
- **`static/styles.css`** - Dark mode CSS with hip-hop aesthetics and animations

### Data Flow Architecture
1. **Input Handling**: Accepts ticker symbol and/or budget via form
2. **Data Fetching**: Uses `yfinance` to get 6 months of historical data
3. **Analysis**: Calculates 14-period RSI using exponential moving averages
4. **Recommendation Engine**: Applies RSI thresholds for trading signals
5. **Visualization**: Chart.js renders dual-axis price/RSI charts
6. **Budget Analysis**: Calculates max shares and remaining budget

### Key Dependencies
- **Flask 2.3.3** - Web framework
- **yfinance 0.2.28** - Yahoo Finance data API
- **pandas 2.1.1** - Data manipulation
- **numpy 1.25.2** - Numerical computations
- **ta-lib 0.4.28** - Technical analysis (if needed for future features)

## RSI Trading Strategy

The bot implements a standard RSI-based options strategy:

- **RSI < 30**: Oversold → BUY CALL (bullish signal)
- **RSI > 70**: Overbought → BUY PUT (bearish signal)  
- **30 ≤ RSI ≤ 70**: Neutral → HOLD

Strength indicators:
- STRONG: RSI < 20 or RSI > 80
- MODERATE: 20 ≤ RSI < 30 or 70 < RSI ≤ 80
- WEAK: 30 ≤ RSI ≤ 70

## API Response Formats

### Stock Analysis Response
```json
{
  "success": true,
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "current_price": 150.25,
  "current_rsi": 65.8,
  "recommendation": {
    "action": "HOLD",
    "signal": "NEUTRAL",
    "reason": "RSI in neutral range - no strong directional signal",
    "strength": "WEAK",
    "color": "#ffa502"
  },
  "chart_data": [...], // 90 days of OHLCV + RSI data
  "shares_info": {...}, // Budget analysis if provided
  "analysis_date": "2024-10-10 19:48:51"
}
```

### Budget Suggestions Response
```json
{
  "success": true,
  "suggestions": [
    {
      "ticker": "F",
      "name": "Ford Motor Company",
      "price": 12.45,
      "max_shares": 80,
      "total_cost": 996.00,
      "remaining_budget": 4.00
    }
  ],
  "message": "Here are some popular stocks that fit your $1000.00 budget:"
}
```

## Development Guidelines

### Adding New Technical Indicators
1. Implement calculation function in `strategy_bot.py`
2. Update analysis endpoint in `app.py` to include new indicator
3. Modify frontend chart configuration to display additional data
4. Update recommendation logic if indicator affects trading signals

### Modifying UI Styling
- CSS custom properties are defined in `:root` for consistent theming
- Color scheme follows hip-hop aesthetics with neon accents
- Animations use CSS transitions and keyframes
- Responsive design breakpoints: 768px and 480px

### Error Handling Patterns
- API endpoints return consistent `{"success": bool, "error": string}` format
- Frontend displays user-friendly error messages
- yfinance errors are caught and returned as "No data found" messages
- Network errors show connection-specific guidance

### Testing Approach
Since this is a web application interfacing with external APIs, testing is primarily done through:
1. Manual testing via the web interface
2. Direct function calls for strategy_bot.py functions
3. API endpoint testing with different input combinations

### Popular Stock Lists
The budget suggestion feature uses a curated list of popular stocks across different price ranges:
- Low-priced (<$50): F, BAC, T, PFE, WFC, KO
- Mid-priced ($50-200): AAPL, MSFT, GOOGL, TSLA, META, NVDA  
- High-priced ($200+): AMZN, BRK-B, UNH, V

## Future Development Notes

Planned features mentioned in README:
- Live trade tracking integration
- Multiple technical indicators (MACD, Bollinger Bands)
- Portfolio management
- Price alerts and notifications
- Mobile app version

The current architecture supports these extensions through the modular design of `strategy_bot.py` and the flexible API structure in `app.py`.