# Quick Start Guide

## Prerequisites

Before you begin, ensure you have:

- [ ] GCP account with billing enabled
- [ ] Project owner/editor permissions
- [ ] `gcloud` CLI installed and configured
- [ ] Terraform >= 1.0 installed
- [ ] Node.js >= 18 (for Prisma)
- [ ] Python >= 3.9 (for dbt/Airflow)
- [ ] Docker Desktop (for local development)

## Step 1: Clone Repository

```bash
git clone https://github.com/your-org/Telehealth_platform_architecture_US.git
cd Telehealth_platform_architecture_US
```

## Step 2: Configure GCP

```bash
# Authenticate
gcloud auth application-default login

# Set project
export GCP_PROJECT_ID="your-project-id"
export GCP_PHI_PROJECT_ID="your-phi-project-id"
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
gcloud services enable sqladmin.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable composer.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudkms.googleapis.com
```

## Step 3: Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan \
  -var="project_id=$GCP_PROJECT_ID" \
  -var="phi_project_id=$GCP_PHI_PROJECT_ID" \
  -var="environment=prod"

# Apply (this will take 20-30 minutes)
terraform apply \
  -var="project_id=$GCP_PROJECT_ID" \
  -var="phi_project_id=$GCP_PHI_PROJECT_ID" \
  -var="environment=prod"
```

## Step 4: Set Up Databases with Prisma

```bash
cd ../prisma

# Install dependencies
npm install

# Set database URLs (use Cloud SQL Proxy or update connection strings)
export MEN_DATABASE_URL="postgresql://user:pass@localhost:5432/telehealth_men_prod"
export WOMEN_DATABASE_URL="postgresql://user:pass@localhost:5433/telehealth_women_prod"
export PHI_DATABASE_URL="postgresql://user:pass@localhost:5434/telehealth_phi_prod"
export SHARED_DATABASE_URL="postgresql://user:pass@localhost:5435/telehealth_shared_prod"

# Generate Prisma clients
npx prisma generate --schema=men_health/schema.prisma
npx prisma generate --schema=women_health/schema.prisma
npx prisma generate --schema=phi/schema.prisma
npx prisma generate --schema=shared/schema.prisma

# Run migrations
npx prisma migrate deploy --schema=men_health/schema.prisma
npx prisma migrate deploy --schema=women_health/schema.prisma
npx prisma migrate deploy --schema=phi/schema.prisma
npx prisma migrate deploy --schema=shared/schema.prisma
```

## Step 5: Configure Debezium CDC

```bash
cd ../debezium

# Set up Cloud SQL replication user
gcloud sql users create debezium_user \
  --instance=telehealth-men-prod \
  --password=SECURE_PASSWORD

# Enable logical replication on Cloud SQL
# (already configured in Terraform via database flags)

# Deploy Debezium connectors
curl -X POST http://kafka-connect-endpoint:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connectors/men-health-connector.json

curl -X POST http://kafka-connect-endpoint:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connectors/women-health-connector.json
```

## Step 6: Set Up dbt

```bash
cd ../dbt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install dbt-bigquery great-expectations

# Test connection
dbt debug --profiles-dir .

# Install dbt packages
dbt deps

# Run initial load (may take 1-2 hours)
dbt run --full-refresh

# Run tests
dbt test
```

## Step 7: Deploy Airflow DAGs

```bash
cd ../airflow

# Get Composer environment details
gcloud composer environments describe telehealth-composer \
  --location us-central1 \
  --format="value(config.dagGcsPrefix)"

# Upload DAGs
gcloud composer environments storage dags import \
  --environment telehealth-composer \
  --location us-central1 \
  --source dags/

# Trigger manual run
gcloud composer environments run telehealth-composer \
  --location us-central1 \
  dags trigger -- dbt_transformations_pipeline
```

## Step 8: Initialize Great Expectations

```bash
cd ../great_expectations

# Initialize
great_expectations init

# Run checkpoint
great_expectations checkpoint run daily_validation
```

## Step 9: Verify Installation

### Check Database Connectivity
```bash
# Test each database connection
psql $MEN_DATABASE_URL -c "SELECT COUNT(*) FROM products;"
psql $WOMEN_DATABASE_URL -c "SELECT COUNT(*) FROM products;"
psql $PHI_DATABASE_URL -c "SELECT COUNT(*) FROM patient_demographics;"
psql $SHARED_DATABASE_URL -c "SELECT COUNT(*) FROM providers;"
```

### Check CDC Pipeline
```bash
# Verify Kafka topics
kafka-topics --bootstrap-server $KAFKA_BROKER --list | grep telehealth

# Check BigQuery bronze tables
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`$GCP_PROJECT_ID.bronze.bronze_men_products\`"
```

### Check dbt Models
```bash
cd dbt
dbt run --select gold_product_performance
dbt test
```

### Check  Airflow
```bash
# List DAGs
gcloud composer environments run telehealth-composer \
  --location us-central1 \
  dags list

# Check DAG status
gcloud composer environments run telehealth-composer \
  --location us-central1 \
  dags state dbt_transformations_pipeline
```

## Step 10: Access Dashboards

### BigQuery Data
```bash
# Open BigQuery console
open "https://console.cloud.google.com/bigquery?project=$GCP_PROJECT_ID"
```

### Great Expectations Data Docs
```bash
cd great_expectations
great_expectations docs build
# Open uncommitted/data_docs/local_site/index.html
```

### Airflow UI
```bash
# Get Airflow web UI URL
gcloud composer environments describe telehealth-composer \
  --location us-central1 \
  --format="value(config.airflowUri)"
```

## Troubleshooting

### Cloud SQL Connection Issues
```bash
# Start Cloud SQL Proxy
cloud_sql_proxy -instances=$GCP_PROJECT_ID:us-central1:telehealth-men-prod=tcp:5432
```

### Debezium Not Streaming
```bash
# Check connector status
curl http://kafka-connect-endpoint:8083/connectors/men-health-products-connector/status

# Restart connector
curl -X POST http://kafka-connect-endpoint:8083/connectors/men-health-products-connector/restart
```

### dbt Run Failures
```bash
# Check logs
dbt run --debug

# Test specific model
dbt run --select silver_products --full-refresh
```

### Airflow DAG Not Running
```bash
# Check logs in Composer
gcloud composer environments storage logs list \
  --environment telehealth-composer \
  --location us-central1
```

## Next Steps

1. **Load Sample Data**: See [docs/sample_data/LOAD_SAMPLE_DATA.md]
2. **Set Up Monitoring**: See [docs/monitoring/MONITORING_SETUP.md]
3. **Configure Alerts**: See [docs/alerts/ALERT_CONFIGURATION.md]
4. **Deploy BI Dashboards**: See [docs/bi/LOOKER_SETUP.md]
5. **Security Hardening**: See [docs/security/HARDENING_GUIDE.md]

## Support

For help:
- 📚 [Full Documentation](docs/)
- 💬 Slack: #data-engineering
- 📧 Email: data-team@telehealth.com
- 🐛 Issues: GitHub Issues tab
