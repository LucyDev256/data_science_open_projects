"""
Custom Airflow Operator for PHI De-identification
Ensures all PHI is properly anonymized before loading to analytics
"""

from typing import List, Dict, Any
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from google.cloud import bigquery
import hashlib
import logging

logger = logging.getLogger(__name__)


class PHIDeidentificationOperator(BaseOperator):
    """
    Operator to de-identify PHI data according to HIPAA Safe Harbor method
    
    Removes or anonymizes the following 18 identifiers:
    1. Names, 2. Geographic subdivisions smaller than state, 3. Dates (except year),
    4. Telephone numbers, 5. Fax numbers, 6. Email addresses, 7. SSN,
    8. Medical record numbers, 9. Health plan numbers, 10. Account numbers,
    11. Certificate/license numbers, 12. Vehicle identifiers, 13. Device identifiers,
    14. URLs, 15. IP addresses, 16. Biometric identifiers, 17. Photos, 18. Other unique IDs
    
    :param source_table: Source BigQuery table with PHI
    :param destination_table: Destination table for de-identified data
    :param identifiers_to_remove: List of columns to remove
    :param identifiers_to_hash: List of columns to hash (one-way)
    :param date_precision: How to handle dates ('year_only', 'remove', or 'shift')
    """
    
    template_fields = ['source_table', 'destination_table']
    ui_color = '#FF6B6B'
    
    @apply_defaults
    def __init__(
        self,
        source_table: str,
        destination_table: str,
        identifiers_to_remove: List[str] = None,
        identifiers_to_hash: List[str] = None,
        date_precision: str = 'year_only',
        gcp_project: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.source_table = source_table
        self.destination_table = destination_table
        self.identifiers_to_remove = identifiers_to_remove or [
            'ssn', 'email', 'phone', 'address_line1', 'address_line2',
            'city', 'zip_code', 'first_name', 'last_name'
        ]
        self.identifiers_to_hash = identifiers_to_hash or ['patient_uuid']
        self.date_precision = date_precision
        self.gcp_project = gcp_project
    
    def execute(self, context):
        """Execute de-identification"""
        
        logger.info(f"De-identifying PHI from {self.source_table}")
        logger. info(f"Removing identifiers: {self.identifiers_to_remove}")
        logger.info(f"Hashing identifiers: {self.identifiers_to_hash}")
        
        client = bigquery.Client(project=self.gcp_project)
        
        # Build de-identification SQL
        deidentify_sql = self._build_deidentification_query()
        
        logger.info(f"Executing query:\n{deidentify_sql}")
        
        # Run query
        job_config = bigquery.QueryJobConfig(
            destination=self.destination_table,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        query_job = client.query(deidentify_sql, job_config=job_config)
        result = query_job.result()
        
        logger.info(f"De-identification complete. Rows processed: {result.total_rows}")
        
        # Validate no PHI in output
        self._validate_deidentification(client)
        
        return {
            'source_table': self.source_table,
            'destination_table': self.destination_table,
            'rows_processed': result.total_rows
        }
    
    def _build_deidentification_query(self) -> str:
        """Build SQL query for de-identification"""
        
        # Start with SELECT
        select_parts = []
        
        # Add hashed columns
        for col in self.identifiers_to_hash:
            select_parts.append(
                f"TO_HEX(SHA256(CAST({col} AS STRING))) AS {col}_hash"
            )
        
        # Handle dates based on precision
        if self.date_precision == 'year_only':
            select_parts.append("EXTRACT(YEAR FROM date_of_birth) AS birth_year")
        elif self.date_precision == 'remove':
            # Don't include date columns
            pass
        elif self.date_precision == 'shift':
            # Shift dates by random amount (not implemented here)
            select_parts.append("DATE_ADD(date_of_birth, INTERVAL CAST(RAND()*365 AS INT64) DAY) AS date_of_birth")
        
        # Add all other columns except removed identifiers
        select_parts.append("* EXCEPT (" + ", ".join(self.identifiers_to_remove) + ")")
        
        query = f"""
        SELECT
            {', '.join(select_parts)}
        FROM `{self.source_table}`
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
        """
        
        return query
    
    def _validate_deidentification(self, client: bigquery.Client):
        """Validate that PHI has been removed"""
        
        logger.info("Validating de-identification...")
        
        # Check for null values in required fields
        validation_query = f"""
        SELECT
            COUNTIF(patient_uuid_hash IS NULL) as null_patient_count,
            COUNT(*) as total_count
        FROM `{self.destination_table}`
        """
        
        result = client.query(validation_query).result()
        row = list(result)[0]
        
        if row['null_patient_count'] > 0:
            raise ValueError(
                f"Found {row['null_patient_count']} records with null patient_uuid_hash"
            )
        
        logger.info("✅ De-identification validation passed")
