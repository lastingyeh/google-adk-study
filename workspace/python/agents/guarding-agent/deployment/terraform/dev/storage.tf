# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Terraform 設定：開發環境存儲資源 (Dev Storage)
# 此檔案定義了開發環境中用於日誌存儲的 Cloud Storage Bucket

provider "google" {
  region                = var.region
  user_project_override = true
}

# 建立開發環境專用的日誌資料儲存桶 (Bucket)
resource "google_storage_bucket" "logs_data_bucket" {
  name                        = "${var.dev_project_id}-${var.project_name}-logs"
  location                    = var.region
  project                     = var.dev_project_id
  uniform_bucket_level_access = true # 啟用統一儲存桶層級存取權限

  depends_on = [resource.google_project_service.services]
}

/*
重點摘要：
- 核心概念：為開發環境配置專屬的資料存放空間。
- 關鍵技術：Cloud Storage (GCS).
- 重要結論：確保開發階段產生的日誌與數據有獨立的存儲位置，與其他環境隔離。
*/
