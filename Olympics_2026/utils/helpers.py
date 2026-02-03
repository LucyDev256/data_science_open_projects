"""
Helper Utilities for Olympics Dashboard
"""

from datetime import datetime
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional


class StreamlitHelpers:
    """Helper functions for Streamlit UI"""
    
    @staticmethod
    def format_countdown(hours: float) -> str:
        """Format hours into readable countdown"""
        if hours < 0:
            return "🔴 Event finished"
        elif hours == 0:
            return "🟡 Starting now!"
        elif hours < 1:
            minutes = int(hours * 60)
            return f"🟡 {minutes}m away"
        elif hours < 24:
            return f"🔴 {int(hours)}h away"
        else:
            days = int(hours // 24)
            return f"⚪ {days}d away"
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables"""
        defaults = {
            "auto_refresh_enabled": True,
            "refresh_interval": 10,
            "selected_country": None,
            "selected_sport": None,
            "show_stats": True,
            "dark_mode": False,
            "api_status": "idle"
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get_country_flag(country_code: str) -> str:
        """Get flag emoji for country code"""
        # Common country flag mapping
        flags = {
            "USA": "🇺🇸", "CAN": "🇨🇦", "GBR": "🇬🇧", "AUS": "🇦🇺",
            "NZL": "🇳🇿", "FRA": "🇫🇷", "DEU": "🇩🇪", "ITA": "🇮🇹",
            "ESP": "🇪🇸", "SWE": "🇸🇪", "NOR": "🇳🇴", "FIN": "🇫🇮",
            "AUT": "🇦🇹", "SUI": "🇨🇭", "NED": "🇳🇱", "BEL": "🇧🇪",
            "ROU": "🇷🇴", "CZE": "🇨🇿", "POL": "🇵🇱", "RUS": "🇷🇺",
            "JPN": "🇯🇵", "CHN": "🇨🇳", "KOR": "🇰🇷", "UKR": "🇺🇦",
            "UZB": "🇺🇿", "KAZ": "🇰🇿", "IND": "🇮🇳", "THA": "🇹🇭",
            "ARG": "🇦🇷", "BRA": "🇧🇷", "MEX": "🇲🇽", "CHL": "🇨🇱",
            "COL": "🇨🇴", "TUR": "🇹🇷", "GRE": "🇬🇷", "ISL": "🇮🇸",
            "SVK": "🇸🇰", "SVN": "🇸🇮", "CRO": "🇭🇷"
        }
        return flags.get(country_code, "🏳️")
    
    @staticmethod
    def get_medal_emoji(medal_position: Optional[int]) -> str:
        """Get medal emoji for position"""
        if medal_position == 1:
            return "🥇"
        elif medal_position == 2:
            return "🥈"
        elif medal_position == 3:
            return "🥉"
        else:
            return "🏅"
    
    @staticmethod
    def create_info_card(title: str, value: str, emoji: str = "📊"):
        """Create metric card using Streamlit columns"""
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric(label=emoji, value="", delta="")
        with col2:
            st.write(f"<h4 style='margin: 0;'>{title}</h4>", unsafe_allow_html=True)
            st.write(f"<h2 style='margin: 0; color: #3498DB;'>{value}</h2>", unsafe_allow_html=True)
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
        """Format datetime object to string"""
        if dt is None or pd.isna(dt):
            return "N/A"
        return dt.strftime(format_str)
    
    @staticmethod
    def create_sidebar_section(title: str, icon: str = ""):
        """Create formatted sidebar section"""
        st.sidebar.markdown(f"### {icon} {title}")
    
    @staticmethod
    def show_loading_animation():
        """Show loading animation with Lottie"""
        st.info("🔄 Loading data... Please wait.")
    
    @staticmethod
    def format_table_for_display(df, columns_to_show: List[str] = None):
        """Format DataFrame for display in Streamlit"""
        if df.empty:
            st.info("No data available")
            return
        
        if columns_to_show:
            display_df = df[columns_to_show].copy()
        else:
            display_df = df.copy()
        
        # Format datetime columns
        for col in display_df.columns:
            if display_df[col].dtype == 'datetime64[ns]':
                display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(display_df, use_container_width=True)
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Get color for status badge"""
        colors = {
            "Completed": "#27AE60",
            "Today": "#F39C12",
            "Upcoming": "#E74C3C",
            "Scheduled": "#95A5A6"
        }
        return colors.get(status, "#3498DB")


class ValidationHelpers:
    """Validation helper functions"""
    
    @staticmethod
    def is_valid_country_code(code: str) -> bool:
        """Validate country code format"""
        return isinstance(code, str) and len(code) == 3 and code.isupper()
    
    @staticmethod
    def is_valid_sport_code(code: str) -> bool:
        """Validate sport code format"""
        valid_codes = ["alp", "iho", "fsk", "ssk", "stk", "cur", "bth", "ccs", "sjp", "ncb", "frs", "sbd", "bob", "skn", "lug", "smt"]
        return code in valid_codes
    
    @staticmethod
    def is_valid_api_response(response: dict) -> bool:
        """Validate API response structure"""
        return isinstance(response, dict) and "events" in response


# pandas is imported for the format_datetime function
import pandas as pd
