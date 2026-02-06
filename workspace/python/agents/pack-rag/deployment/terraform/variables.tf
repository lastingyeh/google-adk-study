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

variable "prod_project_id" {
  type        = string
  description = "**正式環境 (Production)** Google Cloud 資源部署專案 ID (**Production** Google Cloud Project ID for resource deployment.)"
}

variable "staging_project_id" {
  type        = string
  description = "**預備環境 (Staging)** Google Cloud 資源部署專案 ID (**Staging** Google Cloud Project ID for resource deployment.)"
}

variable "cicd_runner_project_id" {
  type        = string
  description = "執行 CI/CD 流程的 Google Cloud 專案 ID (Google Cloud Project ID where CI/CD pipelines will execute.)"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域 (Google Cloud region for resource deployment.)"
  default     = "us-central1"
}

variable "host_connection_name" {
  description = "在 Cloud Build 中建立的主機連線名稱 (Name of the host connection to create in Cloud Build)"
  type        = string
  default     = "pack-rag-github-connection"
}

variable "repository_name" {
  description = "您想要連結到 Cloud Build 的儲存庫名稱 (Name of the repository you'd like to connect to Cloud Build)"
  type        = string
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

variable "cicd_roles" {
  description = "在 CICD 專案中指派給 CICD Runner 服務帳戶的角色清單 (List of roles to assign to the CICD runner service account in the CICD project)"
  type        = list(string)
  default = [
    "roles/run.invoker",
    "roles/storage.admin",
    "roles/aiplatform.user",
    "roles/discoveryengine.editor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/artifactregistry.writer",
    "roles/cloudbuild.builds.builder"
  ]
}

variable "cicd_sa_deployment_required_roles" {
  description = "在 Staging 和 Prod 專案中指派給 CICD Runner 服務帳戶的角色清單 (List of roles to assign to the CICD runner service account for the Staging and Prod projects.)"
  type        = list(string)
  default = [
    "roles/run.developer",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin"
  ]
}


variable "repository_owner" {
  description = "Git 儲存庫擁有者 - 使用者名稱或組織 (Owner of the Git repository - username or organization)"
  type        = string
}


variable "github_app_installation_id" {
  description = "Cloud Build 的 GitHub App 安裝 ID (GitHub App Installation ID for Cloud Build)"
  type        = string
  default     = null
}


variable "github_pat_secret_id" {
  description = "由 gcloud CLI 建立的 GitHub PAT Secret ID (GitHub PAT Secret ID created by gcloud CLI)"
  type        = string
  default     = null
}

variable "create_cb_connection" {
  description = "指示 Cloud Build 連線是否已存在的旗標 (Flag indicating if a Cloud Build connection already exists)"
  type        = bool
  default     = false
}

variable "create_repository" {
  description = "指示是否建立新 Git 儲存庫的旗標 (Flag indicating whether to create a new Git repository)"
  type        = bool
  default     = false
}


variable "feedback_logs_filter" {
  type        = string
  description = "用於擷取回饋資料的 Log Sink 過濾器。擷取 `log_type` 欄位為 `feedback` 的日誌。(Log Sink filter for capturing feedback data. Captures logs where the `log_type` field is `feedback`.)"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"pack-rag\""
}

# 重點摘要
# - **核心概念**：輸入變數 (Variables)
# - **關鍵技術**：Terraform Input Variables
# - **重要結論**：定義了部署所需的各項參數，包含專案 ID、區域、儲存庫資訊、IAM 角色列表等，使 Terraform 配置具備高度的彈性與可重用性。
# - **行動項目**：無
