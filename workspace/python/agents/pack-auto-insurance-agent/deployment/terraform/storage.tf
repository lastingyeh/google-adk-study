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
- **核心概念**：配置用於存儲日誌的 Cloud Storage Bucket 以及用於管理容器鏡像的 Artifact Registry。
- **關鍵技術**：Cloud Storage, Artifact Registry, Docker 格式。
- **重要結論**：為每個相關專案都建立了一個日誌桶，並在 CI/CD 專案中建立了一個中心化的 Artifact Registry 儲存庫。
- **行動項目**：確認儲存桶名稱在全域上是唯一的。
*/
provider "google" {
  region = var.region
  user_project_override = true
}

# 為所有專案建立日誌數據存儲桶 (Bucket)
resource "google_storage_bucket" "logs_data_bucket" {
  for_each                    = toset(local.all_project_ids)
  name                        = "${each.value}-${var.project_name}-logs"
  location                    = var.region
  project                     = each.value
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}

# 建立 Artifact Registry 儲存庫以存放 Docker 鏡像
resource "google_artifact_registry_repository" "repo-artifacts-genai" {
  location      = var.region
  repository_id = "${var.project_name}-repo"
  description   = "用於生成式 AI 應用程式的儲存庫"
  format        = "DOCKER"
  project       = var.cicd_runner_project_id
  depends_on    = [resource.google_project_service.cicd_services, resource.google_project_service.deploy_project_services]
}
