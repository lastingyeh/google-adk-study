locals {
  # 開發環境需要啟用的 Google Cloud 服務列表
  services = [
    "aiplatform.googleapis.com",          # Vertex AI API
    "cloudbuild.googleapis.com",          # Cloud Build API
    "run.googleapis.com",                 # Cloud Run API
    "bigquery.googleapis.com",            # BigQuery API
    "discoveryengine.googleapis.com",     # Discovery Engine API
    "cloudresourcemanager.googleapis.com",# Cloud Resource Manager API
    "iam.googleapis.com",                 # IAM API
    "bigquery.googleapis.com",            # BigQuery API (重複列出，可忽略)
    "serviceusage.googleapis.com",        # Service Usage API
    "logging.googleapis.com",             # Cloud Logging API
    "cloudtrace.googleapis.com",          # Cloud Trace API
    "telemetry.googleapis.com",           # Telemetry API
  ]
}

# 啟用必要的 Google Cloud 服務
# 遍歷 local.services 列表啟用每個服務
resource "google_project_service" "services" {
  count              = length(local.services)
  project            = var.dev_project_id
  service            = local.services[count.index]
  disable_on_destroy = false
}

# 建立 Vertex AI 服務識別 (Service Identity)
# 這對於某些 Vertex AI 功能是必需的
resource "google_project_service_identity" "vertex_sa" {
  provider = google-beta
  project = var.dev_project_id
  service = "aiplatform.googleapis.com"
}
