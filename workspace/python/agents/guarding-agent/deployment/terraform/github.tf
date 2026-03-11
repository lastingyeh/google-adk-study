# Terraform 設定：GitHub 整合 (GitHub Integration)
# 此檔案定義了與 GitHub 儲存庫的連線及 Cloud Build 整合設定

provider "github" {
  owner = var.repository_owner # GitHub 帳號或組織名稱
}

# 嘗試獲取現有的儲存庫資訊
data "github_repository" "existing_repo" {
  count = var.create_repository ? 0 : 1
  full_name = "${var.repository_owner}/${var.repository_name}"
}

# 僅在 create_repository 為 true 時建立新的 GitHub 儲存庫
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

# 引用現有的 GitHub PAT (個人訪問令牌) 密鑰
data "google_secret_manager_secret" "github_pat" {
  project   = var.cicd_runner_project_id
  secret_id = var.github_pat_secret_id
}

# 獲取 CICD 專案資料以取得 Cloud Build 服務帳戶資訊
data "google_project" "cicd_project" {
  project_id = var.cicd_runner_project_id
}

# 授予 Cloud Build 服務帳戶存取 GitHub PAT 密鑰的權限
resource "google_secret_manager_secret_iam_member" "cloudbuild_secret_accessor" {
  project   = var.cicd_runner_project_id
  secret_id = data.google_secret_manager_secret.github_pat.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:service-${data.google_project.cicd_project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
  depends_on = [resource.google_project_service.cicd_services]
}

# 建立 Cloud Build 的 GitHub 連線
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

# 將 GitHub 儲存庫註冊到 Cloud Build 連線中
resource "google_cloudbuildv2_repository" "repo" {
  project  = var.cicd_runner_project_id
  location = var.region
  name     = var.repository_name

  # 使用現有連線或新建立的連線
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