# Terraform 設定：啟用 Google Cloud API 服務
# 此檔案定義了專案中需要啟用的各種 Google Cloud 服務介面 (API)

# 為 CI/CD 執行專案啟用相關服務
resource "google_project_service" "cicd_services" {
  count              = length(local.cicd_services)
  project            = var.cicd_runner_project_id
  service            = local.cicd_services[count.index]
  disable_on_destroy = false # 銷毀資源時不禁用服務，以防影響其他資源
}

# 為部署目標專案啟用必要的服務
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
# 這是管理專案資源所必需的 API
resource "google_project_service" "cicd_cloud_resource_manager_api" {
  project            = var.cicd_runner_project_id
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}
