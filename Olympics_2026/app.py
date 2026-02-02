"""
Milano-Cortina 2026 Winter Olympics Live Dashboard
Interactive Streamlit app for viewing all Olympic events and results
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

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
        if response.get("success"):
            CacheManager.set("all_sports", response, "sports")
            return response
        return {}
    except Exception as e:
        st.warning(f"⚠️ Could not fetch sports: {str(e)}")
        return {}


@st.cache_data(ttl=86400)
def fetch_all_countries():
    """Fetch all countries"""
    api = init_api_client()
    
    cached = CacheManager.get("all_countries", "countries")
    if cached:
        return cached
    
    try:
        response = api.get_all_countries()
        if response.get("success"):
            CacheManager.set("all_countries", response, "countries")
            return response
        return {}
    except Exception as e:
        st.warning(f"⚠️ Could not fetch countries: {str(e)}")
        return {}


def render_header():
    """Render page header"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.write("")
    with col2:
        st.markdown("# 🏅 MILANO-CORTINA 2026")
        st.markdown("### Winter Olympics Live Dashboard")
    with col3:
        st.write("")
    
    st.markdown("---")


def render_stats_cards(df: pd.DataFrame):
    """Render statistics cards"""
    stats = OlympicsVisualizations.create_stats_cards(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Events", stats["total_events"])
    
    with col2:
        st.metric("🔴 Upcoming/Today", stats["upcoming_events"])
    
    with col3:
        st.metric("⛷️ Sports", stats["sports_count"])
    
    with col4:
        st.metric("🌍 Countries", stats["countries_count"])


def render_live_dashboard_tab():
    """Render Live Results Dashboard tab"""
    st.subheader("🏆 Live Results Dashboard")
    
    # Fetch today's events
    today_response = fetch_today_events()
    today_df = OlympicsDataProcessor.parse_events_response(today_response)
    
    if today_df.empty:
        st.info("No events scheduled for today")
        return
    
    render_stats_cards(today_df)
    st.markdown("---")
    
    # Split into columns for layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.write("### 📅 Today's Events")
        
        # Filter by status
        status_filter = st.selectbox(
            "Filter by Status:",
            options=["All", "Upcoming", "Completed", "Today"],
            key="today_status_filter"
        )
        
        filtered_df = today_df.copy()
        if status_filter != "All":
            filtered_df = OlympicsDataProcessor.filter_by_status(filtered_df, status_filter)
        
        if not filtered_df.empty:
            # Reset index for pandas 3.12 compatibility
            filtered_df = filtered_df.reset_index(drop=True)
            # Display as table - create clean DataFrame to avoid duplicate columns
            display_df = pd.DataFrame({
                "event_name": filtered_df["event_name"].fillna("").tolist(),
                "sport": filtered_df["sport_code"].apply(OlympicsDataProcessor.get_sport_name).fillna("").tolist(),
                "time": filtered_df["datetime"].dt.strftime("%H:%M").fillna("").tolist(),
                "venue": filtered_df["venue"].fillna("").tolist(),
                "status": filtered_df["status"].fillna("").tolist()
            })
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No events match the selected filter")
    
    with col_right:
        st.write("### 📈 Status Distribution")
        fig = OlympicsVisualizations.create_events_by_status(today_df)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now().date(), datetime.now().date() + timedelta(days=7)),
            key="schedule_date_range"
        )
    
    with col2:
        sports_response = fetch_all_sports()
        sports_list = sports_response.get("sports", []) if sports_response.get("success") else []
        sport_codes = [s.get("code") for s in sports_list if s.get("code")]
        sport_names = [OlympicsDataProcessor.get_sport_name(code) for code in sport_codes]
        
        selected_sport = st.selectbox(
            "Filter by Sport",
            options=["All"] + sport_names,
            key="schedule_sport_filter"
        )
    
    with col3:
        venue_list = all_df["venue"].dropna().unique().tolist()
        selected_venue = st.selectbox(
            "Filter by Venue",
            options=["All"] + sorted(venue_list),
            key="schedule_venue_filter"
        )
    
    with col4:
        st.write("")  # Spacer
    
    # Apply filters
    filtered_df = all_df.copy()
    
    if date_range and len(date_range) == 2:
        start_date = pd.Timestamp(date_range[0])
        end_date = pd.Timestamp(date_range[1])
        filtered_df = OlympicsDataProcessor.filter_by_date_range(filtered_df, start_date, end_date)
    
    if selected_sport != "All":
        sport_code = [k for k, v in {s.get("code"): OlympicsDataProcessor.get_sport_name(s.get("code")) for s in sports_list}.items() if v == selected_sport][0] if sports_list else None
        if sport_code:
            filtered_df = OlympicsDataProcessor.filter_by_sport(filtered_df, sport_code)
    
    if selected_venue != "All":
        filtered_df = filtered_df[filtered_df["venue"] == selected_venue]
    
    st.markdown("---")
    
    # Display timeline and statistics
    col_timeline, col_stats = st.columns([2, 1])
    
    with col_timeline:
        st.write(f"### 📊 Events Timeline ({len(filtered_df)} events)")
        if not filtered_df.empty:
            fig = OlympicsVisualizations.create_events_timeline(filtered_df, max_events=30)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No events match the selected filters")
    
    with col_stats:
        st.write("### 📍 Distribution")
        if not filtered_df.empty:
            fig = OlympicsVisualizations.create_sports_distribution(filtered_df)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    # Detailed table
    st.write("### 📋 Event Details")
    if not filtered_df.empty:
        # Reset index for pandas 3.12 compatibility
        filtered_df = filtered_df.reset_index(drop=True)
        # Create clean DataFrame to avoid duplicate columns
        display_df = pd.DataFrame({
            "event_name": filtered_df["event_name"].fillna("").tolist(),
            "sport": filtered_df["sport_code"].apply(OlympicsDataProcessor.get_sport_name).fillna("").tolist(),
            "date_time": filtered_df["datetime"].dt.strftime("%Y-%m-%d %H:%M").fillna("").tolist(),
            "venue": filtered_df["venue"].fillna("").tolist(),
            "city": filtered_df["city"].fillna("").tolist(),
            "status": filtered_df["status"].fillna("").tolist()
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
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
        for teams in all_df["teams"]:
            if isinstance(teams, list):
                for team in teams:
                    if isinstance(team, dict) and "code" in team:
                        countries_set.add(team["code"])
    
    countries_list = sorted(list(countries_set))
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_country = st.selectbox(
            "Select Country",
            options=countries_list,
            format_func=lambda x: f"{StreamlitHelpers.get_country_flag(x)} {x}",
            key="country_tracker_select"
        )
    
    with col2:
        st.write("")  # Spacer
    
    if selected_country:
        # Filter events for selected country
        country_events = OlympicsDataProcessor.filter_by_country(all_df, selected_country)
        
        st.markdown("---")
        st.write(f"## {StreamlitHelpers.get_country_flag(selected_country)} {selected_country} - Events")
        
        if not country_events.empty:
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Events", len(country_events))
            with col2:
                upcoming = len(country_events[country_events["status"].isin(["Upcoming", "Today"])])
                st.metric("🔴 Upcoming", upcoming)
            with col3:
                sports_count = country_events["sport_code"].nunique()
                st.metric("⛷️ Sports Involved", sports_count)
            
            st.markdown("---")
            
            # Sport distribution
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.write("### 📅 Country's Event Schedule")
                
                # Filter by sport for this country
                sports_response = fetch_all_sports()
                sports_list = sports_response.get("sports", []) if sports_response.get("success") else []
                sport_codes = [s.get("code") for s in sports_list if s.get("code")]
                sport_names = [OlympicsDataProcessor.get_sport_name(code) for code in sport_codes]
                
                selected_sport = st.selectbox(
                    "Filter by Sport",
                    options=["All"] + sport_names,
                    key="country_sport_filter"
                )
                
                filtered_country_events = country_events.copy()
                if selected_sport != "All":
                    sport_code = [k for k, v in {s.get("code"): OlympicsDataProcessor.get_sport_name(s.get("code")) for s in sports_list}.items() if v == selected_sport][0] if sports_list else None
                    if sport_code:
                        filtered_country_events = OlympicsDataProcessor.filter_by_sport(filtered_country_events, sport_code)
                
                if not filtered_country_events.empty:
                    # Reset index for pandas 3.12 compatibility
                    filtered_country_events = filtered_country_events.reset_index(drop=True)
                    # Create clean DataFrame to avoid duplicate columns
                    display_df = pd.DataFrame({
                        "event_name": filtered_country_events["event_name"].fillna("").tolist(),
                        "sport": filtered_country_events["sport_code"].apply(OlympicsDataProcessor.get_sport_name).fillna("").tolist(),
                        "date_time": filtered_country_events["datetime"].dt.strftime("%Y-%m-%d %H:%M").fillna("").tolist(),
                        "venue": filtered_country_events["venue"].fillna("").tolist(),
                        "status": filtered_country_events["status"].fillna("").tolist()
                    })
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
            
            with col_right:
                st.write("### ⛷️ Sports Breakdown")
                fig = OlympicsVisualizations.create_sports_distribution(country_events)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
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
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = OlympicsVisualizations.create_venue_distribution(all_df)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = OlympicsVisualizations.create_hourly_distribution(all_df)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = OlympicsVisualizations.create_events_by_status(all_df)
        st.plotly_chart(fig, use_container_width=True)


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
            min_value=5,
            max_value=30,
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
            "🔄 Updates: Every 10 minutes\n\n"
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Live Dashboard",
        "📅 Schedule",
        "🌍 Country Tracker",
        "📊 Analytics"
    ])
    
    with tab1:
        render_live_dashboard_tab()
    
    with tab2:
        render_schedule_explorer_tab()
    
    with tab3:
        render_country_tracker_tab()
    
    with tab4:
        render_analytics_tab()
    
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
