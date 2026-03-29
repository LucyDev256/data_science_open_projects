"""
Historical Data Backfill Script
Runs dbt models on historical data and validates completeness
"""

import subprocess
import logging
from datetime import datetime, timedelta
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoricalDataBackfill:
    """Backfills historical data through dbt transformations"""
    
    def __init__(self, start_date: str, end_date: str):
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.bq_client = bigquery.Client()
        
    def backfill_by_partition(self):
        """Process historical data in daily partitions"""
        current_date = self.start_date
        
        while current_date <= self.end_date:
            logger.info(f"Processing partition: {current_date.strftime('%Y-%m-%d')}")
            
            # Run dbt for specific partition
            cmd = [
                'dbt', 'run',
                '--select', 'bronze silver gold',
                '--vars', f'{{"target_date": "{current_date.strftime("%Y-%m-%d")}"}}',
                '--profiles-dir', './dbt'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully processed {current_date.strftime('%Y-%m-%d')}")
                self.validate_partition(current_date)
            else:
                logger.error(f"Error processing {current_date.strftime('%Y-%m-%d')}: {result.stderr}")
                
            current_date += timedelta(days=1)
    
    def validate_partition(self, date):
        """Validate row counts and data completeness for partition"""
        query = f"""
        SELECT 
            COUNT(*) as row_count,
            COUNT(DISTINCT patient_uuid) as unique_patients,
            MIN(created_at) as min_date,
            MAX(created_at) as max_date
        FROM `analytics_prod.gold_patient_journey`
        WHERE DATE(created_at) = '{date.strftime('%Y-%m-%d')}'
        """
        
        results = self.bq_client.query(query).result()
        for row in results:
            logger.info(f"Validation: {row}")


def main():
    # Backfill last 2 years of data
    backfill = HistoricalDataBackfill(
        start_date='2024-03-14',
        end_date='2026-03-14'
    )
    backfill.backfill_by_partition()


if __name__ == "__main__":
    main()
