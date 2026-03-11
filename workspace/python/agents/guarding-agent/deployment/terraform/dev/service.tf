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

# Terraform 設定：開發環境服務與 Kubernetes 資源 (Dev Service & K8s)
# 此檔案定義了開發環境中的基礎架構元件，以及由 Terraform 直接管理的 Kubernetes 資源

# 獲取專案資訊以取得專案編號
data "google_project" "project" {
  project_id = var.dev_project_id
}

# 為資料庫使用者產生隨機密碼
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Cloud SQL 執行個體 (開發環境)
resource "google_sql_database_instance" "session_db" {
  project          = var.dev_project_id
  name             = "${var.project_name}-db-dev"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false

  settings {
    tier = "db-custom-1-3840"
    backup_configuration {
      enabled = false # 開發環境不啟用備份以節省成本
    }
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }
  depends_on = [resource.google_project_service.services]
}

# Cloud SQL 資料庫
resource "google_sql_database" "database" {
  project  = var.dev_project_id
  name     = "${var.project_name}"
  instance = google_sql_database_instance.session_db.name
}

# Cloud SQL 使用者
resource "google_sql_user" "db_user" {
  project  = var.dev_project_id
  name     = "${var.project_name}"
  instance = google_sql_database_instance.session_db.name
  password = google_secret_manager_secret_version.db_password.secret_data
}

# 將密碼儲存於 Secret Manager
resource "google_secret_manager_secret" "db_password" {
  project   = var.dev_project_id
  secret_id = "${var.project_name}-db-password"
  replication {
    auto {}
  }
  depends_on = [resource.google_project_service.services]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# VPC 網路
resource "google_compute_network" "gke_network" {
  name                    = "${var.project_name}-network"
  project                 = var.dev_project_id
  auto_create_subnetworks = false
  depends_on = [resource.google_project_service.services]
}

# GKE 叢集子網
resource "google_compute_subnetwork" "gke_subnet" {
  name          = "${var.project_name}-subnet"
  project       = var.dev_project_id
  region        = var.region
  network       = google_compute_network.gke_network.id
  ip_cidr_range = "10.0.0.0/20"
}

# 防火牆規則：允許內部流量
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.project_name}-allow-internal"
  network = google_compute_network.gke_network.name
  project = var.dev_project_id
  allow { protocol = "tcp" }
  allow { protocol = "udp" }
  allow { protocol = "icmp" }
  source_ranges = ["10.0.0.0/8"]
}

# GKE Autopilot 叢集 (開發環境)
resource "google_container_cluster" "app" {
  name     = "${var.project_name}-dev"
  location = var.region
  project  = var.dev_project_id
  network    = google_compute_network.gke_network.name
  subnetwork = google_compute_subnetwork.gke_subnet.name
  enable_autopilot = true
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
  }
  ip_allocation_policy {}
  deletion_protection = false
  depends_on = [resource.google_project_service.services]
}

# 用於 NAT 閘道的 Cloud Router
resource "google_compute_router" "router" {
  name    = "${var.project_name}-router"
  project = var.dev_project_id
  region  = var.region
  network = google_compute_network.gke_network.id
}

# Cloud NAT
resource "google_compute_router_nat" "nat" {
  name                               = "${var.project_name}-nat"
  project                            = var.dev_project_id
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Artifact Registry 儲存庫
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = var.project_name
  format        = "DOCKER"
  project       = var.dev_project_id
  depends_on = [resource.google_project_service.services]
}

# 允許 Kubernetes 服務帳戶透過 Workload Identity 模擬 GCP 應用程式服務帳戶
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.app_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.dev_project_id}.svc.id.goog[${var.project_name}/${var.project_name}]"
  depends_on = [google_container_cluster.app]
}

# --- Kubernetes 資源 (在開發環境由 Terraform 直接管理) ---

# 建立命名空間
resource "kubernetes_namespace_v1" "app" {
  metadata {
    name = var.project_name
  }
  depends_on = [google_container_cluster.app]
}

# 建立服務帳戶並綁定 GCP 身分
resource "kubernetes_service_account_v1" "app" {
  metadata {
    name      = var.project_name
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    annotations = {
      "iam.gke.io/gcp-service-account" = "${var.project_name}-app@${var.dev_project_id}.iam.gserviceaccount.com"
    }
  }
}

# 建立服務 (LoadBalancer)
resource "kubernetes_service_v1" "app" {
  metadata {
    name      = var.project_name
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels = {
      app = var.project_name
    }
  }
  spec {
    type = "LoadBalancer"
    port {
      port        = 8080
      target_port = 8080
      protocol    = "TCP"
    }
    selector = {
      app = var.project_name
    }
  }
}

# 建立水平 Pod 自動擴縮 (HPA)
resource "kubernetes_horizontal_pod_autoscaler_v2" "app" {
  metadata {
    name      = var.project_name
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels = {
      app = var.project_name
    }
  }
  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = var.project_name
    }
    min_replicas = 2
    max_replicas = 10
    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }
  }
}

# 建立 Pod 中斷預算 (PDB)
resource "kubernetes_pod_disruption_budget_v1" "app" {
  metadata {
    name      = var.project_name
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels = {
      app = var.project_name
    }
  }
  spec {
    min_available = 1
    selector {
      match_labels = {
        app = var.project_name
      }
    }
  }
}

/*
重點摘要：
- 核心概念：在開發環境中，除基礎架構外，連同 Kubernetes 的基本元件也透過 Terraform 一併管理。
- 關鍵技術：GKE Autopilot, Workload Identity, Kubernetes Resources in Terraform.
- 重要結論：這種做法有助於開發人員快速拉起完整環境，並確保開發與部署設定的一致性。
*/
