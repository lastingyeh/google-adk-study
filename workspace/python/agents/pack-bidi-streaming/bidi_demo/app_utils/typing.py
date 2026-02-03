# 版權所有 2026 Google LLC
#
# 根據 Apache License, Version 2.0（以下簡稱「授權」）授權。
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在下列網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權分發的軟體是以「現狀」提供，
# 不附帶任何明示或暗示的擔保或條件。
# 請參閱授權以了解授權下的特定語言及限制。
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



# 聊天請求的輸入資料模型，包含可選的設定。
class Request(BaseModel):
    """
    代表聊天請求的輸入資料，包含訊息內容、事件列表、使用者 ID 與會話 ID。
    user_id 與 session_id 預設會自動產生唯一識別碼。
    """

    message: Content  # 聊天訊息內容
    events: list[Event]  # 事件列表
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 使用者唯一識別碼
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 會話唯一識別碼

    model_config = {"extra": "allow"}  # 允許額外欄位



# 對話回饋資料模型。
class Feedback(BaseModel):
    """
    代表對話的回饋資訊。
    包含分數、文字回饋、日誌類型、服務名稱、使用者 ID 與會話 ID。
    user_id 與 session_id 預設會自動產生唯一識別碼。
    """

    score: int | float  # 回饋分數，可為整數或浮點數
    text: str | None = ""  # 回饋文字，可為空字串
    log_type: Literal["feedback"] = "feedback"  # 日誌類型，固定為 'feedback'
    service_name: Literal["pack-bidi-streaming"] = "pack-bidi-streaming"  # 服務名稱，固定為 'pack-bidi-streaming'
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 使用者唯一識別碼
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 會話唯一識別碼
