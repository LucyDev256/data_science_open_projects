"""
Airflow DAG: External Integrations Batch Processing
Handles batch ingestion from EMR/EHR, labs, pharmacy partners, etc.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.task_group import TaskGroup
import requests
import json

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email': ['data-alerts@telehealth.com'],
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'external_integrations_batch',
    default_args=default_args,
    description='Batch ingestion from external partners',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['integration', 'batch', 'external'],
)

# Lab Results Integration (Quest, LabCorp)
def fetch_lab_results(**context):
    """Fetch lab results from partner APIs"""
    execution_date = context['ds']
    
    lab_providers = ['quest', 'labcorp']
    results = []
    
    for provider in lab_providers:
        # API call to lab provider
        response = requests.get(
            f"https://api.{provider}.com/v1/results",
            headers={"Authorization": f"Bearer {context['var']['value'][provider + '_api_key']}"},
            params={"date": execution_date}
        )
        
        if response.status_code == 200:
            results.extend(response.json()['results'])
        else:
            raise Exception(f"Failed to fetch from {provider}: {response.status_code}")
    
    # Store to GCS
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket('telehealth-external-data')
    blob = bucket.blob(f'lab_results/{execution_date}/results.json')
    blob.upload_from_string(json.dumps(results))
    
    return f'gs://telehealth-external-data/lab_results/{execution_date}/results.json'

fetch_labs = PythonOperator(
    task_id='fetch_lab_results',
    python_callable=fetch_lab_results,
    dag=dag,
)

load_labs_to_bq = GCSToBigQueryOperator(
    task_id='load_lab_results_to_bigquery',
    bucket='telehealth-external-data',
    source_objects=['lab_results/{{ ds }}/results.json'],
    destination_project_dataset_table='bronze.external_lab_results',
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_APPEND',
    autodetect=True,
    dag=dag,
)

# Pharmacy Partner Integration
def fetch_pharmacy_updates(**context):
    """Fetch prescription fulfillment updates from pharmacy partners"""
    execution_date = context['ds']
    
    # Fetch from compounding pharmacy API
    response = requests.get(
        "https://api.compounding-pharmacy.com/v1/fulfillment",
        headers={"X-API-Key": context['var']['value']['pharmacy_api_key']},
        params={
            "date": execution_date,
            "status": "shipped,delivered"
        }
    )
    
    if response.status_code == 200:
        updates = response.json()['fulfillment_updates']
        
        # Store to GCS
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket('telehealth-external-data')
        blob = bucket.blob(f'pharmacy_updates/{execution_date}/updates.json')
        blob.upload_from_string(json.dumps(updates))
        
        return f'gs://telehealth-external-data/pharmacy_updates/{execution_date}/updates.json'
    else:
        raise Exception(f"Failed to fetch pharmacy updates: {response.status_code}")

fetch_pharmacy = PythonOperator(
    task_id='fetch_pharmacy_updates',
    python_callable=fetch_pharmacy_updates,
    dag=dag,
)

# Shipping Integration (FedEx, UPS, USPS)
def fetch_shipping_tracking(**context):
    """Fetch shipping tracking updates"""
    execution_date = context['ds']
    
    # Query for orders with tracking numbers
    from google.cloud import bigquery
    client = bigquery.Client()
    
    query = """
        SELECT DISTINCT shipping_tracking_number, carrier
        FROM `telehealth-prod-project.bronze.bronze_men_orders`
        WHERE status = 'SHIPPED'
          AND delivered_at IS NULL
          AND shipping_tracking_number IS NOT NULL
        UNION ALL
        SELECT DISTINCT shipping_tracking_number, carrier
        FROM `telehealth-prod-project.bronze.bronze_women_orders`
        WHERE status = 'SHIPPED'
          AND delivered_at IS NULL
          AND shipping_tracking_number IS NOT NULL
    """
    
    tracking_numbers = list(client.query(query).result())
    
    updates = []
    for row in tracking_numbers:
        tracking_number = row.shipping_tracking_number
        carrier = row.carrier
        
        # Call carrier API (example for FedEx)
        if carrier == 'FEDEX':
            response = requests.get(
                f"https://api.fedex.com/track/v1/trackingnumbers",
                headers={"Authorization": f"Bearer {context['var']['value']['fedex_token']}"},
                params={"tracking_number": tracking_number}
            )
            
            if response.status_code == 200:
                updates.append(response.json())
    
    # Store updates
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket('telehealth-external-data')
    blob = bucket.blob(f'shipping_tracking/{execution_date}/tracking.json')
    blob.upload_from_string(json.dumps(updates))
    
    return len(updates)

fetch_shipping = PythonOperator(
    task_id='fetch_shipping_tracking',
    python_callable=fetch_shipping_tracking,
    dag=dag,
)

# Payment Reconciliation (Stripe)
def fetch_payment_data(**context):
    """Fetch payment and refund data from Stripe"""
    execution_date = context['ds']
    
    import stripe
    stripe.api_key = context['var']['value']['stripe_secret_key']
    
    # Fetch payments from previous day
    from datetime import datetime, timedelta
    start_date = datetime.strptime(execution_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    
    charges = stripe.Charge.list(
        created={'gte': int(start_date.timestamp()), 'lt': int(end_date.timestamp())},
        limit=100
    )
    
    # Store to GCS
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket('telehealth-external-data')
    blob = bucket.blob(f'stripe_payments/{execution_date}/charges.json')
    blob.upload_from_string(json.dumps([c.to_dict() for c in charges.data]))
    
    return len(charges.data)

fetch_payments = PythonOperator(
    task_id='fetch_stripe_payments',
    python_callable=fetch_payment_data,
    dag=dag,
)

# Task dependencies
[fetch_labs, fetch_pharmacy, fetch_shipping, fetch_payments]

fetch_labs >> load_labs_to_bq
