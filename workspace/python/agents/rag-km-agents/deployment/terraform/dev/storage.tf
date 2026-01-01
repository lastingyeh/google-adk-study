provider "google" {
  region = var.region
  user_project_override = true
}

# 建立日誌資料儲存桶 (Logs Data Bucket)
# 用於存儲開發環境的應用程式日誌和遙測資料
resource "google_storage_bucket" "logs_data_bucket" {
  name                        = "${var.dev_project_id}-${var.project_name}-logs"
  location                    = var.region
  project                     = var.dev_project_id
  uniform_bucket_level_access = true

  depends_on = [resource.google_project_service.services]
}


# 建立資料攝取 Pipeline 的 GCS 根目錄
# 用於 Vertex AI Pipeline 執行過程中的暫存和工件存儲
resource "google_storage_bucket" "data_ingestion_PIPELINE_GCS_ROOT" {
  name                        = "${var.dev_project_id}-${var.project_name}-rag"
  location                    = var.region
  project                     = var.dev_project_id
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [resource.google_project_service.services]
}


# 建立開發環境的 Discovery Engine Data Store
# 用於存儲和索引知識庫內容 (RAG)
resource "google_discovery_engine_data_store" "data_store_dev" {
  location                    = var.data_store_region
  project                     = var.dev_project_id
  data_store_id               = "${var.project_name}-datastore"
  display_name                = "${var.project_name}-datastore"
  industry_vertical           = "GENERIC"
  content_config              = "NO_CONTENT"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]
  create_advanced_site_search = false
  provider                    = google.dev_billing_override
  depends_on             = [resource.google_project_service.services]
}

# 建立開發環境的 Discovery Engine Search Engine
# 用於提供搜尋功能介面
resource "google_discovery_engine_search_engine" "search_engine_dev" {
  project        = var.dev_project_id
  engine_id      = "${var.project_name}-search"
  collection_id  = "default_collection"
  location       = google_discovery_engine_data_store.data_store_dev.location
  display_name   = "Search Engine App Staging"
  data_store_ids = [google_discovery_engine_data_store.data_store_dev.data_store_id]
  search_engine_config {
    search_tier = "SEARCH_TIER_ENTERPRISE"
  }
  provider      = google.dev_billing_override
}
