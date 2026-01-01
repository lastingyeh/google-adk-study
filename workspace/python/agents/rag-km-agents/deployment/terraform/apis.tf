# 啟用 CI/CD 執行專案所需的 Google Cloud 服務 API
# 這些服務定義在 locals.tf 的 cicd_services 列表中
resource "google_project_service" "cicd_services" {
  count              = length(local.cicd_services)
  project            = var.cicd_runner_project_id
  service            = local.cicd_services[count.index]
  disable_on_destroy = false
}

# 啟用部署專案 (Prod 和 Staging) 所需的 Google Cloud 服務 API
# 使用 setproduct 交叉組合專案 ID 和服務列表，確保所有環境都啟用必要的 API
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

# 為 CI/CD 執行專案啟用 Cloud Resource Manager API
# 這是一個關鍵的 API，用於管理專案資源和權限
resource "google_project_service" "cicd_cloud_resource_manager_api" {
  project            = var.cicd_runner_project_id
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}
