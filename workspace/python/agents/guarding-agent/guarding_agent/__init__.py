"""
AI 代理防護系統（Guarding Agent System）

多層防護架構：
- 階段一：靜態過濾機制（Static Filtering）
- 階段二：高風險操作人工審核（Human-in-the-Loop）
- 階段三：智能安全審核層（Intelligent Review）
- 階段四：維運監控與優化（Monitoring & Optimization）
"""

__version__ = "0.1.0"

from . import plugins
from .agent import root_agent

__all__ = ["root_agent", "plugins"]
