# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，不附帶任何形式的明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理權限和限制的特定語言。
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
    """代表帶有選擇性配置的聊天請求輸入。"""

    message: Content # 使用者發送的訊息內容
    events: list[Event] # 之前的事件歷史列表
    # 使用者 ID，預設生成隨機 UUID
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 工作階段 ID，預設生成隨機 UUID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    model_config = {"extra": "allow"}


class Feedback(BaseModel):
    """代表對對話的回饋數據。"""

    score: int | float # 評分（整數或浮點數）
    text: str | None = "" # 回饋文字內容
    invocation_id: str # 呼叫 ID
    log_type: Literal["feedback"] = "feedback" # 日誌類型
    service_name: Literal["test-agent"] = "test-agent" # 服務名稱
    user_id: str = "" # 使用者 ID
