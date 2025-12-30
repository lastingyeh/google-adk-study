variable "project_name" {
  type        = string
  description = "專案名稱，用作資源命名的基礎"
  default     = "rag-km-agents"
}

variable "prod_project_id" {
  type        = string
  description = "**Production** 生產環境 Google Cloud 專案 ID，用於資源部署"
}

variable "staging_project_id" {
  type        = string
  description = "**Staging** 測試環境 Google Cloud 專案 ID，用於資源部署"
}

variable "cicd_runner_project_id" {
  type        = string
  description = "執行 CI/CD Pipeline 的 Google Cloud 專案 ID"
}

variable "region" {
  type        = string
  description = "資源部署的 Google Cloud 區域"
  default     = "us-central1"
}

variable "host_connection_name" {
  description = "在 Cloud Build 中建立的主機連接名稱"
  type        = string
  default     = "rag-km-agents-github-connection"
}

variable "repository_name" {
  description = "要連接到 Cloud Build 的儲存庫名稱"
  type        = string
}

variable "app_sa_roles" {
  description = "分配給應用程式服務帳號的角色列表"
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
  description = "分配給 CI/CD 專案中 CI/CD Runner 服務帳號的角色列表"
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
  description = "分配給 Staging 和 Prod 專案中 CI/CD Runner 服務帳號的角色列表"
  type        = list(string)
  default = [
    "roles/run.developer",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
    "roles/storage.admin"
  ]
}



variable "pipeline_cron_schedule" {
  type        = string
  description = "定義自動資料攝取排程的 Cron 表達式"
  default     = "0 0 * * 0" # 每週日 UTC 00:00 執行
}

variable "pipelines_roles" {
  description = "分配給 Vertex AI Pipelines 服務帳號的角色列表"
  type        = list(string)
  default = [
    "roles/storage.admin",
    "roles/aiplatform.user",
    "roles/discoveryengine.admin",
    "roles/logging.logWriter",
    "roles/artifactregistry.writer",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/bigquery.readSessionUser",
    "roles/bigquery.connectionAdmin",
    "roles/resourcemanager.projectIamAdmin"
  ]
}

variable "data_store_region" {
  type        = string
  description = "Data Store 部署區域 (通常為 global 或特定多區域)"
  default     = "us"
}


variable "repository_owner" {
  description = "Git 儲存庫擁有者 - 使用者名稱或組織名稱"
  type        = string
}




variable "create_repository" {
  description = "是否建立新的 Git 儲存庫的旗標"
  type        = bool
  default     = false
}


variable "feedback_logs_filter" {
  type        = string
  description = "用於捕獲回饋資料的 Log Sink 過濾器。捕獲 `log_type` 為 `feedback` 的日誌。"
  default     = "jsonPayload.log_type=\"feedback\" jsonPayload.service_name=\"rag-km-agents\""
}
