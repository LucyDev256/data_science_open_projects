"""
Cache Manager for API Responses
Handles smart caching with TTL and fallback storage
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import streamlit as st


class CacheManager:
    """
    Manages caching of API responses with automatic expiration
    Uses Streamlit's session state for in-memory cache
    """
    
    CACHE_DIR = ".cache"
    
    # Cache TTL (Time To Live) in seconds
    TTL = {
        "sports": 86400,        # 24 hours
        "countries": 86400,     # 24 hours
        "events": 600,          # 10 minutes
        "country_events": 600,  # 10 minutes
        "today_events": 300     # 5 minutes
    }
    
    def __init__(self):
        """Initialize cache manager"""
        self._ensure_cache_dir()
    
    @staticmethod
    def _ensure_cache_dir():
        """Ensure cache directory exists"""
        if not os.path.exists(CacheManager.CACHE_DIR):
            os.makedirs(CacheManager.CACHE_DIR)
    
    @staticmethod
    def get(key: str, cache_type: str = "events") -> Optional[Dict[str, Any]]:
        """
        Get cached data
        
        Args:
            key: Cache key
            cache_type: Type of cache (determines TTL)
            
        Returns:
            Cached data if valid and exists, None otherwise
        """
        # Try session state first (fastest)
        if key in st.session_state:
            cache_entry = st.session_state[key]
            if not CacheManager._is_expired(cache_entry, cache_type):
                return cache_entry.get("data")
        
        # Try file cache as fallback
        file_path = CacheManager._get_file_path(key)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    cache_entry = json.load(f)
                    if not CacheManager._is_expired(cache_entry, cache_type):
                        # Restore to session state
                        st.session_state[key] = cache_entry
                        return cache_entry.get("data")
            except (json.JSONDecodeError, IOError):
                pass
        
        return None
    
    @staticmethod
    def set(key: str, data: Dict[str, Any], cache_type: str = "events"):
        """
        Store data in cache
        
        Args:
            key: Cache key
            data: Data to cache
            cache_type: Type of cache (determines TTL)
        """
        cache_entry = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "type": cache_type
        }
        
        # Store in session state
        st.session_state[key] = cache_entry
        
        # Store in file cache as backup
        file_path = CacheManager._get_file_path(key)
        try:
            with open(file_path, 'w') as f:
                json.dump(cache_entry, f)
        except IOError:
            pass  # Silently fail if file writing fails
    
    @staticmethod
    def clear(key: Optional[str] = None):
        """
        Clear cache entry or entire cache
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        if key:
            if key in st.session_state:
                del st.session_state[key]
            
            file_path = CacheManager._get_file_path(key)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        else:
            # Clear all session state cache keys
            keys_to_delete = [k for k in st.session_state.keys() if isinstance(st.session_state.get(k), dict) and "timestamp" in str(st.session_state.get(k))]
            for k in keys_to_delete:
                del st.session_state[k]
            
            # Clear all files in cache directory
            if os.path.exists(CacheManager.CACHE_DIR):
                for file in os.listdir(CacheManager.CACHE_DIR):
                    try:
                        os.remove(os.path.join(CacheManager.CACHE_DIR, file))
                    except OSError:
                        pass
    
    @staticmethod
    def _is_expired(cache_entry: Dict[str, Any], cache_type: str) -> bool:
        """Check if cache entry has expired"""
        try:
            timestamp = datetime.fromisoformat(cache_entry.get("timestamp", ""))
            ttl = CacheManager.TTL.get(cache_type, 600)
            return (datetime.now() - timestamp).total_seconds() > ttl
        except (ValueError, AttributeError):
            return True
    
    @staticmethod
    def _get_file_path(key: str) -> str:
        """Get file path for cache key"""
        # Sanitize key for use as filename
        safe_key = key.replace("/", "_").replace("?", "_").replace("&", "_")
        return os.path.join(CacheManager.CACHE_DIR, f"{safe_key}.json")
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        if not os.path.exists(CacheManager.CACHE_DIR):
            return {"cache_size": 0, "file_count": 0}
        
        files = os.listdir(CacheManager.CACHE_DIR)
        total_size = sum(
            os.path.getsize(os.path.join(CacheManager.CACHE_DIR, f))
            for f in files
        )
        
        return {
            "cache_size": f"{total_size / 1024:.2f} KB",
            "file_count": len(files)
        }


class StreamlitCacheDecorator:
    """Decorator for Streamlit cache with custom TTL"""
    
    @staticmethod
    def cached(cache_type: str = "events"):
        """
        Decorator to cache function results
        
        Args:
            cache_type: Type of cache (determines TTL)
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
                
                # Try to get from cache
                cached_data = CacheManager.get(cache_key, cache_type)
                if cached_data is not None:
                    return cached_data
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                CacheManager.set(cache_key, result, cache_type)
                
                return result
            
            return wrapper
        return decorator
