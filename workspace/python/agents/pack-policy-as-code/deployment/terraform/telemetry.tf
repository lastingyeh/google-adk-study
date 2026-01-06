# 建立 BigQuery Dataset
# 用於存放遙測資料的外部表 (External Tables) 和視圖 (Views)
resource "google_bigquery_dataset" "telemetry_dataset" {
  for_each      = local.deploy_project_ids
  project       = each.value
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} Telemetry"
  location      = var.region
  description   = "儲存於 GCS 的 GenAI 遙測資料 Dataset"
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 BigQuery 連接 (Connection)
# 用於存取 GCS 中的遙測資料 (BigLake/External Table 需求)
resource "google_bigquery_connection" "genai_telemetry_connection" {
  for_each      = local.deploy_project_ids
  project       = each.value
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI Telemetry 連接"

  cloud_resource {}

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 等待 BigQuery 連接的 Service Account 在 IAM 中傳播生效
resource "time_sleep" "wait_for_bq_connection_sa" {
  for_each = local.deploy_project_ids

  create_duration = "10s"

  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授權 BigQuery 連接 Service Account 讀取日誌 Bucket
# 讓 BigQuery 能夠讀取儲存在 GCS 中的遙測資料
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  for_each = local.deploy_project_ids
  bucket   = google_storage_bucket.logs_data_bucket[each.value].name
  role     = "roles/storage.objectViewer"
  member   = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection[each.key].cloud_resource[0].service_account_id}"

  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# GenAI 遙測專用 Cloud Logging Bucket
# ====================================================================

# 建立專用的 Cloud Logging Bucket (Log Bucket)
# 用於長期儲存 GenAI 遙測日誌 (設定 10 年保留期)
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  for_each         = local.deploy_project_ids
  project          = each.value
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 10 年保留期 (最大值)
  enable_analytics = true  # 啟用分析功能 (Linked Datasets 所需)
  description      = "${var.project_name} GenAI 遙測專用 Log Bucket (10 年保留期)"

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 設定 Log Sink 將 GenAI 相關日誌路由到專用 Bucket
# 透過過濾器篩選出特定 Agent 的推論日誌
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  for_each    = local.deploy_project_ids
  name        = "${var.project_name}-genai-logs"
  project     = each.value
  destination = "logging.googleapis.com/projects/${each.value}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id}"
  filter      = "log_name=\"projects/${each.value}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 建立 Linked Dataset 連結 Log Bucket 與 BigQuery
# 允許直接在 BigQuery 中查詢 Log Bucket 的資料
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  for_each    = local.deploy_project_ids
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id
  description = "${var.project_name} GenAI 遙測 Log Bucket 的 Linked Dataset"
  location    = var.region
  parent      = "projects/${each.value}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待 Linked Dataset 完全生效
resource "time_sleep" "wait_for_linked_dataset" {
  for_each = local.deploy_project_ids

  create_duration = "10s"

  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 使用者回饋日誌 (Feedback Logs)
# ====================================================================

# 設定 Log Sink 將使用者回饋日誌路由到同一個專用 Bucket
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
# Completions 外部表 (GCS-based)
# ====================================================================

# 建立指向 GCS 資料的 BigQuery 外部表
# 用於分析存儲在 GCS 中的詳細對話內容 (Completions)
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

  # 定義與 ADK completions 格式相符的 Schema
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
# Completions 視圖 (整合 Log 與 GCS 資料)
# ====================================================================

# 建立 BigQuery 視圖
# 將 Cloud Logging 中的日誌與 GCS 中的詳細內容 (External Table) 進行關聯查詢
resource "google_bigquery_table" "completions_view" {
  for_each            = local.deploy_project_ids
  project             = each.value
  dataset_id          = google_bigquery_dataset.telemetry_dataset[each.key].dataset_id
  table_id            = "completions_view"
  description         = "整合 GenAI Completion Log 與 GCS 外部表資料的視圖"
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
