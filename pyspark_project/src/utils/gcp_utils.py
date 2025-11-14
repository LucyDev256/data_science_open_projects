"""
Google Cloud Platform Utilities
Authentication, BigQuery, Cloud Storage helpers
"""

from google.cloud import bigquery, storage
from google.oauth2 import service_account
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import os


def load_gcp_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load GCP configuration from YAML file.
    
    Args:
        config_path: Path to gcp_config.yaml. If None, uses default location.
        
    Returns:
        Dictionary with GCP configuration
    """
    if config_path is None:
        # Default to config/gcp_config.yaml
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "gcp_config.yaml"
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_bigquery_client(
    project_id: Optional[str] = None,
    credentials_path: Optional[str] = None
) -> bigquery.Client:
    """
    Create BigQuery client with authentication.
    
    Args:
        project_id: GCP project ID
        credentials_path: Path to service account JSON key
        
    Returns:
        Authenticated BigQuery client
        
    Example:
        >>> client = get_bigquery_client()
        >>> query = "SELECT * FROM dataset.table LIMIT 10"
        >>> df = client.query(query).to_dataframe()
    """
    
    # Try to get credentials from environment variable
    if credentials_path is None:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if credentials_path and Path(credentials_path).exists():
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        client = bigquery.Client(
            project=project_id, 
            credentials=credentials
        )
    else:
        # Use default credentials (works on GCP services)
        client = bigquery.Client(project=project_id)
    
    print(f"✅ BigQuery client created for project: {client.project}")
    return client


def get_storage_client(
    credentials_path: Optional[str] = None
) -> storage.Client:
    """
    Create Cloud Storage client with authentication.
    
    Returns:
        Authenticated Cloud Storage client
        
    Example:
        >>> client = get_storage_client()
        >>> bucket = client.bucket("my-bucket")
        >>> blob = bucket.blob("data/file.csv")
    """
    
    if credentials_path is None:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if credentials_path and Path(credentials_path).exists():
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        client = storage.Client(credentials=credentials)
    else:
        client = storage.Client()
    
    print(f"✅ Cloud Storage client created")
    return client


def read_from_bigquery(
    query: str,
    project_id: Optional[str] = None,
    to_pandas: bool = True
):
    """
    Read data from BigQuery using SQL query.
    
    Args:
        query: SQL query string
        project_id: GCP project ID
        to_pandas: If True, return pandas DataFrame. If False, return iterator.
        
    Returns:
        pandas DataFrame or query result iterator
        
    Example:
        >>> query = '''
        ...     SELECT patient_id, age, gender
        ...     FROM `bigquery-public-data.cms_synthetic_patient_data_omop.person`
        ...     LIMIT 1000
        ... '''
        >>> df = read_from_bigquery(query)
    """
    client = get_bigquery_client(project_id)
    
    print(f"🔍 Executing BigQuery query...")
    query_job = client.query(query)
    
    if to_pandas:
        df = query_job.to_dataframe()
        print(f"✅ Query complete: {len(df):,} rows returned")
        return df
    else:
        return query_job.result()


def upload_to_gcs(
    local_path: str,
    bucket_name: str,
    blob_name: str
) -> str:
    """
    Upload file to Google Cloud Storage.
    
    Args:
        local_path: Path to local file
        bucket_name: GCS bucket name
        blob_name: Destination path in bucket (e.g., "data/file.csv")
        
    Returns:
        GCS URI (gs://bucket/path)
        
    Example:
        >>> uri = upload_to_gcs(
        ...     "models/model.pkl",
        ...     "my-bucket",
        ...     "models/latest/model.pkl"
        ... )
        >>> print(uri)  # gs://my-bucket/models/latest/model.pkl
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    print(f"⬆️  Uploading {local_path} to gs://{bucket_name}/{blob_name}")
    blob.upload_from_filename(local_path)
    
    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    print(f"✅ Upload complete: {gcs_uri}")
    return gcs_uri


def download_from_gcs(
    bucket_name: str,
    blob_name: str,
    local_path: str
) -> str:
    """
    Download file from Google Cloud Storage.
    
    Args:
        bucket_name: GCS bucket name
        blob_name: Source path in bucket
        local_path: Destination local path
        
    Returns:
        Local file path
        
    Example:
        >>> path = download_from_gcs(
        ...     "my-bucket",
        ...     "data/raw/patients.csv",
        ...     "data/local/patients.csv"
        ... )
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Create local directory if it doesn't exist
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    
    print(f"⬇️  Downloading gs://{bucket_name}/{blob_name} to {local_path}")
    blob.download_to_filename(local_path)
    
    print(f"✅ Download complete: {local_path}")
    return local_path


def list_gcs_files(
    bucket_name: str,
    prefix: Optional[str] = None
) -> list:
    """
    List files in GCS bucket with optional prefix filter.
    
    Args:
        bucket_name: GCS bucket name
        prefix: Filter by prefix (e.g., "data/raw/")
        
    Returns:
        List of blob names
        
    Example:
        >>> files = list_gcs_files("my-bucket", prefix="data/raw/")
        >>> print(files)
        ['data/raw/patients.csv', 'data/raw/encounters.csv']
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    
    blobs = bucket.list_blobs(prefix=prefix)
    files = [blob.name for blob in blobs]
    
    print(f"📁 Found {len(files)} files in gs://{bucket_name}/{prefix or ''}")
    return files


# Example usage
if __name__ == "__main__":
    # Test BigQuery connection
    print("Testing BigQuery connection...")
    
    query = """
    SELECT 
        COUNT(*) as patient_count,
        AVG(EXTRACT(YEAR FROM birth_datetime)) as avg_birth_year
    FROM `bigquery-public-data.cms_synthetic_patient_data_omop.person`
    """
    
    try:
        df = read_from_bigquery(query)
        print("\n📊 Query Results:")
        print(df)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you've authenticated with: gcloud auth application-default login")
