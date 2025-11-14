#!/bin/bash

# Setup Google Cloud Platform for Healthcare Analytics Project
# This script configures GCP resources for PySpark processing

set -e  # Exit on error

echo "🚀 Setting up GCP for Healthcare Analytics Project"
echo "=================================================="

# Configuration (CHANGE THESE)
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
BUCKET_NAME="${PROJECT_ID}-healthcare-data"
DATASET_NAME="healthcare_processed"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI found"

# Set project
echo ""
echo "📌 Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo "🔧 Enabling required APIs..."
gcloud services enable dataproc.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable compute.googleapis.com

echo "✅ APIs enabled"

# Create GCS bucket
echo ""
echo "📦 Creating Cloud Storage bucket: $BUCKET_NAME"
if gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
    echo "⚠️  Bucket already exists"
else
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "✅ Bucket created"
fi

# Create bucket folders
echo ""
echo "📁 Creating bucket folders..."
gsutil mkdir -p gs://$BUCKET_NAME/data/raw
gsutil mkdir -p gs://$BUCKET_NAME/data/processed
gsutil mkdir -p gs://$BUCKET_NAME/models
gsutil mkdir -p gs://$BUCKET_NAME/checkpoints
gsutil mkdir -p gs://$BUCKET_NAME/logs
gsutil mkdir -p gs://$BUCKET_NAME/temp

echo "✅ Bucket structure created"

# Create BigQuery dataset
echo ""
echo "📊 Creating BigQuery dataset: $DATASET_NAME"
if bq ls -d $PROJECT_ID:$DATASET_NAME &> /dev/null; then
    echo "⚠️  Dataset already exists"
else
    bq mk --location=US $DATASET_NAME
    echo "✅ Dataset created"
fi

# Test BigQuery access to public dataset
echo ""
echo "🔍 Testing BigQuery access to Synthea data..."
bq query --use_legacy_sql=false --format=pretty \
    'SELECT COUNT(*) as patient_count 
     FROM `bigquery-public-data.cms_synthetic_patient_data_omop.person` 
     LIMIT 1'

echo "✅ BigQuery access verified"

# Summary
echo ""
echo "=================================================="
echo "✅ GCP Setup Complete!"
echo "=================================================="
echo ""
echo "📋 Resources Created:"
echo "   • Project: $PROJECT_ID"
echo "   • Region: $REGION"
echo "   • GCS Bucket: gs://$BUCKET_NAME"
echo "   • BigQuery Dataset: $DATASET_NAME"
echo ""
echo "📝 Next Steps:"
echo "   1. Update config/gcp_config.yaml with your project ID"
echo "   2. Run: pip install -r requirements.txt"
echo "   3. Authenticate: gcloud auth application-default login"
echo "   4. Test with: jupyter notebook notebooks/01_data_exploration.ipynb"
echo ""
echo "🚀 Ready to run PySpark jobs on GCP!"
