# 🏅 Milano-Cortina 2026 Winter Olympics Live Dashboard

Interactive Streamlit dashboard for exploring and analyzing all events from the Milano-Cortina 2026 Winter Olympics (February 6-22, 2026). Built with Python, Streamlit, and powered by real-time data from the Milano-Cortina 2026 Olympics REST API.

## ✨ Key Features

### 📊 **Live Events Dashboard**
- Browse all Olympic events with smart filtering by date range and sport
- View detailed event information: name, sport, datetime (CET), venue, and status
- Export filtered events to CSV for offline analysis
- Real-time data updates from the official API

### 📈 **Advanced Analytics & Visualizations**
- **Event Distribution by Discipline**: Interactive pie chart showing breakdown across all winter sports
  - Freestyle Skiing split into 7 detailed disciplines (Moguls, Aerials, Slopestyle, Big Air, etc.)
  - Snowboarding categories (Halfpipe, Cross, Parallel, Slopestyle, Big Air)
- **Venue Usage Distribution**: Visual analysis of Olympic venue utilization
  - Livigno venues split into 5 specialized areas (Slopestyle Park, Halfpipe Park, etc.)
  - Top 10 venues with detailed breakdowns

### 🎿 **Comprehensive Sport Descriptions**
- Select any of the 16 Olympic sports to see detailed information
- Learn about competition formats, venues, and fascinating facts
- Covers all disciplines from Alpine Skiing to Ski Mountaineering

### 🌍 **Olympic Overview**
- Track 90+ nations competing across 16 winter sports
- 608+ total events including all qualification rounds and finals
- 109 medal events
- Official Olympic resources with direct links

### 👤 **Personal Touch**
- Download interactive PowerPoint presentation on Olympic downhill skiing
- Embedded YouTube videos showcasing alpine skiing highlights

## 🛠️ Tech Stack

- **Frontend Framework**: Streamlit with responsive design and custom CSS
- **Backend**: Python 3.12
- **Data Processing**: Pandas for ETL operations
- **API Integration**: REST API client for Milano-Cortina 2026 Olympics API (RapidAPI)
- **Visualization**: Plotly for interactive charts and graphs
- **Timezone Handling**: PyTZ (Europe/Rome - CET)
- **Caching**: Smart caching strategy with TTL for optimal performance
- **Version Control**: Git/GitHub

## 📦 Installation

### Prerequisites
- Python 3.12+ (recommended) or 3.9+
- RapidAPI account with Milano-Cortina 2026 Olympics API subscription
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/LucyDev256/data_science_open_projects.git
cd data_science_open_projects/Olympics_2026
```

2. **Create and activate virtual environment**
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

4. **Configure API credentials**

Create a `.env` file in the project root:
```env
RAPIDAPI_KEY=your_rapidapi_key_here
```

Get your API key from: https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api

5. **Run the application**
```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`

## ☁️ Deployment to Streamlit Cloud

### One-Click Deployment

1. **Ensure code is pushed to GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy via Streamlit Cloud**
- Visit https://share.streamlit.io
- Click "New app"
- Select your GitHub repository and branch
- Set main file path: `app.py`
- Add secrets in the Secrets section:
```toml
RAPIDAPI_KEY = "your_api_key_here"
```
- Click "Deploy"

Your app will be live at: `https://[your-app-name].streamlit.app`

## 🔧 Technical Implementation Details

### REST API Integration
- Custom API client class wrapping the Milano-Cortina 2026 Olympics API
- Error handling and retry logic for robust connections
- Support for multiple endpoints (events, sports, countries)

### Data Transformation
- DateTime parsing with timezone awareness (CET)
- Venue information extraction from nested JSON
- Sport name mapping from codes to full names
- Duplicate event removal and data deduplication

### Performance Optimization
- Smart caching with configurable TTL (Time To Live)
- Streamlit's `@st.cache_data` decorator for function memoization
- File-based caching for persistence across sessions
- Efficient DataFrame operations with Pandas

### UI/UX Features
- Responsive layout with Streamlit columns
- Custom CSS for enhanced styling
- Color-coded visualizations for better readability
- Interactive charts with hover information
- Download functionality for data export

## 🎓 Skills & Technologies Demonstrated

This project showcases proficiency in:

- **REST API Integration**: Working with external APIs, handling authentication, error management
- **Python Development**: Object-oriented programming, data structures, error handling
- **Data Engineering**: ETL pipelines, data cleaning, transformation, and categorization
- **Web Development**: Building interactive dashboards with Streamlit framework
- **Data Visualization**: Creating meaningful charts with Plotly
- **Version Control**: Git/GitHub for source code management
- **Cloud Deployment**: Deploying Python applications to cloud platforms
- **Timezone Management**: Handling international date/time with PyTZ
- **Performance Optimization**: Implementing caching strategies
- **Documentation**: Writing clear technical documentation and README files

## 🏅 Olympic Sports Covered

1. Alpine Skiing
2. Ice Hockey  
3. Figure Skating
4. Speed Skating
5. Short Track Speed Skating
6. Curling
7. Biathlon
8. Cross-Country Skiing
9. Ski Jumping
10. Nordic Combined
11. Freestyle Skiing (with 7 sub-disciplines)
12. Snowboarding (with 5 sub-disciplines)
13. Bobsleigh
14. Skeleton
15. Luge
16. Ski Mountaineering (NEW for 2026!)

## 📁 Project Structure

```
Olympics_2026/
├── app.py                      # Main Streamlit application with dashboard UI
├── requirements.txt            # Python dependencies
├── .env                        # API credentials (not in repo)
├── .gitignore                  # Git ignore patterns
├── src/
│   ├── __init__.py
│   ├── api_client.py          # REST API client for Milano-Cortina 2026 API
│   ├── data_processor.py      # Data transformation and filtering logic
│   └── visualizations.py      # Plotly chart generation functions
├── utils/
│   ├── __init__.py
│   ├── cache_manager.py       # Smart caching with TTL expiration
│   └── helpers.py             # Utility functions and sport descriptions
├── src/
│   └── MWN Olympic Games downhill skiing presentation 2126.pptx
└── assets/                     # Images and resources
```

## 🎯 Core Functionality

### Data Processing Pipeline
1. **API Integration**: Fetch real-time data from Milano-Cortina 2026 Olympics API
2. **Data Cleaning**: Parse timestamps, extract venue details, categorize disciplines
3. **Smart Categorization**: 
   - Split Freestyle Skiing into 7 detailed disciplines
   - Organize Livigno venues into 5 specialized areas
4. **Timezone Handling**: All times displayed in CET (Europe/Rome)

### Filtering & Search
- **Date Range Filter**: Select custom date ranges within the Olympic period
- **Sport Filter**: Choose from all 16 Olympic winter sports
- **Dynamic Results**: Real-time filtering without page refresh

### Visualization Features
- **Interactive Pie Charts**: Click to explore data segments
- **Color-coded Categories**: Distinct colors for each discipline/venue
- **Legend Navigation**: Easy identification of all categories
- **Responsive Design**: Charts adapt to screen size

## 🚀 Usage Guide

### Live Dashboard
The main dashboard provides comprehensive access to all Olympic events:

**Filters Section:**
- **Date Range**: Select start and end dates (Feb 6-22, 2026)
- **Sport Selection**: Filter by specific sport or view "All Sports"

**Events Display:**
- See complete event details in sortable table format
- Columns: Event Name, Sport, Date/Time (CET), Venue, Status
- Export functionality to download filtered results as CSV

**Event Analytics:**
Two interactive visualizations side-by-side:
1. **Event Distribution by Discipline** - Shows how events are distributed across all winter sport disciplines
2. **Venue Usage Distribution** - Displays which venues host the most events

**Sport Information:**
When you select a specific sport from the filter:
- Detailed sport description and history
- Competition format and rules
- Venue information
- Interesting facts and Olympic records

**Olympic Overview (All Sports view):**
- Quick statistics: 16 sports, 608+ events, 90+ nations, 109 medal events
- Explanation of why there are so many events (multiple rounds, qualifications, etc.)

**About Me Section:**
- Download interactive PowerPoint presentation on Olympic downhill skiing
- Features embedded YouTube videos and detailed analysis

## 🎨 Data Visualization Highlights

### Discipline Breakdown
The Event Distribution chart categorizes Freestyle Skiing and Snowboarding into specific disciplines:
- Freestyle - Moguls, Aerials, Slopestyle, Big Air
- Snowboard - Slopestyle, Halfpipe, Big Air, Cross, Parallel
This provides a more accurate representation than lumping all freestyle events together.

### Venue Analysis
Livigno Snow Park is split into specialized venues:
- Livigno - Slopestyle Park
- Livigno - Parallel Course
- Livigno - Halfpipe Park
- Livigno - Big Air Park
- Livigno - Cross Course
- Livigno - Aerials & Moguls Park

This granular breakdown helps visualize how different Olympic venues are utilized.

## 🐛 Troubleshooting

### Common Issues

**API Connection Errors**
- Verify API key is correctly set in `.env` file
- Check RapidAPI subscription is active
- Ensure no trailing spaces in API key

**Data Not Displaying**
- Clear cache using sidebar "Clear Cache" button
- Check internet connection
- Verify API endpoint status on RapidAPI dashboard

**Slow Performance**
- Clear browser cache
- Reduce date range filter to smaller window
- Check API rate limits haven't been exceeded

**Installation Issues**
- Ensure Python 3.9+ is installed: `python --version`
- Try upgrading pip: `pip install --upgrade pip`
- Install dependencies one by one if bulk install fails

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Data Source**: [Milano-Cortina 2026 Olympics API](https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api) on RapidAPI
- **Framework**: [Streamlit](https://streamlit.io) for the interactive dashboard
- **Visualization**: [Plotly](https://plotly.com/python/) for interactive charts
- **Data Processing**: [Pandas](https://pandas.pydata.org/) for data manipulation

## 📞 Contact & Support

- **GitHub**: [@LucyDev256](https://github.com/LucyDev256)
- **Project Issues**: [GitHub Issues](https://github.com/LucyDev256/data_science_open_projects/issues)
- **LinkedIn**: Connect for professional inquiries

## 🗓️ Olympic Schedule

**Milano-Cortina 2026 Winter Olympics**
- 📅 Opening Ceremony: February 6, 2026
- 🏅 Competition Period: February 6-22, 2026
- 🎉 Closing Ceremony: February 22, 2026

**Major Venues:**
- Milano (Ice Hockey, Figure Skating, Speed Skating)
- Cortina d'Ampezzo (Alpine Skiing, Bobsleigh, Luge, Skeleton)
- Livigno (Freestyle Skiing, Snowboarding)
- Bormio (Alpine Skiing)
- Anterselva (Biathlon)
- Val di Fiemme (Cross-Country, Ski Jumping, Nordic Combined)

---

**Built with ❤️ for Olympic enthusiasts | Last Updated: February 5, 2026**

⭐ Star this repo if you found it helpful!
