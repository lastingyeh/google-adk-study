# Terraform 設定：存儲資源 (Storage)
# 此檔案定義了用於日誌存儲的 Cloud Storage Bucket 以及容器映像檔的 Artifact Registry

provider "google" {
  region                = var.region
  user_project_override = true
}

# 建立用於存放日誌資料的 Cloud Storage Bucket
resource "google_storage_bucket" "logs_data_bucket" {
  for_each                    = toset(local.all_project_ids) # 為所有專案建立
  name                        = "${each.value}-${var.project_name}-logs"
  location                    = var.region
  project                     = each.value
  uniform_bucket_level_access = true # 啟用統一儲存桶層級存取權限
  force_destroy               = true # 允許強制刪除 (即使內含資料)

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 在 CI/CD 專案建立 Artifact Registry 儲存庫
resource "google_artifact_registry_repository" "repo-artifacts-genai" {
  location      = var.region
  repository_id = "${var.project_name}-repo"
  description   = "產生式 AI 應用程式的儲存庫"
  format        = "DOCKER"
  project       = var.cicd_runner_project_id
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
