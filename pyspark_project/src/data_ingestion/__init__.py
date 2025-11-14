"""Data Ingestion Package - Load data from BigQuery and Cloud Storage"""

from .bigquery_loader import BigQueryLoader

__all__ = ["BigQueryLoader"]
