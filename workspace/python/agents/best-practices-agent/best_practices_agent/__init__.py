"""
最佳實踐代理 - 生產就緒模式 (Best Practices Agent - Production-Ready Patterns)

本模組展示了建置生產就緒代理的綜合最佳實踐，包括：
- 安全性 (Security)：輸入驗證、錯誤處理
- 效能 (Performance)：快取、批次處理
- 可靠性 (Reliability)：重試邏輯、斷路器
- 可觀測性 (Observability)：指標、健康檢查
"""

from .agent import root_agent

__all__ = ["root_agent"]

# 重點摘要 (Code Summary)
# - **核心概念**：模組初始化檔案，匯出 `root_agent` 以供外部使用。
# - **關鍵技術**：Python 模組化 (Modules)。
# - **重要結論**：簡化套件的匯入路徑，提供統一的進入點。
# - **行動項目**：無。
