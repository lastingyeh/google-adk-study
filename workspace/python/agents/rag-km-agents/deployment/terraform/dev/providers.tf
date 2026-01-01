terraform {
  # 指定 Terraform 最低版本要求
  required_version = ">= 1.0.0"

  # 定義所需的 Providers 及其版本
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

# 為 Dev 環境設定 Google Provider
# 使用 user_project_override = true 來確保配額 (Quota) 計費歸屬正確
provider "google" {
  alias                 = "dev_billing_override"
  billing_project       = var.dev_project_id
  region                = var.region
  user_project_override = true
}
