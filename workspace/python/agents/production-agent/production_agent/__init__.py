"""
生產環境部署代理套件 (Production deployment agent package)。
"""

from .agent import root_agent

__all__ = ["root_agent"]

"""
重點摘要:
- **核心概念**: 生產環境部署代理的套件入口點
- **關鍵技術**: Python 模組匯出 (__all__)
- **重要結論**: 將 root_agent 作為主要接口暴露給外部使用
"""
