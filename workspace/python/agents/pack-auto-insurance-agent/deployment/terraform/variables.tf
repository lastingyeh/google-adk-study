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
- **核心概念**：定義部署代理基礎設施所需的各種輸入變數。
- **關鍵技術**：Terraform 變數 (Variables), GCP 角色 (IAM Roles), GitHub 整合。
- **重要結論**：區分了生產、測試與 CI/CD 專案，並預設了多項安全與日誌相關的角色。
- **行動項目**：在部署前需填寫必要的 `prod_project_id`, `staging_project_id`, `cicd_runner_project_id` 等變數。
*/

# 專案名稱變數，作為資源命名的基礎
variable "project_name" {
  type        = string
  description = "用於資源命名的基礎專案名稱"
  default     = "pack-auto-insurance-agent"
}

# 生產環境的 GCP 專案 ID
variable "prod_project_id" {
  type        = string
  description = "**生產 (Production)** 環境的 Google Cloud 專案 ID。"
}

# 測試環境的 GCP 專案 ID
variable "staging_project_id" {
  type        = string
  description = "**測試 (Staging)** 環境的 Google Cloud 專案 ID。"
}

# CI/CD 執行器的 GCP 專案 ID
variable "cicd_runner_project_id" {
  type        = string
  description = "執行 CI/CD 流行的 Google Cloud 專案 ID。"
}

# GCP 資源部署區域
variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域。"
  default     = "us-central1"
}

# Cloud Build 的主機連接名稱
variable "host_connection_name" {
  description = "要在 Cloud Build 中建立的主機連接名稱"
  type        = string
  default     = "pack-auto-insurance-agent-github-connection"
}

# 要連接到 Cloud Build 的儲存庫名稱
variable "repository_name" {
  description = "您想要連接到 Cloud Build 的儲存庫名稱"
  type        = string
}

# 應用程式服務帳號所需的角色清單
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

# CI/CD 專案中分配給 CICD 執行器服務帳號的角色清單
variable "cicd_roles" {
  description = "在 CICD 專案中分配給 CICD 執行器服務帳號的角色清單"
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

# Staging 和 Prod 專案中分配給 CICD 執行器服務帳號的部署角色清單
variable "cicd_sa_deployment_required_roles" {
  description = "分配給 Staging 和 Prod 專案中 CICD 執行器服務帳號的角色清單。"
  type        = list(string)
  default = [
    "roles/run.developer",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin"
  ]
}

# Git 儲存庫擁有者（使用者名稱或組織）
variable "repository_owner" {
  description = "Git 儲存庫的擁有者 - 使用者名稱或組織"
  type        = string
}

# Cloud Build 的 GitHub App 安裝 ID
variable "github_app_installation_id" {
  description = "Cloud Build 的 GitHub App 安裝 ID"
  type        = string
  default     = null
}

# 由 gcloud CLI 建立的 GitHub PAT Secret ID
variable "github_pat_secret_id" {
  description = "由 gcloud CLI 建立的 GitHub PAT Secret ID"
  type        = string
  default     = null
}

# 標記是否已存在 Cloud Build 連接
variable "create_cb_connection" {
  description = "指示 Cloud Build 連接是否已存在的標記"
  type        = bool
  default     = false
}

# 標記是否建立新的 Git 儲存庫
variable "create_repository" {
  description = "指示是否建立新 Git 儲存庫的標記"
  type        = bool
  default     = false
}

# 用於捕獲反饋數據的日誌接收器篩選器
variable "feedback_logs_filter" {
  type        = string
  description = "捕獲反饋數據的日誌接收器 (Log Sink) 篩選器。捕獲 `log_type` 欄位為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"pack-auto-insurance-agent\""
}
