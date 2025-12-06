
"""Commerce Agent - A specialized e-commerce assistant using Google ADK. (商務代理人 - 使用 Google ADK 的專門電子商務助理)

This agent handles (此代理人處理):
- Product searches and recommendations (產品搜尋與推薦)
- Price comparisons (價格比較)
- Technical specifications (技術規格)
- Delivery information (運送資訊)
- User preferences management (使用者偏好管理)

The agent uses Google Search for grounding (source attribution) and maintains
user preferences across sessions.
代理人使用 Google Search 進行接地 (來源歸因) 並跨會話維護使用者偏好。
"""

from .agent import root_agent
from .callbacks import create_grounding_callback
from .types import ToolResult, UserPreferences, GroundingMetadata, GroundingSource

__all__ = [
    "root_agent",
    "create_grounding_callback",
    "ToolResult",
    "UserPreferences",
    "GroundingMetadata",
    "GroundingSource",
]
