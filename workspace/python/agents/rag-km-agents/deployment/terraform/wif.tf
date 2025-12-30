# 獲取 CI/CD 專案資訊
# 用於構建 Workload Identity 資源的完整名稱
data "google_project" "cicd_project" {
  project_id = var.cicd_runner_project_id
}

# 授予 GitHub Actions 身份 Workload Identity 使用者角色
# 允許 GitHub Actions 工作流使用 Workload Identity Pool
resource "google_service_account_iam_member" "github_oidc_access" {
  service_account_id = resource.google_service_account.cicd_runner_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${data.google_project.cicd_project.number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.github_pool.workload_identity_pool_id}/attribute.repository/${var.repository_owner}/${var.repository_name}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 允許 GitHub Actions 身份模擬 CI/CD Runner 服務帳號
# 這是實現 "Keyless" 身份驗證的關鍵，GitHub Actions 將扮演此服務帳號執行操作
resource "google_service_account_iam_member" "github_sa_impersonation" {
  service_account_id = resource.google_service_account.cicd_runner_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "principalSet://iam.googleapis.com/projects/${data.google_project.cicd_project.number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.github_pool.workload_identity_pool_id}/attribute.repository/${var.repository_owner}/${var.repository_name}"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 GitHub Actions 用的 Workload Identity Pool
# 管理外部身份 (GitHub) 與 Google Cloud 身份的映射
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "${var.project_name}-pool"
  project                   = var.cicd_runner_project_id
  display_name              = "GitHub Actions Pool"
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 GitHub OIDC Provider
# 設定 GitHub 作為 OpenID Connect 提供者
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_provider_id = "${var.project_name}-oidc"
  project                            = var.cicd_runner_project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  display_name                       = "GitHub OIDC Provider"
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
  attribute_mapping = {
    "google.subject"         = "assertion.sub"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
  }
  # 限制僅允許特定倉庫的 Actions 進行身份驗證
  attribute_condition = "attribute.repository == '${var.repository_owner}/${var.repository_name}'"
  depends_on          = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
