# a. 建立 PR 檢查觸發器 (PR checks trigger)
# 當針對 main 分支發起 Pull Request 時觸發
# 執行 .cloudbuild/pr_checks.yaml 定義的建構步驟
resource "google_cloudbuild_trigger" "pr_checks" {
  name            = "pr-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  description     = "PR 檢查觸發器 (Trigger for PR checks)"
  service_account = resource.google_service_account.cicd_runner_sa.id

  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    pull_request {
      branch = "main"
    }
  }

  filename = ".cloudbuild/pr_checks.yaml"
  # 指定觸發建構的檔案路徑模式
  # 只有當這些路徑下的檔案變更時才會觸發
  included_files = [
    "policy_as_code_agent/**",
    "data_ingestion/**",
    "tests/**",
    "deployment/**",
    "uv.lock",

  ]
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]
}

# b. 建立 CD 流水線觸發器 (CD pipeline trigger)
# 當 main 分支有新的 Push 時觸發
# 執行 .cloudbuild/staging.yaml 定義的建構和部署步驟 (部署到 Staging)
resource "google_cloudbuild_trigger" "cd_pipeline" {
  name            = "cd-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  service_account = resource.google_service_account.cicd_runner_sa.id
  description     = "CD 流水線觸發器 (Trigger for CD pipeline)"

  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    push {
      branch = "main"
    }
  }

  filename = ".cloudbuild/staging.yaml"
  included_files = [
    "policy_as_code_agent/**",
    "data_ingestion/**",
    "tests/**",
    "deployment/**",
    "uv.lock"
  ]
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"

  # 定義建構過程中的變數替換
  # 將 Terraform 變數傳遞給 Cloud Build
  substitutions = {
    _STAGING_PROJECT_ID            = var.staging_project_id
    _LOGS_BUCKET_NAME_STAGING      = resource.google_storage_bucket.logs_data_bucket[var.staging_project_id].name
    _APP_SERVICE_ACCOUNT_STAGING   = google_service_account.app_sa["staging"].email
    _REGION                        = var.region
    _CONTAINER_NAME                = var.project_name
    _ARTIFACT_REGISTRY_REPO_NAME   = resource.google_artifact_registry_repository.repo-artifacts-genai.repository_id
    # 其他 CD Pipeline 替換變數
  }
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]

}

# c. 建立生產環境部署觸發器 (Deploy to production trigger)
# 手動觸發，用於將應用部署到 Production 環境
# 需要審核 (approval_required = true)
resource "google_cloudbuild_trigger" "deploy_to_prod_pipeline" {
  name            = "deploy-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  description     = "生產環境部署觸發器 (Trigger for deployment to production)"
  service_account = resource.google_service_account.cicd_runner_sa.id
  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
  }
  filename = ".cloudbuild/deploy-to-prod.yaml"
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"

  # 設定需要手動批准才能執行
  approval_config {
    approval_required = true
  }

  substitutions = {
    _PROD_PROJECT_ID             = var.prod_project_id
    _LOGS_BUCKET_NAME_PROD       = resource.google_storage_bucket.logs_data_bucket[var.prod_project_id].name
    _APP_SERVICE_ACCOUNT_PROD    = google_service_account.app_sa["prod"].email
    _REGION                      = var.region
    _CONTAINER_NAME              = var.project_name
    _ARTIFACT_REGISTRY_REPO_NAME = resource.google_artifact_registry_repository.repo-artifacts-genai.repository_id
    # 其他 Deploy to Prod Pipeline 替換變數
  }
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]

}
