"""
Data Processing Module for Olympics Events
Transforms raw API responses into clean, usable DataFrames
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz


class OlympicsDataProcessor:
    """
    Processes Olympic events data from API responses
    Handles filtering, sorting, and computing additional fields
    """
    
    # Sport code to full name mapping
    SPORT_NAMES = {
        "alp": "Alpine Skiing",
        "iho": "Ice Hockey",
        "fsk": "Figure Skating",
        "ssk": "Speed Skating",
        "stk": "Short Track",
        "cur": "Curling",
        "bth": "Biathlon",
        "ccs": "Cross-Country Skiing",
        "sjp": "Ski Jumping",
        "ncb": "Nordic Combined",
        "frs": "Freestyle Skiing",
        "sbd": "Snowboarding",
        "bob": "Bobsleigh",
        "skn": "Skeleton",
        "lug": "Luge",
        "smt": "Ski Mountaineering"
    }
    
    # Discipline patterns for categorization
    DISCIPLINE_TYPES = {
        "downhill": ["downhill"],
        "slalom": ["slalom"],
        "giant slalom": ["giant slalom", "gs"],
        "super-g": ["super-g", "super g"],
        "combined": ["combined"],
        "parallel": ["parallel"],
        "halfpipe": ["halfpipe"],
        "slopestyle": ["slopestyle"],
        "big air": ["big air"],
        "cross": ["cross"],
        "pursuit": ["pursuit"],
        "sprint": ["sprint"],
        "mass start": ["mass start"],
        "team": ["team"],
    }
    
    @staticmethod
    def parse_events_response(response: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert API response to DataFrame with added computed columns
        
        Args:
            response: Raw API response dictionary
            
        Returns:
            Processed DataFrame with events
        """
        if not response.get("success") or not response.get("events"):
            return pd.DataFrame()
        
        events = response["events"]
        df = pd.DataFrame(events)
        
        if df.empty:
            return df
        
        # Parse dates and times
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
        df["datetime"] = pd.to_datetime(
            df["date"].astype(str) + " " + df.get("time", "00:00"),
            format="%Y-%m-%d %H:%M",
            errors="coerce"
        )
        
        # Extract venue information
        if "venue" in df.columns and df["venue"].notna().any():
            venue_data = pd.json_normalize(df["venue"])
            df = pd.concat([df, venue_data.add_prefix("venue_")], axis=1)
        
        # Add computed columns
        df = OlympicsDataProcessor._add_computed_columns(df)
        
        # Rename columns for consistency
        df = df.rename(columns={
            "venue_name": "venue",
            "venue_city": "city",
            "sport_code": "sport_code",
            "discipline": "event_name"
        })
        
        return df
    
    @staticmethod
    def _add_computed_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Add computed columns for filtering and display"""
        
        # Get current time in Milan timezone
        milan_tz = pytz.timezone("Europe/Rome")
        now = datetime.now(milan_tz)
        
        # Time calculations
        df["time_until_event"] = df["datetime"] - now
        df["hours_until"] = df["time_until_event"].dt.total_seconds() / 3600
        
        # Status determination
        df["status"] = "Scheduled"
        df.loc[df["hours_until"] < 0, "status"] = "Completed"
        df.loc[(df["hours_until"] >= 0) & (df["hours_until"] < 2), "status"] = "Upcoming"
        df.loc[(df["hours_until"] >= 2) & (df["hours_until"] < 24), "status"] = "Today"
        
        # Date flags
        df["is_today"] = df["date"].dt.date == now.date()
        df["is_medal_event"] = True  # Per user note: all Olympic events are medal events
        
        # Sort by datetime
        df = df.sort_values("datetime", ascending=True)
        
        return df
    
    @staticmethod
    def filter_by_country(df: pd.DataFrame, country_code: str) -> pd.DataFrame:
        """
        Filter events by country
        
        Args:
            df: Events DataFrame
            country_code: Country code to filter by
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or "teams" not in df.columns:
            return df
        
        # Check if country appears in teams
        mask = df["teams"].apply(
            lambda x: isinstance(x, list) and any(
                team.get("code") == country_code for team in x if isinstance(team, dict)
            )
        )
        return df[mask].copy()
    
    @staticmethod
    def filter_by_sport(df: pd.DataFrame, sport_code: str) -> pd.DataFrame:
        """Filter events by sport code"""
        if df.empty:
            return df
        return df[df["sport_code"] == sport_code].copy()
    
    @staticmethod
    def filter_by_date_range(
        df: pd.DataFrame,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Filter events by date range"""
        if df.empty:
            return df
        
        if date_from:
            df = df[df["datetime"] >= date_from]
        if date_to:
            df = df[df["datetime"] <= date_to]
        
        return df.copy()
    
    @staticmethod
    def filter_by_status(df: pd.DataFrame, status: str) -> pd.DataFrame:
        """Filter events by status (Completed, Upcoming, Today, Scheduled)"""
        if df.empty:
            return df
        return df[df["status"] == status].copy()
    
    @staticmethod
    def get_sport_name(sport_code: str) -> str:
        """Get full sport name from code"""
        return OlympicsDataProcessor.SPORT_NAMES.get(sport_code, sport_code.upper())
    
    @staticmethod
    def categorize_discipline(discipline: str) -> str:
        """Categorize discipline into broader type"""
        discipline_lower = discipline.lower()
        for category, keywords in OlympicsDataProcessor.DISCIPLINE_TYPES.items():
            if any(keyword in discipline_lower for keyword in keywords):
                return category
        return "other"
    
    @staticmethod
    def get_event_emoji(sport_code: str) -> str:
        """Get emoji for sport code"""
        emoji_map = {
            "alp": "⛷️",
            "iho": "🏒",
            "fsk": "🎭",
            "ssk": "⛸️",
            "stk": "⛸️",
            "cur": "🥌",
            "bth": "🎯",
            "ccs": "🏂",
            "sjp": "🛷",
            "ncb": "⛷️",
            "frs": "🏂",
            "sbd": "🏂",
            "bob": "🛷",
            "skn": "🛷",
            "lug": "🛷",
            "smt": "⛰️"
        }
        return emoji_map.get(sport_code, "🏅")
    
    @staticmethod
    def get_status_emoji(status: str) -> str:
        """Get emoji for event status"""
        emoji_map = {
            "Completed": "✅",
            "Today": "🟡",
            "Upcoming": "🔴",
            "Scheduled": "⚪"
        }
        return emoji_map.get(status, "⚪")
    
    @staticmethod
    def format_event_for_display(event: pd.Series) -> Dict[str, str]:
        """Format a single event for display"""
        sport_emoji = OlympicsDataProcessor.get_event_emoji(event.get("sport_code", ""))
        status_emoji = OlympicsDataProcessor.get_status_emoji(event.get("status", ""))
        
        return {
            "emoji": sport_emoji,
            "sport": OlympicsDataProcessor.get_sport_name(event.get("sport_code", "")),
            "event": event.get("event_name", ""),
            "date": event["datetime"].strftime("%Y-%m-%d") if pd.notna(event.get("datetime")) else "N/A",
            "time": event["datetime"].strftime("%H:%M") if pd.notna(event.get("datetime")) else "N/A",
            "venue": event.get("venue", "N/A"),
            "city": event.get("city", "N/A"),
            "status": f"{status_emoji} {event.get('status', 'N/A')}"
        }
    
    @staticmethod
    def get_upcoming_events(df: pd.DataFrame, hours: int = 24) -> pd.DataFrame:
        """Get events happening in the next N hours"""
        if df.empty:
            return df
        return df[df["hours_until"] <= hours].copy()
    
    @staticmethod
    def get_medal_events_count_by_sport(df: pd.DataFrame) -> pd.DataFrame:
        """Get count of medal events by sport"""
        if df.empty:
            return pd.DataFrame()
        
        counts = df.groupby("sport_code").size().reset_index(name="count")
        counts["sport_name"] = counts["sport_code"].apply(
            OlympicsDataProcessor.get_sport_name
        )
        counts["emoji"] = counts["sport_code"].apply(
            OlympicsDataProcessor.get_event_emoji
        )
        
        return counts.sort_values("count", ascending=False)
    
    @staticmethod
    def get_events_by_venue(df: pd.DataFrame) -> pd.DataFrame:
        """Get event count by venue"""
        if df.empty:
            return pd.DataFrame()
        
        venue_counts = df.groupby(["venue", "city"]).size().reset_index(name="count")
        return venue_counts.sort_values("count", ascending=False)
    
    @staticmethod
    def get_timeline_data(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for timeline visualization"""
        if df.empty:
            return pd.DataFrame()
        
        timeline_df = df[["datetime", "event_name", "sport_code", "status"]].copy()
        timeline_df["emoji"] = timeline_df["sport_code"].apply(
            OlympicsDataProcessor.get_event_emoji
        )
        timeline_df = timeline_df.sort_values("datetime")
        
        return timeline_df
