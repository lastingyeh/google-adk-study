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

"""
### 重點摘要 (程式碼除外)
- **核心概念**：定義了 AI 代理人系統中通訊所需的資料結構（Data Schema），包含請求（Request）與反饋（Feedback）。
- **關鍵技術**：
    - **Pydantic (BaseModel)**：用於資料驗證與結構化管理。
    - **UUID**：用於生成唯一的身分識別碼，確保對話追蹤的準確性。
    - **Python Typing**：使用 `Literal` 與 `Union` (管道符號 `|`) 進行嚴格的類型檢查。
- **重要結論**：該模組標準化了前端與後端之間的資料交換格式，確保了系統的可擴充性與健壯性。
- **行動項目**：
    - 在調用 API 時，請確保傳入的 `message` 與 `events` 符合對應的類型定義。
"""

import uuid
from typing import (
    Literal,
)

from google.adk.events.event import Event
from google.genai.types import Content
from pydantic import (
    BaseModel,
    Field,
)


class Request(BaseModel):
    """
    表示聊天請求的輸入，包含選擇性的配置。
    """

    # 訊息內容 (Content)
    message: Content
    # 事件列表 (Event List)
    events: list[Event]
    # 使用者識別碼 (User ID)，預設產生一個隨機的 UUID
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 會話識別碼 (Session ID)，預設產生一個隨機的 UUID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # 允許額外的模型屬性
    model_config = {"extra": "allow"}


class Feedback(BaseModel):
    """
    表示對話的反饋。
    """

    # 評分 (Score)，可以是整數或浮點數
    score: int | float
    # 反饋文字 (Text)，可為空
    text: str | None = ""
    # 日誌類型 (Log Type)，固定為 "feedback"
    log_type: Literal["feedback"] = "feedback"
    # 服務名稱 (Service Name)，固定為汽車保險代理人名稱
    service_name: Literal["pack-auto-insurance-agent"] = "pack-auto-insurance-agent"
    # 使用者識別碼 (User ID)，預設產生隨機 UUID
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 會話識別碼 (Session ID)，預設產生隨機 UUID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
