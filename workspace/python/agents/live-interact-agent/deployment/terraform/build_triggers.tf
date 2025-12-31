# a. 建立 PR 檢查觸發器
# 當對主分支 (main) 建立拉取請求 (PR) 時觸發
# 包含在應用程式、資料擷取、測試或部署目錄中的變更
resource "google_cloudbuild_trigger" "pr_checks" {
  name            = "pr-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  description     = "PR 檢查的觸發器"
  service_account = resource.google_service_account.cicd_runner_sa.id

  # 設定儲存庫事件設定，監聽指定儲存庫的拉取請求
  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    pull_request {
      branch = "main"
    }
  }

  # 指定 Cloud Build 設定檔路徑
  filename = ".cloudbuild/pr_checks.yaml"
  # 指定包含的檔案路徑，只有這些路徑下的變更才會觸發建置
  included_files = [
    "app/**",
    "data_ingestion/**",
    "tests/**",
    "deployment/**",
    "uv.lock",

  ]
  # 設定建置日誌包含狀態資訊
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"

  # 確保相關資源先建立
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]
}

# b. 建立 CD 管線觸發器
# 當推送到主分支 (main) 時觸發，部署到測試環境 (Staging)
resource "google_cloudbuild_trigger" "cd_pipeline" {
  name            = "cd-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  service_account = resource.google_service_account.cicd_runner_sa.id
  description     = "CD 管線的觸發器"

  # 設定儲存庫事件設定，監聽指定儲存庫的推送事件
  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    push {
      branch = "main"
    }
  }

  filename = ".cloudbuild/staging.yaml"
  included_files = [
    "app/**",
    "data_ingestion/**",
    "tests/**",
    "deployment/**",
    "uv.lock"
  ]
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"

  # 設定替換變數，將 Terraform 變數傳遞給 Cloud Build
  substitutions = {
    _STAGING_PROJECT_ID            = var.staging_project_id
    _LOGS_BUCKET_NAME_STAGING      = resource.google_storage_bucket.logs_data_bucket[var.staging_project_id].name
    _APP_SERVICE_ACCOUNT_STAGING   = google_service_account.app_sa["staging"].email
    _REGION                        = var.region
    _CONTAINER_NAME                = var.project_name
    _ARTIFACT_REGISTRY_REPO_NAME   = resource.google_artifact_registry_repository.repo-artifacts-genai.repository_id
    # 您的其他 CD 管線替換變數
  }
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]

}

# c. 建立生產環境部署觸發器
# 需要手動核准才能執行
resource "google_cloudbuild_trigger" "deploy_to_prod_pipeline" {
  name            = "deploy-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  description     = "部署到生產環境的觸發器"
  service_account = resource.google_service_account.cicd_runner_sa.id
  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
  }
  filename = ".cloudbuild/deploy-to-prod.yaml"
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"

  # 設定需要核准
  approval_config {
    approval_required = true
  }

  # 設定替換變數，將 Terraform 變數傳遞給 Cloud Build
  substitutions = {
    _PROD_PROJECT_ID             = var.prod_project_id
    _LOGS_BUCKET_NAME_PROD       = resource.google_storage_bucket.logs_data_bucket[var.prod_project_id].name
    _APP_SERVICE_ACCOUNT_PROD    = google_service_account.app_sa["prod"].email
    _REGION                      = var.region
    _CONTAINER_NAME              = var.project_name
    _ARTIFACT_REGISTRY_REPO_NAME = resource.google_artifact_registry_repository.repo-artifacts-genai.repository_id
    # 您的其他部署到生產環境管線替換變數
  }
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]

}
