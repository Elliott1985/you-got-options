# Hip-Hop Album Cover Setup

## Required Images

To complete the hip-hop theme transformation, add these album cover images to `/static/images/`:

### 1. **wu-tang-logo.png** (400x400px recommended)
- Classic Wu-Tang "W" logo
- Used as background watermark
- PNG with transparent background preferred

### 2. **ready-to-die.jpg** (500x500px)
- Biggie's "Ready to Die" album cover
- Used for BUY signals with "If you don't know, now you know"

### 3. **illmatic.jpg** (500x500px) 
- Nas "Illmatic" album cover
- Classic hip-hop aesthetic

### 4. **atliens.jpg** (500x500px)
- OutKast "ATLiens" album cover  
- Southern hip-hop representation

### 5. **all-eyez-on-me.jpg** (500x500px)
- Tupac "All Eyez On Me" album cover
- West Coast hip-hop classic

## Image Sources
- Use high-quality, square album covers
- Recommended format: JPG for album covers, PNG for logo
- Ensure you have proper licensing/fair use rights

## Features Added

✅ **Wu-Tang watermark background**
✅ **Rotating vinyl album showcase** (top-right)
✅ **Hip-hop quotes** based on trading signals:
- "If you don't know, now you know." - Biggie (Strong Buy)
- "Started from the bottom, now we here." - Drake (Buy)
- "You played yourself." - DJ Khaled (Strong Sell)
- "Don't let me into my zone." - Kanye (Sell)  
- "Cash rules everything around me." - Wu-Tang (Hold)

✅ **Graffiti-style fonts** (Bebas Neue, Permanent Marker)
✅ **Neon accent colors** (#00ffcc, #ffd700)
✅ **Vinyl scratch hover effects**
✅ **Album gallery in footer**
✅ **Fully responsive design**

## Usage
1. Add the 5 image files to `/static/images/`
2. Restart your Flask app: `python3 app.py`  
3. Visit `http://localhost:5001`
4. Test different stock tickers to see hip-hop quotes
5. Click album covers in footer to change the rotating showcase

The album showcase rotates automatically every 10 seconds!