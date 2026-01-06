# 建立 CI/CD Runner Service Account
# 此帳戶將用於執行 Cloud Build 建構和部署任務
resource "google_service_account" "cicd_runner_sa" {
  account_id   = "${var.project_name}-cb"
  display_name = "CI/CD Runner 服務帳戶"
  project      = var.cicd_runner_project_id
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Agent 應用程式 Service Account
# 每個部署環境 (Staging, Production) 都會有一個獨立的 App SA
# 用於運行 Cloud Run 服務並存取所需的 Google Cloud 資源
resource "google_service_account" "app_sa" {
  for_each = local.deploy_project_ids

  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent 服務帳戶"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
