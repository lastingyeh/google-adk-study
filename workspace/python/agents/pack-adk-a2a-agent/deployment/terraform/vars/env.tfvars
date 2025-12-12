# ============================================================================
# Terraform 變數設定檔（正式環境）
# ============================================================================
# 此檔案包含正式環境（Staging 和 Production）的實際變數值
# 使用方式：terraform plan -var-file="vars/env.tfvars"
#
# 請將以下佔位值替換為您的實際值：
# - your-production-project-id: 您的正式環境 GCP 專案 ID
# - your-staging-project-id: 您的測試環境 GCP 專案 ID
# - your-cicd-project-id: 您的 CI/CD 專案 ID
# - Your GitHub organization or username: GitHub 組織或使用者名稱
# ============================================================================

# 專案名稱，用於資源命名
project_name = "pack-adk-a2a-agent"

# Your Production Google Cloud project id
prod_project_id = "your-production-project-id"

# Your Staging / Test Google Cloud project id
staging_project_id = "your-staging-project-id"

# Your Google Cloud project ID that will be used to host the Cloud Build pipelines.
cicd_runner_project_id = "your-cicd-project-id"

repository_owner = "Your GitHub organization or username."

# Name of the repository you added to Cloud Build
repository_name = "pack-adk-a2a-agent"

# The Google Cloud region you will use to deploy the infrastructure
region = "us-central1"
