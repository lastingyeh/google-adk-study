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

# Google Provider 配置：Staging 環境計費覆寫
# 用於確保在 Staging 專案的操作計費歸屬於 Staging 專案
provider "google" {
  alias                 = "staging_billing_override"
  billing_project       = var.staging_project_id
  region = var.region
  user_project_override = true
}

# Google Provider 配置：Production 環境計費覆寫
# 用於確保在 Production 專案的操作計費歸屬於 Production 專案
provider "google" {
  alias                 = "prod_billing_override"
  billing_project       = var.prod_project_id
  region = var.region
  user_project_override = true
}
