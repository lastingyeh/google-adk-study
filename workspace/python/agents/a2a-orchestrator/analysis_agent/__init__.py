"""
分析代理套件

用於資料分析與統計洞察的 A2A 伺服器實作。
注意：此為舊版 A2A 實作的一部分。
"""

# 從 .agent_executor 模組匯入 AnalysisAgentExecutor 類別。
# 這使得套件的使用者可以更容易地存取這個類別。
from .agent_executor import AnalysisAgentExecutor

# __all__ 變數定義了當使用 'from analysis_agent import *' 時，
# 應該匯入哪些公開的物件。在這裡，我們只公開 AnalysisAgentExecutor。
__all__ = ['AnalysisAgentExecutor']
