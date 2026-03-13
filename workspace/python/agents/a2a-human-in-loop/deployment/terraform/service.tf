# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Get project information to access the project number
data "google_project" "project" {
  for_each = local.deploy_project_ids

  project_id = local.deploy_project_ids[each.key]
}

# VPC Network
resource "google_compute_network" "gke_network" {
  for_each = local.deploy_project_ids

  name                    = "${var.project_name}-network"
  project                 = each.value
  auto_create_subnetworks = false

  depends_on = [google_project_service.deploy_project_services]
}

# Subnet for GKE cluster
resource "google_compute_subnetwork" "gke_subnet" {
  for_each = local.deploy_project_ids

  name          = "${var.project_name}-subnet"
  project       = each.value
  region        = var.region
  network       = google_compute_network.gke_network[each.key].id
  ip_cidr_range = "10.0.0.0/20"
}

# Firewall rule to allow internal traffic (metrics-server, pod-to-pod, etc.)
resource "google_compute_firewall" "allow_internal" {
  for_each = local.deploy_project_ids

  name    = "${var.project_name}-allow-internal"
  network = google_compute_network.gke_network[each.key].name
  project = each.value

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/8"]
}

# GKE Autopilot Cluster
resource "google_container_cluster" "app" {
  for_each = local.deploy_project_ids

  name     = "${var.project_name}-${each.key}"
  location = var.region
  project  = each.value

  network    = google_compute_network.gke_network[each.key].name
  subnetwork = google_compute_subnetwork.gke_subnet[each.key].name

  # Enable Autopilot mode
  enable_autopilot = true

  # Use private nodes (no external IPs) for security and org policy compliance
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
  }

  ip_allocation_policy {
    # Let GKE auto-assign secondary ranges for pods and services
  }

  deletion_protection = false

  # Make dependencies conditional to avoid errors.
  depends_on = [
    google_project_service.deploy_project_services,
  ]
}

# Cloud Router for NAT gateway
resource "google_compute_router" "router" {
  for_each = local.deploy_project_ids

  name    = "${var.project_name}-router"
  project = each.value
  region  = var.region
  network = google_compute_network.gke_network[each.key].id
}

# Cloud NAT for private GKE nodes to access the internet
resource "google_compute_router_nat" "nat" {
  for_each = local.deploy_project_ids

  name                               = "${var.project_name}-nat"
  project                            = each.value
  router                             = google_compute_router.router[each.key].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "docker_repo" {
  for_each = local.deploy_project_ids

  location      = var.region
  repository_id = var.project_name
  format        = "DOCKER"
  project       = each.value

  depends_on = [google_project_service.deploy_project_services]
}
