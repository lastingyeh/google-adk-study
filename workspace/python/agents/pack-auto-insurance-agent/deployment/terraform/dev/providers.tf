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
# 請參閱本授權以了解管理權限和限制的特定語言。

/*
## 重點摘要
- **核心概念**：定義開發環境所需的 Terraform 與 Provider 版本，並設置開發專用的 Google Provider。
- **關鍵技術**：Terraform `required_providers`, `provider` 別名, `user_project_override`。
- **重要結論**：確保開發環境的資源操作能正確連結到開發專案的帳單帳戶。
- **行動項目**：確認已正確填寫 `dev_project_id`。
*/

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

# 開發環境的 Google Provider，啟用帳單專案覆蓋
provider "google" {
  alias                 = "dev_billing_override"
  billing_project       = var.dev_project_id
  region = var.region
  user_project_override = true
}
