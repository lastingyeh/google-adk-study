# 獲取專案資訊以存取專案編號
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

# 建立 Cloud SQL 實例 (PostgreSQL)
# 用於儲存 Session 資料和應用程式狀態
resource "google_sql_database_instance" "session_db" {
  for_each = local.deploy_project_ids

  project          = local.deploy_project_ids[each.key]
  name             = "${var.project_name}-db-${each.key}"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false # 在 Starter Pack 中設為 false 以便於清理，生產環境建議設為 true

  settings {
    tier = "db-custom-1-3840" # 1 vCPU, 3.75 GB RAM

    backup_configuration {
      enabled = true
      start_time = "03:00"
    }

    # 啟用 IAM 驗證
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  depends_on = [google_project_service.deploy_project_services]
}

# 建立 Cloud SQL 資料庫
resource "google_sql_database" "database" {
  for_each = local.deploy_project_ids

  project  = local.deploy_project_ids[each.key]
  name     = "${var.project_name}" # 使用專案名稱作為資料庫名稱，避免與預設 'postgres' 衝突
  instance = google_sql_database_instance.session_db[each.key].name
}

# 建立 Cloud SQL 使用者
resource "google_sql_user" "db_user" {
  for_each = local.deploy_project_ids

  project  = local.deploy_project_ids[each.key]
  name     = "${var.project_name}" # 使用專案名稱作為使用者名稱
  instance = google_sql_database_instance.session_db[each.key].name
  password = random_password.db_password[each.key].result
}

# 將資料庫密碼儲存在 Secret Manager 中
# 安全地管理敏感憑證
resource "google_secret_manager_secret" "db_password" {
  for_each = local.deploy_project_ids

  project   = local.deploy_project_ids[each.key]
  secret_id = "${var.project_name}-db-password"

  replication {
    auto {}
  }

  depends_on = [google_project_service.deploy_project_services]
}

# 建立 Secret 版本 (儲存實際密碼值)
resource "google_secret_manager_secret_version" "db_password" {
  for_each = local.deploy_project_ids

  secret      = google_secret_manager_secret.db_password[each.key].id
  secret_data = random_password.db_password[each.key].result
}

# 部署 Cloud Run 服務 (應用程式本體)
# 包含容器配置、環境變數、Cloud SQL 連線等設定
resource "google_cloud_run_v2_service" "app" {
  for_each = local.deploy_project_ids

  name                = var.project_name
  location            = var.region
  project             = each.value
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"
  labels = {
    "created-by"                  = "adk"
  }

  template {
    containers {
      # 初始部署使用 Hello World 映像檔佔位
      # 實際應用程式映像檔將由 CI/CD 流水線更新
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
        cpu_idle = false
      }
      # 掛載 Cloud SQL Volume
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      # 環境變數設定
      env {
        name  = "INSTANCE_CONNECTION_NAME"
        value = google_sql_database_instance.session_db[each.key].connection_name
      }

      env {
        name = "DB_PASS"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password[each.key].secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "DB_NAME"
        value = "${var.project_name}"
      }

      env {
        name  = "DB_USER"
        value = "${var.project_name}"
      }

      env {
        name  = "LOGS_BUCKET_NAME"
        value = google_storage_bucket.logs_data_bucket[each.value].name
      }

      env {
        name  = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
        value = "NO_CONTENT"
      }
    }

    service_account                = google_service_account.app_sa[each.key].email
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    session_affinity = true
    # 定義 Cloud SQL Volume
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.session_db[each.key].connection_name]
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Lifecycle 區塊：防止 Terraform 覆蓋由 CI/CD 更新的容器映像檔
  # 當 Cloud Build 部署新版本時，這裡的 image 設定會被忽略
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  # 設定依賴關係，避免錯誤
  depends_on = [
    google_project_service.deploy_project_services,
    google_sql_user.db_user,
    google_secret_manager_secret_version.db_password,
  ]
}
