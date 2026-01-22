# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址獲得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱本授權以了解管理權限和限制的特定語言。

/*
## 重點摘要
- **核心概念**：為開發 (Dev) 環境配置 Cloud SQL 與 Cloud Run 服務。
- **關鍵技術**：Cloud SQL (Postgres), Cloud Run, Secret Manager, 隨機密碼。
- **重要結論**：開發環境採用與生產環境類似的架構，但關閉了備份功能以節省成本。
- **行動項目**：確認開發環境專案 ID 正確。
*/


# 獲取專案資訊以存取專案編號
data "google_project" "project" {
  project_id = var.dev_project_id
}

# 為資料庫使用者生成隨機密碼
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Cloud SQL 實例
resource "google_sql_database_instance" "session_db" {
  project          = var.dev_project_id
  name             = "${var.project_name}-db-dev"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false

  settings {
    tier = "db-custom-1-3840"

    backup_configuration {
      enabled = false # 開發環境不啟用備份
    }

    # 啟用 IAM 身分驗證
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
  name     = "${var.project_name}" # 使用專案名稱避免衝突
  instance = google_sql_database_instance.session_db.name
}

# Cloud SQL 使用者
resource "google_sql_user" "db_user" {
  project  = var.dev_project_id
  name     = "${var.project_name}"
  instance = google_sql_database_instance.session_db.name
  password = google_secret_manager_secret_version.db_password.secret_data
}

# 將密碼存儲在 Secret Manager 中
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

# Cloud Run 服務
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
      # 掛載卷
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      # 環境變數
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
    # Cloud SQL 卷掛載
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

  # 生命週期塊：防止 Terraform 覆蓋更新後的鏡像
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  depends_on = [
    resource.google_project_service.services,
    google_sql_user.db_user,
    google_secret_manager_secret_version.db_password,
  ]
}
