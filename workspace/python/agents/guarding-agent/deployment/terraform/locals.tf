# Terraform 設定：本地變數 (Locals)
# 此檔案定義了在 Terraform 設定中重複使用的常數與集合

locals {
  # CI/CD 執行專案需要啟用的服務列表
  cicd_services = [
    "cloudbuild.googleapis.com",
    "aiplatform.googleapis.com",
    "serviceusage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
    "sqladmin.googleapis.com",
  ]

  # 部署目標專案 (Staging/Prod) 務必啟用的服務列表
  deploy_project_services = [
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com",
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

  # 部署目標專案 ID 對照表
  deploy_project_ids = {
    prod    = var.prod_project_id
    staging = var.staging_project_id
  }

  # 所有相關專案 ID 列表
  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]
}
