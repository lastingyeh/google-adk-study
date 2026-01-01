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
    """代表一個聊天請求的輸入，包含可選的配置。"""

    message: Content
    events: list[Event]
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    model_config = {"extra": "allow"}


class Feedback(BaseModel):
    """代表對話的回饋。"""

    score: int | float
    text: str | None = ""
    log_type: Literal["feedback"] = "feedback"
    service_name: Literal["rag-km-agents"] = "rag-km-agents"
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
