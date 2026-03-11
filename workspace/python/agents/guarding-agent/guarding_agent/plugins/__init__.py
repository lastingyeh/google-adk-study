"""
防護系統外掛程式模組 (Guarding System Plugins)

本模組提供多層安全防護插件：
- ContentFilterPlugin: 靜態關鍵字過濾 (Static Keyword Filtering)
- PIIDetectionPlugin: 敏感資訊偵測與處理 (PII Detection & Handling)
- SecurityMetricsPlugin: 安全指標收集 (Security Metrics Collection)

### 模組說明
此檔案為插件目錄的入口，整合並匯出了所有的安全防護插件。

### 重點摘要
- **核心概念**：模組化安全功能，以便在執行器中靈活組合。
- **關鍵技術**：插件模式 (Plugin Pattern)。
- **重要結論**：集中管理安全功能可提升系統的可維護性。
- **行動項目**：在 `agent.py` 中引用此模組以載入插件。
"""

# 匯入具體的插件類別
from .content_filter_plugin import ContentFilterPlugin
from .pii_detection_plugin import PIIDetectionPlugin

# 定義模組導出清單
__all__ = [ContentFilterPlugin, PIIDetectionPlugin]
