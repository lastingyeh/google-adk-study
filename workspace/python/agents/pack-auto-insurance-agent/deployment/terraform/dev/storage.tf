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
- **核心概念**：在開發 (Dev) 環境專案中建立 Cloud Storage 儲存桶以存儲日誌。
- **關鍵技術**：Cloud Storage Bucket。
- **重要結論**：為開發環境提供了獨立的日誌存儲空間，確保開發階段的數據不會與生產環境混淆。
- **行動項目**：確保 `dev_project_id` 填寫正確以避免命名衝突。
*/

provider "google" {
  region = var.region
  user_project_override = true
}

# 建立開發環境專用的日誌數據儲存桶
resource "google_storage_bucket" "logs_data_bucket" {
  name                        = "${var.dev_project_id}-${var.project_name}-logs"
  location                    = var.region
  project                     = var.dev_project_id
  uniform_bucket_level_access = true

  depends_on = [resource.google_project_service.services]
}