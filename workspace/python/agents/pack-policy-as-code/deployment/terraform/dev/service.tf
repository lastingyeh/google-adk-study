
# 獲取專案資訊以存取專案編號
data "google_project" "project" {
  project_id = var.dev_project_id
}

# 為資料庫使用者產生隨機密碼
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# 建立 Cloud SQL 實例 (Dev 環境)
resource "google_sql_database_instance" "session_db" {
  project          = var.dev_project_id
  name             = "${var.project_name}-db-dev"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false

  settings {
    tier = "db-custom-1-3840"

    backup_configuration {
      enabled = false # 開發環境不啟用自動備份
    }

    # 啟用 IAM 驗證
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  depends_on = [resource.google_project_service.services]
}

# 建立 Cloud SQL 資料庫
resource "google_sql_database" "database" {
  project  = var.dev_project_id
  name     = "${var.project_name}" # 使用專案名稱作為資料庫名稱
  instance = google_sql_database_instance.session_db.name
}

# 建立 Cloud SQL 使用者
resource "google_sql_user" "db_user" {
  project  = var.dev_project_id
  name     = "${var.project_name}" # 使用專案名稱作為使用者名稱
  instance = google_sql_database_instance.session_db.name
  password = google_secret_manager_secret_version.db_password.secret_data
}

# 將資料庫密碼儲存在 Secret Manager 中
resource "google_secret_manager_secret" "db_password" {
  project   = var.dev_project_id
  secret_id = "${var.project_name}-db-password"

  replication {
    auto {}
  }

  depends_on = [resource.google_project_service.services]
}

# 建立 Secret 版本 (儲存實際密碼值)
resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}


# 部署 Cloud Run 服務 (Dev 環境)
resource "google_cloud_run_v2_service" "app" {
  name                = var.project_name
  location            = var.region
  project             = var.dev_project_id
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"
  labels = {
    "created-by"                  = "adk"
  }

  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
      }
      # 掛載 Cloud SQL Volume
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      # 環境變數設定
      env {
        name  = "INSTANCE_CONNECTION_NAME"
        value = google_sql_database_instance.session_db.connection_name
      }

      env {
        name = "DB_PASS"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
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
        value = google_storage_bucket.logs_data_bucket.name
      }

      env {
        name  = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
        value = "NO_CONTENT"
      }
    }

    service_account = google_service_account.app_sa.email
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    session_affinity = true
    # Cloud SQL volume
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.session_db.connection_name]
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Lifecycle 區塊：防止 Terraform 覆蓋由外部更新的容器映像檔
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  # 設定依賴關係
  depends_on = [
    resource.google_project_service.services,
    google_sql_user.db_user,
    google_secret_manager_secret_version.db_password,
  ]
}
