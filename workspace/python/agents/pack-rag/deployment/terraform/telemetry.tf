# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# 遙測外部資料表的 BigQuery 資料集
# BigQuery dataset for telemetry external tables
resource "google_bigquery_dataset" "telemetry_dataset" {
  for_each      = local.deploy_project_ids
  project       = each.value
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} Telemetry"
  location      = var.region
  description   = "儲存在 GCS 中的 GenAI 遙測資料的資料集 (Dataset for GenAI telemetry data stored in GCS)"
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 存取 GCS 遙測資料的 BigQuery 連線
# BigQuery connection for accessing GCS telemetry data
resource "google_bigquery_connection" "genai_telemetry_connection" {
  for_each      = local.deploy_project_ids
  project       = each.value
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI Telemetry Connection"

  cloud_resource {}

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 等待 BigQuery 連線服務帳戶在 IAM 中傳播
# Wait for the BigQuery connection service account to propagate in IAM
resource "time_sleep" "wait_for_bq_connection_sa" {
  for_each = local.deploy_project_ids

  create_duration = "10s"

  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授予 BigQuery 連線服務帳戶讀取日誌 Bucket 的權限
# Grant the BigQuery connection service account access to read from the logs bucket
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  for_each = local.deploy_project_ids
  bucket   = google_storage_bucket.logs_data_bucket[each.value].name
  role     = "roles/storage.objectViewer"
  member   = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection[each.key].cloud_resource[0].service_account_id}"

  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# 用於 GenAI 遙測的專用 Cloud Logging Bucket
# Dedicated Cloud Logging Bucket for GenAI Telemetry
# ====================================================================

# 建立具有長期保留策略的 GenAI 遙測日誌專用 Cloud Logging Bucket
# Create a custom Cloud Logging bucket for GenAI telemetry logs with long-term retention
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  for_each         = local.deploy_project_ids
  project          = each.value
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 10 年保留期 (上限) (10 years retention (maximum allowed))
  enable_analytics = true  # 連結資料集所需 (Required for linked datasets)
  description      = "${var.project_name} GenAI 遙測資料的專用 Cloud Logging Bucket，保留 10 年 (Dedicated Cloud Logging bucket for ${var.project_name} GenAI telemetry with 10 year retention)"

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 日誌接收器 (Log Sink)，僅將 GenAI 遙測日誌路由到專用 Bucket
# 透過 GCS 路徑中的 Bucket 名稱 (包含專案名稱) 進行過濾，以隔離此 Agent 的日誌
# Log sink to route only GenAI telemetry logs to the dedicated bucket
# Filter by bucket name in the GCS path (which includes project_name) to isolate this agent's logs
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  for_each    = local.deploy_project_ids
  name        = "${var.project_name}-genai-logs"
  project     = each.value
  destination = "logging.googleapis.com/projects/${each.value}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id}"
  filter      = "log_name=\"projects/${each.value}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 建立連結到 GenAI 遙測日誌 Bucket 的資料集，以便透過 BigQuery 查詢
# Create a linked dataset to the GenAI telemetry logs bucket for querying via BigQuery
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  for_each    = local.deploy_project_ids
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id
  description = "${var.project_name} GenAI 遙測 Cloud Logging Bucket 的連結資料集 (Linked dataset for ${var.project_name} GenAI telemetry Cloud Logging bucket)"
  location    = var.region
  parent      = "projects/${each.value}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待連結資料集完全傳播
# Wait for linked dataset to fully propagate
resource "time_sleep" "wait_for_linked_dataset" {
  for_each = local.deploy_project_ids

  create_duration = "10s"

  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 回饋日誌至 Cloud Logging Bucket
# Feedback Logs to Cloud Logging Bucket
# ====================================================================

# 使用者回饋日誌的 Log Sink - 路由至相同的 Cloud Logging Bucket
# Log sink for user feedback logs - routes to the same Cloud Logging bucket
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
# Completions 外部資料表 (基於 GCS)
# Completions External Table (GCS-based)
# ====================================================================

# 儲存在 GCS 中的 completions 資料 (messages/parts) 的外部資料表
# External table for completions data (messages/parts) stored in GCS
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

  # 符合 ADK completions 格式的 Schema
  # Schema matching the ADK completions format
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
# Completions 視圖 (結合日誌與 GCS 資料)
# Completions View (Joins Logs with GCS Data)
# ====================================================================

# 結合 Cloud Logging 資料與 GCS 儲存的 completions 資料的視圖
# View that joins Cloud Logging data with GCS-stored completions data
resource "google_bigquery_table" "completions_view" {
  for_each            = local.deploy_project_ids
  project             = each.value
  dataset_id          = google_bigquery_dataset.telemetry_dataset[each.key].dataset_id
  table_id            = "completions_view"
  description         = "結合 GenAI completion 日誌與 GCS prompt/response 外部資料表的視圖 (View of GenAI completion logs joined with the GCS prompt/response external table)"
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

# 重點摘要
# - **核心概念**：GenAI 遙測與可觀測性
# - **關鍵技術**：BigQuery, Cloud Logging Linked Datasets, GCS External Tables
# - **重要結論**：建立完整的遙測資料管線。將 GenAI 推論日誌 (來自 Cloud Logging) 與詳細的請求/回應內容 (存於 GCS) 整合至 BigQuery，並提供長期日誌保留與分析能力。
# - **行動項目**：無
