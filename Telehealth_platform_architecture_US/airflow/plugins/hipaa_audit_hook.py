"""
Custom Airflow Hook for HIPAA Audit Logging
Logs all data access to compliance audit tables
"""

from typing import Dict, Any, Optional
from airflow.hooks.base import BaseHook
from google.cloud import bigquery
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class HIPAAAuthook(BaseHook):
    """
    Hook for logging HIPAA-compliant audit events to BigQuery
    
    Logs include:
    - Who accessed the data (user/service account)
    - What data was accessed (table, patient IDs)
    - When it was accessed (timestamp)
    - Why it was accessed (purpose/DAG)
    - Where it was accessed from (IP, service)
    """
    
    def __init__(
        self,
        gcp_project: str,
        audit_dataset: str = 'compliance_audit_prod',
        audit_table: str = 'data_access_log',
        conn_id: str = 'google_cloud_default'
    ):
        super().__init__()
        self.gcp_project = gcp_project
        self.audit_dataset = audit_dataset
        self.audit_table = audit_table
        self.conn_id = conn_id
        self.client = bigquery.Client(project=gcp_project)
    
    def log_data_access(
        self,
        user_email: str,
        resource_type: str,
        resource_id: str,
        action: str,
        purpose: str,
        patient_uuids: Optional[list] = None,
        record_count: int = 0,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """
        Log a data access event to the audit table
        
        :param user_email: Email of user/service account accessing data
        :param resource_type: Type of resource (e.g., 'bigquery_table', 'cloud_sql_table')
        :param resource_id: Full identifier of resource
        :param action: Type of access (SELECT, INSERT, UPDATE, DELETE)
        :param purpose: Business justification for access
        :param patient_uuids: List of patient UUIDs accessed (if applicable)
        :param record_count: Number of records accessed
        :param additional_context: Any additional metadata
        """
        
        audit_record = {
            'event_timestamp': datetime.utcnow().isoformat(),
            'user_email': user_email,
            'service_account': os.getenv('GOOGLE_SERVICE_ACCOUNT', 'unknown'),
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'purpose': purpose,
            'patient_uuids': patient_uuids or [],
            'record_count': record_count,
            'ip_address': self._get_client_ip(),
            'dag_id': additional_context.get('dag_id') if additional_context else None,
            'task_id': additional_context.get('task_id') if additional_context else None,
            'execution_date': additional_context.get('execution_date') if additional_context else None,
            'additional_metadata': str(additional_context) if additional_context else None
        }
        
        logger.info(f"Logging audit event: {audit_record}")
        
        # Insert into BigQuery audit table
        table_ref = f"{self.gcp_project}.{self.audit_dataset}.{self.audit_table}"
        
        errors = self.client.insert_rows_json(table_ref, [audit_record])
        
        if errors:
            logger.error(f"Failed to log audit event: {errors}")
            raise Exception(f"Audit logging failed: {errors}")
        else:
            logger.info(f"✅ Audit event logged successfully")
    
    def log_phi_access(
        self,
        user_email: str,
        table_id: str,
        patient_uuids: list,
        purpose: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Specialized method for logging PHI access
        
        PHI access requires strict audit logging per HIPAA
        """
        
        return self.log_data_access(
            user_email=user_email,
            resource_type='phi_table',
            resource_id=table_id,
            action='SELECT_PHI',
            purpose=purpose,
            patient_uuids=patient_uuids,
            record_count=len(patient_uuids),
            additional_context=context
        )
    
    def _get_client_ip(self) -> str:
        """Get client IP address (best effort)"""
        # In Airflow, this would come from the request context
        # For now, return service IP or 'internal'
        return os.getenv('CLIENT_IP', 'internal')
    
    def query_audit_log(
        self,
        user_email: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> list:
        """
        Query the audit log for compliance reporting
        
        :return: List of audit records matching criteria
        """
        
        conditions = []
        
        if user_email:
            conditions.append(f"user_email = '{user_email}'")
        
        if resource_id:
            conditions.append(f"resource_id = '{resource_id}'")
        
        if start_date:
            conditions.append(f"event_timestamp >= '{start_date.isoformat()}'")
        
        if end_date:
            conditions.append(f"event_timestamp <= '{end_date.isoformat()}'")
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        query = f"""
        SELECT *
        FROM `{self.gcp_project}.{self.audit_dataset}.{self.audit_table}`
        WHERE {where_clause}
        ORDER BY event_timestamp DESC
        LIMIT {limit}
        """
        
        logger.info(f"Querying audit log:\n{query}")
        
        result = self.client.query(query).result()
        
        return [dict(row) for row in result]
