# 版權所有 2026 Google LLC
#
# 根據 Apache License 2.0 版本（「授權」）授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在以下網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權散佈的軟體
# 是按「原樣」散佈的，不附任何明示或暗示的保證或條件。
# 請參閱授權以了解管理授權下權限和限制的特定語言。

"""
### 模組說明
此模組定義了系統中使用的資料類型與 Pydantic 模型，主要用於使用者回饋 (Feedback) 的資料結構化。

### 重點摘要
- **核心概念**：提供結構化的資料模型以確保資料驗證與一致性。
- **關鍵技術**：Pydantic `BaseModel`, `Field`, `Literal` 類型提示。
- **重要結論**：使用 Pydantic 模型可以簡化 FastAPI 的請求解析，並自動產生符合規範的 JSON 結構。
- **行動項目**：在 API 端點中使用 `Feedback` 模型接收使用者回饋。
"""

import uuid
from typing import (
    Literal,
)

from pydantic import (
    BaseModel,
    Field,
)


class Feedback(BaseModel):
    """代表一次對話的回饋資訊模型。"""

    # 評分分數（整數或浮點數）
    score: int | float
    # 回饋文字內容（可選）
    text: str | None = ""
    # 日誌類型，固定為 "feedback"
    log_type: Literal["feedback"] = "feedback"
    # 服務名稱，固定為 "guarding-agent"
    service_name: Literal["guarding-agent"] = "guarding-agent"
    # 使用者 ID，預設自動生成 UUID
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 工作階段 ID，預設自動生成 UUID
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
