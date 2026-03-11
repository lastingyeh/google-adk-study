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

# Terraform 設定：開發環境變數宣告 (Dev Variables)
# 此檔案定義了開發專案配置中使用的輸入參數

variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名基礎"
  default     = "guarding-agent"
}

variable "dev_project_id" {
  type        = string
  description = "**開發環境 (Dev)** 部署資源的 Google Cloud 專案 ID"
}

variable "region" {
  type        = string
  description = "部署資源的 Google Cloud 區域"
  default     = "us-central1"
}

variable "telemetry_logs_filter" {
  type        = string
  description = "用於捕獲遙測數據的日誌接收器過濾器。"
  default     = "labels.service_name=\"guarding-agent\" labels.type=\"agent_telemetry\""
}

variable "feedback_logs_filter" {
  type        = string
  description = "用於捕獲回饋數據的日誌接收器過濾器。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"guarding-agent\""
}

variable "app_sa_roles" {
  description = "指派給應用程式服務帳戶的角色列表"
  type        = list(string)
  default = [
    "roles/aiplatform.user",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/storage.admin",
    "roles/serviceusage.serviceUsageConsumer",
    "roles/cloudsql.client",
    "roles/secretmanager.secretAccessor",
  ]
}

/*
重點摘要：
- 核心概念：定義開發環境特有的動態參數。
- 關鍵技術：Terraform Variables, Log Filters.
- 重要結論：透過變數分離開發與生產環境的配置，提高架構的靈活性。
*/
