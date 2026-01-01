terraform {
  required_version = ">= 1.0.0"
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

# 設定 Google Cloud 提供者別名，用於測試環境計費覆寫
# 使用 staging_project_id 進行計費
provider "google" {
  alias                 = "staging_billing_override"
  billing_project       = var.staging_project_id
  region                = var.region
  user_project_override = true
}

# 設定 Google Cloud 提供者別名，用於生產環境計費覆寫
# 使用 prod_project_id 進行計費
provider "google" {
  alias                 = "prod_billing_override"
  billing_project       = var.prod_project_id
  region                = var.region
  user_project_override = true
}
