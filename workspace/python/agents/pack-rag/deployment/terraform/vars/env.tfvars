# 用於資源命名的專案名稱
# Project name used for resource naming
project_name = "pack-rag"

# 您的正式環境 (Production) Google Cloud 專案 ID
# Your Production Google Cloud project id
prod_project_id = "your-production-project-id"

# 您的預備/測試環境 (Staging/Test) Google Cloud 專案 ID
# Your Staging / Test Google Cloud project id
staging_project_id = "your-staging-project-id"

# 將用於託管 Cloud Build 流程的 Google Cloud 專案 ID
# Your Google Cloud project ID that will be used to host the Cloud Build pipelines.
cicd_runner_project_id = "your-cicd-project-id"
# 您在 Cloud Build 中建立的主機連線名稱
# Name of the host connection you created in Cloud Build
host_connection_name = "git-pack-rag"
github_pat_secret_id = "your-github_pat_secret_id"

repository_owner = "Your GitHub organization or username."

# 您新增到 Cloud Build 的儲存庫名稱
# Name of the repository you added to Cloud Build
repository_name = "pack-rag"

# 您將用於部署基礎架構的 Google Cloud 區域
# The Google Cloud region you will use to deploy the infrastructure
region = "us-central1"

# 重點摘要
# - **核心概念**：環境變數設定
# - **關鍵技術**：Terraform tfvars
# - **重要結論**：設定正式與預備環境部署所需的具體參數值。
# - **行動項目**：使用者需填入實際的專案 ID 與 GitHub 資訊。
