# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址獲得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱本授權以了解管理權限和限制的特定語言。

/*
## 重點摘要
- **核心概念**：管理 GitHub 儲存庫與 Google Cloud Build 之間的整合連接。
- **關鍵技術**：GitHub Provider, Cloud Build V2 Connection, Secret Manager IAM, Data Sources。
- **重要結論**：支援建立新儲存庫或引用現有儲存庫，並自動配置 Cloud Build 存取 GitHub 所需的憑證權限。
- **行動項目**：確保已在 Secret Manager 中建立 GitHub 個人存取權杖 (PAT)。
*/
provider "github" {
  owner = var.repository_owner
}

# 嘗試獲取現有的 GitHub 儲存庫
data "github_repository" "existing_repo" {
  count = var.create_repository ? 0 : 1
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# 僅在 create_repository 為 true 時建立 GitHub 儲存庫
resource "github_repository" "repo" {
  count       = var.create_repository ? 1 : 0
  name        = var.repository_name
  description = "使用 goo.gle/agent-starter-pack 建立的儲存庫"
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

# 引用由 gcloud CLI 建立的現有 GitHub PAT Secret
data "google_secret_manager_secret" "github_pat" {
  project   = var.cicd_runner_project_id
  secret_id = var.github_pat_secret_id
}

# 獲取 CICD 專案數據，以便用於 Cloud Build 服務帳號
data "google_project" "cicd_project" {
  project_id = var.cicd_runner_project_id
}

# 授予 Cloud Build 服務帳號存取 GitHub PAT Secret 的權限
resource "google_secret_manager_secret_iam_member" "cloudbuild_secret_accessor" {
  project   = var.cicd_runner_project_id
  secret_id = data.google_secret_manager_secret.github_pat.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:service-${data.google_project.cicd_project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services]
}

# 建立 GitHub 連接（手動使用 Terraform 時的備案）
resource "google_cloudbuildv2_connection" "github_connection" {
  count      = var.create_cb_connection ? 0 : 1
  project    = var.cicd_runner_project_id
  location   = var.region
  name       = var.host_connection_name

  github_config {
    app_installation_id = var.github_app_installation_id
    authorizer_credential {
      oauth_token_secret_version = "${data.google_secret_manager_secret.github_pat.id}/versions/latest"
    }
  }
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    resource.google_secret_manager_secret_iam_member.cloudbuild_secret_accessor
  ]
}

# 在 Cloud Build V2 中建立儲存庫資源
resource "google_cloudbuildv2_repository" "repo" {
  project  = var.cicd_runner_project_id
  location = var.region
  name     = var.repository_name

  # 如果已存在連接 ID 則使用它，否則使用新建立的連接
  parent_connection = var.create_cb_connection ? "projects/${var.cicd_runner_project_id}/locations/${var.region}/connections/${var.host_connection_name}" : google_cloudbuildv2_connection.github_connection[0].id
  remote_uri       = "https://github.com/${var.repository_owner}/${var.repository_name}.git"
  depends_on = [
    resource.google_project_service.cicd_services,
    resource.google_project_service.deploy_project_services,
    data.github_repository.existing_repo,
    github_repository.repo,
    google_cloudbuildv2_connection.github_connection,
  ]
}
