# Terraform 設定：提供者配置 (Providers)
# 此檔案定義了所需的 Terraform 版本以及要使用的提供者 (Google, GitHub, Random)

terraform {
  required_version = ">= 1.0.0" # 要求 Terraform 版本至少為 1.0.0
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.13.0" # Google Cloud 提供者版本
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.5.0" # GitHub 提供者版本
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7.0" # 隨機數提供者版本
    }
  }
}

# 為測試環境 (Staging) 設定專屬的 Google 提供者別名
# 用於覆蓋計費專案與地區設定
provider "google" {
  alias                 = "staging_billing_override"
  billing_project       = var.staging_project_id
  region                = var.region
  user_project_override = true
}

# 為生產環境 (Prod) 設定專屬的 Google 提供者別名
provider "google" {
  alias                 = "prod_billing_override"
  billing_project       = var.prod_project_id
  region                = var.region
  user_project_override = true
}