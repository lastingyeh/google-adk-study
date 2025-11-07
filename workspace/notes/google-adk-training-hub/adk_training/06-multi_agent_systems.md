# 教學 06：多代理系統 - 複雜的協調流程

## 總覽 (Overview)

本教學示範如何結合循序 (Sequential) 與並行 (Parallel) 代理，建構一個能夠處理複雜現實世界任務的精密多代理系統。我們將建立一個內容發布系統，此系統採用了扇出/收集 (fan-out/gather) 模式，也就是並行收集資料後，再進行循序的綜合整理。

**🎯 提供完整實作**: 在 `tutorial_implementation/tutorial06/` 中可以找到一個完整且經過測試的內容發布系統，包含完整的測試、文件和易於使用的設定流程。

## 先決條件 (Prerequisites)

*   完成教學 01-05，了解代理、工具、循序與並行模式。
*   已安裝 ADK (`pip install google-adk`)。
*   已設定 API 金鑰。
*   可存取 `GoogleSearch` 工具 (Gemini 2.0+ 模型自動啟用)。

## 核心概念 (Core Concepts)

### 多代理架構 (Multi-Agent Architecture)

真實世界的複雜問題需要多個代理以精密的方式協同工作：

*   **循序鏈 (Sequential chains)**: 當順序很重要時 (A → B → C)。
*   **並行分支 (Parallel branches)**: 當速度很重要時 (A, B, C 同時執行)。
*   **巢狀協調 (Nested orchestration)**: 結合兩者，例如在循序中包含並行，反之亦然。
*   **專業化代理 (Specialized agents)**: 每個代理只專注於一項職責。

### 常見的多代理模式 (Common Multi-Agent Patterns)

1.  **循序管線 (Sequential Pipeline)**:
    *   `代理 A → 代理 B → 代理 C`
    *   **用途**: 每一步都需要前一步的輸出。

2.  **扇出/收集 (Fan-Out/Gather)**:
    *   一個輸入分流至多個並行代理，再將結果合併。
    *   **用途**: 從多個來源收集資料後進行綜合處理。

3.  **巢狀工作流程 (Nested Workflows)**: (本教學重點)
    *   在一個並行容器中，運行多個獨立的循序管線，最後再由一個最終代理進行綜合。
    *   **用途**: 當有多個獨立的處理流程，且需要對所有結果進行最終整合時。

### 使用 GoogleSearch 工具進行真實研究

本教學使用 ADK 內建的 `google_search` 工具進行真實的網路研究，取代了模擬的回應。這使得內容發布系統更加強大和真實。

*   ✅ **真實內容**: 基於實際的網路研究。
*   ✅ **最新資訊**: 隨時保持最新。
*   ✅ **可靠來源**: 從真實網站和出版物中提取資料。

## 使用案例 (Use Case)

我們將為一本數位雜誌建立一個**內容發布系統**，其流程如下：

1.  **研究階段 (並行)**:
    *   **新聞管線**: 獲取時事 → 摘要重點。
    *   **社群管線**: 收集熱門話題 → 分析情緒。
    *   **專家管線**: 尋找專家意見 → 提取引言。
2.  **內容創作階段 (循序)**:
    *   結合所有研究成果。
    *   撰寫文章草稿。
    *   編輯以求清晰。
    *   格式化以便發布。

這個案例展示了**巢狀協調**：3 個並行的循序管線，加上一個最終的循序綜合流程。

## 實作步驟

### 步驟 1: 建立專案結構

```bash
mkdir content_publisher
cd content_publisher
touch __init__.py agent.py .env
```
將之前教學中的 `.env` 檔案複製過來。

### 步驟 2: 設定套件匯入

**content_publisher/__init__.py**
```python
from . import agent
```

### 步驟 3: 建立多代理系統

**content_publisher/agent.py**
```python
from __future__ import annotations
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search

# =====================================================
# 並行分支 1: 新聞研究管線
# =====================================================
news_fetcher = Agent(
    name="news_fetcher",
    model="gemini-2.0-flash",
    description="使用 Google Search 獲取當前新聞文章",
    instruction=(
        "你是一位新聞研究員。根據使用者主題，搜尋當前新聞文章和近期發展。\n"
        "使用 google_search 工具尋找 3-4 篇當前新聞文章。\n"
        "專注於過去 6 個月內可靠的新聞來源。\n"
        "輸出一個包含來源、標題、簡短摘要的項目符號列表。"
    ),
    tools=[google_search],
    output_key="raw_news"
)
news_summarizer = Agent(
    name="news_summarizer",
    model="gemini-2.0-flash",
    description="摘要新聞重點",
    instruction=(
        "將新聞文章摘要為 2-3 個關鍵要點。\n"
        "**原始新聞:**\n{raw_news}\n"
        "輸出格式:\nKEY TAKEAWAYS:\n1. ...\n2. ...\n3. ..."
    ),
    output_key="news_summary"
)
news_pipeline = SequentialAgent(
    name="NewsPipeline",
    sub_agents=[news_fetcher, news_summarizer],
    description="獲取並摘要新聞"
)

# =====================================================
# 並行分支 2: 社群媒體研究管線
# =====================================================
social_monitor = Agent(
    name="social_monitor",
    model="gemini-2.0-flash",
    description="使用 Google Search 監控社群媒體趨勢",
    instruction=(
        "你是一位社群媒體分析師。根據使用者主題，搜尋熱門討論、標籤和公眾情緒。\n"
        "使用 google_search 工具尋找趨勢標籤、社群討論和公眾意見。\n"
        "輸出 3-4 個趨勢標籤、熱門討論主題和總體情緒。"
    ),
    tools=[google_search],
    output_key="raw_social"
)
sentiment_analyzer = Agent(
    name="sentiment_analyzer",
    model="gemini-2.0-flash",
    description="分析社群情緒",
    instruction=(
        "分析社群媒體數據並提取關鍵洞察。\n"
        "**社群媒體數據:**\n{raw_social}\n"
        "輸出格式:\nSOCIAL INSIGHTS:\n• 趨勢: ...\n• 情緒: ...\n• 關鍵主題: ..."
    ),
    output_key="social_insights"
)
social_pipeline = SequentialAgent(
    name="SocialPipeline",
    sub_agents=[social_monitor, sentiment_analyzer],
    description="監控並分析社群媒體"
)

# =====================================================
# 並行分支 3: 專家意見管線
# =====================================================
expert_finder = Agent(
    name="expert_finder",
    model="gemini-2.0-flash",
    description="使用 Google Search 尋找專家意見",
    instruction=(
        "你是一位專家意見研究員。根據使用者主題，搜尋行業專家、學者或思想領袖的言論。\n"
        "使用 google_search 工具尋找 2-3 位專家的姓名、資歷及其關鍵陳述。"
    ),
    tools=[google_search],
    output_key="raw_experts"
)
quote_extractor = Agent(
    name="quote_extractor",
    model="gemini-2.0-flash",
    description="提取可引用的洞察",
    instruction=(
        "從專家意見中提取最具影響力的引言和洞察。\n"
        "**專家意見:**\n{raw_experts}\n"
        "輸出格式:\nEXPERT INSIGHTS:\n• 引言 1: \"...\" - [專家姓名], [資歷]\n• 引言 2: \"...\""
    ),
    output_key="expert_quotes"
)
expert_pipeline = SequentialAgent(
    name="ExpertPipeline",
    sub_agents=[expert_finder, quote_extractor],
    description="尋找並提取專家意見"
)

# =====================================================
# 階段 1: 並行研究 (3 個管線同時執行)
# =====================================================
parallel_research = ParallelAgent(
    name="ParallelResearch",
    sub_agents=[
        news_pipeline,
        social_pipeline,
        expert_pipeline
    ],
    description="同時執行所有研究管線"
)

# =====================================================
# 階段 2: 內容創作 (循序綜合)
# =====================================================
article_writer = Agent(
    name="article_writer",
    model="gemini-2.0-flash",
    description="根據所有研究撰寫文章草稿",
    instruction=(
        "你是一位專業作家。使用以下所有研究撰寫一篇引人入勝的文章。\n"
        "**新聞摘要:**\n{news_summary}\n"
        "**社群洞察:**\n{social_insights}\n"
        "**專家引言:**\n{expert_quotes}\n"
        "撰寫一篇 4-5 段的文章，包含引人入勝的開頭、自然地融合研究成果，並有強而有力的結論。"
    ),
    output_key="draft_article"
)
article_editor = Agent(
    name="article_editor",
    model="gemini-2.0-flash",
    description="編輯文章以求清晰和影響力",
    instruction=(
        "你是一位編輯。審閱並改進以下文章草稿。\n"
        "**文章草稿:**\n{draft_article}\n"
        "針對清晰度、流暢度、影響力、文法和風格進行編輯。"
    ),
    output_key="edited_article"
)
article_formatter = Agent(
    name="article_formatter",
    model="gemini-2.0-flash",
    description="格式化文章以便發布",
    instruction=(
        "使用適當的 markdown 格式化文章。\n"
        "**文章:**\n{edited_article}\n"
        "添加標題、署名、章節標題和適當的格式。"
    ),
    output_key="published_article"
)

# =====================================================
# 完整的多代理系統
# =====================================================
content_publishing_system = SequentialAgent(
    name="ContentPublishingSystem",
    sub_agents=[
        parallel_research,
        article_writer,
        article_editor,
        article_formatter
    ],
    description="完整的內容發布系統，包含並行研究和循序創作"
)

root_agent = content_publishing_system
```

### 步驟 4: 執行發布系統

```bash
# 從 tutorial_implementation/tutorial06/
make dev
```
或手動啟動：
```bash
cd ..
adk web
```
打開 `http://localhost:8000` 並選擇 "content_publisher"。

## 架構視覺化 (Architecture Visualization)
``` mermaid
graph TD
    A[使用者：撰寫關於電動車的文章] --> B{階段 1：並行研究};
    B --> C[新聞管線：獲取 → 摘要 → news_summary];
    B --> D[社群管線：監控 → 分析 → social_insights];
    B --> E[專家管線：尋找 → 提取 → expert_quotes];

    subgraph 並行執行
        C
        D
        E
    end

    C --> F{階段 2：循序內容創作};
    D --> F;
    E --> F;

    F --> G[寫作代理：結合研究 → draft_article];
    G --> H[編輯代理：審閱草稿 → edited_article];
    H --> I[格式化代理：添加 markdown → published_article];
    I --> J[最終輸出：可發布的文章];
```

**此架構的優點:**

1.  **階段 1 (並行研究)**: 三個獨立的研究領域同時進行，速度快。
2.  **階段 2 (循序創作)**: 寫作代理需要所有研究成果，編輯需要草稿，格式化需要編輯後的版本，必須按順序執行以確保品質。
3.  **兩全其美**: 透過並行處理獲得速度，透過循序流程確保品質。

## 執行流程解析

在 **Events** 標籤頁中，可以看到協調流程：

1.  **階段 1 開始**: `ParallelResearch` 啟動。
2.  **同時執行**: `NewsPipeline`, `SocialPipeline`, `ExpertPipeline` 及其子代理同時運行。
3.  **階段 1 完成**: 當所有三個管線都完成後，`ParallelResearch` 結束。
4.  **階段 2 開始**: `article_writer` 啟動，並注入所有研究成果。
5.  **循序執行**: `article_writer` → `article_editor` → `article_formatter` 依序完成。

## 重點摘要 (Key Takeaways)

*   ✅ **在並行中巢狀循序**: 多個獨立的管線同時運行。
*   ✅ **在循序中巢狀並行**: 工作流程中需要並行處理的階段。
*   ✅ **每個代理一項工作**: 保持代理的專業化、專注和可測試性。
*   ✅ **狀態透過 `output_keys` 流動**: 明確的數據依賴關係。
*   ✅ **複雜的協調很簡單**: 僅需組合 `SequentialAgent` 和 `ParallelAgent`。
*   ✅ **顯著的性能提升**: 並行研究階段速度提升約 2.4 倍。

## 最佳實踐 (Best Practices)

*   **做**:
    *   在編碼前繪製架構圖。
    *   保持代理職責單一。
    *   使用描述性的名稱。
    *   規劃狀態流 (每個代理需要哪些 key)。
    *   在組合前單獨測試每個管線。
*   **不要**:
    *   過度巢狀 (超過 3 層會變得混亂)。
    *   建立多功能的代理。
    *   忘記設定 `output_keys`。
    *   在並行區塊中假設執行順序。

## 真實世界應用

*   **內容平台**: 研究 → 撰寫 → 編輯 → 發布。
*   **數據分析**: 收集資料 (並行) → 合併 → 分析 → 視覺化。
*   **電子商務**: 檢查庫存 + 定價 + 評論 (並行) → 推薦。
*   **客戶支援**: 分類 → 路由 (並行專家) → 回應 → 跟進。

## 程式碼實現 (Code Implementation)
- content-publisher：[程式碼連結](../../../python/agents/content-publisher/README.md)