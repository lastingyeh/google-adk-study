# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址獲得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱本授權以了解管理權限和限制的特定語言。

/*
## 重點摘要
- **核心概念**：為開發 (Dev) 環境配置完整的遙測與日誌分析鏈。
- **關鍵技術**：Cloud Logging, BigQuery Dataset/Connection, Linked Dataset, External Table。
- **重要結論**：開發環境也能享有與生產環境同等級的監控能力，方便開發者調試提示詞與函式呼叫。
- **行動項目**：確認 `sql/completions.sql` 相對路徑正確。
*/


# 用於遙測 (Telemetry) 外部資料表的 BigQuery 資料集
resource "google_bigquery_dataset" "telemetry_dataset" {
  project       = var.dev_project_id
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} 遙測數據"
  location      = var.region
  description   = "存儲在 GCS 中的 GenAI 遙測數據的資料集"
  depends_on    = [google_project_service.services]
}

# 用於存取 GCS 遙測數據的 BigQuery 連接
resource "google_bigquery_connection" "genai_telemetry_connection" {
  project       = var.dev_project_id
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI 遙測連接"

  cloud_resource {}

  depends_on = [google_project_service.services]
}

# 等待 BigQuery 連接服務帳號在 IAM 中傳播
resource "time_sleep" "wait_for_bq_connection_sa" {
  create_duration = "10s"

  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授予 BigQuery 連接服務帳號從日誌儲存桶讀取的權限
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  bucket = google_storage_bucket.logs_data_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection.cloud_resource[0].service_account_id}"

  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# 用於 GenAI 遙測的專用 Cloud Logging 儲存桶
# ====================================================================

# 建立自定義 Cloud Logging 儲存桶，用於長期保留 GenAI 遙測日誌
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  project          = var.dev_project_id
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 10 年保留期
  enable_analytics = true  # 連結資料集所需
  description      = "專用於 ${var.project_name} GenAI 遙測的 Cloud Logging 儲存桶"

  depends_on = [google_project_service.services]
}

# 日誌接收器，將遙測日誌路由到專用儲存桶
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  name        = "${var.project_name}-genai-logs"
  project     = var.dev_project_id
  destination = "logging.googleapis.com/projects/${var.dev_project_id}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id}"
  filter      = "log_name=\"projects/${var.dev_project_id}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 建立連結資料集
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id
  description = "${var.project_name} GenAI 遙測日誌連結資料集"
  location    = var.region
  parent      = "projects/${var.dev_project_id}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待資料集傳播
resource "time_sleep" "wait_for_linked_dataset" {
  create_duration = "10s"

  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 反饋日誌
# ====================================================================

resource "google_logging_project_sink" "feedback_logs_to_bucket" {
  name        = "${var.project_name}-feedback"
  project     = var.dev_project_id
  destination = "logging.googleapis.com/projects/${var.dev_project_id}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id}"
  filter      = var.feedback_logs_filter

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# ====================================================================
# 完成 (Completions) 外部資料表
# ====================================================================

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
# 完成檢視表
# ====================================================================

resource "google_bigquery_table" "completions_view" {
  project             = var.dev_project_id
  dataset_id          = google_bigquery_dataset.telemetry_dataset.dataset_id
  table_id            = "completions_view"
  description         = "連結 Cloud Logging 與 GCS 完成數據的檢視表"
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
