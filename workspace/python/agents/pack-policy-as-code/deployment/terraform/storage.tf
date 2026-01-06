provider "google" {
  region = var.region
  user_project_override = true
}

# 建立 Cloud Storage Bucket 用於儲存日誌
# 為每個專案 (CI/CD, Staging, Production) 建立一個對應的 Bucket
# 用於收集 Agent 運行時的遙測資料和日誌
resource "google_storage_bucket" "logs_data_bucket" {
  for_each                    = toset(local.all_project_ids)
  name                        = "${each.value}-${var.project_name}-logs"
  location                    = var.region
  project                     = each.value
  uniform_bucket_level_access = true
  force_destroy               = true # 允許在 Bucket 非空時刪除 (開發環境便利設定)

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Artifact Registry 儲存庫
# 位於 CI/CD Runner 專案，用於儲存 Docker 映像檔
# 這是應用程式容器映像檔的集中儲存位置
resource "google_artifact_registry_repository" "repo-artifacts-genai" {
  location      = var.region
  repository_id = "${var.project_name}-repo"
  description   = "Generative AI 應用程式的容器儲存庫"
  format        = "DOCKER"
  project       = var.cicd_runner_project_id
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
