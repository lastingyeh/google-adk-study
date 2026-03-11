# Terraform 設定：Cloud Build 觸發器 (Build Triggers)
# 此檔案定義了 CI/CD 流水線的各種自動化觸發機制

# a. 建立提取請求 (Pull Request, PR) 檢查觸發器
resource "google_cloudbuild_trigger" "pr_checks" {
  name            = "pr-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  description     = "用於 PR 檢查的觸發器"
  service_account = resource.google_service_account.cicd_runner_sa.id

  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    pull_request {
      branch = "main" # 當有 PR 提交到 main 分支時觸發
    }
  }

  filename = ".cloudbuild/pr_checks.yaml"
  included_files = [
    "guarding_agent/**",
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

# b. 建立持續部署 (Continuous Deployment, CD) 流水線觸發器 (Staging 階段)
resource "google_cloudbuild_trigger" "cd_pipeline" {
  name            = "cd-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  service_account = resource.google_service_account.cicd_runner_sa.id
  description     = "用於 CD 流水線的觸發器"

  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
    push {
      branch = "main" # 當程式碼合併到 main 分支時觸發
    }
  }

  filename = ".cloudbuild/staging.yaml"
  included_files = [
    "guarding_agent/**",
    "data_ingestion/**",
    "tests/**",
    "deployment/**",
    "uv.lock"
  ]
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  substitutions = { # 環境變數替換
    _STAGING_PROJECT_ID            = var.staging_project_id
    _LOGS_BUCKET_NAME_STAGING      = resource.google_storage_bucket.logs_data_bucket[var.staging_project_id].name
    _APP_SERVICE_ACCOUNT_STAGING   = google_service_account.app_sa["staging"].email
    _REGION                        = var.region
    _CONTAINER_NAME                = var.project_name
    _ARTIFACT_REGISTRY_REPO_NAME   = resource.google_artifact_registry_repository.repo-artifacts-genai.repository_id
    _GKE_CLUSTER_NAME              = "${var.project_name}-staging"
  }
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]
}

# c. 建立部署至生產環境 (Production) 的觸發器
resource "google_cloudbuild_trigger" "deploy_to_prod_pipeline" {
  name            = "deploy-${var.project_name}"
  project         = var.cicd_runner_project_id
  location        = var.region
  description     = "部署至生產環境的觸發器"
  service_account = resource.google_service_account.cicd_runner_sa.id
  repository_event_config {
    repository = "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}/repositories/${var.repository_name}"
  }
  filename = ".cloudbuild/deploy-to-prod.yaml"
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  approval_config {
    approval_required = true # 需要手動核准才能執行
  }
  substitutions = {
    _PROD_PROJECT_ID             = var.prod_project_id
    _LOGS_BUCKET_NAME_PROD       = resource.google_storage_bucket.logs_data_bucket[var.prod_project_id].name
    _APP_SERVICE_ACCOUNT_PROD    = google_service_account.app_sa["prod"].email
    _REGION                      = var.region
    _CONTAINER_NAME                = var.project_name
    _ARTIFACT_REGISTRY_REPO_NAME   = resource.google_artifact_registry_repository.repo-artifacts-genai.repository_id
    _GKE_CLUSTER_NAME              = "${var.project_name}-prod"
  }
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    google_cloudbuildv2_connection.github_connection,
    google_cloudbuildv2_repository.repo
  ]
}