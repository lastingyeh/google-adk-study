"""TIL 的工具使用品質 (Tool Use Quality) 評估代理 (Agent)。

此模組展示了如何使用 ADK 的「基於評量表的工具使用品質」指標
(Rubric Based Tool Use Quality metric) 來評估代理的工具使用情況。
"""

from .agent import root_agent

__all__ = ["root_agent"]
