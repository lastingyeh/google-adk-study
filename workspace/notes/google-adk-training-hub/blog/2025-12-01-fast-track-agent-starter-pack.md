# 加速您的 GenAI 代理開發：深入解析 Google Cloud Agent Starter Pack (Fast-track Your GenAI Agents: Deep Dive into the Google Cloud Agent Starter Pack)

## 📝 **本文內容主要參考自 Raphaël MANSUY 的 Blog**：[Fast-track Your GenAI Agents: Deep Dive into the Google Cloud Agent Starter Pack](https://raphaelmansuy.github.io/adk_training/blog/2025/12/01/fast-track-agent-starter-pack)

## 簡介 (Introduction)
在筆記型電腦上建立 GenAI 代理原型就像變魔術一樣。您只需寫幾行 Python 程式碼，連接一個 LLM，突然間您就可以與您的資料聊天了。但是，將這種魔法從 Jupyter notebook 轉移到一個安全、可擴展且具備可觀測性的生產環境，才是真正頭痛的開始。

這就是 **Google Cloud Agent Starter Pack** 登場的時候了。

這個開源儲存庫是 Google 對於「原型煉獄 (prototype purgatory)」問題的解答。它是一套全面的工具包，旨在讓您在幾分鐘內（而不是幾個月）於 Google Cloud Platform (GCP) 上啟動已準備好投入生產的生成式 AI 代理。

<!--truncate-->

## 為何您需要關注？ (Why Should You Care?)

大多數的教學在 `print(response.text)` 就結束了。Agent Starter Pack 則從這裡接手，處理那些不性感但至關重要的基礎架構工作，讓您可以專注於代理的認知架構。

以下是它成為改變遊戲規則的關鍵原因：

- **生產優先思維 (Production-First Mindset)：** 它不僅僅給您程式碼；它還提供了基礎架構的 Terraform 腳本、CI/CD 流程 (GitHub Actions 或 Cloud Build)，以及開箱即用的安全性最佳實踐。
- **內建可觀測性 (Observability Built-In)：** 除錯 LLM 很困難。此套件整合了 OpenTelemetry，自動將追蹤和指標記錄到 Cloud Logging 和 BigQuery，讓您確切地檢查您的代理正在「思考」什麼。
- **彈性部署 (Flexible Deployment)：** 可無縫部署到 **Cloud Run** 以獲得無伺服器的簡便性，或部署到新的 **Vertex AI Agent Engine** 以獲得託管的代理執行環境。

## 架構與範本 (Architecture & Templates)

Agent Starter Pack 涵蓋了代理開發的完整生命週期—從原型設計與評估到部署與監控：

![Agent Starter Pack High-Level Architecture](https://github.com/GoogleCloudPlatform/agent-starter-pack/raw/main/docs/images/ags_high_level_architecture.png)

這個入門套件並非「一體適用」的單體架構。它包含了數個針對常見使用案例量身打造的架構範本：

1.  **LangGraph Base ReAct：** 使用 LangChain 的 LangGraph 建構的經典「推理與行動 (Reason and Act)」代理。非常適合複雜的推理工作流程和基於圖形的狀態管理。
2.  **Agentic RAG：** 一個具備自動化資料攝取的檢索增強生成 (Retrieval-Augmented Generation) 代理，支援 **Vertex AI Search** 和 **Vertex AI Vector Search**。
3.  **ADK Base：** Google 的極簡 ReAct 代理範例—非常適合作為開始使用 ADK 並了解代理基礎知識的起點。
4.  **ADK Live：** 一個支援低延遲 WebSocket 通訊，可同時進行音訊、視訊和文字互動的即時多模態代理。

### 可用的 ADK 範本 (Available ADK Templates)

入門套件包含了官方基於 Google ADK 的範本：

- **ADK Base (`adk_base`)**：一個極簡的 ReAct 代理，展示了核心 ADK 概念，如代理建立和工具整合。這是學習 ADK 和建立通用對話代理的首選起點。

- **ADK A2A Base (`adk_a2a_base`)**：一個支援 Agent2Agent (A2A) 協定的 ADK 代理，用於分散式代理通訊以及跨框架與語言的互操作性。非常適合建立基於微服務的代理架構。

- **Agentic RAG (`Built on ADK`)`**：一個已準備好投入生產的 RAG 系統，具備自動化資料攝取功能，支援 Vertex AI Search 和 Vertex AI Vector Search 進行語義檢索。

- **ADK Live (`adk_live`)**：一個由 Gemini 驅動的即時多模態 RAG 代理，支援低延遲 WebSocket 通訊，可同時進行音訊、視訊和文字互動。

每個範本都隨附：
- 完整的原始碼和架構文件
- 生產級基礎架構 (適用於 Cloud Run 或 Vertex AI Agent Engine 的 Terraform 腳本)
- CI/CD 流程 (GitHub Actions 或 Google Cloud Build)
- 內建使用 OpenTelemetry 和 Cloud Logging 的可觀測性
- 全面的測試套件和部署指南

## 開始使用：從零到部署 (Getting Started: From Zero to Deployed)

讓我們看看啟動一個新專案有多容易。

### 1. 安裝 CLI (使用 uvx 快速開始)

最快的方法—無需安裝：

```bash
uvx agent-starter-pack create my-production-agent
```

或者，在本地安裝並執行：

```bash
pip install agent-starter-pack
agent-starter-pack create my-production-agent
```

### 2. 建立您的代理

執行 create 指令並選擇您的範本 (例如：`adk_base`, `langgraph_base`, `agentic_rag`) 以及部署目標 (Cloud Run 或 Vertex AI Agent Engine)。

`create` 指令將會使用選定的範本為您搭建整個專案。

### 3. 部署

生成的專案包含一個 `Makefile` 和完整的 Terraform 基礎架構即程式碼 (Infrastructure-as-Code)。部署指令如下：

```bash
cd my-production-agent
make deploy
```

這將會自動在 Google Cloud 上配置所有資源 (IAM 角色、API、CI/CD、監控)。

## 使用 Google ADK 作為範例代理執行環境 (Using Google ADK as an example agent runtime)

如果您已經使用 Google ADK 框架來建立代理，Starter Pack 可以順利地與以 ADK 為中心的工作流程整合。例如，如果您選擇 `adk_base` 範本，生成的程式碼將遵循標準 ADK 模式，讓您可以透過 `adk web` 在本地執行它以進行互動式開發。

一個極簡的整合範例 (基於 `adk_base` 範本)：

```python
# my_production_agent/app/agent.py
from google.adk.agents import Agent
from google.adk.apps.app import App

def get_weather(city: str) -> str:
    # 取得天氣資訊的簡單函式
    return "It's sunny!"

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful AI assistant.", # 您是一位樂於助人的 AI 助理。
    tools=[get_weather],
)

# App 包裝器啟用 ADK 執行環境功能
app = App(root_agent=root_agent, name="app")
```

這讓您可以在利用 Starter Pack 固執己見的 (opinionated) 基礎架構、CI/CD 和可觀測性模式的同時，仍能使用 ADK 豐富的開發者工具 (REPL、追蹤和測試) 進行開發。

## 「秘方」：可觀測性 (The "Secret Sauce": Observability)

其中一個突出的功能是它處理遙測 (telemetry) 的方式。預設情況下，starter pack 會對您的代理進行儀表化以捕捉：

- **代幣使用量 (Token Usage)：** 用於成本追蹤的區分輸入/輸出代幣計數。
- **延遲 (Latency)：** 鏈中每個步驟花費的時間。
- **追蹤資料 (Trace Data)：** 在 Google Cloud Console 中視覺化整個執行路徑。

這意味著您可以進入 **BigQuery** 並針對您的代理對話紀錄執行 SQL 查詢，以評估效能或發現幻覺 (hallucinations)。

## 結論 (Conclusion)

Google Cloud Agent Starter Pack 彌合了「在我的機器上可以運作」和「為我們的客戶運作」之間的差距。如果您正在 GCP 上建立代理，這個儲存庫是您開始旅程的最佳地點。

## 參考資料 (References)
- [🚀 GoogleCloudPlatform/agent-starter-pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)
- [📝 Agent Starter Pack Production-Ready Agents on Google Cloud, faster](https://googlecloudplatform.github.io/agent-starter-pack/)
- [🔎 Generative AI on Google Cloud](https://github.com/GoogleCloudPlatform/generative-ai)

## 程式碼實現 (Code Implementation)

- pack-adk-a2a-agent：[程式碼連結](../../../python/agents/pack-adk-a2a-agent/)
