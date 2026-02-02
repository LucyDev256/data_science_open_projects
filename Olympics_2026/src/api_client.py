"""
API Client for Milano-Cortina 2026 Winter Olympics
Handles all API requests to RapidAPI Olympics endpoint
"""

import requests
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode


class MilanoCortina2026API:
    """
    Client for Milano-Cortina 2026 Olympics API
    
    Handles authentication, requests, error handling, and retries.
    """
    
    BASE_URL = "https://milano-cortina-2026-olympics-api.p.rapidapi.com"
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(self, api_key: str):
        """
        Initialize API client with RapidAPI key
        
        Args:
            api_key: RapidAPI key for authentication
        """
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "milano-cortina-2026-olympics-api.p.rapidapi.com"
        }
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Make HTTP GET request with retry logic and error handling
        
        Args:
            endpoint: API endpoint path (e.g., "/events")
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Parsed JSON response
            
        Raises:
            requests.exceptions.RequestException: If request fails after retries
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=timeout
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    raise requests.exceptions.HTTPError(
                        "Rate limit exceeded. Consider upgrading your RapidAPI plan."
                    )
                
                # Check for authentication errors
                if response.status_code == 401:
                    raise requests.exceptions.HTTPError(
                        "Invalid API key. Check your credentials."
                    )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        return {"success": False, "events": []}
    
    # ==================== Events Endpoints ====================
    
    def get_all_events(
        self,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sport_code: Optional[str] = None,
        country: Optional[str] = None,
        venue: Optional[str] = None,
        city: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all Olympic events with optional filtering
        
        Args:
            date: Specific date (YYYY-MM-DD)
            date_from: Start date for range (YYYY-MM-DD)
            date_to: End date for range (YYYY-MM-DD)
            sport_code: Filter by sport code (alp, iho, fsk, etc.)
            country: Filter by country code (USA, ITA, etc.)
            venue: Filter by venue name
            city: Filter by city (Milano, Cortina, etc.)
            limit: Maximum results (1-500)
            
        Returns:
            API response with events list
        """
        params = {}
        if date:
            params["date"] = date
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if sport_code:
            params["sport_code"] = sport_code
        if country:
            params["country"] = country
        if venue:
            params["venue"] = venue
        if city:
            params["city"] = city
        if limit:
            params["limit"] = limit
        
        return self._make_request("/events", params)
    
    def get_today_events(self) -> Dict[str, Any]:
        """Get all Olympic events happening today"""
        return self._make_request("/events/today")
    
    def search_events(self, query: str) -> Dict[str, Any]:
        """
        Full-text search across events, disciplines, and venues
        
        Args:
            query: Search query (e.g., "downhill", "slalom", "figure")
            
        Returns:
            API response with matching events
        """
        return self._make_request("/search", {"q": query})
    
    # ==================== Sport Endpoints ====================
    
    def get_all_sports(self) -> Dict[str, Any]:
        """Get all 16 Olympic winter sports with event counts"""
        return self._make_request("/sports")
    
    def get_sport_events(
        self,
        sport_code: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all events for a specific sport
        
        Args:
            sport_code: Sport code (alp, iho, fsk, etc.)
            limit: Maximum results
            
        Returns:
            API response with sport-specific events
        """
        params = {}
        if limit:
            params["limit"] = limit
        
        return self._make_request(f"/sports/{sport_code}/events", params)
    
    # ==================== Country Endpoints ====================
    
    def get_all_countries(self) -> Dict[str, Any]:
        """Get all participating countries"""
        return self._make_request("/countries")
    
    def get_country_events(
        self,
        country_code: str,
        sport_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all events for a specific country
        
        Args:
            country_code: Country code (USA, ITA, CAN, etc.)
            sport_code: Optional sport filter
            
        Returns:
            API response with country-specific events
        """
        params = {}
        if sport_code:
            params["sport_code"] = sport_code
        
        return self._make_request(f"/countries/{country_code}/events", params)
    
    # ==================== Convenience Methods ====================
    
    def get_alpine_skiing_events(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get all alpine skiing events"""
        return self.get_sport_events("alp", limit=limit)
    
    def get_events_by_date_range(
        self,
        date_from: str,
        date_to: str
    ) -> Dict[str, Any]:
        """Get events for a specific date range"""
        return self.get_all_events(
            date_from=date_from,
            date_to=date_to,
            limit=500
        )
    
    def get_country_events_by_sport(
        self,
        country_code: str,
        sport_code: str
    ) -> Dict[str, Any]:
        """Get events for specific country and sport combination"""
        return self.get_country_events(country_code, sport_code)
