locals {
  # CI/CD 專案需要啟用的 Google Cloud 服務列表
  cicd_services = [
    "cloudbuild.googleapis.com",        # Cloud Build 服務，用於 CI/CD
    "discoveryengine.googleapis.com",   # Discovery Engine API (如果使用 Agent Builder)
    "aiplatform.googleapis.com",        # Vertex AI API
    "serviceusage.googleapis.com",      # Service Usage API，用於啟用其他 API
    "bigquery.googleapis.com",          # BigQuery API，用於數據分析
    "cloudresourcemanager.googleapis.com", # Cloud Resource Manager API
    "cloudtrace.googleapis.com",        # Cloud Trace API，用於分散式追蹤
  ]

  # 部署專案 (生產環境和測試環境) 需要啟用的 Google Cloud 服務列表
  deploy_project_services = [
    "aiplatform.googleapis.com",        # Vertex AI API
    "run.googleapis.com",               # Cloud Run API，用於執行容器化應用
    "discoveryengine.googleapis.com",   # Discovery Engine API
    "cloudresourcemanager.googleapis.com", # Cloud Resource Manager API
    "iam.googleapis.com",               # IAM API，用於權限管理
    "bigquery.googleapis.com",          # BigQuery API
    "serviceusage.googleapis.com",      # Service Usage API
    "logging.googleapis.com",           # Cloud Logging API
    "cloudtrace.googleapis.com",        # Cloud Trace API
  ]

  # 部署環境及其對應的專案 ID 對照表
  deploy_project_ids = {
    prod    = var.prod_project_id      # 生產環境專案 ID
    staging = var.staging_project_id   # 測試環境專案 ID
  }

  # 所有相關專案 ID 的列表，用於迭代處理
  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]

}
