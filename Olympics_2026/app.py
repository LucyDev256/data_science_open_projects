"""
Milano-Cortina 2026 Winter Olympics Live Dashboard
Interactive Streamlit app for viewing all Olympic events and results
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pytz

from src.api_client import MilanoCortina2026API
from src.data_processor import OlympicsDataProcessor
from src.visualizations import OlympicsVisualizations
from utils.cache_manager import CacheManager
from utils.helpers import StreamlitHelpers, ValidationHelpers

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🏅 Milano-Cortina 2026 Olympics",
    page_icon="⛷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def init_api_client():
    """Initialize API client (cached)"""
    api_key = os.getenv("RAPIDAPI_KEY") or st.secrets.get("RAPIDAPI_KEY", "")
    if not api_key:
        st.error("❌ API Key not configured. Please add RAPIDAPI_KEY to environment.")
        st.stop()
    return MilanoCortina2026API(api_key)


@st.cache_data(ttl=600)
def fetch_all_events():
    """Fetch all events from API with caching"""
    api = init_api_client()
    
    # Check cache first
    cached = CacheManager.get("all_events", "events")
    if cached:
        return cached
    
    try:
        with st.spinner("📡 Fetching events from API..."):
            response = api.get_all_events(limit=500)
        
        if response.get("success"):
            CacheManager.set("all_events", response, "events")
            return response
        else:
            st.warning("⚠️ Could not fetch events. Showing cached data if available.")
            return {}
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return {}


@st.cache_data(ttl=600)
def fetch_today_events():
    """Fetch today's events"""
    api = init_api_client()
    
    cached = CacheManager.get("today_events", "today_events")
    if cached:
        return cached
    
    try:
        response = api.get_today_events()
        if response.get("success"):
            CacheManager.set("today_events", response, "today_events")
            return response
        return {}
    except Exception as e:
        st.warning(f"⚠️ Could not fetch today's events: {str(e)}")
        return {}


@st.cache_data(ttl=86400)
def fetch_all_sports():
    """Fetch all sports"""
    api = init_api_client()
    
    cached = CacheManager.get("all_sports", "sports")
    if cached:
        return cached
    
    try:
        response = api.get_all_sports()
        # Handle both dict and list responses
        if isinstance(response, dict):
            if response.get("success"):
                CacheManager.set("all_sports", response, "sports")
                return response
            elif "sports" in response:
                # API returned sports directly without success flag
                wrapped = {"success": True, "sports": response["sports"]}
                CacheManager.set("all_sports", wrapped, "sports")
                return wrapped
        elif isinstance(response, list):
            # API returned list of sports directly
            wrapped = {"success": True, "sports": response}
            CacheManager.set("all_sports", wrapped, "sports")
            return wrapped
        return {"success": False, "sports": []}
    except Exception as e:
        st.warning(f"⚠️ Could not fetch sports: {str(e)}")
        return {"success": False, "sports": []}


@st.cache_data(ttl=86400)
def fetch_all_countries():
    """Fetch all countries"""
    api = init_api_client()
    
    cached = CacheManager.get("all_countries", "countries")
    if cached:
        return cached
    
    try:
        response = api.get_all_countries()
        # Handle both dict and list responses
        if isinstance(response, dict):
            if response.get("success"):
                CacheManager.set("all_countries", response, "countries")
                return response
            elif "countries" in response:
                wrapped = {"success": True, "countries": response["countries"]}
                CacheManager.set("all_countries", wrapped, "countries")
                return wrapped
        elif isinstance(response, list):
            wrapped = {"success": True, "countries": response}
            CacheManager.set("all_countries", wrapped, "countries")
            return wrapped
        return {"success": False, "countries": []}
    except Exception as e:
        st.warning(f"⚠️ Could not fetch countries: {str(e)}")
        return {"success": False, "countries": []}


@st.cache_data(ttl=600)
def fetch_country_events(country_code: str):
    """Fetch events for a specific country"""
    api = init_api_client()
    
    cache_key = f"country_events_{country_code}"
    cached = CacheManager.get(cache_key, "country_events")
    if cached:
        return cached
    
    try:
        with st.spinner(f"📡 Fetching events for {country_code}..."):
            response = api.get_country_events(country_code)
        
        if response.get("success"):
            CacheManager.set(cache_key, response, "country_events")
            return response
        else:
            st.warning(f"⚠️ Could not fetch events for {country_code}.")
            return {}
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return {}


def render_header():
    """Render page header"""
    # Center-aligned header
    st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #1e3a8a; margin-bottom: 0.3rem;'>🏅 MILANO-CORTINA 2026</h1>
        <h3 style='color: #374151; margin-bottom: 0.5rem;'>Winter Olympics Live Dashboard</h3>
        <h4 style='color: #1e3a8a; margin-bottom: 0.5rem;'>🎿 Welcome to the Olympic Experience! ⛷️</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Friendly invitation
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background-color: #f0f8ff; border-radius: 10px; margin: 1rem 0;'>
        <p style='color: #374151; font-size: 1.1rem;'>
            Join me in following the journey of <strong>90+ nations</strong> competing across <strong>16 winter sports</strong>! 
            Track and discover exciting events, and celebrate every thrilling moment together. 
            <strong>Let the Games begin!</strong> 🏆
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Official links section
    st.markdown("### 🔗 Official Olympic Resources")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div style='border: 2px solid #e5e7eb; border-radius: 10px; padding: 1rem; min-height: 200px; background-color: white; display: flex; flex-direction: column;'>
            <h4 style='color: #1e3a8a; margin-top: 0;'>📰 Official Olympics Website</h4>
            <p style='color: #6b7280; flex-grow: 1;'>Get official news, schedules, and athlete profiles</p>
            <a href='https://www.olympics.com/en/milano-cortina-2026' target='_blank' style='text-decoration: none;'>
                <div style='background-color: #3b82f6; color: white; padding: 0.75rem; border-radius: 5px; text-align: center; font-weight: bold;'>
                    Visit Olympics.com →
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div style='border: 2px solid #e5e7eb; border-radius: 10px; padding: 1rem; min-height: 200px; background-color: white; display: flex; flex-direction: column;'>
            <h4 style='color: #1e3a8a; margin-top: 0;'>🎥 Official YouTube Channel</h4>
            <p style='color: #6b7280; flex-grow: 1;'>Watch highlights, athlete stories, and live coverage</p>
            <a href='https://www.youtube.com/@Olympics/videos' target='_blank' style='text-decoration: none;'>
                <div style='background-color: #dc2626; color: white; padding: 0.75rem; border-radius: 5px; text-align: center; font-weight: bold;'>
                    Watch on YouTube →
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")


def render_stats_cards(df: pd.DataFrame):
    """Render statistics cards"""
    stats = OlympicsVisualizations.create_stats_cards(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Events", stats["total_events"])
    
    with col2:
        st.metric("🔴 Today", stats["upcoming_events"])
    
    with col3:
        st.metric("⛷️ Sports", stats["sports_count"])
    
    with col4:
        st.metric("🌍 Countries", stats["countries_count"])


def render_live_dashboard_tab():
    """Render Live Dashboard tab with filters"""
    st.subheader("🏟️ Olympics Events Dashboard")
    
    # Filter bar
    st.markdown("### 🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Date range filter
        date_range = st.date_input(
            "Date Range",
            value=(datetime(2026, 2, 6).date(), datetime(2026, 2, 22).date()),
            key="live_date_range"
        )
    
    with col2:
        # Sport filter
        sports_response = fetch_all_sports()
        sports_list = sports_response.get("sports", []) if sports_response.get("success") else []
        
        sport_codes = ["All"]
        sport_names_map = {"All": "All Sports"}
        
        for sport in sports_list:
            if isinstance(sport, dict) and sport.get("code"):
                code = sport.get("code")
                name = OlympicsDataProcessor.get_sport_name(code).strip()
                sport_codes.append(code)
                sport_names_map[code] = name
        
        selected_sport = st.selectbox(
            "Sport",
            options=sport_codes,
            format_func=lambda x: sport_names_map.get(x, x),
            key="live_sport_filter"
        )
    
    with col3:
        # Event status filter
        status_filter = st.selectbox(
            "Event Status",
            options=["All Events", "Completed", "Upcoming", "Today", "Scheduled"],
            key="status_filter"
        )
    
    st.markdown("---")
    
    # Fetch all events
    all_response = fetch_all_events()
    all_df = OlympicsDataProcessor.parse_events_response(all_response)
    
    if all_df.empty:
        st.info("No events data available")
        return
    
    # Apply filters
    filtered_df = all_df.copy()
    
    # Date filter
    if date_range and len(date_range) == 2:
        milan_tz = pytz.timezone("Europe/Rome")
        start_date = pd.Timestamp(date_range[0], tz=milan_tz)
        end_date = pd.Timestamp(date_range[1], tz=milan_tz)
        filtered_df = OlympicsDataProcessor.filter_by_date_range(filtered_df, start_date, end_date)
    
    # Sport filter
    if selected_sport != "All":
        filtered_df = OlympicsDataProcessor.filter_by_sport(filtered_df, selected_sport)
    
    # Status filter
    if status_filter != "All Events" and "status" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["status"] == status_filter].copy()
    
    # Display events
    st.write(f"### 📅 Events")
    
    if not filtered_df.empty:
        # Reset index and remove duplicates
        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
        
        # Remove duplicate events
        dedup_cols = []
        if "event_name" in filtered_df.columns:
            dedup_cols.append("event_name")
        if "datetime" in filtered_df.columns:
            dedup_cols.append("datetime")
        if "venue_full" in filtered_df.columns:
            dedup_cols.append("venue_full")
        elif "venue" in filtered_df.columns:
            dedup_cols.append("venue")
        
        if dedup_cols:
            filtered_df = filtered_df.drop_duplicates(subset=dedup_cols, keep='first')
        
        # Create display DataFrame
        event_names = list(filtered_df["event_name"].astype(str)) if "event_name" in filtered_df.columns else ["N/A"] * len(filtered_df)
        sport_codes = filtered_df["sport_code"] if "sport_code" in filtered_df.columns else pd.Series(["N/A"] * len(filtered_df))
        sports = [str(OlympicsDataProcessor.get_sport_name(code)) for code in sport_codes]
        times = list(filtered_df["datetime"].dt.strftime("%b %d, %H:%M")) if "datetime" in filtered_df.columns else ["N/A"] * len(filtered_df)
        venue_col = "venue_full" if "venue_full" in filtered_df.columns else "venue"
        venues = list(filtered_df[venue_col].astype(str)) if venue_col in filtered_df.columns else ["N/A"] * len(filtered_df)
        statuses = list(filtered_df["status"].astype(str)) if "status" in filtered_df.columns else ["N/A"] * len(filtered_df)
        
        display_df = pd.DataFrame({
            "event_name": event_names,
            "sport": sports,
            "date_time (CET)": times,
            "venue": venues,
            "status": statuses
        })
        
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )
        
        # Export option
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"olympics_events_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Visualizations section
        st.markdown("---")
        st.markdown("### 📊 Event Analytics")
        
        # Two pie charts side by side
        col1, col2 = st.columns(2)
        
        with col1:
            # Sport events distribution pie chart
            sport_fig = OlympicsVisualizations.create_sports_distribution_pie(filtered_df)
            st.plotly_chart(sport_fig, use_container_width=True)
        
        with col2:
            # Venue usage pie chart
            venue_fig = OlympicsVisualizations.create_venue_distribution_pie(filtered_df)
            st.plotly_chart(venue_fig, use_container_width=True)
        
        # Sport Description Section
        st.markdown("---")
        if selected_sport == "All":
            # General Olympics statistics
            st.markdown("### 📖 Milano-Cortina 2026 Olympics Overview")
            
            st.markdown(f"""
            <div style='background-color: #f0f9ff; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #3b82f6;'>
                <h4 style='color: #1e3a8a; margin-top: 0;'>🏔️ Welcome to the Winter Olympics!</h4>
                <p style='color: #374151; font-size: 1.05rem; line-height: 1.6;'>
                    The <strong>Milano-Cortina 2026 Winter Olympics</strong> brings together the world's best athletes 
                    competing across <strong>16 winter sports</strong> from 
                    <strong>February 6-22, 2026</strong>.
                </p>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 1rem 0;'>
                    <div style='background-color: white; padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 2rem; color: #3b82f6;'>🎿</div>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #1e3a8a;'>16</div>
                        <div style='color: #6b7280;'>Olympic Sports</div>
                    </div>
                    <div style='background-color: white; padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 2rem; color: #3b82f6;'>📅</div>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #1e3a8a;'>608+</div>
                        <div style='color: #6b7280;'>Total Events</div>
                    </div>
                    <div style='background-color: white; padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 2rem; color: #3b82f6;'>🌍</div>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #1e3a8a;'>90+</div>
                        <div style='color: #6b7280;'>Nations Competing</div>
                    </div>
                    <div style='background-color: white; padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 2rem; color: #3b82f6;'>🏅</div>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #1e3a8a;'>109</div>
                        <div style='color: #6b7280;'>Medal Events</div>
                    </div>
                </div>
                <p style='color: #374151; margin-top: 1rem;'>
                    <strong>🎯 Why so many events?</strong> Each Olympic competition includes multiple rounds - 
                    qualifications, semifinals, and finals. Some sports like Freestyle Skiing have 2-3 runs per round, 
                    and each run is a separate scheduled event. This gives fans more opportunities to watch their 
                    favorite athletes compete!
                </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Sport-specific description
            st.markdown(f"### 📖 About {sport_names_map.get(selected_sport, 'This Sport')}")
            
            sport_info = ValidationHelpers.get_sport_description(selected_sport, len(filtered_df))
            
            st.markdown(f"""
            <div style='background-color: #f0f9ff; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #3b82f6;'>
                <h3 style='color: #1e3a8a; margin-top: 0;'>{sport_info['emoji']} {sport_info['name']}</h3>
                <p style='color: #374151; font-size: 1.1rem; margin-bottom: 1rem;'>
                    {sport_info['description']}
                </p>
                <div style='background-color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;'>
                    {sport_info['details']}
                </div>
                <div style='background-color: #fef3c7; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                    <p style='color: #78350f; margin: 0;'>
                        {sport_info['fun_fact']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.info("No events match the selected filters")



def render_podium_tab():
    """Render Podium/Medal Tracker tab"""
    st.subheader("🏅 Medal Tracker & Country Scoreboard")
    
    # Note about data availability
    st.info("📌 **Note:** Medal results will be available once events are completed. Currently showing event participation data.")
    
    # Fetch all events
    all_response = fetch_all_events()
    all_df = OlympicsDataProcessor.parse_events_response(all_response)
    
    if all_df.empty:
        st.warning("No events data available")
        return
    
    # Get all countries
    countries_set = set()
    if "teams" in all_df.columns:
        for teams in all_df["teams"]:
            if teams is None or (isinstance(teams, float) and pd.isna(teams)):
                continue
            if isinstance(teams, list):
                for team in teams:
                    if isinstance(team, dict):
                        code = team.get("code") or team.get("country_code")
                        if code:
                            countries_set.add(code.upper())
    
    if not countries_set:
        countries_set = {"USA", "CAN", "ITA", "GER", "FRA", "JPN", "CHN", "KOR"}
    
    countries_list = sorted(list(countries_set))
    
    # Country selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_country = st.selectbox(
            "Select Country",
            options=countries_list,
            key="podium_country_select"
        )
    
    with col2:
        st.write("")  # Spacer
    
    if selected_country:
        # Filter events for selected country
        country_events = OlympicsDataProcessor.filter_by_country(all_df, selected_country)
        
        st.markdown("---")
        st.write(f"## {selected_country} - Olympic Performance")
        
        if not country_events.empty:
            # Stats
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📊 Total Events", len(country_events))
            
            with col2:
                sports_count = country_events["sport_code"].nunique() if "sport_code" in country_events.columns else 0
                st.metric("⛷️ Sports", sports_count)
            
            with col3:
                # Placeholder for gold medals (data not available yet)
                st.metric("🥇 Gold", "TBD")
            
            with col4:
                # Placeholder for silver medals
                st.metric("🥈 Silver", "TBD")
            
            with col5:
                # Placeholder for bronze medals
                st.metric("🥉 Bronze", "TBD")
            
            st.markdown("---")
            
            # Medal events
            st.write("### 🎯 Medal Events")
            medal_events = country_events[country_events.get("is_medal_event", False) == True] if "is_medal_event" in country_events.columns else country_events
            
            if not medal_events.empty:
                st.write(f"**{len(medal_events)} medal events** for {selected_country}")
                
                # Group by sport
                if "sport_code" in medal_events.columns:
                    sport_counts = medal_events.groupby("sport_code").size().reset_index(name="count")
                    sport_counts["sport_name"] = sport_counts["sport_code"].apply(OlympicsDataProcessor.get_sport_name)
                    sport_counts = sport_counts.sort_values("count", ascending=False)
                    
                    fig = go.Figure(data=[go.Bar(
                        x=sport_counts["sport_name"],
                        y=sport_counts["count"],
                        marker=dict(color="#FFD700"),
                        text=sport_counts["count"],
                        textposition="outside"
                    )])
                    
                    fig.update_layout(
                        title=f"Medal Events by Sport - {selected_country}",
                        xaxis_title="Sport",
                        yaxis_title="Number of Events",
                        height=400,
                        showlegend=False,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, width="stretch")
        else:
            st.info(f"No events found for {selected_country}")
    
    st.markdown("---")
    
    # Overall Leaderboard
    st.write("### 🏆 Top 10 Countries Leaderboard")
    st.caption("**Scoring System:** Gold = 9 points | Silver = 3 points | Bronze = 1 point")
    
    # Create placeholder leaderboard
    st.info("📌 **Leaderboard will be populated as medal results become available during the Olympics (Feb 6-22, 2026)**")
    
    # Show top countries by event participation as placeholder
    st.write("**Top Countries by Event Participation:**")
    
    country_participation = {}
    if "teams" in all_df.columns:
        for idx, row in all_df.iterrows():
            teams = row.get("teams")
            if teams is None or (isinstance(teams, float) and pd.isna(teams)):
                continue
            if isinstance(teams, list):
                for team in teams:
                    if isinstance(team, dict):
                        code = team.get("code") or team.get("country_code")
                        if code:
                            code = code.upper()
                            country_participation[code] = country_participation.get(code, 0) + 1
    
    if country_participation:
        # Sort and get top 10
        sorted_countries = sorted(country_participation.items(), key=lambda x: x[1], reverse=True)[:10]
        
        leaderboard_df = pd.DataFrame(sorted_countries, columns=["Country", "Events"])
        leaderboard_df.index = range(1, len(leaderboard_df) + 1)
        leaderboard_df.index.name = "Rank"
        
        st.dataframe(leaderboard_df, width="stretch")
        
        # Visualization
        fig = go.Figure(data=[go.Bar(
            x=[item[0] for item in sorted_countries],
            y=[item[1] for item in sorted_countries],
            marker=dict(
                color=[item[1] for item in sorted_countries],
                colorscale=[[0, "#CD7F32"], [0.5, "#C0C0C0"], [1, "#FFD700"]],
                showscale=False
            ),
            text=[item[1] for item in sorted_countries],
            textposition="outside"
        )])
        
        fig.update_layout(
            title="Top 10 Countries by Event Participation",
            xaxis_title="Country",
            yaxis_title="Number of Events",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, width="stretch")


def render_schedule_explorer_tab():
    """Render Schedule Explorer tab"""
    st.subheader("📅 Schedule Explorer")
    
    # Fetch all events
    all_response = fetch_all_events()
    all_df = OlympicsDataProcessor.parse_events_response(all_response)
    
    if all_df.empty:
        st.warning("No events data available")
        return
    
    # Create filter columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime(2026, 2, 6).date(), datetime(2026, 2, 22).date()),
            key="schedule_date_range"
        )
    
    with col2:
        sports_response = fetch_all_sports()
        sports_list = sports_response.get("sports", []) if sports_response.get("success") else []
        
        # Fallback to sports from DataFrame if API fails
        if not sports_list and "sport_code" in all_df.columns:
            unique_codes = all_df["sport_code"].dropna().unique()
            sport_codes = [str(code) for code in unique_codes if code]
            sport_names = [OlympicsDataProcessor.get_sport_name(code) for code in sport_codes]
        else:
            sport_codes = [s.get("code") for s in sports_list if isinstance(s, dict) and s.get("code")]
            sport_names = [OlympicsDataProcessor.get_sport_name(code) for code in sport_codes if code]
        
        # Ensure we have at least some sports to show
        if not sport_names:
            sport_names = ["Alpine Skiing", "Ice Hockey", "Figure Skating", "Biathlon"]
        
        selected_sport = st.selectbox(
            "Filter by Sport",
            options=["All"] + sport_names,
            key="schedule_sport_filter"
        )
    
    with col3:
        st.write("")  # Spacer
    
    # Apply filters
    filtered_df = all_df.copy()
    
    if date_range and len(date_range) == 2:
        # Convert to timezone-aware timestamps (Europe/Rome)
        milan_tz = pytz.timezone("Europe/Rome")
        start_date = pd.Timestamp(date_range[0], tz=milan_tz)
        end_date = pd.Timestamp(date_range[1], tz=milan_tz)
        filtered_df = OlympicsDataProcessor.filter_by_date_range(filtered_df, start_date, end_date)
    
    if selected_sport != "All" and sports_list:
        # Build sport code mapping safely
        sport_code_map = {}
        for s in sports_list:
            if isinstance(s, dict) and s.get("code"):
                code = s.get("code")
                sport_code_map[code] = OlympicsDataProcessor.get_sport_name(code)
        
        # Find matching sport code
        sport_code = None
        for code, name in sport_code_map.items():
            if name == selected_sport:
                sport_code = code
                break
        
        if sport_code:
            filtered_df = OlympicsDataProcessor.filter_by_sport(filtered_df, sport_code)
    
    st.markdown("---")
    
    # Display timeline and statistics
    col_timeline, col_stats = st.columns([2, 1])
    
    with col_timeline:
        st.write(f"### 📊 Events Timeline ({len(filtered_df)} events)")
        if not filtered_df.empty:
            fig = OlympicsVisualizations.create_events_timeline(filtered_df, max_events=30)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No events match the selected filters")
    
    with col_stats:
        st.write("### 📍 Distribution")
        if not filtered_df.empty:
            fig = OlympicsVisualizations.create_sports_distribution(filtered_df)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    
    # Detailed table
    st.write("### 📋 Event Details")
    if not filtered_df.empty:
        # Reset index and ensure no duplicate columns
        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
        
        # Remove duplicate events based on event_name, datetime, and venue
        dedup_cols = []
        if "event_name" in filtered_df.columns:
            dedup_cols.append("event_name")
        if "datetime" in filtered_df.columns:
            dedup_cols.append("datetime")
        if "venue_full" in filtered_df.columns:
            dedup_cols.append("venue_full")
        elif "venue" in filtered_df.columns:
            dedup_cols.append("venue")
        
        if dedup_cols:
            filtered_df = filtered_df.drop_duplicates(subset=dedup_cols, keep='first')
        
        # Create clean DataFrame with safe extraction
        event_names = list(filtered_df["event_name"].astype(str)) if "event_name" in filtered_df.columns else ["N/A"] * len(filtered_df)
        sport_codes = filtered_df["sport_code"] if "sport_code" in filtered_df.columns else pd.Series(["N/A"] * len(filtered_df))
        sports = [str(OlympicsDataProcessor.get_sport_name(code)) for code in sport_codes]
        date_times = list(filtered_df["datetime"].dt.strftime("%Y-%m-%d %H:%M")) if "datetime" in filtered_df.columns else ["N/A"] * len(filtered_df)
        # Use venue_full if available, otherwise fallback to venue
        venue_col = "venue_full" if "venue_full" in filtered_df.columns else "venue"
        venues = list(filtered_df[venue_col].astype(str)) if venue_col in filtered_df.columns else ["N/A"] * len(filtered_df)
        cities = list(filtered_df["city"].astype(str)) if "city" in filtered_df.columns else ["N/A"] * len(filtered_df)
        statuses = list(filtered_df["status"].astype(str)) if "status" in filtered_df.columns else ["N/A"] * len(filtered_df)
        
        display_df = pd.DataFrame({
            "event_name": event_names,
            "sport": sports,
            "date_time": date_times,
            "venue": venues,
            "city": cities,
            "status": statuses
        })
        
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )
        
        # Export option
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"olympics_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def render_country_tracker_tab():
    """Render Country Tracker tab"""
    st.subheader("🌍 Country Tracker")
    
    # Fetch countries and events
    all_response = fetch_all_events()
    all_df = OlympicsDataProcessor.parse_events_response(all_response)
    
    if all_df.empty:
        st.warning("No events data available")
        return
    
    # Get unique countries
    countries_set = set()
    if "teams" in all_df.columns:
        for idx, teams in enumerate(all_df["teams"]):
            # Skip None, NaN, or empty values - handle arrays safely
            if teams is None or (isinstance(teams, float) and pd.isna(teams)):
                continue
            if not teams:  # Skip empty lists/dicts
                continue
            if isinstance(teams, list):
                for team in teams:
                    if isinstance(team, dict) and "code" in team and team["code"]:
                        countries_set.add(team["code"])
            elif isinstance(teams, dict) and "code" in teams and teams["code"]:
                countries_set.add(teams["code"])
    
    # Add fallback countries if none found
    if not countries_set:
        countries_set = {"USA", "CAN", "ITA", "GER", "FRA", "JPN", "CHN", "KOR", "NOR", "SWE"}
    
    countries_list = sorted(list(countries_set))
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_country = st.selectbox(
            "Select Country",
            options=countries_list,
            key="country_tracker_select"
        )
    
    with col2:
        st.write("")  # Spacer
    
    if selected_country:
        # Filter events for selected country
        country_events = OlympicsDataProcessor.filter_by_country(all_df, selected_country)
        
        st.markdown("---")
        st.write(f"## {selected_country} - Events")
        
        if not country_events.empty:
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Events", len(country_events))
            with col2:
                # Count events that haven't happened yet (status not Completed)
                upcoming = len(country_events[country_events["status"] != "Completed"])
                st.metric("🔴 Upcoming", upcoming)
            with col3:
                sports_count = country_events["sport_code"].nunique() if "sport_code" in country_events.columns else 0
                st.metric("⛷️ Sports Involved", sports_count)
            
            st.markdown("---")
            
            # Sport distribution
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.write("### 📅 Country's Event Schedule")
                
                # Filter by sport for this country
                sports_response = fetch_all_sports()
                sports_list = sports_response.get("sports", []) if sports_response.get("success") else []
                
                # Fallback to sports from country events
                if not sports_list and "sport_code" in country_events.columns:
                    unique_codes = country_events["sport_code"].dropna().unique()
                    sport_codes = [str(code) for code in unique_codes if code]
                    sport_names = [OlympicsDataProcessor.get_sport_name(code) for code in sport_codes]
                else:
                    sport_codes = [s.get("code") for s in sports_list if isinstance(s, dict) and s.get("code")]
                    sport_names = [OlympicsDataProcessor.get_sport_name(code) for code in sport_codes if code]
                
                # Ensure at least one option
                if not sport_names:
                    sport_names = ["Alpine Skiing", "Ice Hockey"]
                
                selected_sport = st.selectbox(
                    "Filter by Sport",
                    options=["All"] + sport_names,
                    key="country_sport_filter"
                )
                
                filtered_country_events = country_events.copy()
                if selected_sport != "All" and sports_list:
                    # Build sport code mapping safely
                    sport_code_map = {}
                    for s in sports_list:
                        if isinstance(s, dict) and s.get("code"):
                            code = s.get("code")
                            sport_code_map[code] = OlympicsDataProcessor.get_sport_name(code)
                    
                    # Find matching sport code
                    sport_code = None
                    for code, name in sport_code_map.items():
                        if name == selected_sport:
                            sport_code = code
                            break
                    
                    if sport_code:
                        filtered_country_events = OlympicsDataProcessor.filter_by_sport(filtered_country_events, sport_code)
                
                if not filtered_country_events.empty:
                    # Reset index and ensure no duplicate columns
                    filtered_country_events = filtered_country_events.reset_index(drop=True)
                    filtered_country_events = filtered_country_events.loc[:, ~filtered_country_events.columns.duplicated()]
                    
                    # Remove duplicate events
                    dedup_cols = []
                    if "event_name" in filtered_country_events.columns:
                        dedup_cols.append("event_name")
                    if "datetime" in filtered_country_events.columns:
                        dedup_cols.append("datetime")
                    if "venue_full" in filtered_country_events.columns:
                        dedup_cols.append("venue_full")
                    elif "venue" in filtered_country_events.columns:
                        dedup_cols.append("venue")
                    
                    if dedup_cols:
                        filtered_country_events = filtered_country_events.drop_duplicates(subset=dedup_cols, keep='first')
                    
                    # Create clean DataFrame with safe extraction
                    event_names = list(filtered_country_events["event_name"].astype(str)) if "event_name" in filtered_country_events.columns else ["N/A"] * len(filtered_country_events)
                    sport_codes = filtered_country_events["sport_code"] if "sport_code" in filtered_country_events.columns else pd.Series(["N/A"] * len(filtered_country_events))
                    sports = [str(OlympicsDataProcessor.get_sport_name(code)) for code in sport_codes]
                    date_times = list(filtered_country_events["datetime"].dt.strftime("%Y-%m-%d %H:%M")) if "datetime" in filtered_country_events.columns else ["N/A"] * len(filtered_country_events)
                    # Use venue_full if available
                    venue_col = "venue_full" if "venue_full" in filtered_country_events.columns else "venue"
                    venues = list(filtered_country_events[venue_col].astype(str)) if venue_col in filtered_country_events.columns else ["N/A"] * len(filtered_country_events)
                    statuses = list(filtered_country_events["status"].astype(str)) if "status" in filtered_country_events.columns else ["N/A"] * len(filtered_country_events)
                    
                    display_df = pd.DataFrame({
                        "event_name": event_names,
                        "sport": sports,
                        "date_time": date_times,
                        "venue": venues,
                        "status": statuses
                    })
                    
                    st.dataframe(
                        display_df,
                        width="stretch",
                        hide_index=True
                    )
            
            with col_right:
                st.write("### ⛷️ Sports Breakdown")
                fig = OlympicsVisualizations.create_sports_distribution(country_events)
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        else:
            st.info(f"No events found for {selected_country}")


def render_analytics_tab():
    """Render Analytics tab"""
    st.subheader("📊 Analytics & Insights")
    
    # Fetch all events
    all_response = fetch_all_events()
    all_df = OlympicsDataProcessor.parse_events_response(all_response)
    
    if all_df.empty:
        st.warning("No events data available for analytics")
        return
    
    render_stats_cards(all_df)
    st.markdown("---")
    
    # Analytics layout
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏅 Sports Distribution",
        "📍 Venues",
        "🕐 Hourly Distribution",
        "📈 Status Overview"
    ])
    
    with tab1:
        fig = OlympicsVisualizations.create_sports_distribution(all_df)
        st.plotly_chart(fig, width="stretch")
    
    with tab2:
        fig = OlympicsVisualizations.create_venue_distribution(all_df)
        st.plotly_chart(fig, width="stretch")
    
    with tab3:
        fig = OlympicsVisualizations.create_hourly_distribution(all_df)
        st.plotly_chart(fig, width="stretch")
    
    with tab4:
        fig = OlympicsVisualizations.create_events_by_status(all_df)
        st.plotly_chart(fig, width="stretch")


def render_sidebar():
    """Render sidebar controls"""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Refresh settings
        st.markdown("**Auto Refresh**")
        auto_refresh = st.checkbox(
            "Enable auto-refresh",
            value=st.session_state.get("auto_refresh_enabled", True),
            key="auto_refresh"
        )
        
        refresh_interval = st.slider(
            "Refresh interval (minutes)",
            min_value=1840,
            max_value=2000,
            value=st.session_state.get("refresh_interval", 10),
            key="refresh_slider"
        )
        
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # API Status
        st.markdown("**API Status**")
        try:
            api = init_api_client()
            st.success("✅ Connected to API")
        except Exception as e:
            st.error(f"❌ API Error: {str(e)[:50]}")
        
        st.markdown("---")
        
        # Cache stats
        cache_stats = CacheManager.get_cache_stats()
        st.markdown("**Cache Info**")
        st.info(f"📦 Size: {cache_stats['cache_size']}\n\n📁 Files: {cache_stats['file_count']}")
        
        if st.button("🗑️ Clear Cache"):
            CacheManager.clear()
            st.rerun()
        
        st.markdown("---")
        
        # About
        st.markdown("**About**")
        st.write(
            "Milano-Cortina 2026 Winter Olympics Live Dashboard\n\n"
            "📊 Data Source: RapidAPI Olympics API\n\n"
            "🔄 Updates: Every 1 day\n\n"
            "🏠 [GitHub](https://github.com/lucydev256/olympics-2026)"
        )


def main():
    """Main application"""
    # Initialize session state
    StreamlitHelpers.initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Main tabs
    # Only Live Dashboard active - other tabs commented out for now
    tab1 = st.tabs([
        "🏟️ Live Dashboard"
    ])[0]
    
    # Podium tab - commented out for now
    # tab2, tab3, tab4, tab5 = st.tabs([
    #     "🏅 Podium",
    #     "📅 Schedule",
    #     "🌍 Country Tracker",
    #     "📊 Analytics"
    # ])
    
    with tab1:
        render_live_dashboard_tab()
    
    # Podium tab - commented out
    # with tab2:
    #     render_podium_tab()
    
    # Schedule tab - removed
    # with tab3:
    #     render_schedule_explorer_tab()
    
    # Country Tracker tab - removed
    # with tab4:
    #     render_country_tracker_tab()
    
    # Analytics tab - removed
    # with tab5:
    #     render_analytics_tab()
    
    # About Me Section - PowerPoint Presentation
    st.markdown("---")
    st.markdown("### 👤 About Me - Through My Olympic Lens")
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #6366f1;'>
        <p style='color: #374151; font-size: 1rem; line-height: 1.6; margin: 0;'>
            Want to learn more about me and my passion for winter sports? Check out my presentation on 
            Olympic downhill skiing - it features interactive content including embedded YouTube videos 
            showcasing the excitement and technical precision of alpine skiing. 🎿 See you you on the slopes! Lucy
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Presentation options - View online or Download
    col1, col2 = st.columns(2)
    
    with col1:
        # Google Drive link
        st.markdown("""
        <a href='https://docs.google.com/presentation/d/1QY3LAVfN14sxP93kH2XjhYo-a2lylF0wZNsg0vtK3CU/edit?usp=sharing' target='_blank' style='text-decoration: none;'>
            <div style='background-color: #6366f1; color: white; padding: 1rem; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1rem; cursor: pointer; transition: background-color 0.3s;'>
                🎿 View on Google Slides
            </div>
        </a>
        """, unsafe_allow_html=True)
        st.caption("💡 View online with embedded videos")
    
    with col2:
        # Download PowerPoint file
        try:
            ppt_path = os.path.join(os.path.dirname(__file__), "src", "MWN Olympic Games downhill skiing presentation 2126.pptx")
            if not os.path.exists(ppt_path):
                ppt_path = "src/MWN Olympic Games downhill skiing presentation 2126.pptx"
            
            with open(ppt_path, "rb") as file:
                ppt_data = file.read()
            
            st.download_button(
                label="📥 Download PowerPoint",
                data=ppt_data,
                file_name="Olympic_Downhill_Skiing_Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                help="Download to present offline",
                use_container_width=True
            )
            st.caption("📂 Download for offline viewing")
        except Exception as e:
            st.caption("⚠️ Download unavailable")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 0.8rem;'>"
        "🏅 Milano-Cortina 2026 Winter Olympics | Last updated: " + 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
