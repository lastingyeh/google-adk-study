# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

provider "github" {
  owner = var.repository_owner
}

# 嘗試獲取現有 Repo
# Try to get existing repo
data "github_repository" "existing_repo" {
  count = var.create_repository ? 0 : 1
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# 僅在 create_repository 為 true 時建立 GitHub Repo
# Only create GitHub repo if create_repository is true
resource "github_repository" "repo" {
  count       = var.create_repository ? 1 : 0
  name        = var.repository_name
  description = "由 goo.gle/agent-starter-pack 建立的儲存庫 (Repository created with goo.gle/agent-starter-pack)"
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
# Reference existing GitHub PAT secret created by gcloud CLI
data "google_secret_manager_secret" "github_pat" {
  project   = var.cicd_runner_project_id
  secret_id = var.github_pat_secret_id
}

# 獲取 Cloud Build 服務帳戶的 CICD 專案資料
# Get CICD project data for Cloud Build service account
data "google_project" "cicd_project" {
  project_id = var.cicd_runner_project_id
}

# 授予 Cloud Build 服務帳戶存取 GitHub PAT Secret 的權限
# Grant Cloud Build service account access to GitHub PAT secret
resource "google_secret_manager_secret_iam_member" "cloudbuild_secret_accessor" {
  project   = var.cicd_runner_project_id
  secret_id = data.google_secret_manager_secret.github_pat.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:service-${data.google_project.cicd_project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services]
}

# 建立 GitHub 連線 (手動 Terraform 使用時的備案)
# Create the GitHub connection (fallback for manual Terraform usage)
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


resource "google_cloudbuildv2_repository" "repo" {
  project  = var.cicd_runner_project_id
  location = var.region
  name     = var.repository_name

  # 如果連線已存在則使用，否則使用新建立的連線 ID
  # Use existing connection ID when it exists, otherwise use the created connection
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

# 重點摘要
# - **核心概念**：GitHub 整合
# - **關鍵技術**：GitHub Provider, Cloud Build Connection, Secret Manager
# - **重要結論**：負責設定 GitHub Repository (可選擇新建或使用現有)、設定 Cloud Build 與 GitHub 的連線，並管理 GitHub PAT (Personal Access Token) 的存取權限。
# - **行動項目**：無
