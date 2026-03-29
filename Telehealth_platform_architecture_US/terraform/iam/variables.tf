variable "project_id" {
  description = "GCP project ID for operational workloads"
  type        = string
}

variable "phi_project_id" {
  description = "GCP project ID for PHI database (isolated)"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}
