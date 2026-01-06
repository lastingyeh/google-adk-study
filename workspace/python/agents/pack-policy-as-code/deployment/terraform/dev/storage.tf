provider "google" {
  region = var.region
  user_project_override = true
}

# 建立 Dev 環境的 Log Storage Bucket
# 用於儲存開發測試期間的遙測資料和應用程式日誌
resource "google_storage_bucket" "logs_data_bucket" {
  name                        = "${var.dev_project_id}-${var.project_name}-logs"
  location                    = var.region
  project                     = var.dev_project_id
  uniform_bucket_level_access = true

  depends_on = [resource.google_project_service.services]
}
