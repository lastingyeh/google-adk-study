# Terraform 設定：變數宣告 (Variables)
# 此檔案定義了基礎架構配置中使用的所有輸入參數

variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名基礎"
  default     = "guarding-agent"
}

variable "prod_project_id" {
  type        = string
  description = "**生產環境 (Production)** 部署資源的 Google Cloud 專案 ID"
}

variable "staging_project_id" {
  type        = string
  description = "**測試環境 (Staging)** 部署資源的 Google Cloud 專案 ID"
}

variable "cicd_runner_project_id" {
  type        = string
  description = "執行 CI/CD 流水線的 Google Cloud 專案 ID"
}

variable "region" {
  type        = string
  description = "部署資源的 Google Cloud 區域"
  default     = "us-central1"
}

variable "host_connection_name" {
  description = "要在 Cloud Build 中建立的主機連線名稱"
  type        = string
  default     = "guarding-agent-github-connection"
}

variable "repository_name" {
  description = "要連接至 Cloud Build 的儲存庫名稱"
  type        = string
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

variable "cicd_roles" {
  description = "指派給 CI/CD Runner 服務帳戶在 CI/CD 專案中的角色列表"
  type        = list(string)
  default = [
    "roles/container.developer",
    "roles/storage.admin",
    "roles/aiplatform.user",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/artifactregistry.writer",
    "roles/cloudbuild.builds.builder"
  ]
}

variable "cicd_sa_deployment_required_roles" {
  description = "指派給 CI/CD Runner 服務帳戶在 Staging 和 Prod 專案中的角色列表"
  type        = list(string)
  default = [
    "roles/container.developer",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin"
  ]
}

variable "repository_owner" {
  description = "Git 儲存庫擁有者 - 使用者名稱或組織"
  type        = string
}

variable "github_app_installation_id" {
  description = "Cloud Build 的 GitHub App 安裝 ID"
  type        = string
  default     = null
}

variable "github_pat_secret_id" {
  description = "透過 gcloud CLI 建立的 GitHub PAT 密鑰 ID"
  type        = string
  default     = null
}

variable "create_cb_connection" {
  description = "標記 Cloud Build 連線是否已存在"
  type        = bool
  default     = false
}

variable "create_repository" {
  description = "是否建立新的 Git 儲存庫"
  type        = bool
  default     = false
}

variable "feedback_logs_filter" {
  type        = string
  description = "用於捕獲回饋數據的日誌接收器過濾器。捕獲 `log_type` 欄位為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"guarding-agent\""
}
