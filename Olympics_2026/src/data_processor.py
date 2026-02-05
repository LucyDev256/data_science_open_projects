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
        
        # Extract venue information and create readable venue strings
        if "venue" in df.columns and df["venue"].notna().any():
            # Extract venue details
            venue_names = []
            venue_cities = []
            venue_countries = []
            
            for v in df["venue"]:
                if isinstance(v, dict):
                    venue_names.append(v.get("name", "N/A"))
                    venue_cities.append(v.get("city", "N/A"))
                    venue_countries.append(v.get("country", "N/A"))
                else:
                    venue_names.append(str(v) if v else "N/A")
                    venue_cities.append("N/A")
                    venue_countries.append("N/A")
            
            df["venue_name"] = venue_names
            df["city"] = venue_cities
            df["venue_country"] = venue_countries
            # Create full venue display
            df["venue_full"] = [f"{name}, {city}, {country}" if name != "N/A" else "N/A" 
                               for name, city, country in zip(venue_names, venue_cities, venue_countries)]
        
        # Add computed columns
        df = OlympicsDataProcessor._add_computed_columns(df)
        
        # Rename columns for consistency
        rename_dict = {}
        if "discipline" in df.columns:
            rename_dict["discipline"] = "event_name"
        
        if rename_dict:
            df = df.rename(columns=rename_dict)
        
        # Ensure venue column exists
        if "venue" not in df.columns and "venue_full" in df.columns:
            df["venue"] = df["venue_full"]
        
        # Add detailed categorization for better visualizations
        df = OlympicsDataProcessor._add_discipline_categories(df)
        df = OlympicsDataProcessor._add_venue_categories(df)
        
        # Filter out events with unknown/invalid sport codes
        if "sport_code" in df.columns:
            df = df[df["sport_code"].notna()].copy()
            df = df[~df["sport_code"].isin(['unk', 'unknown', 'UNK', 'UNKNOWN', 'n/a', 'N/A'])].copy()
            df = df[df["sport_code"].str.len() > 0].copy()
        
        # Remove duplicate events at the source
        # Deduplicate based on event_name, date, time, and venue to catch exact duplicates
        dedup_cols = []
        if "event_name" in df.columns:
            dedup_cols.append("event_name")
        if "date" in df.columns:
            dedup_cols.append("date")
        if "time" in df.columns:
            dedup_cols.append("time")
        if "venue_full" in df.columns:
            dedup_cols.append("venue_full")
        elif "venue" in df.columns:
            dedup_cols.append("venue")
        if "sport_code" in df.columns:
            dedup_cols.append("sport_code")
        
        if dedup_cols and len(df) > 0:
            df = df.drop_duplicates(subset=dedup_cols, keep='first')
        
        return df
    
    @staticmethod
    def _add_discipline_categories(df: pd.DataFrame) -> pd.DataFrame:
        """Add detailed discipline categories for Freestyle/Snowboarding"""
        if df.empty or "event_name" not in df.columns:
            return df
        
        disciplines = []
        for idx, row in df.iterrows():
            if row.get('sport_code') == 'frs':
                name_lower = str(row['event_name']).lower()
                if 'mogul' in name_lower:
                    disciplines.append('Freestyle - Moguls')
                elif 'aerial' in name_lower:
                    disciplines.append('Freestyle - Aerials')
                elif 'slopestyle' in name_lower:
                    if 'freeski' in name_lower:
                        disciplines.append('Freestyle - Slopestyle')
                    else:
                        disciplines.append('Snowboard - Slopestyle')
                elif 'halfpipe' in name_lower or ' hp ' in name_lower:
                    disciplines.append('Snowboard - Halfpipe')
                elif 'big air' in name_lower or ' ba ' in name_lower:
                    if 'freeski' in name_lower:
                        disciplines.append('Freestyle - Big Air')
                    else:
                        disciplines.append('Snowboard - Big Air')
                elif 'cross' in name_lower or 'sbx' in name_lower:
                    disciplines.append('Snowboard - Cross')
                elif 'parallel' in name_lower or 'pgs' in name_lower:
                    disciplines.append('Snowboard - Parallel')
                else:
                    disciplines.append('Freestyle Skiing')
            else:
                sport_name = OlympicsDataProcessor.get_sport_name(row.get('sport_code', ''))
                disciplines.append(sport_name)
        
        df['discipline_detailed'] = disciplines
        return df
    
    @staticmethod
    def _add_venue_categories(df: pd.DataFrame) -> pd.DataFrame:
        """Add detailed venue categories for better distribution"""
        if df.empty or "venue_full" not in df.columns:
            return df
        
        venue_categories = []
        for venue in df['venue_full']:
            venue_str = str(venue)
            if 'Livigno' in venue_str:
                if 'Aerials' in venue_str or 'Moguls' in venue_str:
                    venue_categories.append('Livigno - Aerials & Moguls Park')
                else:
                    venue_categories.append('Livigno - Snow Park')
            else:
                venue_categories.append(venue_str)
        
        df['venue_detailed'] = venue_categories
        return df
    
    @staticmethod
    def _add_computed_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Add computed columns for filtering and display"""
        
        # Get current time in Milan timezone
        milan_tz = pytz.timezone("Europe/Rome")
        now = datetime.now(milan_tz)
        
        # Make datetime timezone-aware (Milan timezone)
        if df["datetime"].dt.tz is None:
            df["datetime"] = df["datetime"].dt.tz_localize("UTC").dt.tz_convert(milan_tz)
        else:
            df["datetime"] = df["datetime"].dt.tz_convert(milan_tz)
        
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
        def check_country(teams_value):
            """Safely check if country is in teams, handling all types"""
            try:
                # Handle None and scalar NaN
                if teams_value is None:
                    return False
                if isinstance(teams_value, float) and pd.isna(teams_value):
                    return False
                # Handle empty values
                if not teams_value:
                    return False
                # Check list of teams
                if isinstance(teams_value, list):
                    for team in teams_value:
                        if isinstance(team, dict):
                            # Check both 'code' and 'country_code' fields
                            if team.get("code") == country_code or team.get("country_code") == country_code:
                                return True
                            # Also check if code/country_code is in the team name or abbreviation
                            team_code = team.get("code", "").upper()
                            if country_code.upper() == team_code:
                                return True
                return False
            except (ValueError, TypeError):
                return False
        
        mask = df["teams"].apply(check_country)
        return df[mask].copy()
    
    @staticmethod
    def filter_by_sport(df: pd.DataFrame, sport_code: str) -> pd.DataFrame:
        """Filter events by sport code"""
        if df.empty or "sport_code" not in df.columns:
            return pd.DataFrame()
        return df[df["sport_code"] == sport_code].copy()
    
    @staticmethod
    def filter_by_date_range(
        df: pd.DataFrame,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Filter events by date range"""
        if df.empty or "datetime" not in df.columns:
            return pd.DataFrame()
        
        result = df.copy()
        if date_from:
            result = result[result["datetime"] >= date_from]
        if date_to:
            # Include entire end date by adding 23:59:59
            end_of_day = date_to + pd.Timedelta(hours=23, minutes=59, seconds=59)
            result = result[result["datetime"] <= end_of_day]
        
        return result
    
    @staticmethod
    def filter_by_status(df: pd.DataFrame, status: str) -> pd.DataFrame:
        """Filter events by status (Completed, Upcoming, Today, Scheduled)"""
        if df.empty or "status" not in df.columns:
            return pd.DataFrame()
        return df[df["status"] == status].copy()
    
    @staticmethod
    def get_sport_name(sport_code: str) -> str:
        """Get full sport name from code"""
        if not sport_code or sport_code.lower() in ['unk', 'unknown', 'n/a']:
            return "Unknown Sport"
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
        if df.empty or "hours_until" not in df.columns:
            return pd.DataFrame()
        return df[df["hours_until"] <= hours].copy()
    
    @staticmethod
    def get_medal_events_count_by_sport(df: pd.DataFrame) -> pd.DataFrame:
        """Get count of medal events by sport"""
        if df.empty or "sport_code" not in df.columns:
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
        
        # Use venue_full if available, otherwise venue
        venue_col = "venue_full" if "venue_full" in df.columns else "venue"
        city_col = "city" if "city" in df.columns else None
        
        if venue_col not in df.columns:
            return pd.DataFrame()
        
        # Remove duplicate columns if they exist
        df_clean = df.loc[:, ~df.columns.duplicated()]
        
        # Create venue counts
        if city_col and city_col in df_clean.columns:
            # Ensure both columns are 1-dimensional
            venue_series = df_clean[venue_col].astype(str)
            city_series = df_clean[city_col].astype(str)
            
            venue_counts = pd.DataFrame({
                "venue": venue_series,
                "city": city_series
            }).groupby(["venue", "city"]).size().reset_index(name="count")
        else:
            venue_counts = df_clean[venue_col].astype(str).value_counts().reset_index()
            venue_counts.columns = ["venue", "count"]
            venue_counts["city"] = "N/A"
        
        return venue_counts.sort_values("count", ascending=False)
    
    @staticmethod
    def get_timeline_data(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for timeline visualization"""
        if df.empty:
            return pd.DataFrame()
        
        required_cols = ["datetime", "event_name", "sport_code", "status"]
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()
        
        timeline_df = df[["datetime", "event_name", "sport_code", "status"]].copy()
        timeline_df["emoji"] = timeline_df["sport_code"].apply(
            OlympicsDataProcessor.get_event_emoji
        )
        timeline_df = timeline_df.sort_values("datetime")
        
        return timeline_df
