# 從 .agent 模組匯入 root_agent
# 這使得 a2a_orchestrator 套件的使用者可以直接從套件層級存取 root_agent，
# 例如：from a2a_orchestrator import root_agent
from .agent import root_agent

# __all__ 變數定義了當使用 'from a2a_orchestrator import *' 時，
# 應該匯入哪些公開的物件。在這裡，我們只公開 root_agent。
__all__ = ['root_agent']
