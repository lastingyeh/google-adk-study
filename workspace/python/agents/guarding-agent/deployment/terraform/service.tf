# Terraform 設定：服務組件 (Services)
# 此檔案定義了代理程式所需的各種核心基礎架構元件，包括資料庫、網路與 GKE 叢集

# 獲取專案資訊以取得專案編號
data "google_project" "project" {
  for_each = local.deploy_project_ids
  project_id = local.deploy_project_ids[each.key]
}

# 為資料庫使用者產生隨機密碼
resource "random_password" "db_password" {
  for_each = local.deploy_project_ids
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Cloud SQL 執行個體 (PostgreSQL)
resource "google_sql_database_instance" "session_db" {
  for_each = local.deploy_project_ids
  project          = local.deploy_project_ids[each.key]
  name             = "${var.project_name}-db-${each.key}"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false # 為方便 starter pack 拆除，設為 false

  settings {
    tier = "db-custom-1-3840"
    backup_configuration {
      enabled = true
      start_time = "03:00"
    }
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on" # 啟用 IAM 驗證
    }
  }
  depends_on = [google_project_service.deploy_project_services]
}

# Cloud SQL 資料庫
resource "google_sql_database" "database" {
  for_each = local.deploy_project_ids
  project  = local.deploy_project_ids[each.key]
  name     = "${var.project_name}"
  instance = google_sql_database_instance.session_db[each.key].name
}

# Cloud SQL 使用者
resource "google_sql_user" "db_user" {
  for_each = local.deploy_project_ids
  project  = local.deploy_project_ids[each.key]
  name     = "${var.project_name}"
  instance = google_sql_database_instance.session_db[each.key].name
  password = random_password.db_password[each.key].result
}

# 將密碼儲存於 Secret Manager
resource "google_secret_manager_secret" "db_password" {
  for_each = local.deploy_project_ids
  project   = local.deploy_project_ids[each.key]
  secret_id = "${var.project_name}-db-password"
  replication {
    auto {}
  }
  depends_on = [google_project_service.deploy_project_services]
}

resource "google_secret_manager_secret_version" "db_password" {
  for_each = local.deploy_project_ids
  secret      = google_secret_manager_secret.db_password[each.key].id
  secret_data = random_password.db_password[each.key].result
}

# VPC 網路
resource "google_compute_network" "gke_network" {
  for_each = local.deploy_project_ids
  name                    = "${var.project_name}-network"
  project                 = each.value
  auto_create_subnetworks = false
  depends_on = [google_project_service.deploy_project_services]
}

# GKE 叢集子網
resource "google_compute_subnetwork" "gke_subnet" {
  for_each = local.deploy_project_ids
  name          = "${var.project_name}-subnet"
  project       = each.value
  region        = var.region
  network       = google_compute_network.gke_network[each.key].id
  ip_cidr_range = "10.0.0.0/20"
}

# 防火牆規則：允許內部流量
resource "google_compute_firewall" "allow_internal" {
  for_each = local.deploy_project_ids
  name    = "${var.project_name}-allow-internal"
  network = google_compute_network.gke_network[each.key].name
  project = each.value
  allow { protocol = "tcp" }
  allow { protocol = "udp" }
  allow { protocol = "icmp" }
  source_ranges = ["10.0.0.0/8"]
}

# GKE Autopilot 叢集
resource "google_container_cluster" "app" {
  for_each = local.deploy_project_ids
  name     = "${var.project_name}-${each.key}"
  location = var.region
  project  = each.value
  network    = google_compute_network.gke_network[each.key].name
  subnetwork = google_compute_subnetwork.gke_subnet[each.key].name
  enable_autopilot = true # 啟用 Autopilot 模式

  private_cluster_config {
    enable_private_nodes    = true # 使用私有節點
    enable_private_endpoint = false
  }
  ip_allocation_policy {}
  deletion_protection = false
  depends_on = [google_project_service.deploy_project_services]
}

# 用於 NAT 閘道的 Cloud Router
resource "google_compute_router" "router" {
  for_each = local.deploy_project_ids
  name    = "${var.project_name}-router"
  project = each.value
  region  = var.region
  network = google_compute_network.gke_network[each.key].id
}

# Cloud NAT：讓私有 GKE 節點能存取外部網路
resource "google_compute_router_nat" "nat" {
  for_each = local.deploy_project_ids
  name                               = "${var.project_name}-nat"
  project                            = each.value
  router                             = google_compute_router.router[each.key].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# 用於儲存容器映像檔的 Artifact Registry
resource "google_artifact_registry_repository" "docker_repo" {
  for_each = local.deploy_project_ids
  location      = var.region
  repository_id = var.project_name
  format        = "DOCKER"
  project       = each.value
  depends_on = [google_project_service.deploy_project_services]
}
