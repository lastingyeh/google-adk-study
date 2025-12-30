provider "github" {
  owner = var.repository_owner
}

# 嘗試獲取現有的 GitHub 倉庫資料
# 當不創建新倉庫時使用此區塊
data "github_repository" "existing_repo" {
  count = var.create_repository ? 0 : 1
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# 僅在 create_repository 為 true 時創建新的 GitHub 倉庫
resource "github_repository" "repo" {
  count       = var.create_repository ? 1 : 0
  name        = var.repository_name
  description = "Repository created with goo.gle/agent-starter-pack"
  visibility  = "private"

  has_issues      = true
  has_wiki        = false
  has_projects    = false
  has_downloads   = false

  allow_merge_commit = true
  allow_squash_merge = true
  allow_rebase_merge = true

  auto_init = false
}

# 設定 GitHub Actions 變數: GCP 專案編號
resource "github_actions_variable" "gcp_project_number" {
  repository    = var.repository_name
  variable_name = "GCP_PROJECT_NUMBER"
  value         = data.google_project.cicd_project.number
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions Secret: Workload Identity Federation Pool ID
# 用於 GitHub Actions 與 GCP 進行身份驗證
resource "github_actions_secret" "wif_pool_id" {
  repository      = var.repository_name
  secret_name     = "WIF_POOL_ID"
  plaintext_value = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  depends_on      = [github_repository.repo, data.github_repository.existing_repo]
}

# 設定 GitHub Actions Secret: Workload Identity Federation Provider ID
resource "github_actions_secret" "wif_provider_id" {
  repository      = var.repository_name
  secret_name     = "WIF_PROVIDER_ID"
  plaintext_value = google_iam_workload_identity_pool_provider.github_provider.workload_identity_pool_provider_id
  depends_on      = [github_repository.repo, data.github_repository.existing_repo]
}

# 設定 GitHub Actions Secret: CICD 執行用的 GCP 服務帳號 Email
resource "github_actions_secret" "gcp_service_account" {
  repository      = var.repository_name
  secret_name     = "GCP_SERVICE_ACCOUNT"
  plaintext_value = google_service_account.cicd_runner_sa.email
  depends_on      = [github_repository.repo, data.github_repository.existing_repo]
}

# 設定 GitHub Actions 變數: Staging 專案 ID
resource "github_actions_variable" "staging_project_id" {
  repository    = var.repository_name
  variable_name = "STAGING_PROJECT_ID"
  value         = var.staging_project_id
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Production 專案 ID
resource "github_actions_variable" "prod_project_id" {
  repository    = var.repository_name
  variable_name = "PROD_PROJECT_ID"
  value         = var.prod_project_id
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: 區域 (Region)
resource "github_actions_variable" "region" {
  repository    = var.repository_name
  variable_name = "REGION"
  value         = var.region
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: CICD 專案 ID
resource "github_actions_variable" "cicd_project_id" {
  repository    = var.repository_name
  variable_name = "CICD_PROJECT_ID"
  value         = var.cicd_runner_project_id
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Staging 應用服務帳號 Email
resource "github_actions_variable" "app_sa_email_staging" {
  repository    = var.repository_name
  variable_name = "APP_SA_EMAIL_STAGING"
  value         = google_service_account.app_sa["staging"].email
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Production 應用服務帳號 Email
resource "github_actions_variable" "app_sa_email_prod" {
  repository    = var.repository_name
  variable_name = "APP_SA_EMAIL_PROD"
  value         = google_service_account.app_sa["prod"].email
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Staging 應用服務帳號 (重複變數以兼容不同命名習慣)
resource "github_actions_variable" "app_service_account_staging" {
  repository    = var.repository_name
  variable_name = "APP_SERVICE_ACCOUNT_STAGING"
  value         = google_service_account.app_sa["staging"].email
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Production 應用服務帳號 (重複變數以兼容不同命名習慣)
resource "github_actions_variable" "app_service_account_prod" {
  repository    = var.repository_name
  variable_name = "APP_SERVICE_ACCOUNT_PROD"
  value         = google_service_account.app_sa["prod"].email
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Staging 日誌 Bucket 名稱
resource "github_actions_variable" "logs_bucket_name_staging" {
  repository    = var.repository_name
  variable_name = "LOGS_BUCKET_NAME_STAGING"
  value         = google_storage_bucket.logs_data_bucket[var.staging_project_id].name
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Production 日誌 Bucket 名稱
resource "github_actions_variable" "logs_bucket_name_prod" {
  repository    = var.repository_name
  variable_name = "LOGS_BUCKET_NAME_PROD"
  value         = google_storage_bucket.logs_data_bucket[var.prod_project_id].name
  depends_on    = [github_repository.repo]
}


# 設定 GitHub Actions 變數: 容器名稱 (預設為專案名稱)
resource "github_actions_variable" "container_name" {
  repository    = var.repository_name
  variable_name = "CONTAINER_NAME"
  value         = var.project_name
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Artifact Registry 倉庫名稱
resource "github_actions_variable" "artifact_registry_repo_name" {
  repository    = var.repository_name
  variable_name = "ARTIFACT_REGISTRY_REPO_NAME"
  value         = google_artifact_registry_repository.repo-artifacts-genai.repository_id
  depends_on    = [github_repository.repo]
}


# 設定 GitHub Actions 變數: Staging Pipeline GCS 根路徑
resource "github_actions_variable" "pipeline_gcs_root_staging" {
  repository    = var.repository_name
  variable_name = "PIPELINE_GCS_ROOT_STAGING"
  value         = "gs://${google_storage_bucket.data_ingestion_pipeline_gcs_root["staging"].name}"
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Production Pipeline GCS 根路徑
resource "github_actions_variable" "pipeline_gcs_root_prod" {
  repository    = var.repository_name
  variable_name = "PIPELINE_GCS_ROOT_PROD"
  value         = "gs://${google_storage_bucket.data_ingestion_pipeline_gcs_root["prod"].name}"
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Staging Pipeline 服務帳號 Email
resource "github_actions_variable" "pipeline_sa_email_staging" {
  repository    = var.repository_name
  variable_name = "PIPELINE_SA_EMAIL_STAGING"
  value         = google_service_account.vertexai_pipeline_app_sa["staging"].email
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Production Pipeline 服務帳號 Email
resource "github_actions_variable" "pipeline_sa_email_prod" {
  repository    = var.repository_name
  variable_name = "PIPELINE_SA_EMAIL_PROD"
  value         = google_service_account.vertexai_pipeline_app_sa["prod"].email
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Pipeline 名稱
resource "github_actions_variable" "pipeline_name" {
  repository    = var.repository_name
  variable_name = "PIPELINE_NAME"
  value         = var.project_name
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Pipeline 排程 (Cron 表達式)
resource "github_actions_variable" "pipeline_cron_schedule" {
  repository    = var.repository_name
  variable_name = "PIPELINE_CRON_SCHEDULE"
  value         = var.pipeline_cron_schedule
  depends_on    = [github_repository.repo]
}


# 設定 GitHub Actions 變數: Staging Discovery Engine Data Store ID
resource "github_actions_variable" "data_store_id_staging" {
  repository    = var.repository_name
  variable_name = "DATA_STORE_ID_STAGING"
  value         = google_discovery_engine_data_store.data_store_staging.data_store_id
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Production Discovery Engine Data Store ID
resource "github_actions_variable" "data_store_id_prod" {
  repository    = var.repository_name
  variable_name = "DATA_STORE_ID_PROD"
  value         = google_discovery_engine_data_store.data_store_prod.data_store_id
  depends_on    = [github_repository.repo]
}

# 設定 GitHub Actions 變數: Data Store 區域
resource "github_actions_variable" "data_store_region" {
  repository    = var.repository_name
  variable_name = "DATA_STORE_REGION"
  value         = var.data_store_region
  depends_on    = [github_repository.repo]
}


# 設定 GitHub 倉庫環境: Production
# 用於管理生產環境的部署策略
resource "github_repository_environment" "production_environment" {
  repository  = var.repository_name
  environment = "production"
  depends_on  = [github_repository.repo, data.github_repository.existing_repo]

  deployment_branch_policy {
    protected_branches     = false
    custom_branch_policies = true
  }
}
