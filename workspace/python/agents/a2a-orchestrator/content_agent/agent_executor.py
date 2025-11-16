"""
內容代理執行器 - A2A 伺服器實作 (舊版)

此代理專門從事內容創作、寫作與摘要。
注意：此檔案代表一種較舊的、手動的 A2A 實作方式，已被官方 ADK 的 `to_a2a()` 函式取代。
保留此檔案僅供參考。

### 程式碼流程註解

#### 核心功能
本腳本定義了 `ContentAgent` 和 `ContentAgentExecutor` 兩個類別，
用於手動處理 A2A 內容創作請求。

-   **ContentAgent**：包含代理的核心業務邏輯。`invoke` 方法根據查詢中的關鍵字
    (例如 "summary", "article")，模擬內容創作過程並回傳格式化的 Markdown 字串。
-   **ContentAgentExecutor**：作為 A2A 伺服器與代理邏輯之間的中介。
    `execute` 方法負責從傳入的請求中提取查詢文字，呼叫 `ContentAgent` 的 `invoke` 方法，
    然後將生成的內容封裝成標準的代理訊息，並將其放入事件佇列以回傳給呼叫者。

#### 運作流程
1.  **請求接收與解析**：A2A 伺服器 (未在此檔案中定義) 接收請求並觸發 `ContentAgentExecutor` 的 `execute` 方法。
2.  **查詢提取**：`execute` 方法從 `context.message` 中解析出使用者查詢。
3.  **邏輯呼叫**：執行器呼叫 `ContentAgent` 的 `invoke` 方法。
4.  **內容生成**：`ContentAgent` 根據查詢模擬生成對應的內容 (摘要或文章)。
5.  **回應封裝與發送**：`execute` 方法將生成的文字內容打包成一個新的代理訊息，並透過 `event_queue` 發送出去。
6.  **錯誤與取消處理**：與分析代理執行器類似，此類別也包含了處理錯誤和取消請求的方法。

### Mermaid 流程圖

```mermaid
sequenceDiagram
    participant Server as A2A 伺服器
    participant Executor as ContentAgentExecutor
    participant Agent as ContentAgent
    participant Queue as EventQueue

    Server->>Executor: execute(context, event_queue)
    Executor->>Agent: invoke(query)
    Agent-->>Executor: result (書面內容)
    Executor->>Queue: enqueue_event(message)
    Queue-->>Server: 傳送事件
```
"""

import asyncio
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


class ContentAgent:
    """內容代理，創作書面內容與摘要。"""

    async def invoke(self, query: str) -> str:
        """處理內容創作查詢並回傳書面內容。"""
        # 模擬內容創作過程的延遲
        await asyncio.sleep(0.5)

        if "summary" in query.lower() or "executive" in query.lower():
            return """# 執行摘要

## 總覽

本綜合分析旨在檢視技術領域的現狀與未來前景。我們的研究指出，在這個快速發展的領域中，存在著顯著的增長與創新機會。

## 主要發現

- **市場機會**：已識別出巨大的增長潛力，預計年均複合增長率 (CAGR) 為 22%
- **技術趨勢**：新興解決方案在企業採用方面顯示出潛力
- **競爭格局**：幾個主要參與者正在積極創新並佔領市場份額

## 策略性意涵

組織應考慮在此領域進行策略性投資，重點關注：
- 技術的採用與整合
- 人才發展與培訓
- 合作夥伴關係與生態系統建設

## 結論

分析顯示前景樂觀，並有明確的成功策略方向。早期投資這些技術的公司很可能獲得顯著的競爭優勢。

## 建議

1. **立即行動**：在 3-6 個月內啟動試點計畫
2. **中期目標**：在 12-18 個月內實現全面生產部署
3. **長期願景**：在不斷變化的市場中建立領導地位

*本摘要基於全面的研究與行業分析。*"""

        elif "article" in query.lower() or "blog" in query.lower():
            return """# 技術的未來：趨勢與創新

## 前言

在技術飛速發展的時代，理解新興趨勢對於尋求維持競爭優勢的組織至關重要。本文探討了塑造我們未來的關鍵技術趨勢及其對商業和社會的潛在影響。

## 當前技術格局

### 人工智慧與機器學習

AI 和 ML 技術的擴散持續加速，應用範圍從自動化客戶服務到預測性分析。組織越來越認識到 AI 不僅僅是一個工具，而是一個策略性的必要條件。

### 雲端計算的演進

雲端技術已從基礎的基礎設施服務成熟為提供 AI、分析和邊緣計算能力的複雜平台。向多雲和混合策略的轉變反映了對靈活性和韌性的需求。

### 邊緣計算與物聯網

物聯網 (IoT) 設備的增長以及對即時處理的需求推動了邊緣計算的採用。這種分散式計算範式使處理更接近資料來源，從而減少延遲和頻寬需求。

## 新興趨勢

### 量子計算

雖然仍處於早期階段，但量子計算有望解決目前傳統電腦無法解決的複雜問題。製藥、材料科學和金融模型等行業將從中顯著受益。

### 永續技術

環保意識正在推動綠色技術的創新，從節能計算到碳中和資料中心。組織越來越多地根據其環境影響來評估技術解決方案。

### 人機協作

未來不在於取代人類工作者，而在於增強其能力。能夠在維持道德標準的同時提高人類生產力的技術將是關鍵的差異化因素。

## 策略性考量

### 投資優先順序

組織應專注於與其策略目標一致的技術，同時建立能夠適應未來變化的靈活平台。

### 技能與人才

技術格局需要新的技能。組織必須投資於培訓和發展，為其勞動力迎接未來做好準備。

### 道德與負責任的創新

隨著技術變得越來越強大，確保道德的開發和部署變得至關重要。組織應建立明確的指導方針和治理框架。

## 結論

技術格局正以前所未有的速度發展。擁抱變革、投資於正確的技術並發展必要技能的組織將最有能力在這個充滿活力的環境中茁壯成長。

成功不僅取決於採用新技術，還取決於將其深思熟慮地整合到組織文化和流程中。"""

        else:
            return """# 內容摘要

## 執行總覽

本綜合分析旨在檢視所調查主題的現狀與未來前景。我們的研究指出，在此領域存在顯著的增長與創新機會。

## 主要發現

- **市場機會**：已識別出巨大的增長潛力
- **技術趨勢**：新興解決方案顯示出潛力
- **競爭格局**：幾個主要參與者正在積極創新

## 策略性意涵

組織應考慮在此領域進行策略性投資，重點關注技術採用和市場定位。

## 結論

分析顯示前景樂觀，並有明確的成功策略方向。

*此內容基於全面的研究與分析生成。*"""


class ContentAgentExecutor(AgentExecutor):
    """內容代理的 A2A 代理執行器。"""

    def __init__(self):
        self.agent = ContentAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """執行內容創作任務。"""
        try:
            # 從請求中提取查詢
            query = ""
            if context.message and context.message.parts:
                for part in context.message.parts:
                    # 處理 A2A SDK 中可能存在的巢狀 root 結構
                    part_data = part
                    if hasattr(part, 'root'):
                        part_data = part.root

                    if hasattr(part_data, 'text'):
                        query += part_data.text

            if not query:
                query = "一般內容創作查詢"

            # 處理內容創作查詢
            result = await self.agent.invoke(query)

            # 將結果作為文字訊息發送
            message = new_agent_text_message(result)
            await event_queue.enqueue_event(message)

        except Exception as e:
            # 發送錯誤訊息
            error_message = new_agent_text_message(f"內容創作失敗：{str(e)}")
            await event_queue.enqueue_event(error_message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """取消目前的內容創作任務。"""
        # 發送取消確認訊息
        message = new_agent_text_message("內容創作任務已取消")
        await event_queue.enqueue_event(message)
