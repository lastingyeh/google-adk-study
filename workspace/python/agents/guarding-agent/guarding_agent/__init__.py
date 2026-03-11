"""
AI 代理防護系統（Guarding Agent System）

多層防護架構：
- 階段一：靜態過濾機制（Static Filtering）
- 階段二：高風險操作人工審核（Human-in-the-Loop）
- 階段三：智能安全審核層（Intelligent Review）
- 階段四：維運監控與優化（Monitoring & Optimization）

### 翻譯內容
此檔案主要定義了 AI 代理防護系統的套件入口，展示了其分層防護的設計藍圖。

### 重點摘要
- **核心概念**：提供多層次 AI 代理安全防護架構（Guarding Agent System）。
- **關鍵技術**：靜態過濾（Static Filtering）、人工審核（Human-in-the-Loop）、智能審核（Intelligent Review）、維運監控（Monitoring & Optimization）。
- **重要結論**：透過分層防護確保 AI 代理在各種應用場景下的安全與合規。
- **行動項目**：初始化核心代理並載入防護插件。
"""

__version__ = "0.1.0"

# 匯入插件與核心代理 (Agent)
from . import plugins
from .agent import root_agent

# 定義模組導出清單
__all__ = ["plugins", "root_agent"]
