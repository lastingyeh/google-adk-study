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
  }
}

# 設定 Google Cloud 提供者別名，用於開發環境計費覆寫
# 使用 dev_project_id 進行計費
provider "google" {
  alias                 = "dev_billing_override"
  billing_project       = var.dev_project_id
  region                = var.region
  user_project_override = true
}
