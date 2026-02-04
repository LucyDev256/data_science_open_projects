"""
Test script to examine API endpoint responses
Shows actual data structure for country filtering and medal events
"""

import os
from dotenv import load_dotenv
from src.api_client import MilanoCortina2026API
import json

load_dotenv()

def test_endpoints():
    """Test key endpoints and show response structure"""
    
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in .env file")
        return
    
    api = MilanoCortina2026API(api_key)
    
    print("=" * 80)
    print("1️⃣  TESTING COUNTRY ENDPOINT: GET /countries/CAN/events")
    print("=" * 80)
    
    try:
        # Test country-specific events endpoint
        canada_response = api.get_country_events("CAN")
        
        print(f"\n✅ Response received successfully")
        print(f"Success: {canada_response.get('success')}")
        print(f"Total Events: {canada_response.get('total', 0)}")
        
        if canada_response.get('events'):
            print(f"\n📋 First Event Structure:")
            first_event = canada_response['events'][0]
            print(json.dumps(first_event, indent=2))
            
            print(f"\n📊 Available Columns in Events:")
            for key in first_event.keys():
                print(f"  - {key}: {type(first_event[key]).__name__}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("2️⃣  TESTING MEDAL EVENTS: Check if endpoint exists")
    print("=" * 80)
    
    try:
        # Try medal events endpoint
        response = api._make_request("/events/medal-events", {"sport_code": "iho"})
        
        print(f"\n✅ Medal Events endpoint exists!")
        print(f"Success: {response.get('success')}")
        print(f"Total Medal Events: {response.get('total', 0)}")
        
        if response.get('events'):
            print(f"\n📋 First Medal Event Structure:")
            first_event = response['events'][0]
            print(json.dumps(first_event, indent=2))
            
            print(f"\n📊 Fields in Medal Events:")
            for key in first_event.keys():
                value = first_event[key]
                print(f"  - {key}: {type(value).__name__} = {value if not isinstance(value, (dict, list)) else '...'}")
        
    except Exception as e:
        print(f"❌ Medal events endpoint error: {str(e)}")
        print("   Checking if is_medal_event field exists in regular events...")
        
        try:
            all_events = api.get_all_events(limit=10)
            if all_events.get('events'):
                first = all_events['events'][0]
                if 'is_medal_event' in first:
                    print(f"   ✅ 'is_medal_event' field exists: {first['is_medal_event']}")
                else:
                    print(f"   ❌ 'is_medal_event' field NOT found")
                    print(f"   Available fields: {list(first.keys())}")
        except Exception as e2:
            print(f"   ❌ Error checking: {str(e2)}")
    
    print("\n" + "=" * 80)
    print("3️⃣  TESTING: GET /events with country filter parameter")
    print("=" * 80)
    
    try:
        # Test using country parameter in /events endpoint
        response = api.get_all_events(country="CAN", limit=5)
        
        print(f"\n✅ Response received")
        print(f"Success: {response.get('success')}")
        print(f"Total Events: {response.get('total', 0)}")
        
        if response.get('events'):
            print(f"\n📋 Sample Event:")
            event = response['events'][0]
            print(f"  Event: {event.get('discipline', 'N/A')}")
            print(f"  Sport: {event.get('sport', 'N/A')}")
            print(f"  Teams: {event.get('teams', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
The API provides:
1. /countries/{code}/events - Direct country endpoint
2. /events?country=CODE - Parameter-based filtering
3. /events/medal-events - Dedicated medal events endpoint (if exists)
4. is_medal_event field - Boolean flag in each event

We can implement proper country filtering using these!
""")

if __name__ == "__main__":
    test_endpoints()
