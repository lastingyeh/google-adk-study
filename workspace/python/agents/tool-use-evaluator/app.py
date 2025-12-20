"""具有工具使用品質 (Tool Use Quality) 評估的 ADK 應用程式配置。"""

from google.adk.apps import App
from tool_use_evaluator import root_agent

# 建立具有工具使用評估代理 (Agent) 的應用程式
app = App(
    name="tool_use_quality_app",
    root_agent=root_agent,
)

__all__ = ["app"]
