"""
Quick analysis script to understand event distribution
"""

import os
from dotenv import load_dotenv
from src.api_client import MilanoCortina2026API
from src.data_processor import OlympicsDataProcessor
import pandas as pd

load_dotenv()

api_key = os.getenv("RAPIDAPI_KEY")
api = MilanoCortina2026API(api_key)

print("Fetching all events...")
response = api.get_all_events(limit=500)
df = OlympicsDataProcessor.parse_events_response(response)

print(f"\n📊 Total events after deduplication: {len(df)}")

# Analyze by sport
print("\n🏅 Events by Sport:")
sport_counts = df['sport_code'].value_counts()
for sport_code, count in sport_counts.items():
    sport_name = OlympicsDataProcessor.get_sport_name(sport_code)
    percentage = (count / len(df)) * 100
    print(f"  {sport_name} ({sport_code}): {count} events ({percentage:.1f}%)")

print("\n📍 Top 10 Venues by Event Count:")
venue_counts = df['venue_full'].value_counts().head(10)
for venue, count in venue_counts.items():
    percentage = (count / len(df)) * 100
    print(f"  {venue}: {count} events ({percentage:.1f}%)")

# Check Freestyle Skiing in detail
print("\n🔍 Freestyle Skiing Events Detail:")
frs_df = df[df['sport_code'] == 'frs'].copy()
print(f"Total FRS events: {len(frs_df)}")

# Show unique event names
print("\nUnique event names in Freestyle Skiing:")
unique_events = frs_df['event_name'].value_counts()
for event_name, count in unique_events.items():
    print(f"  {event_name}: {count} occurrences")

# Check if there are multiple sessions/heats for the same event
print("\n🔍 Livigno Snow Park Events:")
livigno_df = df[df['venue_full'].str.contains('Livigno', na=False)].copy()
print(f"Total events at Livigno: {len(livigno_df)}")

print("\nSports at Livigno:")
livigno_sports = livigno_df['sport_code'].value_counts()
for sport_code, count in livigno_sports.items():
    sport_name = OlympicsDataProcessor.get_sport_name(sport_code)
    print(f"  {sport_name} ({sport_code}): {count} events")

# Check for potential duplicates that weren't caught
print("\n⚠️ Checking for potential near-duplicates in Freestyle Skiing:")
frs_grouped = frs_df.groupby(['event_name', 'date']).size().reset_index(name='count')
duplicates = frs_grouped[frs_grouped['count'] > 1]
if len(duplicates) > 0:
    print("Found multiple events with same name and date:")
    for _, row in duplicates.iterrows():
        print(f"  {row['event_name']} on {row['date']}: {row['count']} events")
        same_events = frs_df[(frs_df['event_name'] == row['event_name']) & (frs_df['date'] == row['date'])]
        print(f"    Times: {same_events['time'].tolist()}")
else:
    print("No obvious duplicates found (same name + date)")
