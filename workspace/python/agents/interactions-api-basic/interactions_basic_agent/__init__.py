# Interactions API 基礎代理 (Basic Agent)
# 展示核心 Interactions API 功能

from .agent import (
    create_basic_interaction,
    create_stateful_conversation,
    create_streaming_interaction,
    create_function_calling_interaction,
    get_client,
    SUPPORTED_MODELS,
)

from .tools import (
    get_weather_tool,
    calculate_tool,
    AVAILABLE_TOOLS,
)

__all__ = [
    "create_basic_interaction",
    "create_stateful_conversation",
    "create_streaming_interaction",
    "create_function_calling_interaction",
    "get_client",
    "get_weather_tool",
    "calculate_tool",
    "SUPPORTED_MODELS",
    "AVAILABLE_TOOLS",
]

"""
=== 重點摘要 ===
- **核心概念**：模組導出定義
- **關鍵技術**：Python 套件初始化
- **重要結論**：集中管理對外公開的函數與變數，簡化導入流程
- **行動項目**：無
"""
