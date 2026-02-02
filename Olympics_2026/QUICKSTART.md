# 🚀 Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Get Your API Key
1. Visit: https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api
2. Click "Subscribe to Test" (BASIC plan is free with limits)
3. Copy your API Key from the dashboard

### Step 2: Set Up Environment
```bash
# Navigate to project directory
cd Olympics_2026

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key
Edit `.env` file:
```
RAPIDAPI_KEY=your_actual_api_key_here
```

### Step 5: Run the App
```bash
streamlit run app.py
```

The app will open at: http://localhost:8501

## Features You'll See

✅ **Live Dashboard** - Today's Olympic events with real-time updates
✅ **Schedule Explorer** - Browse all events with advanced filters
✅ **Country Tracker** - Follow specific nations' participation
✅ **Analytics** - Charts and insights about the Olympics

## Troubleshooting

**Issue: "API Key not configured"**
- Make sure `.env` file exists
- Verify `RAPIDAPI_KEY=` line is correct
- Check for extra spaces or typos

**Issue: "Rate limit exceeded"**
- BASIC plan has 10,000 requests/month
- The app uses smart caching to minimize requests
- Wait a moment before retrying

**Issue: No events showing**
- Confirm today's date is between Feb 6-22, 2026
- Check API status on RapidAPI dashboard
- Try the "Refresh Now" button in sidebar

## Deployment

Ready to share with the world?

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Add `RAPIDAPI_KEY` secret in settings
5. Deploy!

See README.md for detailed deployment instructions.

## Next Steps

- Customize colors in `.streamlit/config.toml`
- Add more visualizations to `src/visualizations.py`
- Extend filters in the Schedule Explorer
- Set up GitHub Actions for auto-updates

Happy tracking! 🏅
