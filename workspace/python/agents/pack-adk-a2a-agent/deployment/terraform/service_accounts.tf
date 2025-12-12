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
# 服務帳號 (Service Accounts) 建立
# ============================================================================
# 此檔案建立系統所需的服務帳號：
# - cicd_runner_sa: CI/CD 流水線使用的服務帳號
# - app_sa: 應用程式執行時使用的服務帳號（為 staging 和 prod 各建立一個）
#
# 這些服務帳號將在 iam.tf 中被授予適當的權限
# ============================================================================

# CI/CD 流水線服務帳號
resource "google_service_account" "cicd_runner_sa" {
  account_id   = "${var.project_name}-cb"
  display_name = "CICD Runner SA"
  project      = var.cicd_runner_project_id
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
# Agent service account
resource "google_service_account" "app_sa" {
  for_each = local.deploy_project_ids

  account_id   = "${var.project_name}-app"
  display_name = "${var.project_name} Agent Service Account"
  project      = each.value
  depends_on   = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
