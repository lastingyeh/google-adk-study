# 在 Agent Development Kit (ADK) 中進行記錄 (Logging)

> 🔔 `更新日期：2026-01-28`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/logging/

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

Agent Development Kit (ADK) 使用 Python 的標準 `logging` 模組來提供靈活且強大的記錄功能。了解如何配置和解讀這些日誌，對於有效監控 Agent 行為和偵錯問題至關重要。

## 記錄哲學 (Logging Philosophy)

ADK 的記錄方法是提供詳細的診斷資訊，但在預設情況下不會過於冗長。它旨在由應用程式開發人員進行配置，讓您可以根據特定需求客製化日誌輸出，無論是在開發還是生產環境中。

- **標準函式庫：** 它使用標準的 `logging` 函式庫，因此任何與其相容的配置或處理常式 (handler) 都適用於 ADK。
- **階層式記錄器 (Hierarchical Loggers)：** 記錄器根據模組路徑進行階層式命名（例如：`google_adk.google.adk.agents.llm_agent`），從而可以精細控制框架的哪些部分產生日誌。
- **使用者配置：** 框架本身不配置記錄。在應用程式的進入點設置所需的記錄配置是使用框架的開發人員的責任。

## 如何配置記錄

您可以在初始化和執行 Agent 之前，在主應用程式腳本（例如 `main.py`）中配置記錄。最簡單的方法是使用 `logging.basicConfig`。

### 配置範例

若要啟用詳細記錄（包括 `DEBUG` 層級訊息），請在腳本頂部加入以下內容：

```python
import logging

# 配置基本記錄設置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# 您的 ADK Agent 程式碼如下...
# from google.adk.agents import LlmAgent
# ...
```

### 使用 ADK CLI 配置記錄

當使用 ADK 內建的 Web 或 API 伺服器執行 Agent 時，您可以直接從命令列輕鬆控制日誌的詳細程度。`adk web`、`adk api_server` 和 `adk deploy cloud_run` 命令都接受 `--log_level` 選項。

這提供了一種方便的方法來設置記錄層級，而無需修改 Agent 的原始碼。

> **注意：** 對於 ADK 的記錄器，命令列設置始終優先於程式化配置（如 `logging.basicConfig`）。建議在生產環境中使用 `INFO` 或 `WARNING`，僅在疑難排解時啟用 `DEBUG`。

**使用 `adk web` 的範例：**

要以 `DEBUG` 層級記錄啟動 Web 伺服器，請執行：

```bash
# 以 DEBUG 層級啟動 web 伺服器
adk web --log_level DEBUG path/to/your/agents_dir
```

`--log_level` 選項的可用日誌層級為：

- `DEBUG`
- `INFO`（預設）
- `WARNING`
- `ERROR`
- `CRITICAL`

> 您也可以使用 `-v` 或 `--verbose` 作為 `--log_level DEBUG` 的快捷方式。
>
> ```bash
> adk web -v path/to/your/agents_dir
> ```

### 日誌層級 (Log Levels)

ADK 使用標準日誌層級來對訊息進行分類。配置的層級決定了哪些資訊會被記錄。

| 層級 | 描述 | 記錄的資訊類型 |
| :--- | :--- | :--- |
| **`DEBUG`** | **對於偵錯至關重要。** 提供精細診斷資訊的最詳細層級。 | <ul><li>**完整的 LLM 提示詞 (Prompts)：** 發送到語言模型的完整請求，包括系統指令、歷史紀錄和工具。</li><li>來自服務的詳細 API 回應。</li><li>內部狀態轉移和變數值。</li></ul> |
| **`INFO`** | 關於 Agent 生命週期的通規資訊。 | <ul><li>Agent 初始化和啟動。</li><li>Session 建立和刪除事件。</li><li>工具的執行，包括其名稱和參數。</li></ul> |
| **`WARNING`** | 表示潛在問題或使用了過時的功能。Agent 繼續運作，但可能需要注意。 | <ul><li>使用過時的方法或參數。</li><li>系統已修復的非關鍵錯誤。</li></ul> |
| **`ERROR`** | 導致操作無法完成的嚴重錯誤。 | <ul><li>對外部服務（例如 LLM、Session Service）的 API 呼叫失敗。</li><li>Agent 執行期間未處理的異常 (Exceptions)。</li><li>配置錯誤。</li></ul> |

> **注意：** 建議在生產環境中使用 `INFO` 或 `WARNING`。僅在主動疑難排解問題時啟用 `DEBUG`，因為 `DEBUG` 日誌可能非常冗長且可能包含敏感資訊。

## 閱讀與理解日誌

`basicConfig` 範例中的 `format` 字串決定了每條日誌訊息的結構。

這是一個日誌條目範本：

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }
```

| 日誌區段 | 格式指定符 | 意義 |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | 時間戳記 |
| `DEBUG`                         | `%(levelname)s`  | 嚴重程度層級 |
| `google_adk.models.google_llm`  | `%(name)s`       | 記錄器名稱（產生該日誌的模組） |
| `LLM Request: contents { ... }` | `%(message)s`    | 實際的日誌訊息 |

透過閱讀記錄器名稱，您可以立即精確定位日誌來源，並了解其在 Agent 架構中的背景。

## 使用日誌進行偵錯：一個實際範例

**場景：** 您的 Agent 沒有產生預期的輸出，並且您懷疑發送到 LLM 的提示詞不正確或缺少資訊。

**步驟：**

1.  **啟用 DEBUG 記錄：** 在您的 `main.py` 中，按照配置範例所示將記錄層級設置為 `DEBUG`。

    ```python
    # 設置記錄層級為 DEBUG 以查看詳細資訊
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```
2.  **執行您的 Agent：** 像往常一樣執行 Agent 的任務。

3.  **檢查日誌：** 在主控台輸出中查找來自 `google.adk.models.google_llm` 記錄器且以 `LLM Request:` 開頭的訊息。

    ```log
    ...
    # 發送請求，包含模型資訊與後端設置
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - Sending out request, model: gemini-2.0-flash, backend: GoogleLLMVariant.GEMINI_API, stream: False
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm -
    LLM Request:
    -----------------------------------------------------------
    System Instruction:

        你會擲骰子並回答有關擲骰結果的問題。
        你可以擲不同面數的骰子。
        你可以透過在同一請求與同一輪次中並行呼叫函式來平行使用多個工具。
        可以討論先前的擲骰紀錄，並對擲骰結果進行評論。

        當被要求擲骰時，必須呼叫 roll_die 工具並傳入骰子的面數。務必以整數傳遞，不要傳入字串。
        你不得自行擲骰，必須使用工具。

        在檢查質數時，請呼叫 check_prime 工具並傳入整數列表。務必傳入整數列表，不可傳入字串。
        在呼叫工具之前，不要自行檢查質數。

        當被要求擲骰並檢查質數時，應始終進行下列兩個函式呼叫：
        1. 先呼叫 roll_die 工具以取得擲骰結果。在呼叫 check_prime 工具之前，請等待該函式的回應。
        2. 在收到 roll_die 的回應後，使用該擲骰結果呼叫 check_prime 工具。
            2.1 若使用者要求基於先前的擲骰結果檢查質數，請確保在列表中包含先前的擲骰結果。
        3. 回應時必須包含步驟 1 的 roll_die 結果。

        在執行擲骰並檢查質數時，應始終遵循上述三個步驟。
        不應依賴先前的質數檢查結果歷史。

        你是個代理（agent）。你的內部名稱為「hello_world_agent」。

        關於你的描述是：「hello world agent，可擲 8 面骰並檢查質數。」
    -----------------------------------------------------------
    Contents:
    {"parts":[{"text":"Roll a 6 sided dice"}],"role":"user"}
    {"parts":[{"function_call":{"args":{"sides":6},"name":"roll_die"}}],"role":"model"}
    {"parts":[{"function_response":{"name":"roll_die","response":{"result":2}}}],"role":"user"}
    -----------------------------------------------------------
    Functions:
    roll_die: {'sides': {'type': <Type.INTEGER: 'INTEGER'>}}
    check_prime: {'nums': {'items': {'type': <Type.INTEGER: 'INTEGER'>}, 'type': <Type.ARRAY: 'ARRAY'>}}
    -----------------------------------------------------------

    # AFC 已啟用
    2025-07-10 15:26:13,779 - INFO - google_genai.models - AFC is enabled with max remote calls: 10.
    2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm -
    LLM Response:
    -----------------------------------------------------------
    Text:
    I have rolled a 6 sided die, and the result is 2.
    ...
    ```

4.  **分析提示詞：** 透過檢查記錄請求中的 `System Instruction`、`contents`、`functions` 部分，您可以驗證：
    -   系統指令是否正確？
    -   對話歷史（`user` 和 `model` 輪次）是否準確？
    -   是否包含最近的使用者查詢？
    -   是否向模型提供了正確的工具？
    -   模型是否正確調用了工具？
    -   模型回應需要多長時間？

這些詳細的輸出讓您可以直接從日誌檔案中診斷各種問題，從錯誤的提示詞工程到工具定義的問題。
