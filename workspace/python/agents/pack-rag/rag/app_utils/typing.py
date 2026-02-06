# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，無任何明示 or 暗示的保證或條件。
# 請參閱許可證以了解管理權限和許可證下的限制。

"""
### 摘要
本檔案定義了應用程式使用的資料類型與 Pydantic 模型，包括聊天請求（Request）與使用者回饋（Feedback）。

### 核心重點
- **核心概念**：定義 API 的輸入與回饋資料結構。
- **關鍵技術**：Pydantic, UUID, Google GenAI Types。
- **重要結論**：使用 Pydantic 模型確保資料驗證的一致性，並自動產生 UUID 作為使用者與會話識別碼。
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
    """代表聊天請求的輸入資料，包含選用配置。"""

    message: Content  # 使用者的訊息內容
    events: list[Event]  # 事件列表
    user_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )  # 使用者 ID，預設為隨機 UUID
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )  # 會話 ID，預設為隨機 UUID

    model_config = {"extra": "allow"}  # 允許額外欄位


class Feedback(BaseModel):
    """代表對對話的回饋資料。"""

    score: int | float  # 評分（整數或浮點數）
    text: str | None = ""  # 回饋文字內容
    log_type: Literal["feedback"] = "feedback"  # 日誌類型，固定為 "feedback"
    service_name: Literal["pack-rag"] = "pack-rag"  # 服務名稱，固定為 "pack-rag"
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 使用者 ID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 會話 ID
