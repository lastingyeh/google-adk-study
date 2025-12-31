# 設定 Google 提供者
# user_project_override = true 確保 API 請求計費歸屬於指定的專案
provider "google" {
  region                = var.region
  user_project_override = true
}

# 建立日誌資料儲存桶
# 為每個專案 (CI/CD, Prod, Staging) 建立一個用於儲存日誌的 GCS Bucket
resource "google_storage_bucket" "logs_data_bucket" {
  for_each                    = toset(local.all_project_ids)
  name                        = "${each.value}-${var.project_name}-logs"
  location                    = var.region
  project                     = each.value
  uniform_bucket_level_access = true
  force_destroy               = true  # 允許 Terraform 刪除包含物件的儲存桶 (請謹慎使用)

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Artifact Registry 儲存庫
# 用於儲存 Generative AI 應用程式的 Docker 映像檔
# 位於 CI/CD 執行器專案中
resource "google_artifact_registry_repository" "repo-artifacts-genai" {
  location      = var.region
  repository_id = "${var.project_name}-repo"
  description   = "生成式 AI 應用程式的儲存庫"
  format        = "DOCKER"
  project       = var.cicd_runner_project_id
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
