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
    
    @staticmethod
    def get_sport_description(sport_code: str, event_count: int = 0) -> Dict[str, str]:
        """Get detailed description for each Olympic sport"""
        descriptions = {
            "frs": {
                "name": "Freestyle Skiing & Snowboarding",
                "emoji": "🎿",
                "description": f"**{event_count} total events** including qualifications, semifinals, and finals",
                "details": """
                **Why so many events?**
                - Multiple rounds per competition (Qualification Run 1, 2, 3 + Finals)
                - Includes both Freestyle Skiing AND Snowboarding disciplines
                - Disciplines: Moguls, Aerials, Ski Cross, Halfpipe, Slopestyle, Big Air
                - Each discipline has Men's and Women's categories
                - Snowboarding includes: Parallel Giant Slalom (16 rounds!), Snowboard Cross, Halfpipe, Slopestyle, Big Air
                
                **Main Venue:** Livigno Snow Park - purpose-built for freestyle/snowboard action sports
                """,
                "fun_fact": "💡 Only about 20% of these events are medal finals - the rest are exciting qualification rounds!"
            },
            "iho": {
                "name": "Ice Hockey",
                "emoji": "🏒",
                "description": f"**{event_count} total events** from group stages to gold medal games",
                "details": """
                **Tournament Structure:**
                - Group stage: Round-robin matches for Men's and Women's tournaments
                - Playoff rounds: Quarterfinals, Semifinals, Bronze Medal, Gold Medal games
                - Each team plays multiple games to advance
                
                **Competition Format:** 
                - Men's and Women's tournaments run parallel
                - Teams compete for Olympic glory in fast-paced 3-period matches
                
                **Main Venues:** Milano Rho & Milano Santagiulia Ice Hockey Arenas
                """,
                "fun_fact": "🏆 Canada has won 13 Olympic ice hockey gold medals - the most in Olympic history!"
            },
            "alp": {
                "name": "Alpine Skiing",
                "emoji": "⛷️",
                "description": f"**{event_count} total events** featuring speed and technical disciplines",
                "details": """
                **Disciplines:**
                - Speed events: Downhill, Super-G (1-2 runs each)
                - Technical events: Slalom, Giant Slalom (2 runs each)
                - Combined: Downhill + Slalom
                
                **Competition Format:**
                - Men's and Women's categories for each discipline
                - Athletes race against the clock on challenging mountain courses
                - Fastest combined time wins
                
                **Main Venue:** Stelvio Ski Centre in Bormio - legendary downhill course
                """,
                "fun_fact": "⚡ Downhill skiers reach speeds over 140 km/h (87 mph)!"
            },
            "cur": {
                "name": "Curling",
                "emoji": "🥌",
                "description": f"**{event_count} total events** of precision and strategy",
                "details": """
                **Tournament Structure:**
                - Round-robin group stage
                - Playoff brackets leading to medal games
                - Men's, Women's, and Mixed Doubles categories
                
                **Format:**
                - Each game has 8-10 ends (similar to innings in baseball)
                - Multiple games per team throughout the tournament
                - Strategic positioning determines winners
                
                **Main Venue:** Dedicated curling venue with pristine ice conditions
                """,
                "fun_fact": "♟️ Curling is called 'chess on ice' due to its strategic complexity!"
            },
            "sjp": {
                "name": "Ski Jumping",
                "emoji": "🎿",
                "description": f"**{event_count} total events** of flying through the air",
                "details": """
                **Competition Structure:**
                - Qualification rounds for each event
                - Competition rounds (2 jumps per athlete)
                - Individual and Team events
                - Men's, Women's, and Mixed Team categories
                
                **Hills:**
                - Normal Hill (98m)
                - Large Hill (125m+)
                
                **Main Venue:** Predazzo Ski Jumping Stadium in Val di Fiemme
                """,
                "fun_fact": "🦅 Ski jumpers can fly over 140 meters - longer than a football field!"
            },
            "ssk": {
                "name": "Speed Skating",
                "emoji": "⛸️",
                "description": f"**{event_count} total events** on the ice oval",
                "details": """
                **Distance Events:**
                - Sprint: 500m, 1000m
                - Middle: 1500m
                - Distance: 3000m, 5000m, 10000m
                - Team Pursuit
                - Mass Start
                
                **Format:**
                - Men's and Women's categories
                - Athletes race against the clock in pairs
                
                **Main Venue:** Milano Speed Skating Stadium - 400m oval track
                """,
                "fun_fact": "🏃 Elite speed skaters reach over 60 km/h on straightaways!"
            },
            "fsk": {
                "name": "Figure Skating",
                "emoji": "⛸️",
                "description": f"**{event_count} total events** of artistry and athleticism",
                "details": """
                **Events:**
                - Men's and Women's Singles (Short Program + Free Skate)
                - Pairs (Short + Free Skate)
                - Ice Dance (Rhythm Dance + Free Dance)
                - Team Event
                
                **Format:**
                - Two-part competitions (short + long programs)
                - Judged on technical elements and artistic presentation
                
                **Main Venue:** Milano Ice Skating Arena
                """,
                "fun_fact": "💫 A quad axel is 4.5 rotations in the air - one of the hardest jumps!"
            },
            "bth": {
                "name": "Biathlon",
                "emoji": "🎿",
                "description": f"**{event_count} total events** combining skiing and shooting",
                "details": """
                **Events:**
                - Sprint, Pursuit, Individual, Mass Start
                - Relay (Men's, Women's, Mixed)
                
                **Format:**
                - Cross-country skiing + rifle shooting
                - Missed shots = penalty loops or time penalties
                - Tests both endurance and precision
                
                **Main Venue:** Anterselva Biathlon Arena
                """,
                "fun_fact": "🎯 Athletes must slow their heart rate from racing to hit 5cm targets at 50m!"
            },
            "ccs": {
                "name": "Cross-Country Skiing",
                "emoji": "🎿",
                "description": f"**{event_count} total events** of endurance racing",
                "details": """
                **Distance Events:**
                - Sprint: 1.4-1.8km
                - Middle: 10-15km
                - Long: 30-50km
                - Relay events
                
                **Styles:**
                - Classic technique
                - Freestyle (skate skiing)
                
                **Main Venue:** Tesero Cross-Country Skiing Stadium in Val di Fiemme
                """,
                "fun_fact": "💪 The 50km race burns over 4,000 calories - equivalent to 8 Big Macs!"
            },
            "stk": {
                "name": "Short Track Speed Skating",
                "emoji": "⛸️",
                "description": f"**{event_count} total events** of high-speed pack racing",
                "details": """
                **Events:**
                - Individual: 500m, 1000m, 1500m
                - Relay: 3000m (Women), 5000m (Men)
                - Mixed Team Relay
                
                **Format:**
                - Multiple skaters racing simultaneously
                - Heats, quarterfinals, semifinals, finals
                - Strategic passing and positioning crucial
                
                **Track:** 111.12m oval - much shorter than long track
                """,
                "fun_fact": "⚡ Speeds reach 50 km/h in tight corners with intense contact!"
            },
            "bob": {
                "name": "Bobsleigh",
                "emoji": "🛷",
                "description": f"**{event_count} total events** down the ice track",
                "details": """
                **Events:**
                - 2-Man Bobsleigh
                - 4-Man Bobsleigh
                - 2-Woman Bobsleigh
                - Women's Monobob
                
                **Format:**
                - Multiple training runs
                - 4 competition runs
                - Fastest combined time wins
                
                **Main Venue:** Cortina Sliding Centre
                """,
                "fun_fact": "🚀 Bobsleds reach 150+ km/h (95 mph) and pull 5G in corners!"
            },
            "lug": {
                "name": "Luge",
                "emoji": "🛷",
                "description": f"**{event_count} total events** feet-first down the track",
                "details": """
                **Events:**
                - Men's Singles
                - Women's Singles
                - Doubles
                - Team Relay
                
                **Format:**
                - Multiple runs per event
                - Athletes lie on their backs, feet-first
                - Steering with leg and shoulder pressure
                
                **Main Venue:** Cortina Sliding Centre
                """,
                "fun_fact": "🏎️ Luge is the fastest sliding sport, reaching 140 km/h face-up!"
            },
            "skn": {
                "name": "Skeleton",
                "emoji": "🛷",
                "description": f"**{event_count} total events** head-first racing",
                "details": """
                **Events:**
                - Men's Skeleton
                - Women's Skeleton
                
                **Format:**
                - Training runs
                - 4 competition runs
                - Combined time determines winner
                - Athletes race head-first, face-down
                
                **Main Venue:** Cortina Sliding Centre
                """,
                "fun_fact": "😱 Skeleton athletes face the ice just centimeters away at 130+ km/h!"
            },
            "ncb": {
                "name": "Nordic Combined",
                "emoji": "🎿",
                "description": f"**{event_count} total events** combining ski jumping and cross-country",
                "details": """
                **Format:**
                - Ski jumping round determines starting order
                - Cross-country skiing race
                - First to cross the finish line wins
                
                **Events:**
                - Individual Gundersen
                - Team events
                
                **Venues:** Predazzo (jumping) + Tesero (cross-country)
                """,
                "fun_fact": "🏆 Nordic Combined tests both flying ability and endurance!"
            },
            "sbd": {
                "name": "Snowboarding",
                "emoji": "🏂",
                "description": f"**{event_count} total events** (included in Freestyle category)",
                "details": """
                **Note:** Snowboarding events are categorized under Freestyle Skiing (frs) in the data.
                
                **Disciplines:**
                - Parallel Giant Slalom (racing)
                - Snowboard Cross (racing)
                - Halfpipe (aerial tricks)
                - Slopestyle (park riding)
                - Big Air (single massive jump)
                
                **Main Venue:** Livigno Snow Park
                """,
                "fun_fact": "🤘 Snowboarding became an Olympic sport in 1998 in Nagano!"
            },
            "smt": {
                "name": "Ski Mountaineering",
                "emoji": "⛰️",
                "description": f"**{event_count} total events** - NEW Olympic sport!",
                "details": """
                **NEW for 2026!** 
                Ski Mountaineering makes its Olympic debut in Milano-Cortina!
                
                **Events:**
                - Individual Sprint
                - Individual Race
                - Mixed Team Relay
                
                **Format:**
                - Athletes climb up and ski down mountains
                - Uses special lightweight equipment
                - Tests endurance, technical skill, and speed
                
                **Historic Addition:** First time in Olympic history!
                """,
                "fun_fact": "🆕 This is the newest Olympic winter sport - watch history being made!"
            }
        }
        
        return descriptions.get(sport_code, {
            "name": "Olympic Sport",
            "emoji": "🏅",
            "description": f"**{event_count} total events**",
            "details": "Olympic competition featuring world-class athletes.",
            "fun_fact": "🎿 Experience the thrill of Olympic competition!"
        })


# pandas is imported for the format_datetime function
import pandas as pd
