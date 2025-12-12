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
# 開發環境 Provider 設定
# ============================================================================
# 此檔案定義開發環境所需的 Terraform Provider：
# - Google Cloud Provider: 管理 GCP 資源
# - Random Provider: 產生隨機值
#
# 注意：開發環境不需要 GitHub Provider，因為通常是本地部署
# ============================================================================

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.10.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7.0"
    }
  }
}

provider "google" {
  alias                 = "dev_billing_override"
  billing_project       = var.dev_project_id
  region = var.region
  user_project_override = true
}
