# 使用 Freeplay 進行 Agent 觀測與評估

> 🔔 `更新日期：2026-01-29`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/freeplay/

[Freeplay](https://freeplay.ai/) 為建構和優化 AI agent 提供了一套端對端的流程，並可與 ADK 整合。透過 Freeplay，您的整個團隊可以輕鬆協作，迭代 agent 指令 (prompts)、實驗並比較不同的模型與 agent 變更、執行離線和在線評估以衡量品質、監控生產環境，以及手動審閱數據。

Freeplay 的關鍵優勢：

* **簡單的觀測能力** - 專注於 agent、LLM 呼叫和工具呼叫，便於人工審閱
* **在線評估/自動評分器** - 用於生產環境中的錯誤偵測
* **離線評估與實驗比較** - 在部署前測試變更
* **提示詞管理** - 支援將變更直接從 Freeplay playground 推送到程式碼
* **人工審閱工作流** - 用於錯誤分析和數據標記的協作
* **強大的 UI** - 讓領域專家能與工程師緊密協作

Freeplay 和 ADK 相輔相成。ADK 為您提供強大且具表現力的 agent 編排框架，而 Freeplay 則插入以進行觀測、提示詞管理、評估和測試。一旦與 Freeplay 整合，您就可以從 Freeplay UI 或程式碼更新提示詞和評估，讓團隊中的任何人都能做出貢獻。

## 影片介紹
[![Freeplay 介紹影片縮圖](https://img.youtube.com/vi/AV2zCkp4aYM/0.jpg)](https://www.youtube.com/watch?v=AV2zCkp4aYM&si=HVuOJFLMEkkpocF7)

### 重點整理

| 項目 | 說明 | 關鍵點 |
|---|---|---|
| 全方位觀測性與追蹤 (End-to-End Observability) | 所有 Agent 日誌匯入 Freeplay，可檢視完整執行路徑並逐步診斷 | 完整堆疊追蹤；逐步精確分析 |
| 內建評估與監控 (Built-in Evaluations) | 提供自動化評分器與監控，可為特定步驟撰寫評估器並量化表現 | 自動化評分；實務效能可視化 |
| 提示詞管理與實驗 (Prompt Management & Experimentation) | 提示詞從程式碼解耦為獨立物件，支援互動編輯與版本控制，並可即時實驗 | 互動式編輯；版本控制；即時回饋 |
| 資料集建置與優化 (Dataset Building) | 以觀測日誌建立黃金集與失敗案例，作為後續測試與優化依據 | 案例策劃（黃金集/失敗集）；持續測試 |
| 兩種整合模式 (Two Implementation Modes) | 可選「僅觀測」(Trace plugin) 或「提示詞管理」(Freeplay LLM agent) 兩種整合深度 | Observability plugin；Freeplay LLM agent 動態抓取提示詞 |

## 開始使用

以下是開始使用 Freeplay 和 ADK 的指南。您也可以在[此處](https://github.com/228Labs/freeplay-google-demo)找到完整的 ADK agent 範例儲存庫。

### 建立 Freeplay 帳戶

註冊免費的 [Freeplay 帳戶](https://freeplay.ai/signup)。

建立帳戶後，您可以定義以下環境變數：

```
FREEPLAY_PROJECT_ID=
FREEPLAY_API_KEY=
FREEPLAY_API_URL=
```

### 使用 Freeplay ADK 函式庫

安裝 Freeplay ADK 函式庫：

```bash
pip install freeplay-python-adk
```

當您初始化觀測能力時，Freeplay 將自動從您的 ADK 應用程式中擷取 OTel 日誌：

```python
from freeplay_python_adk.client import FreeplayADK
# 初始化 Freeplay ADK 的觀測能力，自動擷取 OTel 日誌
FreeplayADK.initialize_observability()
```

您還需要將 Freeplay 外掛程式傳遞給您的 App：

```python
from app.agent import root_agent
from freeplay_python_adk.freeplay_observability_plugin import FreeplayObservabilityPlugin
from google.adk.runners import App

# 建立 ADK App 實例並整合 Freeplay 觀測外掛程式
app = App(
    name="app",
    root_agent=root_agent,
    plugins=[FreeplayObservabilityPlugin()],
)

__all__ = ["app"]
```

您現在可以像往常一樣使用 ADK，您將會在 Observability 章節中看到流入 Freeplay 的日誌。

## 觀測能力 (Observability)

Freeplay 的觀測功能讓您能清楚地看到 agent 在生產環境中的表現。您可以深入研究個別 agent 的追蹤 (traces)，以了解每個步驟並診斷問題：

![追蹤詳情](https://raw.githubusercontent.com/freeplayai/freeplay-google-demo/refs/heads/main/docs/images/trace_detail.png)

您還可以使用 Freeplay 的過濾功能來搜尋和過濾任何感興趣區段的數據：

![過濾](https://raw.githubusercontent.com/freeplayai/freeplay-google-demo/refs/heads/main/docs/images/filter.png)

## 提示詞管理 (選填)

Freeplay 提供[原生提示詞管理](https://docs.freeplay.ai/docs/managing-prompts)，簡化了不同提示詞版本的版控與測試流程。它允許您在 Freeplay UI 中對 ADK agent 指令進行實驗、測試不同模型，並將更新直接推送到程式碼，類似於功能開關 (feature flag)。

要與 ADK 一起發揮 Freeplay 的提示詞管理功能，您需要使用 Freeplay ADK agent 包裝器。`FreeplayLLMAgent` 繼承自 ADK 的基礎 `LlmAgent` 類別，因此您可以在 Freeplay 應用程式中管理提示詞版本，而無需將提示詞寫死在程式碼的 agent 指令中。

首先，前往 Prompts -> Create prompt template 在 Freeplay 中定義一個提示詞：

![提示詞](https://raw.githubusercontent.com/freeplayai/freeplay-google-demo/refs/heads/main/docs/images/prompt.png)

建立提示詞範本時，您需要新增 3 個元素，如下列章節所述：

### 系統訊息 (System Message)

這對應於程式碼中的 "instructions" 部分。

### Agent 上下文變數 (Agent Context Variable)

在系統訊息底部新增以下內容，將為要傳遞的持續 agent 上下文建立一個變數：

```python
# 用於在 Freeplay 提示詞範本中注入 agent 的上下文資訊
{{agent_context}}
```

### 歷史記錄區塊 (History Block)

點擊新訊息並將角色更改為 'history'。這將確保在存在過去的訊息時將其傳遞。

![提示詞編輯器](https://raw.githubusercontent.com/freeplayai/freeplay-google-demo/refs/heads/main/docs/images/prompt_editor.png)

現在您可以在程式碼中使用 `FreeplayLLMAgent`：

```python
from freeplay_python_adk.client import FreeplayADK
from freeplay_python_adk.freeplay_llm_agent import (
    FreeplayLLMAgent,
)

# 初始化觀測能力
FreeplayADK.initialize_observability()

# 使用 FreeplayLLMAgent 建立 root agent，這將會從 Freeplay 獲取提示詞
root_agent = FreeplayLLMAgent(
    name="social_product_researcher",
    tools=[tavily_search],
)
```

當 `social_product_researcher` 被調用時，提示詞將從 Freeplay 檢索並使用適當的輸入變數進行格式化。

## 評估 (Evaluation)

Freeplay 讓您能從 Freeplay 網頁應用程式中定義、版控並執行[評估](https://docs.freeplay.ai/docs/evaluations)。您可以透過前往 Evaluations -> "New evaluation" 為您的任何提示詞或 agent 定義評估。

![在 Freeplay 中建立新評估](https://raw.githubusercontent.com/freeplayai/freeplay-google-demo/refs/heads/main/docs/images/eval_create.png)

這些評估可以配置為同時用於在線監控和離線評估。離線評估的數據集可以上傳到 Freeplay 或從日誌範例中儲存。

## 數據集管理 (Dataset Management)

隨著數據流入 Freeplay，您可以使用這些日誌開始建立[數據集](https://docs.freeplay.ai/docs/datasets)，以便進行重複測試。使用生產環境日誌建立黃金數據集或失敗案例集合，以便在進行更改時用於測試。

![儲存測試案例](https://raw.githubusercontent.com/freeplayai/freeplay-google-demo/refs/heads/main/docs/images/save_test_case.png)

## 批次測試 (Batch Testing)

當您迭代 agent 時，您可以在[提示詞](https://docs.freeplay.ai/docs/component-level-test-runs)和[端對端](https://docs.freeplay.ai/docs/end-to-end-test-runs) agent 層級執行批次測試（即離線實驗）。這允許您比較多個不同的模型或提示詞變更，並在整個 agent 執行過程中量化面對面的變更。

[此處](https://github.com/freeplayai/freeplay-google-demo/blob/main/examples/example_test_run.py)是一個使用 ADK 在 Freeplay 上執行批次測試的程式碼範例。

## 立即註冊

前往 [Freeplay](https://freeplay.ai/) 註冊帳戶，並在[此處](https://github.com/freeplayai/freeplay-google-demo/tree/main)查看完整的 Freeplay <> ADK 整合。
