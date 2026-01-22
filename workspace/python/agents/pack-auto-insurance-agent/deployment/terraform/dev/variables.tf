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
- **核心概念**：定義開發 (Dev) 環境專用的部署變數。
- **關鍵技術**：Terraform Variables, 日誌篩選 (Log Filtering)。
- **重要結論**：與全局變數類似，但專注於單一開發環境的資源隔離與日誌監控設定。
- **行動項目**：在部署開發環境前，需在 `env.tfvars` 中指定 `dev_project_id`。
*/

# 專案名稱變數
variable "project_name" {
  type        = string
  description = "用於資源命名的基礎專案名稱"
  default     = "pack-auto-insurance-agent"
}

# 開發環境 (Dev) 的 GCP 專案 ID
variable "dev_project_id" {
  type        = string
  description = "**開發 (Dev)** 環境的 Google Cloud 專案 ID。"
}

# GCP 區域
variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域。"
  default     = "us-central1"
}

# 遙測日誌篩選器
variable "telemetry_logs_filter" {
  type        = string
  description = "用於捕獲遙測數據的日誌接收器篩選器。"
  default     = "labels.service_name=\"pack-auto-insurance-agent\" labels.type=\"agent_telemetry\""
}

# 反饋日誌篩選器
variable "feedback_logs_filter" {
  type        = string
  description = "用於捕獲反饋數據的日誌接收器篩選器。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"pack-auto-insurance-agent\""
}

# 應用程式服務帳號角色清單
variable "app_sa_roles" {
  description = "分配給應用程式服務帳號的角色清單"
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
