# Terraform IAM Module
# Manages IAM roles and service accounts for Telehealth Platform

resource "google_service_account" "cloud_sql_client" {
  account_id   = "cloud-sql-client"
  display_name = "Cloud SQL Client Service Account"
  description  = "Service account for applications to connect to Cloud SQL"
  project      = var.project_id
}

resource "google_service_account" "bigquery_writer" {
  account_id   = "bigquery-writer"
  display_name = "BigQuery Writer Service Account"
  description  = "Service account for Debezium/CDC to write to BigQuery"
  project      = var.project_id
}

resource "google_service_account" "dbt_runner" {
  account_id   = "dbt-runner"
  display_name = "dbt Transformation Runner"
  description  = "Service account for dbt to run transformations"
  project      = var.project_id
}

resource "google_service_account" "airflow_composer" {
  account_id   = "airflow-composer"
  display_name = "Cloud Composer/Airflow"
  description  = "Service account for Airflow DAGs"
  project      = var.project_id
}

# PHI Database Access (restricted)
resource "google_service_account" "phi_db_access" {
  account_id   = "phi-db-access"
  display_name = "PHI Database Access (Restricted)"
  description  = "Highly restricted service account for PHI database access"
  project      = var.phi_project_id
}

# IAM Bindings for Cloud SQL

resource "google_project_iam_member" "sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_sql_client.email}"
}

# IAM Bindings for BigQuery

resource "google_project_iam_member" "bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.bigquery_writer.email}"
}

resource "google_project_iam_member" "bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.bigquery_writer.email}"
}

resource "google_project_iam_member" "dbt_bigquery_user" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.dbt_runner.email}"
}

resource "google_project_iam_member" "dbt_bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dbt_runner.email}"
}

# Custom IAM Role for PHI Access (minimal permissions)

resource "google_project_iam_custom_role" "phi_readonly" {
  role_id     = "phiReadOnly"
  title       = "PHI Read-Only Access"
  description = "Minimal read-only access to PHI database for de-identification"
  project     = var.phi_project_id
  permissions = [
    "cloudsql.instances.connect",
    "cloudsql.instances.get"
  ]
}

# Audit Logging Configuration

resource "google_project_iam_audit_config" "phi_audit" {
  project = var.phi_project_id
  service = "cloudsql.googleapis.com"

  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type = "DATA_READ"
  }

  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

resource "google_project_iam_audit_config" "bigquery_audit" {
  project = var.project_id
  service = "bigquery.googleapis.com"

  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type = "DATA_READ"
  }

  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# Workload Identity for GKE (if using Kubernetes)

resource "google_service_account_iam_binding" "workload_identity_binding" {
  service_account_id = google_service_account.cloud_sql_client.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[default/telehealth-api]"
  ]
}

# Outputs

output "cloud_sql_client_email" {
  value       = google_service_account.cloud_sql_client.email
  description = "Email of Cloud SQL client service account"
}

output "bigquery_writer_email" {
  value       = google_service_account.bigquery_writer.email
  description = "Email of BigQuery writer service account"
}

output "dbt_runner_email" {
  value       = google_service_account.dbt_runner.email
  description = "Email of dbt runner service account"
}

output "airflow_composer_email" {
  value       = google_service_account.airflow_composer.email
  description = "Email of Airflow/Composer service account"
}
