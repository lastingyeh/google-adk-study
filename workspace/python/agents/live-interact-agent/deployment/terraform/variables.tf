variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名的基礎"
  default     = "live-interact-agent"
}

variable "prod_project_id" {
  type        = string
  description = "用於資源部署的 **生產環境 (Production)** Google Cloud 專案 ID"
}

variable "staging_project_id" {
  type        = string
  description = "用於資源部署的 **測試環境 (Staging)** Google Cloud 專案 ID"
}

variable "cicd_runner_project_id" {
  type        = string
  description = "將執行 CI/CD 管線的 Google Cloud 專案 ID"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域"
  default     = "us-central1"
}

variable "host_connection_name" {
  description = "要在 Cloud Build 中建立的主機連線名稱"
  type        = string
  default     = "live-interact-agent-github-connection"
}

variable "repository_name" {
  description = "您想要連接到 Cloud Build 的儲存庫名稱"
  type        = string
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

variable "cicd_roles" {
  description = "要指派給 CI/CD 專案中的 CI/CD 執行器服務帳戶的角色列表"
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
  description = "要指派給測試環境和生產環境專案中的 CI/CD 執行器服務帳戶的角色列表"
  type        = list(string)
  default = [
    "roles/run.developer",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin"
  ]
}


variable "repository_owner" {
  description = "Git 儲存庫的擁有者 - 使用者名稱或組織名稱"
  type        = string
}


variable "github_app_installation_id" {
  description = "Cloud Build 的 GitHub App 安裝 ID"
  type        = string
  default     = null
}


variable "github_pat_secret_id" {
  description = "由 gcloud CLI 建立的 GitHub PAT Secret ID"
  type        = string
  default     = null
}

variable "create_cb_connection" {
  description = "指示 Cloud Build 連線是否已存在的旗標"
  type        = bool
  default     = false
}

variable "create_repository" {
  description = "指示是否建立新 Git 儲存庫的旗標"
  type        = bool
  default     = false
}


variable "feedback_logs_filter" {
  type        = string
  description = "用於擷取回饋資料的 Log Sink 過濾器。擷取 `log_type` 欄位為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"live-interact-agent\""
}
