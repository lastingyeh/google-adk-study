# Copyright 2025 Google LLC
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

# ============================================================================
# Cloud Run 服務部署
# ============================================================================
# 此檔案定義 Cloud Run 服務的配置：
# - 為 staging 和 production 環境各建立一個 Cloud Run 服務
# - 配置資源限制（4 CPU, 8GB 記憶體）
# - 設定環境變數（APP_URL, LOGS_BUCKET_NAME, OTEL 設定）
# - 配置自動擴展（最小 1 個，最大 10 個實例）
# - 啟用 session affinity 以維持會話親和性
# - 使用 lifecycle 規則忽略容器映像變更（由 CI/CD 管理）
# ============================================================================

# Get project information to access the project number
data "google_project" "project" {
  for_each = local.deploy_project_ids

  project_id = local.deploy_project_ids[each.key]
}

resource "google_cloud_run_v2_service" "app_staging" {
  name                = var.project_name
  location            = var.region
  project             = var.staging_project_id
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"
  labels = {
    "created-by"                  = "adk"
  }

  template {
    containers {
      # Placeholder, will be replaced by the CI/CD pipeline
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      env {
        name  = "APP_URL"
        value = "https://${var.project_name}-${data.google_project.project["staging"].number}.${var.region}.run.app"
      }
      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
        cpu_idle = false
      }

      env {
        name  = "LOGS_BUCKET_NAME"
        value = google_storage_bucket.logs_data_bucket[var.staging_project_id].name
      }

      env {
        name  = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
        value = "NO_CONTENT"
      }
    }

    service_account                = google_service_account.app_sa["staging"].email
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    session_affinity = true
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # This lifecycle block prevents Terraform from overwriting the container image when it's
  # updated by Cloud Run deployments outside of Terraform (e.g., via CI/CD pipelines)
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  # Make dependencies conditional to avoid errors.
  depends_on = [
    google_project_service.deploy_project_services,
  ]
}

resource "google_cloud_run_v2_service" "app_prod" {
  name                = var.project_name
  location            = var.region
  project             = var.prod_project_id
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"
  labels = {
    "created-by"                  = "adk"
  }

  template {
    containers {
      # Placeholder, will be replaced by the CI/CD pipeline
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      env {
        name  = "APP_URL"
        value = "https://${var.project_name}-${data.google_project.project["prod"].number}.${var.region}.run.app"
      }
      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
        cpu_idle = false
      }

      env {
        name  = "LOGS_BUCKET_NAME"
        value = google_storage_bucket.logs_data_bucket[var.prod_project_id].name
      }

      env {
        name  = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
        value = "NO_CONTENT"
      }
    }

    service_account                = google_service_account.app_sa["prod"].email
    max_instance_request_concurrency = 40

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    session_affinity = true
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # This lifecycle block prevents Terraform from overwriting the container image when it's
  # updated by Cloud Run deployments outside of Terraform (e.g., via CI/CD pipelines)
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  # Make dependencies conditional to avoid errors.
  depends_on = [
    google_project_service.deploy_project_services,
  ]
}
