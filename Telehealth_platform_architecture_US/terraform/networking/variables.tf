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
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs for network monitoring"
  type        = bool
  default     = true
}

variable "phi_flow_log_sampling" {
  description = "Flow log sampling rate for PHI VPC (1.0 = 100%)"
  type        = number
  default     = 1.0
}
