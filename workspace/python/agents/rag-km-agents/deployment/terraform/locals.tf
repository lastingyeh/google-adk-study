locals {
  # CI/CD 專案需要啟用的服務列表
  # 包含 Cloud Build, Discovery Engine, AI Platform, BigQuery 等
  cicd_services = [
    "cloudbuild.googleapis.com",
    "discoveryengine.googleapis.com",
    "aiplatform.googleapis.com",
    "serviceusage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "sqladmin.googleapis.com",
  ]

  # 部署專案 (Prod/Staging) 需要啟用的服務列表
  # 包含 Cloud Run, AI Platform, Discovery Engine 等核心服務
  deploy_project_services = [
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "discoveryengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com"
  ]

  # 部署專案 ID 對照表 (Prod, Staging)
  # 用於 Terraform 的 for_each 迴圈來遍歷不同環境
  deploy_project_ids = {
    prod    = var.prod_project_id
    staging = var.staging_project_id
  }

  # 所有相關專案 ID 列表
  # 用於需要對所有專案進行統一操作的資源 (如 Bucket 創建)
  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]

}
