variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名的基礎 (Project name used as a base for resource naming)"
  default     = "pack-policy-as-code"
}

variable "dev_project_id" {
  type        = string
  description = "**Dev (開發環境)** Google Cloud Project ID。"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域 (Region)。"
  default     = "us-central1"
}

variable "telemetry_logs_filter" {
  type        = string
  description = "用於捕獲遙測資料的 Log Sink 過濾器 (Log Sink filter for capturing telemetry data)。捕獲 `traceloop.association.properties.log_type` 屬性設為 `tracing` 的日誌。"
  default     = "labels.service_name=\"pack-policy-as-code\" labels.type=\"agent_telemetry\""
}

variable "feedback_logs_filter" {
  type        = string
  description = "用於捕獲回饋資料的 Log Sink 過濾器 (Log Sink filter for capturing feedback data)。捕獲 `log_type` 為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"pack-policy-as-code\""
}

variable "app_sa_roles" {
  description = "分配給應用程式 Service Account 的 IAM 角色列表 (List of roles to assign to the application service account)"
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
