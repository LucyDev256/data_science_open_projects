# 🏅 Milano-Cortina 2026 API Endpoints Guide

## Overview
This document explains the two key API endpoints that enhance the Olympics 2026 Dashboard.

---

## 1️⃣ Country Filtering: `/countries/{country_code}/events`

### What It Does
Retrieves **ALL events** for a specific nation across **ALL 16 Olympic sports**.

### Why It's Better
Previously, we filtered by the `teams` field in event data, which only listed immediate participants in each heat/session. This caused Canada to show only 1-2 sports instead of all 16.

The dedicated `/countries/CAN/events` endpoint returns **complete country participation** across the entire Olympics.

### API Response Structure
```json
{
  "success": true,
  "total": 207,
  "events": [
    {
      "id": "iho-05-february-1210-0",
      "date": "2026-02-05",
      "time": "12:10",
      "sport": "ice_hockey",
      "sport_code": "iho",
      "discipline": "Women's Prelim. Round - Group B",
      "venue": {
        "name": "Milano Rho Ice Hockey Arena",
        "city": "Milano",
        "country": "ITA"
      },
      "teams": [
        {"code": "USA"},
        {"code": "CAN"}
      ],
      "is_medal_event": false
    }
  ]
}
```

### Key Fields
- `id` - Unique event identifier
- `date`, `time` - Event schedule (CET timezone)
- `sport`, `sport_code` - Sport information
- `discipline` - Specific event name
- `venue` - Object with name/city/country
- `teams` - Participating teams/athletes
- **`is_medal_event`** - Boolean flag (true if event awards medals)

### Implementation
```python
# In src/api_client.py
def get_country_events(country_code: str, sport_code: Optional[str] = None):
    """Get all events for a specific country"""
    params = {}
    if sport_code:
        params["sport_code"] = sport_code
    return self._make_request(f"/countries/{country_code}/events", params)

# In app.py
if selected_country == "All":
    all_response = fetch_all_events()
else:
    # Use dedicated country endpoint
    all_response = api_client.get_country_events(selected_country)
```

### Usage in App
- **Live Dashboard** → Country dropdown filter
- Shows **all 207 Canadian events** across **all 16 sports**
- Resolves the "Canada only showing 1 sport" issue

---

## 2️⃣ Medal Events: `/events/medal-events`

### What It Does
Returns **ONLY finals and events that award medals** (gold/silver/bronze).

### Response Structure
Same as regular events, but **ALL events have `is_medal_event: true`**.

### Optional Filters
```python
# Filter by sport
GET /events/medal-events?sport_code=iho

# Filter by date
GET /events/medal-events?date=2026-02-10

# Filter by date range
GET /events/medal-events?date_from=2026-02-06&date_to=2026-02-12
```

### Implementation
```python
# In src/api_client.py
def get_medal_events(
    self,
    sport_code: Optional[str] = None,
    date: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """Get only finals and events that award medals"""
    params = {}
    if sport_code:
        params["sport_code"] = sport_code
    if date:
        params["date"] = date
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    
    return self._make_request("/events/medal-events", params)
```

### When Data Is Available
- **Schedule data**: ✅ Available NOW (shows when medals will be awarded)
- **Medal results** (winners): ⏳ Available during Olympics (Feb 6-22, 2026)

### Usage in App
- **Live Dashboard** → "🏅 Show Medal Events Only" checkbox
- Filters to show only finals and medal ceremonies
- Perfect for tracking **which events award medals today**

### Use Cases
1. **Medal Alerts** - Push notifications for upcoming medal events
2. **"What's at Stake Today?"** - Daily medal schedule
3. **Podium Predictions** - Pre-event medal trackers
4. **Results Dashboard** - Post-event medal standings (during Olympics)

---

## 🎯 Combined Power

### Example: Track Canadian Medal Opportunities
```python
# Get all Canadian events
canada_events = api_client.get_country_events("CAN")

# Filter to medal events only
medal_events = [e for e in canada_events['events'] if e.get('is_medal_event')]

print(f"Canada competing in {len(medal_events)} medal events")
```

### Example: Today's Medal Ceremonies
```python
# Get today's medal events
today = datetime.now().strftime("%Y-%m-%d")
medal_response = api_client.get_medal_events(date=today)

print(f"🏅 {medal_response['total']} medals up for grabs today!")
```

---

## 📊 Data Coverage

- **Total Events**: 608+ across Olympics
- **Sports**: All 16 Olympic winter sports
- **Countries**: 90+ participating nations
- **Medal Events**: ~120 finals across all sports
- **Update Frequency**: Every 10 minutes (AWS Lambda scraper)
- **Data Source**: Official Olympics.com

---

## 🚀 What We Fixed

### Before ❌
- Country filter showed wrong data (Canada: 1-2 sports instead of 16)
- Used client-side filtering on `teams` field
- No medal events filtering

### After ✅
- Country filter uses dedicated API endpoint
- Shows **all 207 Canadian events across all 16 sports**
- Medal events filter checkbox
- Accurate country participation tracking

---

## 🔗 API Documentation

Full API docs: https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api

### All Available Endpoints
- `GET /events` - All events with filters
- `GET /events/today` - Today's schedule
- `GET /events/medal-events` - Medal events only ✨
- `GET /countries/{code}/events` - Country-specific events ✨
- `GET /sports` - All 16 sports
- `GET /sports/{code}/events` - Events by sport
- `GET /search?q={query}` - Full-text search

---

## 💡 Next Steps

### Potential Enhancements
1. **Medal Tracker** - Uncomment Podium tab, integrate medal events
2. **Country Comparison** - Side-by-side country medal counts
3. **Push Notifications** - Alert users before medal events
4. **Live Results** - Auto-refresh during Olympics (Feb 6-22)

### Ready for 2026! 🎿⛷️🏒
