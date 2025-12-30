# 建立 BigQuery 資料集
# 用於存儲 GenAI 應用程式的遙測資料外部表
resource "google_bigquery_dataset" "telemetry_dataset" {
  project       = var.dev_project_id
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} Telemetry"
  location      = var.region
  description   = "Dataset for GenAI telemetry data stored in GCS"
  depends_on    = [google_project_service.services]
}

# 建立 BigQuery 連接 (Connection)
# 用於從 BigQuery 訪問 GCS 中的遙測資料
resource "google_bigquery_connection" "genai_telemetry_connection" {
  project       = var.dev_project_id
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI Telemetry Connection"

  cloud_resource {}

  depends_on = [google_project_service.services]
}

# 等待 BigQuery 連接服務帳號在 IAM 中生效
# 確保後續授權操作不會因服務帳號尚未傳播而失敗
resource "time_sleep" "wait_for_bq_connection_sa" {
  create_duration = "10s"

  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授權 BigQuery 連接服務帳號讀取日誌 Bucket
# 允許 BigQuery 讀取 GCS 中的遙測檔案
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  bucket = google_storage_bucket.logs_data_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection.cloud_resource[0].service_account_id}"

  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# 專用 GenAI 遙測 Cloud Logging Bucket
# ====================================================================

# 建立自定義 Cloud Logging Bucket
# 用於長期保存 GenAI 相關日誌 (保留 10 年)
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  project          = var.dev_project_id
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 10 年保留期 (最大允許值)
  enable_analytics = true  # 啟用分析功能，以支援 Linked Dataset
  description      = "Dedicated Cloud Logging bucket for ${var.project_name} GenAI telemetry with 10 year retention"

  depends_on = [google_project_service.services]
}

# 設定 Log Sink 將特定日誌導向專用 Bucket
# 過濾條件：包含特定的標籤且涉及此專案的 GenAI 操作
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  name        = "${var.project_name}-genai-logs"
  project     = var.dev_project_id
  destination = "logging.googleapis.com/projects/${var.dev_project_id}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id}"
  filter      = "log_name=\"projects/${var.dev_project_id}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 建立 Linked Dataset
# 讓 Cloud Logging Bucket 中的資料可以透過 BigQuery 查詢
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id
  description = "Linked dataset for ${var.project_name} GenAI telemetry Cloud Logging bucket"
  location    = var.region
  parent      = "projects/${var.dev_project_id}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待 Linked Dataset 完全生效
resource "time_sleep" "wait_for_linked_dataset" {
  create_duration = "10s"

  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 使用者回饋日誌 (Feedback Logs)
# ====================================================================

# 設定 Log Sink 導向使用者回饋日誌
# 將前端收集的 Feedback 傳送到同一個長效 Bucket
resource "google_logging_project_sink" "feedback_logs_to_bucket" {
  name        = "${var.project_name}-feedback"
  project     = var.dev_project_id
  destination = "logging.googleapis.com/projects/${var.dev_project_id}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id}"
  filter      = var.feedback_logs_filter

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# ====================================================================
# Completions 外部資料表 (GCS-based)
# ====================================================================

# 建立 BigQuery 外部資料表
# 直接查詢 GCS 中存儲的 Completions JSON 檔案 (訊息/對話內容)
resource "google_bigquery_table" "completions_external_table" {
  project             = var.dev_project_id
  dataset_id          = google_bigquery_dataset.telemetry_dataset.dataset_id
  table_id            = "completions"
  deletion_protection = false

  external_data_configuration {
    autodetect            = false
    source_format         = "NEWLINE_DELIMITED_JSON"
    source_uris           = ["gs://${google_storage_bucket.logs_data_bucket.name}/completions/*"]
    connection_id         = google_bigquery_connection.genai_telemetry_connection.name
    ignore_unknown_values = true
    max_bad_records       = 1000
  }

  # 定義符合 ADK completions 格式的 Schema
  schema = jsonencode([
    {
      name = "parts"
      type = "RECORD"
      mode = "REPEATED"
      fields = [
        { name = "type", type = "STRING", mode = "NULLABLE" },
        { name = "content", type = "STRING", mode = "NULLABLE" },
        { name = "mime_type", type = "STRING", mode = "NULLABLE" },
        { name = "uri", type = "STRING", mode = "NULLABLE" },
        { name = "data", type = "BYTES", mode = "NULLABLE" },
        { name = "id", type = "STRING", mode = "NULLABLE" },
        { name = "name", type = "STRING", mode = "NULLABLE" },
        { name = "arguments", type = "JSON", mode = "NULLABLE" },
        { name = "response", type = "JSON", mode = "NULLABLE" }
      ]
    },
    { name = "role", type = "STRING", mode = "NULLABLE" },
    { name = "index", type = "INTEGER", mode = "NULLABLE" }
  ])

  depends_on = [
    google_storage_bucket.logs_data_bucket,
    google_bigquery_connection.genai_telemetry_connection,
    google_storage_bucket_iam_member.telemetry_connection_access
  ]
}

# ====================================================================
# Completions 整合視圖 (View)
# ====================================================================

# 建立整合視圖
# 結合 Cloud Logging 的日誌資料與 GCS 的外部資料表，提供完整的查詢視圖
resource "google_bigquery_table" "completions_view" {
  project             = var.dev_project_id
  dataset_id          = google_bigquery_dataset.telemetry_dataset.dataset_id
  table_id            = "completions_view"
  description         = "View of GenAI completion logs joined with the GCS prompt/response external table"
  deletion_protection = false

  view {
    query = templatefile("${path.module}/../sql/completions.sql", {
      project_id                 = var.dev_project_id
      dataset_id                 = google_bigquery_dataset.telemetry_dataset.dataset_id
      completions_external_table = google_bigquery_table.completions_external_table.table_id
      logs_link_id               = google_logging_linked_dataset.genai_logs_linked_dataset.link_id
    })
    use_legacy_sql = false
  }

  depends_on = [
    google_logging_linked_dataset.genai_logs_linked_dataset,
    google_bigquery_table.completions_external_table,
    time_sleep.wait_for_linked_dataset
  ]
}
