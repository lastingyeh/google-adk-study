# Literal 和 Field 的用途說明：

# 1. Literal (來自 typing 模組)
# Literal 是一個型別提示 (Type Hint)，用於限制變數必須是特定的幾個值之一。
# 用途：枚舉限定。它告訴 Pydantic，這個欄位只能接受你列出的那些具體數值（字串、整數等）。
# 驗證：如果輸入的值不在 Literal 列表內，Pydantic 會拋出驗證錯誤。

# 2. Field (來自 pydantic 模組)
# Field 用於提供欄位的額外資訊或更複雜的驗證規則。
# 用途：
# 設置預設值 (default)。
# 定義數值限制（如 gt 大於, le 小於等於）。
# 定義字串限制（如 min_length, max_length, pattern 正規表達式）。

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
    代表聊天請求的輸入，包含可選的設定。
    """

    message: Content  # 訊息內容
    events: list[Event]  # 事件列表
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 使用者 ID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 會話 ID

    model_config = {"extra": "allow"}  # 允許額外欄位


class Feedback(BaseModel):
    """
    代表對話的回饋。
    """

    score: int | float  # 分數
    text: str | None = ""  # 回饋文字
    log_type: Literal["feedback"] = "feedback"  # 日誌類型
    service_name: Literal["pack-policy-as-code"] = "pack-policy-as-code"  # 服務名稱
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 使用者 ID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 會話 ID
