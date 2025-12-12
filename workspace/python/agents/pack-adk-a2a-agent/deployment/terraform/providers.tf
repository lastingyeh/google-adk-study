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
# Provider 供應商設定
# ============================================================================
# 此檔案定義 Terraform 所需的版本和 Provider 設定：
# - Google Cloud Provider: 管理 GCP 資源
# - GitHub Provider: 管理 GitHub 資源（儲存庫、Actions secrets/variables）
# - Random Provider: 產生隨機值
#
# 配置了兩個 Google provider 別名，分別用於 staging 和 prod 專案的計費覆寫
# ============================================================================

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.10.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7.0"
    }
  }
}

provider "google" {
  alias                 = "staging_billing_override"
  billing_project       = var.staging_project_id
  region = var.region
  user_project_override = true
}

provider "google" {
  alias                 = "prod_billing_override"
  billing_project       = var.prod_project_id
  region = var.region
  user_project_override = true
}
