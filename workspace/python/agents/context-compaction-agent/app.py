"""啟用 Context Compaction (上下文壓縮) 的 ADK 應用程式配置。"""

from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from context_compaction_agent import root_agent

# 配置上下文壓縮 (Context Compaction)
# 這會自動摘要對話歷史記錄，以減少 Token 使用量
# 流程：
# 1. 初始化 EventsCompactionConfig 物件
# 2. 設定 compaction_interval (壓縮間隔)
# 3. 設定 overlap_size (重疊大小)
compaction_config = EventsCompactionConfig(
    # 在發生多少次新的互動後進行壓縮
    # 每 5 次使用者互動會觸發一次壓縮程序
    compaction_interval=5,
    # 保留多少個先前的互動以維持上下文連續性
    # 保留 1 個舊訊息，確保摘要與最新對話的銜接
    overlap_size=1,
)

# 建立啟用壓縮功能的應用程式
# 流程：
# 1. 實例化 App 物件
# 2. 指定應用程式名稱
# 3. 綁定根代理 (root_agent)
# 4. 傳入 events_compaction_config 以啟用自動壓縮
app = App(
    name="context_compaction_app",
    root_agent=root_agent,
    events_compaction_config=compaction_config,
)

__all__ = ["app"]
