locals {
  # CI/CD Runner 專案需要啟用的 API 列表
  # 包含 Cloud Build, AI Platform (Vertex AI), BigQuery 等
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

  # 部署目標專案 (Staging 和 Production) 需要啟用的 API 列表
  # 包含 Cloud Run, Cloud SQL, Secret Manager, Logging 等
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

  # 環境名稱與 Project ID 的對應關係
  # 用於在 for_each 迴圈中迭代部署專案
  deploy_project_ids = {
    prod    = var.prod_project_id
    staging = var.staging_project_id
  }

  # 所有參與的專案 ID 列表
  # 包含 CI/CD Runner, Production 和 Staging
  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]

}
