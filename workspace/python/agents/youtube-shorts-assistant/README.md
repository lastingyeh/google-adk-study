# YouTube Shorts Assistant 專案

## 概觀

此專案是一個使用多代理人（multi-agent）系統，旨在自動化 YouTube Shorts 短影音內容的創建流程。系統由一個主要協調代理人（Coordinator Agent）和多個專業子代理人（Sub-agents）組成，每個子代理人負責內容創作流程中的特定環節，例如腳本撰寫、視覺化設計和最終內容格式化。

## 專案結構

```
youtube_shorts_assistant/
├── __init__.py                 # 將目錄標記為 Python 套件
├── agent.py                    # 定義主要的 LLM 協調代理人
├── loop_agent.py               # 定義一個替代的 LoopAgent 工作流程
├── loop_agent_runner.py        # 用於執行 LoopAgent 的腳本
├── shorts_agent_instruction.txt # 主要協調代理人的指令文件
├── sub_agents/                 # 包含所有專業子代理人的目錄
│   ├── scriptwriter_agent/     # 腳本撰寫代理人
│   ├── visualizer_agent/       # 視覺化設計代理人
│   └── formatter_agent/        # 內容格式化代理人
└── util.py                     # 通用工具函式
```

## 核心組件

### 1. 主要代理人 (Coordinator Agent)

-   **`agent.py`**:
    -   定義了名為 `youtube_shorts_agent` 的核心 `LlmAgent`。
    -   此代理人作為總協調者，負責接收使用者請求，並依序調用 `scriptwriter_agent`、`visualizer_agent` 和 `formatter_agent` 來完成整個內容創作流程。
    -   它使用 `AgentTool` 將子代理人作為其工具集的一部分。

-   **`shorts_agent_instruction.txt`**:
    -   這是主要代理人的核心指令集。
    -   詳細描述了代理人從接收使用者請求到最終交付格式化內容的完整工作流程，包括如何分析需求、委派任務給子代理人，以及管理回饋和修訂。

### 2. 循環代理人 (Loop Agent)

-   **`loop_agent.py`**:
    -   提供了一個基於 `LoopAgent` 的替代工作流程。
    -   此代理人會按順序循環執行子代理人（腳本、視覺、格式化），並可設定最大迭代次數（`max_iterations=3`），適用於需要多次修訂或迭代的場景。

-   **`loop_agent_runner.py`**:
    -   這是一個可執行的腳本，用於啟動和運行 `loop_agent`。
    -   它包含了設置 `session` 和 `runner` 的完整邏輯，並提供了一個如何以非同步方式呼叫代理人的範例。

### 3. 子代理人 (Sub-agents)

此專案包含三個專業的子代理人，位於 `sub_agents/` 目錄下：

-   **`scriptwriter_agent`**: 負責根據使用者提供的主題、語氣和關鍵訊息，撰寫簡潔且引人入勝的 YouTube Shorts 腳本。
-   **`visualizer_agent`**: 接收最終腳本，並為腳本的每個段落生成對應的動態、垂直（9:16）視覺創意或概念。
-   **`formatter_agent`**: 將腳本和視覺概念進行結構化整合，並使用 Markdown 格式（例如表格或標題段落）清晰地呈現最終內容。

### 4. 工具函式 (Utilities)

-   **`util.py`**:
    -   包含輔助函式，例如 `load_instructions_from_file`。
    -   此函式用於從 `.txt` 檔案中讀取指令，讓代理人的指令與程式碼分離，更易於管理和修改。

## 工作流程

根據 `shorts_agent_instruction.txt` 的定義，系統的工作流程如下：

1.  **接收請求**: 主要代理人接收使用者的內容請求（主題、目標受眾等）。
2.  **委派腳本撰寫**: 代理人將需求傳遞給 `scriptwriter_agent` 以生成腳本。
3.  **委派視覺設計**: 腳本完成後，代理人將其交給 `visualizer_agent` 以創建視覺概念。
4.  **委派格式化**: 代理人將結構化的腳本和視覺數據傳遞給 `formatter_agent`。
5.  **格式化輸出**: `formatter_agent` 將內容整合成清晰的 Markdown 格式。
6.  **交付成果**: 主要代理人將最終的 Markdown 內容呈現給使用者。
7.  **處理回饋**: 如果使用者需要修改，代理人會協調相關的子代理人進行修訂，並重新觸發格式化流程。

## 如何運行

您可以透過執行 `loop_agent_runner.py` 來啟動代理人。在執行之前，請確保：

1.  已建立 `.env` 檔案並填入您的 `API_KEY`。
2.  已安裝所有必要的套件（例如 `google-generativeai`, `python-dotenv`）。

執行 `loop_agent_runner.py` 後，它將使用 "I want to write a short on how to build AI Agents" 作為預設查詢來呼叫代理人，並在終端機中印出最終的回應。
