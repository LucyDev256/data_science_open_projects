"""
Airflow DAG: dbt Transformations Pipeline
Orchestrates dbt runs for bronze -> silver -> gold transformations
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.utils.task_group import TaskGroup

# Default arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email': ['data-alerts@telehealth.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'dbt_transformations_pipeline',
    default_args=default_args,
    description='Run dbt transformations: bronze -> silver -> gold',
    schedule_interval='0 */4 * * *',  # Every 4 hours
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['dbt', 'transformations', 'etl'],
)

# DBT project path
DBT_PROJECT_DIR = '/opt/airflow/dbt'
DBT_PROFILES_DIR = '/opt/airflow/dbt'

# Helper function for dbt commands
def dbt_command(command, select=None):
    cmd = f"cd {DBT_PROJECT_DIR} && dbt {command} --profiles-dir {DBT_PROFILES_DIR} --target prod"
    if select:
        cmd += f" --select {select}"
    return cmd

# Start task
start = BashOperator(
    task_id='start_pipeline',
    bash_command='echo "Starting dbt transformations pipeline"',
    dag=dag,
)

# Pre-flight checks
with TaskGroup('preflight_checks', dag=dag) as preflight:
    check_bronze_data = BigQueryCheckOperator(
        task_id='check_bronze_data_exists',
        sql="""
            SELECT COUNT(*) > 0 
            FROM `telehealth-prod-project.bronze.bronze_men_products`
            WHERE DATE(updated_at) = CURRENT_DATE()
        """,
        use_legacy_sql=False,
    )
    
    check_dbt_deps = BashOperator(
        task_id='install_dbt_deps',
        bash_command=dbt_command('deps'),
    )

# Bronze layer (validation only - data comes from CDC)
with TaskGroup('bronze_layer', dag=dag) as bronze:
    validate_bronze = BashOperator(
        task_id='validate_bronze_data',
        bash_command=dbt_command('test', select='tag:bronze'),
    )

# Silver layer transformations
with TaskGroup('silver_layer', dag=dag) as silver:
    run_silver_pharmaceutical = BashOperator(
        task_id='transform_pharmaceutical',
        bash_command=dbt_command('run', select='silver.pharmaceutical'),
    )
    
    run_silver_clinical = BashOperator(
        task_id='transform_clinical',
        bash_command=dbt_command('run', select='silver.clinical'),
    )
    
    run_silver_operational = BashOperator(
        task_id='transform_operational',
        bash_command=dbt_command('run', select='silver.operational'),
    )
    
    run_silver_customer = BashOperator(
        task_id='transform_customer',
        bash_command=dbt_command('run', select='silver.customer'),
    )
    
    test_silver = BashOperator(
        task_id='test_silver_data',
        bash_command=dbt_command('test', select='tag:silver'),
    )
    
    # Dependencies within silver layer
    [run_silver_pharmaceutical, run_silver_clinical, 
     run_silver_operational, run_silver_customer] >> test_silver

# Gold layer transformations
with TaskGroup('gold_layer', dag=dag) as gold:
    run_gold_dimensions = BashOperator(
        task_id='build_dimensions',
        bash_command=dbt_command('run', select='gold.dimensions'),
    )
    
    run_gold_facts = BashOperator(
        task_id='build_facts',
        bash_command=dbt_command('run', select='gold.facts'),
    )
    
    run_gold_aggregates = BashOperator(
        task_id='build_aggregates',
        bash_command=dbt_command('run', select='gold.aggregates'),
    )
    
    test_gold = BashOperator(
        task_id='test_gold_data',
        bash_command=dbt_command('test', select='tag:gold'),
    )
    
    # Dependencies within gold layer
    run_gold_dimensions >> [run_gold_facts, run_gold_aggregates] >> test_gold

# Data quality validation
validate_data_quality = BashOperator(
    task_id='validate_data_quality',
    bash_command='cd /opt/airflow/great_expectations && great_expectations checkpoint run daily_validation',
    dag=dag,
)

# Generate documentation
generate_docs = BashOperator(
    task_id='generate_dbt_docs',
    bash_command=dbt_command('docs generate'),
    dag=dag,
)

# Success notification
success_notification = SlackWebhookOperator(
    task_id='notify_success',
    http_conn_id='slack_data_alerts',
    message="""
    ✅ dbt Transformations Pipeline Completed Successfully
    
    Execution Date: {{ ds }}
    Duration: {{ (ti.end_date - ti.start_date).total_seconds() / 60 }} minutes
    
    All bronze, silver, and gold layers updated.
    """,
    channel='#data-pipeline-alerts',
    dag=dag,
)

# Build pipeline dependencies
start >> preflight >> bronze >> silver >> gold >> validate_data_quality >> generate_docs >> success_notification

# Failure callback
def notify_failure(context):
    """Send Slack notification on DAG failure"""
    slack_msg = f"""
    ❌ dbt Transformations Pipeline FAILED
    
    Task: {context.get('task_instance').task_id}
    Execution Date: {context.get('ds')}
    Log URL: {context.get('task_instance').log_url}
    """
    
    SlackWebhookOperator(
        task_id='slack_failure_notification',
        http_conn_id='slack_data_alerts',
        message=slack_msg,
        channel='#data-pipeline-alerts',
    ).execute(context=context)

dag.on_failure_callback = notify_failure
