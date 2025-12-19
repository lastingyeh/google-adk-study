"""支援暫停/恢復調用 (Pause/Resume Invocation) 的 ADK App 配置。"""

from google.adk.apps import App, ResumabilityConfig
from pause_resume_agent import root_agent

# 配置可恢復調用 (Resumable Invocations)
# 這讓 Agent 能夠支援暫停/恢復功能
resumability_config = ResumabilityConfig(
    # 為此 App 的調用啟用暫停/恢復支援
    is_resumable=True,
)

# 建立已啟用可恢復調用支援的 App
app = App(
    name="pause_resume_app",
    root_agent=root_agent,
    resumability_config=resumability_config,
)

__all__ = ["app"]

"""
重點摘要
- 核心概念：透過 ResumabilityConfig 啟用 App 級別的暫停與恢復功能。
- 關鍵技術：使用 is_resumable=True 參數來配置 App 物件。
- 重要結論：這是實現檢查點 (Checkpoint) 儲存與狀態還原的必要配置。
- 行動項目：確保 root_agent 正確匯入，並在生產環境中驗證 is_resumable 設定。
"""
