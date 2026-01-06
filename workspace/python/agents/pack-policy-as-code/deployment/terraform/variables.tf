variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名的基礎 (Project name used as a base for resource naming)"
  default     = "pack-policy-as-code"
}

variable "prod_project_id" {
  type        = string
  description = "**Production (生產環境)** Google Cloud Project ID。"
}

variable "staging_project_id" {
  type        = string
  description = "**Staging (預發布環境)** Google Cloud Project ID。"
}

variable "cicd_runner_project_id" {
  type        = string
  description = "CI/CD 流水線執行的 Google Cloud Project ID。"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域 (Region)。"
  default     = "us-central1"
}

variable "host_connection_name" {
  description = "在 Cloud Build 中建立的主機連接名稱 (Name of the host connection to create in Cloud Build)"
  type        = string
  default     = "pack-policy-as-code-github-connection"
}

variable "repository_name" {
  description = "要連接到 Cloud Build 的儲存庫名稱 (Name of the repository you'd like to connect to Cloud Build)"
  type        = string
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

variable "cicd_roles" {
  description = "在 CI/CD 專案中分配給 CI/CD Runner Service Account 的角色列表 (List of roles to assign to the CICD runner service account in the CICD project)"
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
  description = "在 Staging 和 Production 專案中分配給 CI/CD Runner Service Account 的角色列表 (List of roles to assign to the CICD runner service account for the Staging and Prod projects.)"
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
  description = "由 gcloud CLI 建立的 GitHub PAT Secret ID"
  type        = string
  default     = null
}

variable "create_cb_connection" {
  description = "指示 Cloud Build 連接是否已存在的旗標 (Flag indicating if a Cloud Build connection already exists)"
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
  description = "用於捕獲回饋資料的 Log Sink 過濾器 (Log Sink filter for capturing feedback data)。捕獲 `log_type` 為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"pack-policy-as-code\""
}
