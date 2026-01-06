

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

# Google Provider 配置：Dev 環境計費覆寫
# 用於確保在 Dev 專案的操作計費歸屬於 Dev 專案
provider "google" {
  alias                 = "dev_billing_override"
  billing_project       = var.dev_project_id
  region = var.region
  user_project_override = true
}
