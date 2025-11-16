"""
研究代理執行器 - A2A 伺服器實作 (舊版)

此代理專門從事研究、事實查核與資訊收集。
注意：此檔案代表一種較舊的、手動的 A2A 實作方式，已被官方 ADK 的 `to_a2a()` 函式取代。
保留此檔案僅供參考。

### 程式碼流程註解

#### 核心功能
本腳本定義了 `ResearchAgent` 和 `ResearchAgentExecutor` 兩個類別，
用於手動處理 A2A 研究請求。

-   **ResearchAgent**：包含代理的核心業務邏輯。`invoke` 方法根據查詢中的關鍵字
    (例如 "quantum", "ai")，模擬研究過程並回傳帶有引用來源的摘要報告。
-   **ResearchAgentExecutor**：作為 A2A 伺服器與代理邏輯之間的中介。
    `execute` 方法負責從傳入的請求中提取查詢文字，呼叫 `ResearchAgent` 的 `invoke` 方法，
    然後將研究結果封裝成標準的代理訊息，並將其放入事件佇列以回傳給呼叫者。

#### 運作流程
1.  **請求接收與解析**：A2A 伺服器 (未在此檔案中定義) 接收請求並觸發 `ResearchAgentExecutor` 的 `execute` 方法。
2.  **查詢提取**：`execute` 方法從 `context.message` 中解析出使用者查詢。
3.  **邏輯呼叫**：執行器呼叫 `ResearchAgent` 的 `invoke` 方法。
4.  **研究模擬**：`ResearchAgent` 根據查詢模擬生成對應的研究結果。
5.  **回應封裝與發送**：`execute` 方法將生成的文字內容打包成一個新的代理訊息，並透過 `event_queue` 發送出去。
6.  **錯誤與取消處理**：與其他執行器類似，此類別也包含了處理錯誤和取消請求的方法。

### Mermaid 流程圖

```mermaid
sequenceDiagram
    participant Server as A2A 伺服器
    participant Executor as ResearchAgentExecutor
    participant Agent as ResearchAgent
    participant Queue as EventQueue

    Server->>Executor: execute(context, event_queue)
    Executor->>Agent: invoke(query)
    Agent-->>Executor: result (研究報告)
    Executor->>Queue: enqueue_event(message)
    Queue-->>Server: 傳送事件
```
"""

import asyncio

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


class ResearchAgent:
    """研究代理，負責收集與分析資訊。"""

    async def invoke(self, query: str = "") -> str:
        """處理研究查詢並回傳研究發現。"""
        # 模擬研究過程的延遲
        await asyncio.sleep(0.5)

        if "quantum" in query.lower():
            return """
            量子計算研究結果：

            基於全面的網路研究：

            1. **當前趨勢**：量子計算在興新技術的推動下呈現顯著增長。
            2. **主要發現**：
            - 主要科技公司 (Google, IBM, Microsoft) 已擁有可運作的量子電腦。
            - 錯誤修正仍是關鍵挑戰，但已取得進展。
            - 混合式量子-傳統演算法正展現出實際應用價值。
            3. **來源**：已檢閱學術論文、行業報告與專家分析。
            4. **結論**：發展勢頭強勁，未來在量子優勢方面有著光明的發展前景。

            **引用文獻**：
            [1] Google 量子 AI 研究論文 (2024)
            [2] IBM 量子發展報告 2024 年第四季度
            [3] 《麻省理工科技評論》 - 量子計算特刊"""

        elif "ai" in query.lower() or "artificial intelligence" in query.lower():
            return """
            人工智慧研究結果：

            基於全面的網路研究：

            1. **當前趨勢**：AI 在各行各業的採用正在加速。
            2. **主要發現**：
            - 預計到 2030 年，生成式 AI 市場將達到 1.3 兆美元。
            - 企業 AI 支出同比增長 30%。
            - 基礎模型變得更容易取得且更專業化。
            3. **來源**：行業報告、學術研究、市場分析。
            4. **結論**：AI 轉型正在進行中，並帶來顯著的經濟影響。

            **引用文獻**：
            [1] 麥肯錫全球 AI 調查 2024
            [2] Gartner AI 市場報告 2024 年第四季度
            [3] 史丹佛 AI 指數年度報告"""

        elif query:
            return f"""
            {query} 的研究結果：

            基於全面的網路研究：

            1. **當前趨勢**：該領域顯示出顯著的增長與創新。
            2. **主要發現**：多個來源指出採用與發展日益增加。
            3. **來源**：已檢閱學術論文、行業報告與專家分析。
            4. **結論**：發展勢頭強勁，未來有著光明的發展前景。

            **引用文獻**：[1] 2025 年研究論文, [2] 2025 年第一季度行業報告, [3] 專家分析"""
        else:
            return """
            研究代理已就緒

            我專門從事研究、事實查核與資訊收集。請提供具體的研究查詢以獲得帶有引用的詳細發現。"""


class ResearchAgentExecutor(AgentExecutor):
    """研究代理的 A2A 代理執行器。"""

    def __init__(self):
        self.agent = ResearchAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """執行研究任務。"""
        try:
            # 從請求訊息中提取查詢
            query = ""
            if context.message and context.message.parts:
                for part in context.message.parts:
                    # 處理 A2A SDK 的 Part 結構
                    part_data = part
                    if hasattr(part, 'root'):
                        part_data = part.root

                    if hasattr(part_data, 'text') and part_data.text:
                        query += part_data.text

            # 處理研究查詢
            result = await self.agent.invoke(query)

            # 將結果作為文字訊息發送
            message = new_agent_text_message(result)
            await event_queue.enqueue_event(message)

        except Exception as e:
            # 發送錯誤訊息
            error_message = new_agent_text_message(f"研究失敗：{str(e)}")
            await event_queue.enqueue_event(error_message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """取消目前的研究任務。"""
        # 發送取消確認訊息
        message = new_agent_text_message("研究任務已取消")
        await event_queue.enqueue_event(message)
