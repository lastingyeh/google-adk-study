"""包含代理（Agent）的所有共享程式庫。"""

import os

import google.auth

# 獲取預設的 Google 認證資訊與專案 ID
_, project_id = google.auth.default()

# 設定環境變數，確保 Google Cloud 相關配置正確
# 設定 Google Cloud 專案 ID
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
# 設定 Google Cloud 區域為全域（global）
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
# 預設啟用 Vertex AI 作為 Google GenAI 的後端
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# 匯入內部的 agent 模組
from . import agent

# 定義公開導出的模組成員
__all__ = ["agent"]
