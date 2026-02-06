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

variable "project_name" {
  type        = string
  description = "用作資源命名基礎的專案名稱 (Project name used as a base for resource naming)"
  default     = "pack-rag"
}

variable "dev_project_id" {
  type        = string
  description = "**開發環境 (Dev)** Google Cloud 資源部署專案 ID (**Dev** Google Cloud Project ID for resource deployment.)"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域 (Google Cloud region for resource deployment.)"
  default     = "us-central1"
}

variable "telemetry_logs_filter" {
  type        = string
  description = "用於擷取遙測資料的 Log Sink 過濾器。擷取 `traceloop.association.properties.log_type` 屬性設定為 `tracing` 的日誌。(Log Sink filter for capturing telemetry data. Captures logs with the `traceloop.association.properties.log_type` attribute set to `tracing`.)"
  default     = "labels.service_name=\"pack-rag\" labels.type=\"agent_telemetry\""
}

variable "feedback_logs_filter" {
  type        = string
  description = "用於擷取回饋資料的 Log Sink 過濾器。擷取 `log_type` 欄位為 `feedback` 的日誌。(Log Sink filter for capturing feedback data. Captures logs where the `log_type` field is `feedback`.)"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"pack-rag\""
}

variable "app_sa_roles" {
  description = "指派給應用程式服務帳戶的角色清單 (List of roles to assign to the application service account)"
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

# 重點摘要
# - **核心概念**：Dev 環境變數
# - **關鍵技術**：Terraform Input Variables
# - **重要結論**：定義 Dev 環境特定的輸入參數，如 `dev_project_id`。
# - **行動項目**：無
