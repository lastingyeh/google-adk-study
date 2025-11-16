"""
分析代理 - A2A 伺服器 (舊版)

一個專門用於資料分析、統計洞察與量化分析的代理。
作為一個 A2A 伺服器運行於 localhost:9002。
注意：此檔案代表一種較舊的、手動設定 A2A 伺服器的方式，已被官方 ADK 的 `to_a2a()` 函式取代。
保留此檔案僅供參考。

### 程式碼流程註解

#### 核心功能
本腳本的主要功能是手動設定並啟動一個 A2A (Agent-to-Agent) 伺服器。
這個伺服器託管了 `AnalysisAgentExecutor`，使其能夠透過網路接收並處理請求。

#### 運作流程
1.  **技能定義 (`AgentSkill`)**：首先，定義了代理的核心能力，即 `analysis_skill`。
    這包括了技能的 ID、名稱、描述、標籤和使用範例，這些資訊會被公開在代理卡片中。
2.  **代理卡片建立 (`AgentCard`)**：接著，建立了一個 `agent_card` 物件。
    這張卡片是代理的「名片」，包含了代理的名稱、描述、URL、版本、支援的輸入/輸出模式、
    能力 (例如是否支援串流) 以及它所擁有的技能。這是其他代理探索此代理能力的標準方式。
3.  **請求處理器設定 (`DefaultRequestHandler`)**：
    -   建立了一個請求處理器，它將 `AnalysisAgentExecutor` (包含業務邏輯) 與一個 `InMemoryTaskStore` (用於在記憶體中追蹤任務) 連結起來。
    -   這個處理器負責接收傳入的請求，並將其分派給正確的執行器。
4.  **A2A 應用程式建立 (`A2AStarletteApplication`)**：
    -   使用前面建立的 `agent_card` 和 `request_handler` 來建立一個 `A2AStarletteApplication` 實例。
    -   這個物件代表了整個 ASGI 應用程式，它遵循 A2A 通訊協定。
5.  **伺服器啟動 (`uvicorn.run`)**：
    -   最後，使用 `uvicorn` 來運行 `server.build()` 所建立的 ASGI 應用程式。
    -   伺服器會監聽在 `0.0.0.0:9002`，使其可以從本地網路的其他服務存取。
    -   腳本會印出啟動訊息，包括代理卡片的 URL。

### Mermaid 流程圖

```mermaid
graph TD
    A[main() 函式] --> B(定義 AgentSkill);
    B --> C(建立 AgentCard);
    C --> D{建立 DefaultRequestHandler};
    D -- 包含 --> E[AnalysisAgentExecutor];
    D -- 包含 --> F[InMemoryTaskStore];
    D --> G(建立 A2AStarletteApplication);
    G --> H[uvicorn.run];

    subgraph "伺服器啟動"
        H
    end
```
"""

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from .agent_executor import AnalysisAgentExecutor


def main():
    """啟動分析代理 A2A 伺服器。"""

    # 定義分析技能
    analysis_skill = AgentSkill(
        id='analysis',
        name='資料分析與洞察',
        description='分析資料、產生統計洞察並提供量化分析',
        tags=['分析', '資料', '統計', '洞察'],
        examples=[
            '分析市場增長趨勢',
            '提供績效指標分析',
            '為資料集 X 產生統計洞察'
        ],
    )

    # 建立代理卡片
    agent_card = AgentCard(
        name='資料分析代理',
        description='專門用於資料分析、統計洞察與量化研究的代理',
        url='http://localhost:9002/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[analysis_skill],
        supports_authenticated_extended_card=False,
    )

    # 建立請求處理器
    request_handler = DefaultRequestHandler(
        agent_executor=AnalysisAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # 建立並啟動 A2A 伺服器
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    print("🚀 正在於 http://localhost:9002 啟動分析代理 A2A 伺服器")
    print("📊 代理專門從事資料分析與統計洞察")
    print("🔗 代理卡片位於：http://localhost:9002/.well-known/agent.json")

    uvicorn.run(server.build(), host='0.0.0.0', port=9002)


if __name__ == '__main__':
    main()
