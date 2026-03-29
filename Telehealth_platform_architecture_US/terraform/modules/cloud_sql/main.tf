# Cloud SQL PostgreSQL Instances

variable "project_id" {}
variable "phi_project_id" {}
variable "region" {}
variable "environment" {}
variable "vpc_id" {}

# Men's Health Operational Database
resource "google_sql_database_instance" "men_health_db" {
  name             = "telehealth-men-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  
  settings {
    tier              = "db-custom-4-16384"  # 4 vCPU, 16GB RAM
    availability_type = "REGIONAL"  # Multi-zone for HA
    disk_type         = "PD_SSD"
    disk_size         = 100
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_id
      require_ssl     = true
    }
    
    database_flags {
      name  = "cloudsql.logical_decoding"
      value = "on"  # Required for Debezium CDC
    }
    
    database_flags {
      name  = "max_replication_slots"
      value = "10"
    }
    
    database_flags {
      name  = "max_wal_senders"
      value = "10"
    }
    
    maintenance_window {
      day          = 7  # Sunday
      hour         = 3
      update_track = "stable"
    }
    
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
    }
  }
  
  deletion_protection = true
}

resource "google_sql_database" "men_health_database" {
  name     = "telehealth_men_${var.environment}"
  instance = google_sql_database_instance.men_health_db.name
  project  = var.project_id
}

# Women's Health Operational Database
resource "google_sql_database_instance" "women_health_db" {
  name             = "telehealth-women-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  
  settings {
    tier              = "db-custom-4-16384"
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = 100
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:30"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_id
      require_ssl     = true
    }
    
    database_flags {
      name  = "cloudsql.logical_decoding"
      value = "on"
    }
    
    database_flags {
      name  = "max_replication_slots"
      value = "10"
    }
    
    database_flags {
      name  = "max_wal_senders"
      value = "10"
    }
    
    maintenance_window {
      day          = 7
      hour         = 4
      update_track = "stable"
    }
    
    insights_config {
      query_insights_enabled = true
      query_plans_per_minute = 5
    }
  }
  
  deletion_protection = true
}

resource "google_sql_database" "women_health_database" {
  name     = "telehealth_women_${var.environment}"
  instance = google_sql_database_instance.women_health_db.name
  project  = var.project_id
}

# PHI Database (HIPAA-compliant, separate project)
resource "google_sql_database_instance" "phi_db" {
  name             = "telehealth-phi-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.phi_project_id  # Separate project for PHI
  
  settings {
    tier              = "db-custom-2-8192"  # 2 vCPU, 8GB RAM
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = 50
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 90  # 90 days for PHI
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_id
      require_ssl     = true
    }
    
    database_flags {
      name  = "cloudsql.logical_decoding"
      value = "on"
    }
    
    # Enhanced logging for PHI access
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    
    database_flags {
      name  = "log_statement"
      value = "all"  # Log all statements for audit
    }
    
    maintenance_window {
      day          = 7
      hour         = 2
      update_track = "stable"
    }
  }
  
  deletion_protection = true
}

resource "google_sql_database" "phi_database" {
  name     = "telehealth_phi_${var.environment}"
  instance = google_sql_database_instance.phi_db.name
  project  = var.phi_project_id
}

# Shared Resources Database
resource "google_sql_database_instance" "shared_db" {
  name             = "telehealth-shared-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  
  settings {
    tier              = "db-custom-2-8192"
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = 50
    
    backup_configuration {
      enabled                        = true
      start_time                     = "04:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 14
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_id
      require_ssl     = true
    }
  }
  
  deletion_protection = true
}

resource "google_sql_database" "shared_database" {
  name     = "telehealth_shared_${var.environment}"
  instance = google_sql_database_instance.shared_db.name
  project  = var.project_id
}

# Outputs
output "men_db_connection_name" {
  value = google_sql_database_instance.men_health_db.connection_name
}

output "women_db_connection_name" {
  value = google_sql_database_instance.women_health_db.connection_name
}

output "phi_db_connection_name" {
  value = google_sql_database_instance.phi_db.connection_name
}

output "shared_db_connection_name" {
  value = google_sql_database_instance.shared_db.connection_name
}
