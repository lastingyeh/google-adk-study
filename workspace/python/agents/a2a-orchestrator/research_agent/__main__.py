"""
研究代理 - A2A 伺服器 (舊版)

一個專門用於研究、資訊收集與事實查核的代理。
作為一個 A2A 伺服器運行於 localhost:9001。
注意：此檔案代表一種較舊的、手動設定 A2A 伺服器的方式，已被官方 ADK 的 `to_a2a()` 函式取代。
保留此檔案僅供參考。

### 程式碼流程註解

#### 核心功能
本腳本的主要功能是手動設定並啟動一個用於研究代理的 A2A (Agent-to-Agent) 伺服器。
其結構與其他兩個代理的 `__main__.py` 檔案非常相似，但專為研究代理的技能和執行器而設定。

#### 運作流程
1.  **技能定義 (`AgentSkill`)**：定義了代理的核心能力，即 `research_skill`，
    包括其 ID、名稱、描述、標籤和使用範例。
2.  **代理卡片建立 (`AgentCard`)**：建立 `agent_card` 物件，詳細說明代理的元數據，
    如名稱、描述、URL、版本、能力和技能。
3.  **請求處理器設定 (`DefaultRequestHandler`)**：
    -   建立一個請求處理器，將 `ResearchAgentExecutor` (包含研究邏輯) 與 `InMemoryTaskStore` 連結起來。
4.  **A2A 應用程式建立 (`A2AStarletteApplication`)**：
    -   使用 `agent_card` 和 `request_handler` 建立 ASGI 應用程式實例。
5.  **伺服器啟動 (`uvicorn.run`)**：
    -   使用 `uvicorn` 在 `0.0.0.0:9001` 上運行 ASGI 應用程式，
    -   使其可以接收來自協調器或其他服務的網路請求。

### Mermaid 流程圖

```mermaid
graph TD
    A[main() 函式] --> B(定義 AgentSkill);
    B --> C(建立 AgentCard);
    C --> D{建立 DefaultRequestHandler};
    D -- 包含 --> E[ResearchAgentExecutor];
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
from .agent_executor import ResearchAgentExecutor


def main():
    """啟動研究代理 A2A 伺服器。"""

    # 定義研究技能
    research_skill = AgentSkill(
        id='research',
        name='研究與分析',
        description='對主題進行全面研究、收集事實並提供引用',
        tags=['研究', '分析', '事實', '資訊'],
        examples=[
            '研究量子計算趨勢',
            '尋找有關 AI 採用的資訊',
            '分析技術 X 的市場趨勢'
        ],
    )

    # 建立代理卡片
    agent_card = AgentCard(
        name='研究專家代理',
        description='專門從事研究、事實查核與資訊收集的代理',
        url='http://localhost:9001/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[research_skill],
        supports_authenticated_extended_card=False,
    )

    # 建立請求處理器
    request_handler = DefaultRequestHandler(
        agent_executor=ResearchAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # 建立並啟動 A2A 伺服器
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    print("🚀 正在於 http://localhost:9001 啟動研究代理 A2A 伺服器")
    print("📚 代理專門從事研究與資訊收集")
    print("🔗 代理卡片位於：http://localhost:9001/.well-known/agent.json")

    uvicorn.run(server.build(), host='0.0.0.0', port=9001)


if __name__ == '__main__':
    main()
