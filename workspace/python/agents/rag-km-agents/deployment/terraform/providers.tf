terraform {
  # 指定 Terraform 最低版本要求
  required_version = ">= 1.0.0"

  # 定義所需的 Providers 及其版本
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.13.0"
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

# 為 Staging 環境設定 Google Provider
# 使用 user_project_override = true 來確保配額 (Quota) 計費歸屬正確
provider "google" {
  alias                 = "staging_billing_override"
  billing_project       = var.staging_project_id
  region                = var.region
  user_project_override = true
}

# 為 Production 環境設定 Google Provider
# 使用 user_project_override = true 來確保配額 (Quota) 計費歸屬正確
provider "google" {
  alias                 = "prod_billing_override"
  billing_project       = var.prod_project_id
  region                = var.region
  user_project_override = true
}
