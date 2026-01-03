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
    """表示帶有可選配置的對話請求輸入。"""

    # 訊息內容
    message: Content
    # 事件清單
    events: list[Event]
    # 使用者 ID，預設隨機生成一個 UUID
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 會話 ID，預設隨機生成一個 UUID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    model_config = {"extra": "allow"}


class Feedback(BaseModel):
    """表示對話的回饋資訊。"""

    # 評分（整數或浮點數）
    score: int | float
    # 評論文字內容
    text: str | None = ""
    # 調用 ID，用於關聯特定的回應
    invocation_id: str
    # 日誌類型，固定為 "feedback"
    log_type: Literal["feedback"] = "feedback"
    # 服務名稱，固定為 "pack-customer-service"
    service_name: Literal["pack-customer-service"] = "pack-customer-service"
    # 使用者 ID
    user_id: str = ""
