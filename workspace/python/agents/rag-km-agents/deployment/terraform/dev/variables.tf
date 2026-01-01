variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名的基礎"
  default     = "rag-km-agents"
}

variable "dev_project_id" {
  type        = string
  description = "**Dev** 開發環境 Google Cloud 專案 ID，用於資源部署"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域"
  default     = "us-central1"
}

variable "telemetry_logs_filter" {
  type        = string
  description = "用於捕獲遙測資料的 Log Sink 過濾器。捕獲 `traceloop.association.properties.log_type` 屬性設置為 `tracing` 的日誌。"
  default     = "labels.service_name=\"rag-km-agents\" labels.type=\"agent_telemetry\""
}

variable "feedback_logs_filter" {
  type        = string
  description = "用於捕獲回饋資料的 Log Sink 過濾器。捕獲 `log_type` 為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"rag-km-agents\""
}

variable "app_sa_roles" {
  description = "分配給應用程式服務帳號的角色列表"
  type        = list(string)
  default = [

    "roles/aiplatform.user",
    "roles/discoveryengine.editor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/storage.admin",
    "roles/serviceusage.serviceUsageConsumer",
    "roles/cloudsql.client",
    "roles/secretmanager.secretAccessor",
  ]
}


variable "pipelines_roles" {
  description = "分配給 Vertex AI Runner 服務帳號的角色列表"
  type        = list(string)
  default = [
    "roles/storage.admin",
    "roles/run.invoker",
    "roles/aiplatform.user",
    "roles/discoveryengine.admin",
    "roles/logging.logWriter",
    "roles/artifactregistry.writer",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/bigquery.readSessionUser",
    "roles/bigquery.connectionAdmin",
    "roles/resourcemanager.projectIamAdmin"
  ]
}

variable "data_store_region" {
  type        = string
  description = "Data Store 部署區域 (通常為 global 或特定多區域)"
  default     = "us"
}
