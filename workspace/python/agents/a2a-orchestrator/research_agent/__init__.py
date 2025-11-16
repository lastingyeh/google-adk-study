"""
研究代理套件

用於研究與資訊收集的 A2A 伺服器實作。
注意：此為舊版 A2A 實作的一部分。
"""

# 從 .agent_executor 模組匯入 ResearchAgentExecutor 類別。
# 這使得套件的使用者可以更容易地存取這個類別。
from .agent_executor import ResearchAgentExecutor

# __all__ 變數定義了當使用 'from research_agent import *' 時，
# 應該匯入哪些公開的物件。在這裡，我們只公開 ResearchAgentExecutor。
__all__ = ['ResearchAgentExecutor']
