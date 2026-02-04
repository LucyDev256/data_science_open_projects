"""
Visualization Module for Olympics Dashboard
Creates interactive Plotly charts and displays
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional
from src.data_processor import OlympicsDataProcessor


class OlympicsVisualizations:
    """Creates interactive visualizations for Olympics events"""
    
    # Color palette
    COLORS = {
        "completed": "#2ECC71",
        "today": "#F39C12",
        "upcoming": "#E74C3C",
        "scheduled": "#95A5A6",
        "primary": "#3498DB",
        "secondary": "#9B59B6"
    }
    
    SPORT_COLORS = {
        "alp": "#FF6B6B",
        "iho": "#4ECDC4",
        "fsk": "#FFD93D",
        "ssk": "#6BCB77",
        "stk": "#A8E6CF",
        "cur": "#FF8B94",
        "bth": "#8E72FF",
        "ccs": "#4A90E2",
        "sjp": "#F5A623",
        "ncb": "#BD10E0",
        "frs": "#50E3C2",
        "sbd": "#F8E71C",
        "bob": "#7D3C98",
        "skn": "#27AE60",
        "lug": "#2980B9",
        "smt": "#8E44AD"
    }
    
    @staticmethod
    def create_events_timeline(df: pd.DataFrame, max_events: int = 50) -> go.Figure:
        """
        Create timeline chart of upcoming events
        
        Args:
            df: Events DataFrame
            max_events: Maximum events to show
            
        Returns:
            Plotly figure object
        """
        if df.empty:
            return OlympicsVisualizations._create_empty_chart("No events to display")
        
        # Limit to max events and remove duplicate columns
        display_df = df.head(max_events).copy()
        display_df = display_df.loc[:, ~display_df.columns.duplicated()]
        
        # Create color mapping
        status_colors = {
            "Completed": OlympicsVisualizations.COLORS["completed"],
            "Today": OlympicsVisualizations.COLORS["today"],
            "Upcoming": OlympicsVisualizations.COLORS["upcoming"],
            "Scheduled": OlympicsVisualizations.COLORS["scheduled"]
        }
        display_df["color"] = display_df["status"].map(status_colors).fillna(OlympicsVisualizations.COLORS["scheduled"])
        
        # Create hover text safely - avoid string concatenation with Series that have duplicate indices
        event_names = display_df["event_name"].fillna("N/A").astype(str) if "event_name" in display_df.columns else pd.Series(["N/A"] * len(display_df), index=display_df.index)
        sport_codes = display_df["sport_code"] if "sport_code" in display_df.columns else pd.Series(["N/A"] * len(display_df), index=display_df.index)
        sport_names = sport_codes.apply(OlympicsDataProcessor.get_sport_name).astype(str)
        # Use venue_full if available
        venue_col = "venue_full" if "venue_full" in display_df.columns else "venue"
        venues = display_df[venue_col].fillna("N/A").astype(str) if venue_col in display_df.columns else pd.Series(["N/A"] * len(display_df), index=display_df.index)
        cities = display_df["city"].fillna("N/A").astype(str) if "city" in display_df.columns else pd.Series(["N/A"] * len(display_df), index=display_df.index)
        
        # Build hover text using list comprehension to avoid pandas alignment issues
        display_df["hover_text"] = [
            f"{name}<br><b>Sport:</b> {sport}<br><b>Venue:</b> {venue}<br><b>City:</b> {city}"
            for name, sport, venue, city in zip(event_names, sport_names, venues, cities)
        ]
        
        fig = go.Figure()
        
        for sport in display_df["sport_code"].unique():
            sport_data = display_df[display_df["sport_code"] == sport]
            
            fig.add_trace(go.Bar(
                y=sport_data["event_name"],
                x=sport_data["datetime"],
                orientation="h",
                marker=dict(
                    color=sport_data["color"],
                    line=dict(color="white", width=1)
                ),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=sport_data["hover_text"],
                name=OlympicsDataProcessor.get_sport_name(sport)
            ))
        
        fig.update_layout(
            title="📅 Olympics Events Timeline",
            xaxis_title="Date & Time",
            yaxis_title="Event",
            height=800,
            showlegend=False,
            hovermode="closest",
            template="plotly_white",
            xaxis=dict(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='LightGray',
                type='date',
                tickformat="%b %d<br>%H:%M",
                tickangle=0
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(size=9)
            )
        )
        
        return fig
    
    @staticmethod
    def create_sports_distribution(df: pd.DataFrame) -> go.Figure:
        """
        Create pie chart of events by sport
        
        Args:
            df: Events DataFrame
            
        Returns:
            Plotly figure object
        """
        if df.empty or "sport_code" not in df.columns:
            return OlympicsVisualizations._create_empty_chart("No data available")
        
        sport_counts = OlympicsDataProcessor.get_medal_events_count_by_sport(df)
        
        if sport_counts.empty:
            return OlympicsVisualizations._create_empty_chart("No sports data")
        
        colors = [
            OlympicsVisualizations.SPORT_COLORS.get(code, "#95A5A6")
            for code in sport_counts["sport_code"]
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=sport_counts["sport_name"],
            values=sport_counts["count"],
            marker=dict(colors=colors, line=dict(color="white", width=2)),
            hovertemplate="<b>%{label}</b><br>Events: %{value}<extra></extra>",
            textposition="inside",
            textinfo="percent+label"
        )])
        
        fig.update_layout(
            title="🏅 Events Distribution by Sport",
            height=600,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
    
    @staticmethod
    def create_venue_distribution(df: pd.DataFrame) -> go.Figure:
        """Create bar chart of events by venue"""
        if df.empty:
            return OlympicsVisualizations._create_empty_chart("No venue data")
        
        venue_data = OlympicsDataProcessor.get_events_by_venue(df)
        
        fig = go.Figure(data=[go.Bar(
            x=venue_data["venue"],
            y=venue_data["count"],
            marker=dict(color=OlympicsVisualizations.COLORS["primary"]),
            hovertemplate="<b>%{x}</b><br>Events: %{y}<extra></extra>",
            text=venue_data["count"],
            textposition="outside"
        )])
        
        fig.update_layout(
            title="📍 Events by Venue",
            xaxis_title="Venue",
            yaxis_title="Number of Events",
            height=500,
            showlegend=False,
            template="plotly_white",
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    @staticmethod
    def create_events_by_status(df: pd.DataFrame) -> go.Figure:
        """Create bar chart of events by status"""
        if df.empty:
            return OlympicsVisualizations._create_empty_chart("No status data")
        
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        
        # Define status order
        status_order = ["Completed", "Today", "Upcoming", "Scheduled"]
        status_counts["status"] = pd.Categorical(
            status_counts["status"],
            categories=status_order,
            ordered=True
        )
        status_counts = status_counts.sort_values("status")
        
        colors = [
            OlympicsVisualizations.COLORS.get(status.lower(), "#95A5A6")
            for status in status_counts["status"]
        ]
        
        fig = go.Figure(data=[go.Bar(
            x=status_counts["status"],
            y=status_counts["count"],
            marker=dict(color=colors),
            hovertemplate="<b>%{x}</b><br>Events: %{y}<extra></extra>",
            text=status_counts["count"],
            textposition="outside"
        )])
        
        fig.update_layout(
            title="📊 Events by Status",
            xaxis_title="Status",
            yaxis_title="Count",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        
        return fig
    
    @staticmethod
    def create_country_events_comparison(
        country_events: Dict[str, int],
        top_n: int = 15
    ) -> go.Figure:
        """Create bar chart comparing events across countries"""
        if not country_events:
            return OlympicsVisualizations._create_empty_chart("No country data")
        
        # Convert to sorted DataFrame
        df = pd.DataFrame(
            list(country_events.items()),
            columns=["country", "count"]
        ).sort_values("count", ascending=False).head(top_n)
        
        fig = go.Figure(data=[go.Bar(
            x=df["country"],
            y=df["count"],
            marker=dict(color=OlympicsVisualizations.COLORS["secondary"]),
            hovertemplate="<b>%{x}</b><br>Events: %{y}<extra></extra>",
            text=df["count"],
            textposition="outside"
        )])
        
        fig.update_layout(
            title=f"🌍 Top {top_n} Countries by Event Participation",
            xaxis_title="Country",
            yaxis_title="Number of Events",
            height=500,
            showlegend=False,
            template="plotly_white",
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    @staticmethod
    def create_hourly_distribution(df: pd.DataFrame) -> go.Figure:
        """Create chart showing events distribution by hour of day"""
        if df.empty or "datetime" not in df.columns:
            return OlympicsVisualizations._create_empty_chart("No hourly data")
        
        df_copy = df.copy()
        # Check datetime is valid
        if not pd.api.types.is_datetime64_any_dtype(df_copy["datetime"]):
            return OlympicsVisualizations._create_empty_chart("Invalid datetime data")
        
        df_copy["hour"] = df_copy["datetime"].dt.hour
        hourly_dist = df_copy.groupby("hour").size().reset_index(name="count")
        
        # Ensure all hours are represented
        all_hours = pd.DataFrame({"hour": range(24)})
        hourly_dist = all_hours.merge(hourly_dist, on="hour", how="left").fillna(0)
        hourly_dist["count"] = hourly_dist["count"].astype(int)
        
        fig = go.Figure(data=[go.Bar(
            x=hourly_dist["hour"],
            y=hourly_dist["count"],
            marker=dict(color=OlympicsVisualizations.COLORS["primary"]),
            hovertemplate="<b>%{x}:00</b><br>Events: %{y}<extra></extra>",
            text=hourly_dist["count"],
            textposition="outside"
        )])
        
        fig.update_layout(
            title="🕐 Events Distribution by Time of Day",
            xaxis_title="Hour (24H)",
            yaxis_title="Number of Events",
            height=400,
            showlegend=False,
            template="plotly_white",
            xaxis=dict(tickmode="linear", tick0=0, dtick=1)
        )
        
        return fig
    
    @staticmethod
    def _create_empty_chart(message: str) -> go.Figure:
        """Create a placeholder chart for empty data"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400,
            template="plotly_white"
        )
        return fig
    
    @staticmethod
    def create_stats_cards(df: pd.DataFrame) -> Dict[str, str]:
        """Create statistics for display cards"""
        if df.empty:
            return {
                "total_events": "0",
                "upcoming_events": "0",
                "sports_count": "0",
                "countries_count": "0"
            }
        
        total = len(df)
        upcoming = len(df[df["status"].isin(["Upcoming", "Today"])])
        sports = df["sport_code"].nunique()
        
        # Count unique countries
        countries_set = set()
        if "teams" in df.columns:
            for teams in df["teams"]:
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
        
        return {
            "total_events": str(total),
            "upcoming_events": str(upcoming),
            "sports_count": str(sports),
            "countries_count": str(len(countries_set))
        }
