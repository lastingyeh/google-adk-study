# ============================================================================
# Terraform 變數設定檔（開發環境）
# ============================================================================
# 此檔案包含開發環境的實際變數值
# 使用方式：terraform plan -var-file="dev/vars/env.tfvars"
#
# 開發環境簡化了配置，只需要單一專案 ID
# 請將 "your-dev-project-id" 替換為您的開發環境 GCP 專案 ID
# ============================================================================

# 專案名稱，用於資源命名
project_name = "pack-adk-a2a-agent"

# Your Dev Google Cloud project id
dev_project_id = "your-dev-project-id"

# The Google Cloud region you will use to deploy the infrastructure
region = "us-central1"
