# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，無任何明示或暗示的保證或條件。
# 請參閱許可證以了解管理權限和許可證下的限制。

"""
### 摘要
本檔案為 `rag` 套件的初始化程式碼，主要負責設定 Google Cloud 環境變數，確保 Agent 能夠正確連接到 Vertex AI 服務。

### 重點摘要
- **核心概念**：初始化 RAG 模組的環境組態。
- **關鍵技術**：使用 `google.auth` 自動獲取專案 ID，並設定系統環境變數。
- **重要結論**：確保所有 RAG 相關操作都在正確的專案與區域下執行。
- **行動項目**：確認環境中已配置正確的 Google Cloud 認證 (ADC)。
"""

import os

import google.auth

from . import agent as agent

# 初始化 Google Auth 並設定專案 ID
_, project_id = google.auth.default()

# 設定環境變數
# 1. 設定 Google Cloud 專案 ID (Project ID)
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "")

# 2. 設定 Google Cloud 區域 (Location)，預設為 global
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

# 3. 預設啟動 Vertex AI 的 Generative AI 功能
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
