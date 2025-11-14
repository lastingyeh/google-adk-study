"""
串流代理套件（Tutorial 14）

本套件提供建置與操作「可逐步輸出」AI 串流代理的工具，透過 Server-Sent Events (SSE)
即時傳送增量內容。適用於示範、效能評測，以及整合至更大型的對話或處理流程。

主要功能 (Functions Overview):
- root_agent：協調請求的基礎入口點（根代理）。
- create_streaming_agent：建立並配置具備串流能力的代理工廠函式。
- stream_agent_response：生成適合 SSE 傳輸的增量（分段）輸出。
- get_complete_response：彙整所有串流片段為最終整合結果。
- create_demo_session：建立示範 / 測試用互動工作階段。
- format_streaming_info：格式化串流過程的中繼資料與統計資訊供記錄或顯示。
- analyze_streaming_performance：分析時間、吞吐量與效率等指標。

使用情境 (Usage Scenarios):
1. 即時介面更新（例：網頁儀表板、聊天應用）。
2. 逐步生成以提升回應速度與使用者感知。
3. 評估串流與非串流生成效能差異。

設計理念 (Design Notes):
- 職責分離：建立、串流、格式化與分析模組化。
- 可擴充性：可疊加自訂記錄、快取或轉換流程。
- 可觀察性：效能分析協助調整分段大小、延遲與緩衝策略。

快速開始 (Quick Start Outline):
1. 先呼叫 create_streaming_agent(...) 取得代理實例。
2. 使用 stream_agent_response(...) 迭代取得部分輸出。
3. 需要完整結果時可用 get_complete_response(...) 收集。
4. 結束後以 analyze_streaming_performance(...) 檢視指標。

回傳資料型態 (Data Characteristics):
- 串流輸出可為字典、文字片段或結構化物件（取決於代理設定）。
- 效能分析通常回傳包含時間、計數與衍生統計的字典。

注意事項 (Notes / Caveats):
- 若部署於 Web，請確保 HTTP 層支援 SSE。
- 串流迴圈中避免阻塞操作以維持回應性。
- 過度細碎的記錄可能影響吞吐效能。

擴充建議 (Extension Ideas):
- 為不穩定上游模型加入重試機制。
- 依消費端讀取速度自適性調節節流。
- 整合追蹤（如 OpenTelemetry）以掌握端到端延遲。

Tutorial 14: 串流代理套件

本套件示範使用 Server-Sent Events (SSE) 進行即時、漸進式回應輸出。
"""

from .agent import (
    root_agent,
    create_streaming_agent,
    stream_agent_response,
    get_complete_response,
    create_demo_session,
    format_streaming_info,
    analyze_streaming_performance
)

__all__ = [
    'root_agent',
    'create_streaming_agent',
    'stream_agent_response',
    'get_complete_response',
    'create_demo_session',
    'format_streaming_info',
    'analyze_streaming_performance'
]