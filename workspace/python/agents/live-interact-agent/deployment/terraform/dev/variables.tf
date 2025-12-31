variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名的基礎"
  default     = "live-interact-agent"
}

variable "dev_project_id" {
  type        = string
  description = "用於資源部署的 **開發環境 (Dev)** Google Cloud 專案 ID"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域"
  default     = "us-central1"
}

variable "telemetry_logs_filter" {
  type        = string
  description = "用於擷取遙測資料的 Log Sink 過濾器。擷取 `traceloop.association.properties.log_type` 屬性設定為 `tracing` 的日誌。"
  default     = "labels.service_name=\"live-interact-agent\" labels.type=\"agent_telemetry\""
}

variable "feedback_logs_filter" {
  type        = string
  description = "用於擷取回饋資料的 Log Sink 過濾器。擷取 `log_type` 欄位為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"live-interact-agent\""
}

variable "app_sa_roles" {
  description = "要指派給應用程式服務帳戶的角色列表"
  type        = list(string)
  default = [
    "roles/aiplatform.user",
    "roles/discoveryengine.editor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/storage.admin",
    "roles/serviceusage.serviceUsageConsumer",
  ]
}
