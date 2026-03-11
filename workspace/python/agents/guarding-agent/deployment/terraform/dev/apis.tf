# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Terraform 設定：開發環境 API 服務 (Dev APIs)
# 此檔案定義了開發環境專案中需要啟用的 Google Cloud 服務介面

locals {
  # 開發專案需要啟用的服務列表
  services = [
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com"
  ]
}

# 啟用上述定義的所有服務
resource "google_project_service" "services" {
  count              = length(local.services)
  project            = var.dev_project_id
  service            = local.services[count.index]
  disable_on_destroy = false
}

# 為 Vertex AI 建立服務識別身分 (Service Identity)
resource "google_project_service_identity" "vertex_sa" {
  provider = google-beta
  project  = var.dev_project_id
  service  = "aiplatform.googleapis.com"
}

/*
重點摘要：
- 核心概念：為開發環境配置必要的 API 存取權限。
- 關鍵技術：Terraform Locals, `google_project_service`, `google_project_service_identity`.
- 重要結論：集中管理開發環境所需的服務，確保環境建置的一致性。
*/
