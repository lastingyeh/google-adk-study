provider "google" {
  region                = var.region
  user_project_override = true
}

# 建立日誌資料儲存桶 (Logs Data Bucket)
# 用於存儲應用程式日誌和遙測資料
resource "google_storage_bucket" "logs_data_bucket" {
  for_each                    = toset(local.all_project_ids)
  name                        = "${each.value}-${var.project_name}-logs"
  location                    = var.region
  project                     = each.value
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Artifact Registry 倉庫
# 用於存儲生成式 AI 應用程式的 Docker 容器映像
resource "google_artifact_registry_repository" "repo-artifacts-genai" {
  location      = var.region
  repository_id = "${var.project_name}-repo"
  description   = "Repo for Generative AI applications"
  format        = "DOCKER"
  project       = var.cicd_runner_project_id
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}


# 建立資料攝取 Pipeline 的 GCS 根目錄
# 用於 Vertex AI Pipeline 執行過程中的暫存和工件存儲
resource "google_storage_bucket" "data_ingestion_pipeline_gcs_root" {
  for_each                    = local.deploy_project_ids
  name                        = "${each.value}-${var.project_name}-rag"
  location                    = var.region
  project                     = each.value
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}


# 建立 Staging 環境的 Discovery Engine Data Store
# 用於存儲和索引知識庫內容 (RAG)
resource "google_discovery_engine_data_store" "data_store_staging" {
  location                    = var.data_store_region
  project                     = var.staging_project_id
  data_store_id               = "${var.project_name}-datastore"
  display_name                = "${var.project_name}-datastore"
  industry_vertical           = "GENERIC"
  content_config              = "NO_CONTENT"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]
  create_advanced_site_search = false
  provider                    = google.staging_billing_override
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Staging 環境的 Discovery Engine Search Engine
# 用於提供搜尋功能介面
resource "google_discovery_engine_search_engine" "search_engine_staging" {
  project        = var.staging_project_id
  engine_id      = "${var.project_name}-search"
  collection_id  = "default_collection"
  location       = google_discovery_engine_data_store.data_store_staging.location
  display_name   = "Search Engine App Staging"
  data_store_ids = [google_discovery_engine_data_store.data_store_staging.data_store_id]
  search_engine_config {
    search_tier = "SEARCH_TIER_ENTERPRISE"
  }
  provider = google.staging_billing_override
}

# 建立 Production 環境的 Discovery Engine Data Store
# 用於存儲和索引知識庫內容 (RAG)
resource "google_discovery_engine_data_store" "data_store_prod" {
  location                    = var.data_store_region
  project                     = var.prod_project_id
  data_store_id               = "${var.project_name}-datastore"
  display_name                = "${var.project_name}-datastore"
  industry_vertical           = "GENERIC"
  content_config              = "NO_CONTENT"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]
  create_advanced_site_search = false
  provider                    = google.prod_billing_override
  depends_on         = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Production 環境的 Discovery Engine Search Engine
# 用於提供搜尋功能介面
resource "google_discovery_engine_search_engine" "search_engine_prod" {
  project        = var.prod_project_id
  engine_id      = "${var.project_name}-search"
  collection_id  = "default_collection"
  location       = google_discovery_engine_data_store.data_store_prod.location
  display_name   = "Search Engine App Prod"
  data_store_ids = [google_discovery_engine_data_store.data_store_prod.data_store_id]
  search_engine_config {
    search_tier = "SEARCH_TIER_ENTERPRISE"
  }
  provider = google.prod_billing_override
}
