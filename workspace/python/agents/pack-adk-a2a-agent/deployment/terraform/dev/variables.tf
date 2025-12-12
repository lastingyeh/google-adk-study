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

# ============================================================================
# 開發環境變數定義
# ============================================================================
# 此檔案定義開發環境所需的輸入變數：
# - dev_project_id: 開發環境的 GCP 專案 ID
# - region: 部署區域
# - 日誌過濾器（telemetry_logs_filter, feedback_logs_filter）
# - app_sa_roles: 應用程式服務帳號所需的 IAM 角色
#
# 開發環境簡化了配置，只需要單一專案 ID
# ============================================================================

variable "project_name" {
  type        = string
  description = "Project name used as a base for resource naming"
  default     = "pack-adk-a2a-agent"
}

variable "dev_project_id" {
  type        = string
  description = "**Dev** Google Cloud Project ID for resource deployment."
}

variable "region" {
  type        = string
  description = "Google Cloud region for resource deployment."
  default     = "us-central1"
}

variable "telemetry_logs_filter" {
  type        = string
  description = "Log Sink filter for capturing telemetry data. Captures logs with the `traceloop.association.properties.log_type` attribute set to `tracing`."
  default     = "labels.service_name=\"pack-adk-a2a-agent\" labels.type=\"agent_telemetry\""
}

variable "feedback_logs_filter" {
  type        = string
  description = "Log Sink filter for capturing feedback data. Captures logs where the `log_type` field is `feedback`."
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"pack-adk-a2a-agent\""
}

variable "app_sa_roles" {
  description = "List of roles to assign to the application service account"
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
