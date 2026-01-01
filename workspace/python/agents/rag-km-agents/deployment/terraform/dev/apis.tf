locals {
  # 開發環境需要啟用的 Google Cloud 服務列表
  services = [
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "bigquery.googleapis.com",
    "discoveryengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com"
  ]
}

# 啟用開發環境專案所需的 Google Cloud 服務 API
resource "google_project_service" "services" {
  count              = length(local.services)
  project            = var.dev_project_id
  service            = local.services[count.index]
  disable_on_destroy = false
}

# 為 AI Platform (Vertex AI) 建立專案服務身份
# 這通常用於授權 Google 管理的服務帳號訪問其他資源
resource "google_project_service_identity" "vertex_sa" {
  provider = google-beta
  project = var.dev_project_id
  service = "aiplatform.googleapis.com"
}
