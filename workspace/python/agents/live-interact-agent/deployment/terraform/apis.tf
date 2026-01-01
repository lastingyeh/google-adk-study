# 為 CI/CD 執行器專案啟用必要的服務
# 這些服務定義在 locals.tf 檔案中的 local.cicd_services 變數
resource "google_project_service" "cicd_services" {
  count              = length(local.cicd_services)
  project            = var.cicd_runner_project_id
  service            = local.cicd_services[count.index]
  disable_on_destroy = false
}

# 為部署專案啟用必要的服務
# 使用 setproduct 函式組合部署專案 ID 和服務列表，為每個組合建立服務啟用資源
resource "google_project_service" "deploy_project_services" {
  for_each = {
    for pair in setproduct(keys(local.deploy_project_ids), local.deploy_project_services) :
    "${pair[0]}_${replace(pair[1], ".", "_")}" => {
      project = local.deploy_project_ids[pair[0]]
      service = pair[1]
    }
  }
  project            = each.value.project
  service            = each.value.service
  disable_on_destroy = false
}

# 為 CI/CD 執行器專案啟用 Cloud Resource Manager API
# 這對於管理 Google Cloud 資源是必需的
resource "google_project_service" "cicd_cloud_resource_manager_api" {
  project            = var.cicd_runner_project_id
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}
