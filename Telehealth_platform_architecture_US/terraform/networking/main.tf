# Terraform Networking Module
# VPC, subnets, firewall rules, and private service connections

# VPC Network

resource "google_compute_network" "telehealth_vpc" {
  name                    = "telehealth-vpc-${var.environment}"
  project                 = var.project_id
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  description             = "VPC network for Telehealth Platform ${var.environment}"
}

# Subnets

resource "google_compute_subnetwork" "application_subnet" {
  name          = "application-subnet-${var.environment}"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.telehealth_vpc.id
  ip_cidr_range = "10.0.1.0/24"
  
  description = "Subnet for application servers (GKE, Cloud Run)"
  
  private_ip_google_access = true
  
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

resource "google_compute_subnetwork" "database_subnet" {
  name          = "database-subnet-${var.environment}"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.telehealth_vpc.id
  ip_cidr_range = "10.0.2.0/24"
  
  description = "Subnet for Cloud SQL databases"
  
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "dataflow_subnet" {
  name          = "dataflow-subnet-${var.environment}"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.telehealth_vpc.id
  ip_cidr_range = "10.0.3.0/24"
  
  description = "Subnet for Dataflow jobs"
  
  private_ip_google_access = true
}

# PHI VPC (Isolated)

resource "google_compute_network" "phi_vpc" {
  name                    = "phi-isolated-vpc"
  project                 = var.phi_project_id
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  description             = "Isolated VPC for PHI database (HIPAA compliance)"
}

resource "google_compute_subnetwork" "phi_subnet" {
  name          = "phi-database-subnet"
  project       = var.phi_project_id
  region        = var.region
  network       = google_compute_network.phi_vpc.id
  ip_cidr_range = "192.168.1.0/24"
  
  description = "Isolated subnet for PHI database"
  
  private_ip_google_access = true
  
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 1.0  # 100% sampling for PHI
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Private Service Connection for Cloud SQL

resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address-${var.environment}"
  project       = var.project_id
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.telehealth_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.telehealth_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# PHI VPC Private Connection

resource "google_compute_global_address" "phi_private_ip" {
  name          = "phi-private-ip"
  project       = var.phi_project_id
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.phi_vpc.id
}

resource "google_service_networking_connection" "phi_private_connection" {
  network                 = google_compute_network.phi_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.phi_private_ip.name]
}

# Firewall Rules

# Allow internal traffic within VPC
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal-${var.environment}"
  project = var.project_id
  network = google_compute_network.telehealth_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/16"]
  description   = "Allow all internal traffic within VPC"
}

# Allow Cloud SQL Proxy connections
resource "google_compute_firewall" "allow_sql_proxy" {
  name    = "allow-cloud-sql-proxy-${var.environment}"
  project = var.project_id
  network = google_compute_network.telehealth_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["5432"]  # PostgreSQL
  }

  source_ranges = [
    google_compute_subnetwork.application_subnet.ip_cidr_range,
    google_compute_subnetwork.dataflow_subnet.ip_cidr_range
  ]
  
  target_tags = ["cloud-sql"]
  description = "Allow PostgreSQL connections from application and Dataflow subnets"
}

# Deny all external access to PHI VPC
resource "google_compute_firewall" "deny_phi_external" {
  name     = "deny-all-external-phi"
  project  = var.phi_project_id
  network  = google_compute_network.phi_vpc.name
  priority = 1000

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]
  description   = "Deny all external access to PHI VPC (HIPAA compliance)"
}

# Allow only specific internal access to PHI
resource "google_compute_firewall" "allow_phi_internal" {
  name     = "allow-phi-internal-restricted"
  project  = var.phi_project_id
  network  = google_compute_network.phi_vpc.name
  priority = 900

  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }

  source_ranges = ["192.168.1.0/24"]
  target_tags   = ["phi-database"]
  description   = "Allow PostgreSQL only within PHI subnet"
}

# Cloud NAT for outbound internet access (without exposing instances)

resource "google_compute_router" "nat_router" {
  name    = "nat-router-${var.environment}"
  project = var.project_id
  region  = var.region
  network = google_compute_network.telehealth_vpc.id
}

resource "google_compute_router_nat" "nat_gateway" {
  name                               = "nat-gateway-${var.environment}"
  project                            = var.project_id
  router                             = google_compute_router.nat_router.name
  region                             = google_compute_router.nat_router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# VPC Peering (if needed between projects)

# Note: For production, keep PHI VPC completely isolated
# Only use VPC peering if absolutely necessary with strict controls

# Outputs

output "vpc_id" {
  value       = google_compute_network.telehealth_vpc.id
  description = "VPC network ID"
}

output "vpc_name" {
  value       = google_compute_network.telehealth_vpc.name
  description = "VPC network name"
}

output "application_subnet_name" {
  value       = google_compute_subnetwork.application_subnet.name
  description = "Application subnet name"
}

output "database_subnet_name" {
  value       = google_compute_subnetwork.database_subnet.name
  description = "Database subnet name"
}

output "phi_vpc_id" {
  value       = google_compute_network.phi_vpc.id
  description = "PHI VPC network ID (isolated)"
}

output "phi_subnet_name" {
  value       = google_compute_subnetwork.phi_subnet.name
  description = "PHI database subnet name"
}
