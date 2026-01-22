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
- **核心概念**：建立端對端的遙測解決方案，結合 Cloud Logging、Cloud Storage 與 BigQuery 進行 GenAI 代理的監控與分析。
- **關鍵技術**：Cloud Logging 儲存桶, 日誌接收器 (Log Sinks), BigQuery 外部資料表 (External Tables), 連結資料集 (Linked Datasets), SQL 檢視表。
- **重要結論**：實現了長達 10 年的日誌保留期，並通過 BigQuery 提供了強大的查詢能力，可直接分析提示 (Prompts) 與回應 (Responses)。
- **行動項目**：確認 `sql/completions.sql` 檔案路徑正確，以便生成檢視表查詢。
*/

# 用於遙測 (Telemetry) 外部資料表的 BigQuery 資料集
resource "google_bigquery_dataset" "telemetry_dataset" {
  for_each      = local.deploy_project_ids
  project       = each.value
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} 遙測數據"
  location      = var.region
  description   = "存儲在 GCS 中的 GenAI 遙測數據的資料集"
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 用於存取 GCS 遙測數據的 BigQuery 連接
resource "google_bigquery_connection" "genai_telemetry_connection" {
  for_each      = local.deploy_project_ids
  project       = each.value
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI 遙測連接"

  cloud_resource {}

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 等待 BigQuery 連接服務帳號在 IAM 中傳播
resource "time_sleep" "wait_for_bq_connection_sa" {
  for_each = local.deploy_project_ids

  create_duration = "10s"

  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授予 BigQuery 連接服務帳號從日誌儲存桶讀取的權限
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  for_each = local.deploy_project_ids
  bucket   = google_storage_bucket.logs_data_bucket[each.value].name
  role     = "roles/storage.objectViewer"
  member   = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection[each.key].cloud_resource[0].service_account_id}"

  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# 用於 GenAI 遙測的專用 Cloud Logging 儲存桶
# ====================================================================

# 建立自定義 Cloud Logging 儲存桶，用於長期保留 GenAI 遙測日誌
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  for_each         = local.deploy_project_ids
  project          = each.value
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 10 年保留期（允許的最大值）
  enable_analytics = true  # 連結資料集所需
  description      = "專用於 ${var.project_name} GenAI 遙測的 Cloud Logging 儲存桶，保留期 10 年"

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 日誌接收器，僅將 GenAI 遙測日誌路由到專用儲存桶
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  for_each    = local.deploy_project_ids
  name        = "${var.project_name}-genai-logs"
  project     = each.value
  destination = "logging.googleapis.com/projects/${each.value}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id}"
  filter      = "log_name=\"projects/${each.value}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 建立連結到 GenAI 遙測日誌儲存桶的連結資料集，以便透過 BigQuery 查詢
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  for_each    = local.deploy_project_ids
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id
  description = "${var.project_name} GenAI 遙測 Cloud Logging 儲存桶的連結資料集"
  location    = var.region
  parent      = "projects/${each.value}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待連結資料集完全傳播
resource "time_sleep" "wait_for_linked_dataset" {
  for_each = local.deploy_project_ids

  create_duration = "10s"

  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 反饋日誌到 Cloud Logging 儲存桶
# ====================================================================

# 使用者反饋日誌的日誌接收器 - 路由到同一個 Cloud Logging 儲存桶
resource "google_logging_project_sink" "feedback_logs_to_bucket" {
  for_each    = local.deploy_project_ids
  name        = "${var.project_name}-feedback"
  project     = each.value
  destination = "logging.googleapis.com/projects/${each.value}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id}"
  filter      = var.feedback_logs_filter

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# ====================================================================
# 完成 (Completions) 外部資料表 (基於 GCS)
# ====================================================================

# 存儲在 GCS 中的完成數據（訊息/組件）的外部資料表
resource "google_bigquery_table" "completions_external_table" {
  for_each            = local.deploy_project_ids
  project             = each.value
  dataset_id          = google_bigquery_dataset.telemetry_dataset[each.key].dataset_id
  table_id            = "completions"
  deletion_protection = false

  external_data_configuration {
    autodetect            = false
    source_format         = "NEWLINE_DELIMITED_JSON"
    source_uris           = ["gs://${google_storage_bucket.logs_data_bucket[each.value].name}/completions/*"]
    connection_id         = google_bigquery_connection.genai_telemetry_connection[each.key].name
    ignore_unknown_values = true
    max_bad_records       = 1000
  }

  # 與 ADK 完成格式匹配的結構描述 (Schema)
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
# 完成檢視表 (Completions View - 連結日誌與 GCS 數據)
# ====================================================================

# 連結 Cloud Logging 數據與 GCS 存儲的完成數據的檢視表
resource "google_bigquery_table" "completions_view" {
  for_each            = local.deploy_project_ids
  project             = each.value
  dataset_id          = google_bigquery_dataset.telemetry_dataset[each.key].dataset_id
  table_id            = "completions_view"
  description         = "GenAI 完成日誌與 GCS 提示/回應外部資料表連結的檢視表"
  deletion_protection = false

  view {
    query = templatefile("${path.module}/sql/completions.sql", {
      project_id                 = each.value
      dataset_id                 = google_bigquery_dataset.telemetry_dataset[each.key].dataset_id
      completions_external_table = google_bigquery_table.completions_external_table[each.key].table_id
      logs_link_id               = google_logging_linked_dataset.genai_logs_linked_dataset[each.key].link_id
    })
    use_legacy_sql = false
  }

  depends_on = [
    google_logging_linked_dataset.genai_logs_linked_dataset,
    google_bigquery_table.completions_external_table,
    time_sleep.wait_for_linked_dataset
  ]
}
