# 用於遙測外部資料表的 BigQuery 資料集
resource "google_bigquery_dataset" "telemetry_dataset" {
  project       = var.dev_project_id
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} Telemetry"
  location      = var.region
  description   = "儲存在 GCS 中的 GenAI 遙測資料的資料集"
  depends_on    = [google_project_service.services]
}

# 用於存取 GCS 遙測資料的 BigQuery 連線
resource "google_bigquery_connection" "genai_telemetry_connection" {
  project       = var.dev_project_id
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI Telemetry Connection"

  cloud_resource {}

  depends_on = [google_project_service.services]
}

# 等待 BigQuery 連線服務帳戶在 IAM 中傳播
resource "time_sleep" "wait_for_bq_connection_sa" {
  create_duration = "10s"

  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授權 BigQuery 連線服務帳戶讀取日誌儲存桶的權限
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  bucket = google_storage_bucket.logs_data_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection.cloud_resource[0].service_account_id}"

  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# GenAI 遙測專用的 Cloud Logging 儲存桶
# ====================================================================

# 建立自訂的 Cloud Logging 儲存桶，用於長期保存 GenAI 遙測日誌
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  project          = var.dev_project_id
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 保存 10 年 (允許的最大值)
  enable_analytics = true  # 連結資料集所需
  description      = "${var.project_name} GenAI 遙測的專用 Cloud Logging 儲存桶，保存期限 10 年"

  depends_on = [google_project_service.services]
}

# 日誌路由器 (Log Sink)，將 GenAI 遙測日誌路由到專用儲存桶
# 通過 GCS 路徑中的儲存桶名稱 (包含 project_name) 進行過濾，以隔離此代理程式的日誌
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  name        = "${var.project_name}-genai-logs"
  project     = var.dev_project_id
  destination = "logging.googleapis.com/projects/${var.dev_project_id}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id}"
  filter      = "log_name=\"projects/${var.dev_project_id}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 建立連結到 GenAI 遙測日誌儲存桶的資料集，以便透過 BigQuery 查詢
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id
  description = "${var.project_name} GenAI 遙測 Cloud Logging 儲存桶的連結資料集"
  location    = var.region
  parent      = "projects/${var.dev_project_id}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待連結資料集完全傳播
resource "time_sleep" "wait_for_linked_dataset" {
  create_duration = "10s"

  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 回饋日誌到 Cloud Logging 儲存桶
# ====================================================================

# 用於使用者回饋日誌的日誌路由器 - 路由到同一個 Cloud Logging 儲存桶
resource "google_logging_project_sink" "feedback_logs_to_bucket" {
  name        = "${var.project_name}-feedback"
  project     = var.dev_project_id
  destination = "logging.googleapis.com/projects/${var.dev_project_id}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id}"
  filter      = var.feedback_logs_filter

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# ====================================================================
# 完成 (Completions) 外部資料表 (基於 GCS)
# ====================================================================

# 用於儲存在 GCS 中的完成資料 (訊息/部分) 的外部資料表
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

  # 符合 ADK 完成格式的架構
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
# 完成視圖 (連接日誌與 GCS 資料)
# ====================================================================

# 連接 Cloud Logging 資料與 GCS 儲存的完成資料的視圖
resource "google_bigquery_table" "completions_view" {
  project             = var.dev_project_id
  dataset_id          = google_bigquery_dataset.telemetry_dataset.dataset_id
  table_id            = "completions_view"
  description         = "GenAI 完成日誌與 GCS 提示/回應外部資料表連接的視圖"
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
