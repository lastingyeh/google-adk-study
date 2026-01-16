# Copyright 2025 Google LLC
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

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# 從 app 目錄中的 .env 檔案載入環境變數
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# 驗證設定:
# 預設情況下，使用 .env 檔案中的 GOOGLE_API_KEY 使用 AI Studio。
# 若要改用 Vertex AI，請在 .env 中設定 GOOGLE_GENAI_USE_VERTEXAI=TRUE
# 並確保已配置 Google Cloud 憑證。

if os.getenv("GOOGLE_API_KEY"):
    # AI Studio 模式（預設）:使用 API 金鑰驗證
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
else:
    # Vertex AI 模式:回退到 Google Cloud 憑證
    import google.auth
    # google.auth.default() 可能傳回 None 作為 project_id，但 setdefault 需要 str 類型。
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "")
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class ResearchConfiguration:
    """研究相關模型和參數的設定。

    屬性:
        critic_model (str): 用於評估任務的模型。
        worker_model (str): 用於工作/生成任務的模型。
        max_search_iterations (int): 允許的最大搜尋迭代次數。
    """

    critic_model: str = "gemini-3-pro-preview"
    worker_model: str = "gemini-3-pro-preview"
    max_search_iterations: int = 5


# 建立全域設定實例
config = ResearchConfiguration()

