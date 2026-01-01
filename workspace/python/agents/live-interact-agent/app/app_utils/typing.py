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
    """表示具有可選配置的聊天請求輸入模型。"""

    # 訊息內容，使用 GenAI 的 Content 類型
    message: Content
    # 事件列表
    events: list[Event]
    # 使用者 ID，預設為隨機生成的 UUID
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 工作階段 ID，預設為隨機生成的 UUID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # 允許額外的欄位
    model_config = {"extra": "allow"}


class Feedback(BaseModel):
    """表示對話的回饋模型。"""

    # 回饋分數
    score: int | float
    # 回饋文字內容 (可選)
    text: str | None = ""
    # 日誌類型，固定為 "feedback"
    log_type: Literal["feedback"] = "feedback"
    # 服務名稱，固定為 "live-interact-agent"
    service_name: Literal["live-interact-agent"] = "live-interact-agent"
    # 使用者 ID
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 工作階段 ID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
