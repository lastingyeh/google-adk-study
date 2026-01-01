# GitHub 提供者設定
provider "github" {
  owner = var.repository_owner
}

# 嘗試獲取現有的 GitHub 儲存庫資訊
# 當 create_repository 為 false 時執行
data "github_repository" "existing_repo" {
  count = var.create_repository ? 0 : 1
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# 僅當 create_repository 為 true 時建立新的 GitHub 儲存庫
resource "github_repository" "repo" {
  count       = var.create_repository ? 1 : 0
  name        = var.repository_name
  description = "由 goo.gle/agent-starter-pack 建立的儲存庫"
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



# 引用由 gcloud CLI 建立的現有 GitHub PAT (Personal Access Token) Secret
data "google_secret_manager_secret" "github_pat" {
  project   = var.cicd_runner_project_id
  secret_id = var.github_pat_secret_id
}

# 獲取 CI/CD 專案資訊，用於 Cloud Build 服務帳戶
data "google_project" "cicd_project" {
  project_id = var.cicd_runner_project_id
}

# 授權 Cloud Build 服務帳戶存取 GitHub PAT Secret
# 這是為了讓 Cloud Build 能夠與 GitHub 互動
resource "google_secret_manager_secret_iam_member" "cloudbuild_secret_accessor" {
  project   = var.cicd_runner_project_id
  secret_id = data.google_secret_manager_secret.github_pat.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:service-${data.google_project.cicd_project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services]
}

# 建立 GitHub 連線 (手動使用 Terraform 時的備案)
# 用於連接 Cloud Build 和 GitHub
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

# 在 Cloud Build 中建立儲存庫資源
# 將 Cloud Build 連接到 GitHub 儲存庫
resource "google_cloudbuildv2_repository" "repo" {
  project  = var.cicd_runner_project_id
  location = var.region
  name     = var.repository_name

  # 如果連線已存在則使用現有的，否則使用新建立的連線 ID
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
