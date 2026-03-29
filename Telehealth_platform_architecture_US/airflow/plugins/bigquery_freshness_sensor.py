"""
Custom Airflow Sensor for BigQuery Table Freshness
Waits until a BigQuery table has been updated within a specified time window
"""

from typing import Optional
from datetime import datetime, timedelta
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)


class BigQueryTableFreshnessSensor(BaseSensorOperator):
    """
    Sensor that waits for a BigQuery table to be updated within max_age
    
    Useful for:
    - Ensuring upstream data is fresh before running transformations
    - Detecting stale data from CDC pipelines
    - Monitoring real-time data ingestion
    
    :param table_id: Full table ID (project.dataset.table)
    :param max_age_hours: Maximum acceptable data age in hours
    :param timestamp_column: Column to check for freshness (default: 'updated_at')
    :param gcp_project: GCP project ID
    """
    
    template_fields = ['table_id', 'timestamp_column']
    ui_color = '#4DA6FF'
    
    @apply_defaults
    def __init__(
        self,
        table_id: str,
        max_age_hours: float = 1.0,
        timestamp_column: str = 'updated_at',
        gcp_project: Optional[str] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_id = table_id
        self.max_age_hours = max_age_hours
        self.timestamp_column = timestamp_column
        self.gcp_project = gcp_project
    
    def poke(self, context):
        """Check if table is fresh enough"""
        
        logger.info(f"Checking freshness of {self.table_id}")
        logger.info(f"Max acceptable age: {self.max_age_hours} hours")
        
        client = bigquery.Client(project=self.gcp_project)
        
        # Query for latest timestamp
        query = f"""
        SELECT 
            MAX({self.timestamp_column}) as latest_update,
            TIMESTAMP_DIFF(
                CURRENT_TIMESTAMP(), 
                MAX({self.timestamp_column}), 
                MINUTE
            ) as age_minutes
        FROM `{self.table_id}`
        """
        
        try:
            result = client.query(query).result()
            row = list(result)[0]
            
            if row['latest_update'] is None:
                logger.warning(f"Table {self.table_id} is empty or has no {self.timestamp_column}")
                return False
            
            age_minutes = row['age_minutes']
            age_hours = age_minutes / 60.0
            
            logger.info(f"Table last updated: {row['latest_update']}")
            logger.info(f"Data age: {age_hours:.2f} hours")
            
            is_fresh = age_hours <= self.max_age_hours
            
            if is_fresh:
                logger.info(f"✅ Table is fresh (age: {age_hours:.2f}h <= {self.max_age_hours}h)")
            else:
                logger.info(f"⏳ Table is stale (age: {age_hours:.2f}h > {self.max_age_hours}h)")
            
            return is_fresh
            
        except Exception as e:
            logger.error(f"Error checking table freshness: {str(e)}")
            return False
