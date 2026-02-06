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

locals {
  project_ids = {
    dev = var.dev_project_id
  }
}


# 獲取 Dev 專案的專案編號
# Get the project number for the dev project
data "google_project" "dev_project" {
  project_id = var.dev_project_id
}

# 授予預設運算服務帳戶 Storage Object Creator 角色
# Grant Storage Object Creator role to default compute service account
resource "google_project_iam_member" "default_compute_sa_storage_object_creator" {
  project    = var.dev_project_id
  role       = "roles/cloudbuild.builds.builder"
  member     = "serviceAccount:${data.google_project.dev_project.number}-compute@developer.gserviceaccount.com"
  depends_on = [resource.google_project_service.services]
}

# Agent 服務帳戶
# Agent service account
resource "google_service_account" "app_sa" {
  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent Service Account"
  project      = var.dev_project_id
  depends_on   = [resource.google_project_service.services]
}

# 授予應用程式服務帳戶 (Application SA) 執行應用程式所需的權限
# Grant application SA the required permissions to run the application
resource "google_project_iam_member" "app_sa_roles" {
  for_each = {
    for pair in setproduct(keys(local.project_ids), var.app_sa_roles) :
    join(",", pair) => {
      project = local.project_ids[pair[0]]
      role    = pair[1]
    }
  }

  project    = each.value.project
  role       = each.value.role
  member     = "serviceAccount:${google_service_account.app_sa.email}"
  depends_on = [resource.google_project_service.services]
}

# 重點摘要
# - **核心概念**：Dev 環境 IAM 設定
# - **關鍵技術**：IAM Roles, Service Accounts
# - **重要結論**：配置 Dev 環境的權限，包括 Compute SA 和 App SA。
# - **行動項目**：無
