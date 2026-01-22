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

# 重點摘要
/*
#- **核心概念**：在 CI/CD 專案中啟用必要的 Google Cloud API 服務。
- **關鍵技術**：Terraform `google_project_service`, `for_each` 迴圈。
- **重要結論**：集中管理所需的雲端服務，確保部署流程中所有依賴的 API 都已正確開啟。
- **行動項目**：確保執行帳號具備在專案中啟用服務的權限。
*/

# 初始化 Google Cloud 服務
resource "google_project_service" "apis" {
  for_each = toset([
    "aiplatform.googleapis.com",      # Vertex AI API
    "cloudbuild.googleapis.com",      # Cloud Build API
    "iam.googleapis.com",             # IAM API
    "run.googleapis.com",             # Cloud Run API
    "secretmanager.googleapis.com",   # Secret Manager API
    "storage.googleapis.com",         # Cloud Storage API
    "compute.googleapis.com",         # Compute Engine API
    "artifactregistry.googleapis.com", # Artifact Registry API
    "cloudresourcemanager.googleapis.com" # Cloud Resource Manager API
  ])
  project            = var.cicd_runner_project_id
  service            = each.key
  disable_on_destroy = false
}
