"""Support Bot Agent - 課程 33: Slack 機器人與 ADK 整合 (Tutorial 33: Slack Bot Integration with ADK)

此模組匯出了用於與 Slack Bolt 整合的 root_agent。
該 Agent 提供團隊支援功能，包括知識庫搜尋與工單建立。
"""

from support_bot.agent import root_agent

__all__ = ["root_agent"]

# 重點摘要 (__init__.py)
# - 核心概念：模組初始化檔案，負責匯出主要的 Agent 物件。
# - 關鍵技術：Python 模組封裝 (Module encapsulation)。
# - 重要結論：將 `root_agent` 暴露給外部模組 (如 `bot.py` 或 `__main__.py`) 使用，簡化了匯入路徑。
