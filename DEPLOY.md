# 🚀 Deployment Guide - You Got Options

## Deploy to Render.com (Recommended)

### Quick Deploy Steps:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New" → "Web Service"
   - Connect your GitHub repo: `you-got-options`
   - Render will auto-detect the configuration from `render.yaml`

3. **Configuration:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment:** Python 3.11
   - **Plan:** Free (or paid for better performance)

### Environment Variables:
The following will be auto-configured:
- `PORT` - Set by Render automatically
- `SECRET_KEY` - Generated automatically
- `FLASK_ENV` - Set to `production`

### Features Available After Deploy:
✅ **Professional Neon Trading Interface**  
✅ **Real-time RSI & MACD Analysis**  
✅ **Trade Monitoring & Alerts**  
✅ **Demo Mode** (use ticker "DEMO")  
✅ **Market Status Detection**  
✅ **Budget Analysis & Suggestions**  

### Testing Your Deployed App:
1. Visit your Render URL (e.g., `https://you-got-options.onrender.com`)
2. Try ticker: `DEMO` with budget: `1000`
3. Test the trade monitoring features
4. Verify all neon glow effects work

---

## Alternative: Docker Deployment

```bash
# Build image
docker build -t you-got-options .

# Run container
docker run -p 5001:5001 you-got-options
```

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Visit: http://localhost:5001
```

---

## Health Check
Your app includes a health check endpoint at `/api/health` that Render uses to monitor the service.

## Troubleshooting
- If deployment fails, check the Render build logs
- For memory issues, consider upgrading from free tier
- Yahoo Finance API may have rate limits - use DEMO ticker for testing

**🎉 Your neon cyberpunk trading app will be live and ready to use!**