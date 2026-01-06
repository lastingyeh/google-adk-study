

locals {
  # Dev 環境需要啟用的 Google Cloud 服務列表
  # 包含 AI Platform, Cloud Run, BigQuery, Discovery Engine 等
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

# 啟用 Dev 專案所需的服務 API
resource "google_project_service" "services" {
  count              = length(local.services)
  project            = var.dev_project_id
  service            = local.services[count.index]
  disable_on_destroy = false
}

# 建立 Vertex AI 的 Service Identity
# 用於讓 Vertex AI 服務代理存取專案中的其他資源
resource "google_project_service_identity" "vertex_sa" {
  provider = google-beta
  project = var.dev_project_id
  service = "aiplatform.googleapis.com"
}
