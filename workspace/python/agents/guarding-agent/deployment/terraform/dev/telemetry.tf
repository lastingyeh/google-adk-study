# Copyright 2026 Google LLC
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

# Terraform 設定：開發環境遙測數據 (Dev Telemetry)
# 此檔案定義了開發專案中用於收集、存儲與分析產生式 AI 遙測數據的相關設定

# 用於遙測外部資料表的 BigQuery 資料集
resource "google_bigquery_dataset" "telemetry_dataset" {
  project       = var.dev_project_id
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} 遙測數據"
  location      = var.region
  description   = "存儲在 GCS 中的 GenAI 遙測數據資料集"
  depends_on    = [google_project_service.services]
}

# 用於存取 GCS 遙測數據的 BigQuery 連線
resource "google_bigquery_connection" "genai_telemetry_connection" {
  project       = var.dev_project_id
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI 遙測連線"
  cloud_resource {}
  depends_on = [google_project_service.services]
}

# 等待 BigQuery 連線服務帳戶在 IAM 中完成同步
resource "time_sleep" "wait_for_bq_connection_sa" {
  create_duration = "10s"
  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授予 BigQuery 連線服務帳戶讀取日誌儲存桶的權限
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  bucket = google_storage_bucket.logs_data_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection.cloud_resource[0].service_account_id}"
  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# GenAI 遙測專用的 Cloud Logging 儲存桶
# ====================================================================

# 等待 Logging API 完成同步
resource "time_sleep" "wait_for_logging_api" {
  create_duration = "30s"
  depends_on = [google_project_service.services]
}

# 建立自定義 Cloud Logging 儲存桶
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  project          = var.dev_project_id
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 保存 10 年
  enable_analytics = true
  description      = "專用的 ${var.project_name} GenAI 遙測日誌儲存桶"
  depends_on = [time_sleep.wait_for_logging_api]
}

# 日誌接收器 (Log Sink)
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  name        = "${var.project_name}-genai-logs"
  project     = var.dev_project_id
  destination = "logging.googleapis.com/projects/${var.dev_project_id}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id}"
  filter      = "log_name=\"projects/${var.dev_project_id}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 連結資料集 (Linked Dataset)
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket.bucket_id
  description = "${var.project_name} GenAI 遙測日誌儲存桶的連結資料集"
  location    = var.region
  parent      = "projects/${var.dev_project_id}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待連結資料集同步
resource "time_sleep" "wait_for_linked_dataset" {
  create_duration = "10s"
  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 使用者回饋日誌 (Feedback Logs)
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
# 回覆結果外部資料表 (Completions External Table)
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
# 回覆結果視圖 (Completions View)
# ====================================================================

resource "google_bigquery_table" "completions_view" {
  project             = var.dev_project_id
  dataset_id          = google_bigquery_dataset.telemetry_dataset.dataset_id
  table_id            = "completions_view"
  description         = "結合了 GenAI 回覆日誌與 GCS 提示/回覆外部資料表的視圖"
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

/*
重點摘要：
- 核心概念：在開發環境中建立與頂層設定一致的遙測收集與分析機制。
- 關鍵技術：BigQuery, Cloud Logging Sink, GCS External Table.
- 重要結論：即使在開發階段也保留完整的數據追蹤能力，有助於模型調優與問題排查。
*/
