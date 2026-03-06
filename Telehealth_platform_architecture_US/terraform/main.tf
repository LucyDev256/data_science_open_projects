# Terraform configuration for Telehealth Platform Infrastructure
# Provider: Google Cloud Platform

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "telehealth-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "phi_project_id" {
  description = "Separate GCP Project ID for PHI database (HIPAA compliance)"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Modules
module "networking" {
  source = "./modules/networking"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
}

module "cloud_sql" {
  source = "./modules/cloud_sql"
  
  project_id     = var.project_id
  phi_project_id = var.phi_project_id
  region         = var.region
  environment    = var.environment
  vpc_id         = module.networking.vpc_id
}

module "bigquery" {
  source = "./modules/bigquery"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
}

module "iam" {
  source = "./modules/iam"
  
  project_id     = var.project_id
  phi_project_id = var.phi_project_id
  environment    = var.environment
}

module "composer" {
  source = "./modules/composer"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  vpc_id      = module.networking.vpc_id
  subnet_id   = module.networking.subnet_id
}

# Outputs
output "cloud_sql_men_connection" {
  value     = module.cloud_sql.men_db_connection_name
  sensitive = true
}

output "cloud_sql_women_connection" {
  value     = module.cloud_sql.women_db_connection_name
  sensitive = true
}

output "cloud_sql_phi_connection" {
  value     = module.cloud_sql.phi_db_connection_name
  sensitive = true
}

output "bigquery_analytics_dataset" {
  value = module.bigquery.analytics_dataset_id
}

output "composer_airflow_uri" {
  value = module.composer.airflow_uri
}
