# Copyright 2025 Google LLC
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

# ============================================================================
# 開發環境 Google Cloud API 服務啟用
# ============================================================================
# 此檔案啟用開發環境所需的 GCP API 服務：
# - AI Platform: AI 模型和推論
# - Cloud Build: 建構容器映像
# - Cloud Run: 部署容器化應用程式
# - BigQuery: 遙測資料分析
# - Discovery Engine: 搜尋和推薦功能
# - Cloud Logging: 日誌記錄
# - Cloud Trace: 分散式追蹤
#
# 也建立 Vertex AI 服務身份以便服務正常運作
# ============================================================================

locals {
  services = [
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "bigquery.googleapis.com",
    "discoveryengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
  ]
}

resource "google_project_service" "services" {
  count              = length(local.services)
  project            = var.dev_project_id
  service            = local.services[count.index]
  disable_on_destroy = false
}

resource "google_project_service_identity" "vertex_sa" {
  provider = google-beta
  project = var.dev_project_id
  service = "aiplatform.googleapis.com"
}
