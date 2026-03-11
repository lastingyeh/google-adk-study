# Terraform 設定：遙測數據 (Telemetry)
# 此檔案定義了用於收集、存儲與分析產生式 AI 遙測數據的 BigQuery、Cloud Logging 與相關整合設定

# 用於遙測外部資料表的 BigQuery 資料集
resource "google_bigquery_dataset" "telemetry_dataset" {
  for_each      = local.deploy_project_ids
  project       = each.value
  dataset_id    = replace("${var.project_name}_telemetry", "-", "_")
  friendly_name = "${var.project_name} 遙測數據"
  location      = var.region
  description   = "存儲在 GCS 中的 GenAI 遙測數據資料集"
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 用於存取 GCS 遙測數據的 BigQuery 連線
resource "google_bigquery_connection" "genai_telemetry_connection" {
  for_each      = local.deploy_project_ids
  project       = each.value
  location      = var.region
  connection_id = "${var.project_name}-genai-telemetry"
  friendly_name = "${var.project_name} GenAI 遙測連線"

  cloud_resource {} # 建立雲端資源連線

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 等待 BigQuery 連線服務帳戶在 IAM 中完成同步
resource "time_sleep" "wait_for_bq_connection_sa" {
  for_each = local.deploy_project_ids
  create_duration = "10s"
  depends_on = [google_bigquery_connection.genai_telemetry_connection]
}

# 授予 BigQuery 連線服務帳戶讀取日誌儲存桶的權限
resource "google_storage_bucket_iam_member" "telemetry_connection_access" {
  for_each = local.deploy_project_ids
  bucket   = google_storage_bucket.logs_data_bucket[each.value].name
  role     = "roles/storage.objectViewer"
  member   = "serviceAccount:${google_bigquery_connection.genai_telemetry_connection[each.key].cloud_resource[0].service_account_id}"

  depends_on = [time_sleep.wait_for_bq_connection_sa]
}

# ====================================================================
# GenAI 遙測專用的 Cloud Logging 儲存桶
# ====================================================================

# 等待 Logging API 啟用後完成同步
resource "time_sleep" "wait_for_logging_api" {
  for_each = local.deploy_project_ids
  create_duration = "30s"
  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立具備長期保存能力的自定義 Cloud Logging 儲存桶
resource "google_logging_project_bucket_config" "genai_telemetry_bucket" {
  for_each         = local.deploy_project_ids
  project          = each.value
  location         = var.region
  bucket_id        = "${var.project_name}-genai-telemetry"
  retention_days   = 3650  # 保存 10 年 (最高上限)
  enable_analytics = true  # 連結資料集所需
  description      = "專用的 ${var.project_name} GenAI 遙測日誌儲存桶，保存期限 10 年"

  depends_on = [time_sleep.wait_for_logging_api]
}

# 日誌接收器 (Log Sink)：將 GenAI 遙測日誌導向專用儲存桶
resource "google_logging_project_sink" "genai_logs_to_bucket" {
  for_each    = local.deploy_project_ids
  name        = "${var.project_name}-genai-logs"
  project     = each.value
  destination = "logging.googleapis.com/projects/${each.value}/locations/${var.region}/buckets/${google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id}"
  filter      = "log_name=\"projects/${each.value}/logs/gen_ai.client.inference.operation.details\" AND (labels.\"gen_ai.input.messages_ref\" =~ \".*${var.project_name}.*\" OR labels.\"gen_ai.output.messages_ref\" =~ \".*${var.project_name}.*\")"

  unique_writer_identity = true
  depends_on             = [google_logging_project_bucket_config.genai_telemetry_bucket]
}

# 建立連結資料集 (Linked Dataset)，以便透過 BigQuery 查詢日誌儲存桶內容
resource "google_logging_linked_dataset" "genai_logs_linked_dataset" {
  for_each    = local.deploy_project_ids
  link_id     = replace("${var.project_name}_genai_telemetry_logs", "-", "_")
  bucket      = google_logging_project_bucket_config.genai_telemetry_bucket[each.key].bucket_id
  description = "${var.project_name} GenAI 遙測日誌儲存桶的連結資料集"
  location    = var.region
  parent      = "projects/${each.value}"

  depends_on = [
    google_logging_project_bucket_config.genai_telemetry_bucket,
    google_logging_project_sink.genai_logs_to_bucket
  ]
}

# 等待連結資料集完成同步
resource "time_sleep" "wait_for_linked_dataset" {
  for_each = local.deploy_project_ids
  create_duration = "10s"
  depends_on = [google_logging_linked_dataset.genai_logs_linked_dataset]
}

# ====================================================================
# 使用者回饋日誌 (Feedback Logs)
# ====================================================================

# 使用者回饋日誌接收器：導向相同的日誌儲存桶
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
# 回覆結果外部資料表 (Completions External Table, GCS-based)
# ====================================================================

# 以 GCS 中的回覆數據為基礎建立 BigQuery 外部資料表
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

  # 與 ADK 回覆格式相符的結構定義 (Schema)
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
# 回覆結果視圖 (Completions View：結合日誌與 GCS 數據)
# ====================================================================

# 結合 Cloud Logging 日誌與 GCS 回覆數據的 BigQuery 視圖
resource "google_bigquery_table" "completions_view" {
  for_each            = local.deploy_project_ids
  project             = each.value
  dataset_id          = google_bigquery_dataset.telemetry_dataset[each.key].dataset_id
  table_id            = "completions_view"
  description         = "結合了 GenAI 回覆日誌與 GCS 提示/回覆外部資料表的視圖"
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