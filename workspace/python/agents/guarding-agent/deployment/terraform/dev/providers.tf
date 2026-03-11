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

# Terraform 設定：開發環境提供者配置 (Dev Providers)
# 此檔案定義了開發環境所需的 Terraform 版本以及相關提供者設定

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.13.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.37.0"
    }
  }
}

# 為開發環境 (Dev) 設定專屬的 Google 提供者別名
provider "google" {
  alias                 = "dev_billing_override"
  billing_project       = var.dev_project_id
  region                = var.region
  user_project_override = true
}

# 獲取 Google 用戶端的配置資訊（如存取權杖）
data "google_client_config" "default" {}

# 配置 Kubernetes 提供者以與 GKE 叢集互動
provider "kubernetes" {
  host                   = "https://${google_container_cluster.app.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.app.master_auth[0].cluster_ca_certificate)
}

/*
重點摘要：
- 核心概念：配置開發環境特有的基礎架構提供者。
- 關鍵技術：Terraform Providers, Kubernetes Provider Auth, Google Client Config.
- 重要結論：透過整合 Google 與 Kubernetes 提供者，實現對 GKE 叢集的自動化管理。
*/
