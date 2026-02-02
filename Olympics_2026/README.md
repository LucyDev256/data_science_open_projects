# 🏅 Milano-Cortina 2026 Winter Olympics Live Dashboard

Interactive Streamlit dashboard for viewing live results and schedules from all Winter Olympic sports at Milano-Cortina 2026 (February 6-22, 2026).

## Features

✨ **Multi-Sport Coverage** - All 16 winter Olympic sports included (Alpine Skiing, Ice Hockey, Figure Skating, Speed Skating, and more)

🏆 **Live Results Dashboard** - Real-time event tracking with auto-refresh capability

📅 **Schedule Explorer** - Browse events by date, sport, and venue with advanced filtering

🌍 **Country Tracker** - Follow specific nations across all Olympic disciplines

📊 **Interactive Analytics** - Visual insights into event distribution, venues, timings, and more

🎨 **Streamlit-Lottie Animations** - Beautiful loading and transition animations

⚡ **Smart Caching** - Optimized API usage with intelligent caching strategy

## Tech Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with requests library
- **Data Processing**: Pandas & Plotly
- **API**: RapidAPI Milano-Cortina 2026 Olympics API
- **Visualization**: Plotly interactive charts
- **Animations**: Streamlit-Lottie

## Installation

### Prerequisites
- Python 3.9+
- RapidAPI account with Milano-Cortina 2026 Olympics API subscription (Basic or higher)
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/lucydev256/olympics-2026.git
cd Olympics_2026
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key**

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your RapidAPI key:
```
RAPIDAPI_KEY=your_rapidapi_key_here
```

Get your API key from: https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api

5. **Run the app**
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account with the repository pushed
- Streamlit Community Cloud account (free)

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial Olympics dashboard commit"
git branch -M main
git remote add origin https://github.com/lucydev256/olympics-2026.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "New app"
- Connect your GitHub repository
- Select main branch and `app.py` as the main file
- Click "Deploy"

3. **Configure Secrets**
- In the Streamlit Cloud app settings
- Add `RAPIDAPI_KEY` under "Secrets"
- Format: `RAPIDAPI_KEY=your_key`

### App URL
Once deployed, your app will be available at:
```
https://share.streamlit.io/lucydev256/olympics-2026/main/app.py
```

## Usage Guide

### Live Dashboard Tab
- View today's scheduled events
- Filter by event status (Upcoming, Completed, etc.)
- See real-time event counts and status distribution

### Schedule Explorer Tab
- Browse all Olympic events
- Filter by date range, sport, and venue
- Download event schedules as CSV
- Interactive timeline visualization

### Country Tracker Tab
- Select any participating country
- View all events featuring that nation
- Filter by sport within country selection
- See country-specific statistics

### Analytics Tab
- Sports distribution pie chart
- Events by venue breakdown
- Hourly event distribution
- Overall status summary

## API Rate Limits

**BASIC Plan** (Recommended)
- 10,000 requests/month
- 30 requests/minute
- Enough for the smart caching strategy implemented

**Higher Plans Available**
- PRO: 100,000 requests/month
- ULTRA: 500,000 requests/month
- MEGA: Unlimited

Upgrade at: https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api/pricing

## Project Structure

```
Olympics_2026/
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── src/
│   ├── api_client.py       # RapidAPI client wrapper
│   ├── data_processor.py   # Data transformation logic
│   └── visualizations.py   # Plotly chart functions
├── utils/
│   ├── cache_manager.py    # Smart caching with TTL
│   └── helpers.py          # Utility functions
└── assets/                 # Logos and images
```

## Caching Strategy

To optimize API usage within the BASIC plan (10,000 requests/month):

1. **In-Memory Cache** - Streamlit session state (fast access)
2. **File Cache** - JSON files with TTL expiration
3. **Smart TTL**:
   - Sports/Countries: 24 hours
   - Events: 10 minutes
   - Today's Events: 5 minutes

The caching ensures smooth operation even with multiple concurrent users.

## Features by Tab

### 🏆 Live Dashboard
- Real-time event counter
- Today's schedule with status indicators
- Quick status filtering
- Event statistics cards

### 📅 Schedule Explorer
- Multi-filter support (date, sport, venue)
- Interactive timeline visualization
- Detailed event information table
- CSV export functionality

### 🌍 Country Tracker
- 90+ participating nations
- Country flag emojis
- Country-specific event count
- Sport distribution within country

### 📊 Analytics
- Distribution by sport (pie chart)
- Distribution by venue (bar chart)
- Hourly event distribution
- Status overview

## Development

### Adding New Features
1. Add API methods to `src/api_client.py`
2. Create processing logic in `src/data_processor.py`
3. Build visualizations in `src/visualizations.py`
4. Add UI in `app.py`

### Running Tests
```bash
pytest tests/
```

## Troubleshooting

### API Key Issues
- Verify API key in `.env` file
- Check RapidAPI dashboard for valid subscription
- Ensure key has no extra spaces

### Rate Limiting
- Check remaining requests in RapidAPI dashboard
- Clear cache with the "Clear Cache" button
- Reduce auto-refresh frequency

### Data Not Loading
- Check internet connection
- Verify API status at RapidAPI
- Clear browser cache and reload

## Support & Issues

For issues or feature requests:
- GitHub Issues: https://github.com/lucydev256/olympics-2026/issues
- RapidAPI Support: Support link in API dashboard

## License

MIT License - See LICENSE file for details

## Acknowledgments

- 🏅 **Data Source**: Milano-Cortina 2026 Olympics API on RapidAPI
- 🎨 **Framework**: Streamlit
- 📊 **Visualization**: Plotly
- ✨ **Animations**: Streamlit-Lottie

## Events Schedule

**Winter Olympics 2026**
- Opening Ceremony: February 6, 2026
- Competition: February 6-22, 2026
- Closing Ceremony: February 22, 2026

Venues:
- Milano (Hockey, Curling)
- Cortina d'Ampezzo (Alpine Skiing)
- Livigno (Cross-Country, Biathlon)
- Bormio (Speed Skiing)
- And more...

---

**Built with ❤️ for Olympic enthusiasts**

Last Updated: February 2, 2026
