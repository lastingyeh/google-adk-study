# 建立 CI/CD 執行器服務帳戶
# 該服務帳戶將用於執行 Cloud Build 建置和部署任務
resource "google_service_account" "cicd_runner_sa" {
  account_id   = "${var.project_name}-cb"
  display_name = "CICD Runner SA"
  project      = var.cicd_runner_project_id
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立應用程式代理服務帳戶
# 為每個部署專案 (生產環境和測試環境) 建立對應的服務帳戶
# 該帳戶將被應用程式用於存取 Google Cloud 資源
resource "google_service_account" "app_sa" {
  for_each = local.deploy_project_ids

  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent Service Account"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
