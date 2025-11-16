"""
分析代理執行器 - A2A 伺服器實作 (舊版)

此代理專門從事資料分析、統計洞察與量化研究。
注意：此檔案代表一種較舊的、手動的 A2A 實作方式，已被官方 ADK 的 `to_a2a()` 函式取代。
保留此檔案僅供參考。

### 程式碼流程註解

#### 核心功能
本腳本定義了 `AnalysisAgent` 和 `AnalysisAgentExecutor` 兩個類別，
用於手動處理 A2A 請求。這是一種在 `to_a2a()` 函式出現之前的實作模式。

-   **AnalysisAgent**：包含代理的核心業務邏輯。`invoke` 方法根據查詢中的關鍵字，
    模擬資料分析過程並回傳格式化的報告字串。
-   **AnalysisAgentExecutor**：作為 A2A 伺服器與代理邏輯之間的橋樑。
    `execute` 方法負責從傳入的請求 (`RequestContext`) 中提取查詢文字，
    呼叫 `AnalysisAgent` 的 `invoke` 方法，然後將結果封裝成一個新的代理訊息，
    並將其放入事件佇列 (`EventQueue`) 中以回傳給呼叫者。

#### 運作流程
1.  **請求接收**：A2A 伺服器 (未在此檔案中定義，但會使用此執行器) 接收到一個請求。
2.  **執行器觸發**：伺服器呼叫 `AnalysisAgentExecutor` 的 `execute` 方法，並傳入請求上下文和事件佇列。
3.  **查詢提取**：`execute` 方法從 `context.message` 中解析出使用者傳送的查詢文字。
4.  **邏輯呼叫**：執行器實例化 `AnalysisAgent` 並呼叫其 `invoke` 方法，傳入查詢。
5.  **結果生成**：`AnalysisAgent` 根據查詢內容，非同步地 (模擬) 生成一份分析報告。
6.  **回應排隊**：`execute` 方法使用 `new_agent_text_message` 工具函式將報告文字打包成標準的代理訊息格式。
7.  **事件發送**：最後，將此訊息放入 `event_queue`，A2A 伺服器會將其發送回給協調器。
8.  **錯誤與取消**：`execute` 方法包含錯誤處理邏輯，`cancel` 方法則處理任務取消的請求。

### Mermaid 流程圖

```mermaid
sequenceDiagram
    participant Server as A2A 伺服器
    participant Executor as AnalysisAgentExecutor
    participant Agent as AnalysisAgent
    participant Queue as EventQueue

    Server->>Executor: execute(context, event_queue)
    Executor->>Agent: invoke(query)
    Agent-->>Executor: result (分析報告)
    Executor->>Queue: enqueue_event(message)
    Queue-->>Server: 傳送事件
```
"""

import asyncio
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


class AnalysisAgent:
    """分析代理，執行資料分析並產生洞察。"""

    async def invoke(self, query: str = "") -> str:
        """處理分析查詢並回傳洞察。"""
        # 模擬分析過程的延遲
        await asyncio.sleep(0.7)

        # 根據查詢中的關鍵字回傳不同的模擬報告
        if "growth" in query.lower() or "trend" in query.lower():
            return """
            資料分析報告：增長趨勢

            ## 執行摘要
            全面的趨勢分析揭示了顯著的增長模式與新興機會。

            ## 關鍵指標
            - **增長率**：年同比增長 28%
            - **市場滲透率**：目標市場區隔中達到 67% 的採用率
            - **績效指標**：所有 KPI 皆呈現正向軌跡

            ## 統計分析
            ### 趨勢模式
            - **線性增長**：每月持續增長 5-7%
            - **季節性變化**：第四季度通常有 15% 的增長
            - **市場波動性**：標準差較低 (±3%)

            ### 預測模型
            - **6 個月預測**：預計將持續上升趨勢
            - **信賴區間**：預測準確率達 95%
            - **風險因素**：已識別的下行風險極小

            ## 比較分析
            - **基準績效**：比行業平均水平高出 23%
            - **競爭地位**：保持強勁的市場領導地位
            - **市場份額**：在分析期間內增加了 12%

            ## 建議
            1. **持續投資**：維持目前的增長策略
            2. **擴展營運**：為增加的需求做好準備
            3. **監控指標**：建立即時追蹤系統

            *此分析基於全面的資料模型與統計方法。*"""

        elif "performance" in query.lower() or "metric" in query.lower():
            return """
            績效分析報告

            ## 績效總覽
            對關鍵績效指標與營運指標的詳細分析。

            ## 核心指標分析
            ### 營運效率
            - **處理速度**：比基準提升 34%
            - **錯誤率**：降至 0.08% (行業標準：0.15%)
            - **正常運行時間**：維持 99.97% 的可用性

            ### 使用者參與度
            - **滿意度分數**：4.7/5.0
            - **留存率**：每月留存率 92%
            - **使用模式**：每日活躍使用者佔 78%

            ## 統計洞察
            ### 績效分佈
            - **頂尖四分位**：45% 的指標超過目標
            - **中位數績效**：比基準高出 12%
            - **待改進區域**：有 3 個指標需要關注

            ### 相關性分析
            - **強正相關**：使用者滿意度 ↔ 績效 (r=0.89)
            - **中度相關**：使用量 ↔ 效率 (r=0.67)
            - **關鍵驅動因素**：品質與速度是主要因素

            ## 可執行的洞察
            1. **優化流程**：專注於已識別的瓶頸
            2. **提升品質**：投資於降低錯誤率的措施
            3. **使用者體驗**：優先考慮滿意度的驅動因素

            *全面的績效分析與統計驗證。*"""

        elif query:
            return f"""
            分析報告：{query}

            ## 資料分析摘要
            已對請求的主題進行了嚴謹的統計分析。

            ## 主要發現
            - **主要洞察**：在資料中識別出顯著的模式
            - **統計顯著性**：結果在 95% 的信賴水準下得到驗證
            - **趨勢分析**：觀察到明確的方向性指標

            ## 量化結果
            ### 指標總覽
            - **績效指數**：高於基準預期
            - **相關強度**：識別出強烈的關聯性
            - **變異數分析**：核心指標波動性低

            ### 預測模型
            - **預測準確性**：對預測有高度信心
            - **風險評估**：不利結果的風險極小
            - **機會分析**：識別出多個增長途徑

            ## 策略性意涵
            1. **資料驅動決策**：證據支持策略方向
            2. **資源分配**：根據分析洞察進行優化
            3. **績效監控**：建立持續的測量框架

            *此分析使用先進的統計方法與行業最佳實踐進行。*"""
        else:
            return """
            資料分析代理已就緒

            我專門從事資料分析、統計洞察與量化研究。請提供具體的資料或指標以進行詳細的統計洞察與建議。"""


class AnalysisAgentExecutor(AgentExecutor):
    """分析代理的 A2A 代理執行器。"""

    def __init__(self):
        """初始化執行器，並建立一個 AnalysisAgent 實例。"""
        self.agent = AnalysisAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """執行分析任務。"""
        try:
            # 從請求的 message 中提取查詢文字
            query = ""
            if context.message and context.message.parts:
                for part in context.message.parts:
                    # 處理 A2A SDK 的 Part 結構
                    part_data = part
                    if hasattr(part, 'root'):
                        part_data = part.root

                    if hasattr(part_data, 'text') and part_data.text:
                        query += part_data.text

            # 呼叫代理的核心邏輯來處理分析查詢
            result = await self.agent.invoke(query)

            # 將結果封裝成一個新的文字訊息事件
            message = new_agent_text_message(result)
            # 將事件放入佇列中，以發送回呼叫者
            await event_queue.enqueue_event(message)

        except Exception as e:
            # 如果發生錯誤，發送一個錯誤訊息
            error_message = new_agent_text_message(f"分析失敗：{str(e)}")
            await event_queue.enqueue_event(error_message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """取消目前的分析任務。"""
        # 發送一個取消確認訊息
        message = new_agent_text_message("分析任務已取消")
        await event_queue.enqueue_event(message)
