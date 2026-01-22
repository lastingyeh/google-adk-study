# Copyright 2025 Google LLC
#
# 根據 Apache License 2.0 版本（「本授權」）授權；
# 除非遵守本授權，否則您不得使用此檔案。
# 您可以在以下網址獲得本授權的副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據本授權分發的軟體
# 是按「現狀」基礎分發的，無任何明示或暗示的保證或條件。
# 請參閱本授權以了解管理權限 and 限制的特定語言。

/*
## 重點摘要
- **核心概念**：定義所需的 Terraform 版本、Provider 依賴以及 Google Provider 的別名 (Alias) 設定。
- **關鍵技術**：Terraform `required_providers`, `provider` 別名, `user_project_override`。
- **重要結論**：通過別名設定，可以在特定資源操作時覆蓋預設的帳單專案，這對於跨專案資源管理至關重要。
- **行動項目**：確保安裝了符合版本要求的 Terraform 執行環境。
*/

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

# 測試環境的 Google Provider，啟用帳單專案覆蓋
provider "google" {
  alias                 = "staging_billing_override"
  billing_project       = var.staging_project_id
  region = var.region
  user_project_override = true
}

# 生產環境的 Google Provider，啟用帳單專案覆蓋
provider "google" {
  alias                 = "prod_billing_override"
  billing_project       = var.prod_project_id
  region = var.region
  user_project_override = true
}
