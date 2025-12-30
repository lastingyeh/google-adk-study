# 用於資源命名的專案名稱
project_name = "rag-km-agents"

# 您的生產環境 Google Cloud 專案 ID
prod_project_id = "your-production-project-id"

# 您的預備/測試環境 Google Cloud 專案 ID
staging_project_id = "your-staging-project-id"

# 將用於託管 Cloud Build 管線的 Google Cloud 專案 ID
cicd_runner_project_id = "your-cicd-project-id"

repository_owner = "您的 GitHub 組織或使用者名稱。"

# 您新增至 Cloud Build 的儲存庫名稱
repository_name = "rag-km-agents"

# 您將用來部署基礎設施的 Google Cloud 區域
region                 = "us-central1"
pipeline_cron_schedule = "0 0 * * 0"
# 此值只能是 "global"、"us" 或 "eu" 其中之一。
data_store_region = "us"
