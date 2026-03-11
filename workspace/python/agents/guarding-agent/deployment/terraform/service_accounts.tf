# Terraform 設定：服務帳戶 (Service Accounts)
# 此檔案定義了 CI/CD 流水線與應用程式代理程式所使用的服務帳戶

# 建立 CI/CD Runner 服務帳戶
resource "google_service_account" "cicd_runner_sa" {
  account_id   = "${var.project_name}-cb" # 帳戶 ID，格式為：專案名稱-cb
  display_name = "CICD Runner SA" # 顯示名稱
  project      = var.cicd_runner_project_id
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立代理程式 (Agent) 服務帳戶
resource "google_service_account" "app_sa" {
  for_each = local.deploy_project_ids # 為 Staging 和 Prod 環境各建立一個

  account_id   = "${var.project_name}-app" # 帳戶 ID，格式為：專案名稱-app
  display_name = "${var.project_name} 代理程式服務帳戶"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

