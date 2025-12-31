# 設定 Google 提供者
# user_project_override = true 確保 API 請求計費歸屬於指定的專案
provider "google" {
  region                = var.region
  user_project_override = true
}

# 建立日誌資料儲存桶
# 為開發環境專案建立一個用於儲存日誌的 GCS Bucket
resource "google_storage_bucket" "logs_data_bucket" {
  name                        = "${var.dev_project_id}-${var.project_name}-logs"
  location                    = var.region
  project                     = var.dev_project_id
  uniform_bucket_level_access = true

  depends_on = [resource.google_project_service.services]
}
