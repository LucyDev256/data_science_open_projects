# BigQuery Datasets and Tables

variable "project_id" {}
variable "region" {}
variable "environment" {}

# Analytics Production Dataset
resource "google_bigquery_dataset" "analytics_prod" {
  dataset_id  = "analytics_${var.environment}"
  project     = var.project_id
  location    = "US"
  description = "De-identified analytics data for telehealth platform"
  
  default_table_expiration_ms = null  # No auto-expiration
  
  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.bigquery_key.id
  }
  
  labels = {
    environment = var.environment
    data_classification = "confidential"
    hipaa_deidentified = "true"
  }
  
  access {
    role          = "OWNER"
    user_by_email = "data-engineering@telehealth.com"
  }
  
  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }
  
  access {
    role          = "READER"
    special_group = "projectReaders"
  }
}

# Compliance Audit Dataset
resource "google_bigquery_dataset" "compliance_audit" {
  dataset_id  = "compliance_audit_${var.environment}"
  project     = var.project_id
  location    = "US"
  description = "Audit logs and compliance reporting"
  
  default_table_expiration_ms = null
  
  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.bigquery_key.id
  }
  
  labels = {
    environment = var.environment
    data_classification = "highly_confidential"
    retention_period = "7_years"
  }
}

# ML Features Dataset
resource "google_bigquery_dataset" "ml_features" {
  dataset_id  = "ml_features_${var.environment}"
  project     = var.project_id
  location    = "US"
  description = "Feature store for ML models"
  
  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.bigquery_key.id
  }
  
  labels = {
    environment = var.environment
    purpose = "machine_learning"
  }
}

# Bronze Layer Dataset (Raw CDC data)
resource "google_bigquery_dataset" "bronze" {
  dataset_id  = "bronze"
  project     = var.project_id
  location    = "US"
  description = "Bronze layer - raw data from CDC pipeline"
  
  labels = {
    layer = "bronze"
  }
}

# Silver Layer Dataset (Cleaned data)
resource "google_bigquery_dataset" "silver" {
  dataset_id  = "silver"
  project     = var.project_id
  location    = "US"
  description = "Silver layer - cleaned and validated data"
  
  labels = {
    layer = "silver"
  }
}

# Gold Layer Dataset (Analytics-ready)
resource "google_bigquery_dataset" "gold" {
  dataset_id  = "gold"
  project     = var.project_id
  location    = "US"
  description = "Gold layer - analytics-ready dimensional models"
  
  labels = {
    layer = "gold"
  }
}

# KMS Key for BigQuery encryption
resource "google_kms_key_ring" "bigquery_keyring" {
  name     = "telehealth-bigquery-keyring"
  location = "us"
  project  = var.project_id
}

resource "google_kms_crypto_key" "bigquery_key" {
  name            = "telehealth-bigquery-key"
  key_ring        = google_kms_key_ring.bigquery_keyring.id
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# PHI Access Audit Table
resource "google_bigquery_table" "phi_access_log" {
  dataset_id = google_bigquery_dataset.compliance_audit.dataset_id
  table_id   = "phi_access_log"
  project    = var.project_id
  
  time_partitioning {
    type  = "DAY"
    field = "accessed_at"
    expiration_ms = 220898880000  # 7 years in milliseconds
  }
  
  clustering = ["user_id", "patient_uuid"]
  
  schema = jsonencode([
    {
      name = "access_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "user_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "patient_uuid"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "accessed_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "access_type"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "ip_address"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "reason"
      type = "STRING"
      mode = "REQUIRED"
    }
  ])
}

# Outputs
output "analytics_dataset_id" {
  value = google_bigquery_dataset.analytics_prod.dataset_id
}

output "compliance_audit_dataset_id" {
  value = google_bigquery_dataset.compliance_audit.dataset_id
}

output "ml_features_dataset_id" {
  value = google_bigquery_dataset.ml_features.dataset_id
}
