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
- **核心概念**：部署核心服務元件，包括 Cloud SQL 資料庫與 Cloud Run 應用程式服務。
- **關鍵技術**：Cloud SQL (PostgreSQL), Cloud Run V2, Secret Manager, 隨機密碼生成, 掛載 Cloud SQL 卷。
- **重要結論**：採用 PostgreSQL 15 作為對話會話存儲，並使用 Cloud Run 託管代理程式應用，兩者皆支援跨環境 (Staging/Prod) 部署。
- **行動項目**：在生產環境中考慮啟用 `deletion_protection` 以增加安全性。
*/

# 獲取專案資訊以存取專案編號
data "google_project" "project" {
  for_each = local.deploy_project_ids

  project_id = local.deploy_project_ids[each.key]
}

# 為資料庫使用者生成隨機密碼
resource "random_password" "db_password" {
  for_each = local.deploy_project_ids

  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Cloud SQL 實例
resource "google_sql_database_instance" "session_db" {
  for_each = local.deploy_project_ids

  project          = local.deploy_project_ids[each.key]
  name             = "${var.project_name}-db-${each.key}"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false # 為了方便範例專案拆除，設為 false

  settings {
    tier = "db-custom-1-3840"

    backup_configuration {
      enabled = true
      start_time = "03:00"
    }

    # 啟用 IAM 身分驗證
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  depends_on = [google_project_service.deploy_project_services]
}

# Cloud SQL 資料庫
resource "google_sql_database" "database" {
  for_each = local.deploy_project_ids

  project  = local.deploy_project_ids[each.key]
  name     = "${var.project_name}" # 使用專案名稱作為資料庫名稱，避免與預設的 'postgres' 衝突
  instance = google_sql_database_instance.session_db[each.key].name
}

# Cloud SQL 使用者
resource "google_sql_user" "db_user" {
  for_each = local.deploy_project_ids

  project  = local.deploy_project_ids[each.key]
  name     = "${var.project_name}" # 使用專案名稱作為使用者名稱
  instance = google_sql_database_instance.session_db[each.key].name
  password = random_password.db_password[each.key].result
}

# 將密碼存儲在 Secret Manager 中
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

# Cloud Run 服務
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
      # 佔位符，將由 CI/CD 流程替換為實際鏡像
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
        cpu_idle = false
      }
      # 掛載卷
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      # 環境變數
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
    # Cloud SQL 卷掛載
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

  # 生命週期塊：防止 Terraform 在 CI/CD 流程更新鏡像後將其覆蓋回佔位符
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  # 設定依賴項，確保按順序建立
  depends_on = [
    google_project_service.deploy_project_services,
    google_sql_user.db_user,
    google_secret_manager_secret_version.db_password,
  ]
}
