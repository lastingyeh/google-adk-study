# 代理活動日誌 (Agent activity logging)

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/logging/

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

Agent Development Kit (ADK) 使用 Python 的標準 `logging` 模組來提供靈活且強大的日誌記錄功能。了解如何配置和解讀這些日誌對於監控代理行為和有效地調試問題至關重要。

## 日誌記錄理念 (Logging Philosophy)

ADK 的日誌記錄方法是提供詳細的診斷資訊，而預設情況下不會過於冗長。它旨在由應用程式開發人員進行配置，允許您根據特定需求量身定制日誌輸出，無論是在開發還是生產環境中。

- **標準函式庫：** 它使用標準的 `logging` 函式庫，因此任何與之搭配使用的配置或處理程序 (handler) 都將適用於 ADK。
- **階層式日誌記錄器：** 日誌記錄器根據模組路徑進行階層式命名（例如 `google_adk.google.adk.agents.llm_agent`），從而可以對框架的哪些部分產生日誌進行細粒度控制。
- **用戶配置：** 框架本身不配置日誌記錄。使用該框架的開發人員有責任在其應用程式的進入點設置所需的日誌記錄配置。

## 如何配置日誌記錄 (How to Configure Logging)

您可以在初始化和運行代理之前，在主應用程式腳本（例如 `main.py`）中配置日誌記錄。最簡單的方法是使用 `logging.basicConfig`。

### 範例配置 (Example Configuration)

```python
import logging

# 配置基本的日誌記錄設定
logging.basicConfig(
    level=logging.DEBUG, # 設定日誌層級為 DEBUG 以顯示詳細資訊
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s' # 定義日誌輸出格式
)

# 您的 ADK 代理代碼如下...
# from google.adk.agents import LlmAgent
# ...
```

### 使用 ADK CLI 配置日誌記錄 (Configuring Logging with the ADK CLI)

當使用 ADK 內建的 Web 或 API 伺服器運行代理時，您可以直接從命令列輕鬆控制日誌詳細程度。`adk web`、`adk api_server` 和 `adk deploy cloud_run` 命令都接受 `--log_level` 選項。

這提供了一種無需修改代理原始碼即可設置日誌層級的便捷方式。

> **注意：** 對於 ADK 的日誌記錄器，命令列設置始終優先於程式化配置（如 `logging.basicConfig`）。建議在生產環境中使用 `INFO` 或 `WARNING`，並僅在疑難排解時啟用 `DEBUG`。

**使用 `adk web` 的範例：**

要啟動具有 `DEBUG` 層級日誌記錄的 Web 伺服器，請執行：

```bash
# 以 DEBUG 模式啟動 ADK web 伺服器
adk web --log_level DEBUG path/to/your/agents_dir
```

`--log_level` 選項的可用日誌層級為：

- `DEBUG`
- `INFO`（預設值）
- `WARNING`
- `ERROR`
- `CRITICAL`

> 您也可以使用 `-v` 或 `--verbose` 作為 `--log_level DEBUG` 的快捷方式。
>
> ```bash
> adk web -v path/to/your/agents_dir
> ```

### 日誌層級 (Log Levels)

ADK 使用標準日誌層級對訊息進行分類。配置的層級決定了記錄哪些資訊。

| 層級          | 描述                                                                                                   | 記錄的資訊類型                                                                                                                                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`DEBUG`**   | **調試的關鍵。** 用於細粒度診斷資訊的最詳細層級。                                                     | - **完整的 LLM 提示詞：** 發送給語言模型的完整請求，包括系統指令、歷史記錄和工具。 - 來自服務的詳細 API 回應。 - 內部狀態轉換和變數值。                                                                               |
| **`INFO`**    | 關於代理生命週期的通用資訊。                                                                           | - 代理初始化和啟動。 - 會話創建和刪除事件。 - 工具的執行，包括其名稱和參數。                                                                                                                                           |
| **`WARNING`** | 表示潛在問題或使用了已棄用的功能。代理繼續運行，但可能需要注意。                                       | - 使用已棄用的方法或參數。 - 系統已從中恢復的非關鍵錯誤。                                                                                                                                                             |
| **`ERROR`**   | 阻止操作完成的嚴重錯誤。                                                                               | - 對外部服務（例如 LLM、會話服務）的 API 調用失敗。 - 代理執行期間未處理的異常。 - 配置錯誤。                                                                                                                         |

> **注意：** 建議在生產環境中使用 `INFO` 或 `WARNING`。僅在積極排查問題時才啟用 `DEBUG`，因為 `DEBUG` 日誌可能非常冗長且可能包含敏感資訊。

## 閱讀並理解日誌 (Reading and Understanding the Logs)

`basicConfig` 範例中的 `format` 字串決定了每條日誌訊息的結構。

這是一個日誌條目範例：

```
2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }
```

| 日誌區段                        | 格式說明符       | 意義                                           |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | 時間戳記                                       |
| `DEBUG`                         | `%(levelname)s`  | 嚴重程度層級                                   |
| `google_adk.models.google_llm`  | `%(name)s`       | 日誌記錄器名稱（產生該日誌的模組）             |
| `LLM Request: contents { ... }` | `%(message)s`    | 實際的日誌訊息                                 |

透過閱讀日誌記錄器名稱，您可以立即精確定位日誌來源，並了解其在代理架構中的背景。

## 使用日誌進行調試：一個實際範例 (Debugging with Logs: A Practical Example)

**場景：** 您的代理沒有產生預期的輸出，並且您懷疑發送給 LLM 的提示詞不正確或缺少資訊。

**步驟：**

1.  **啟用 DEBUG 日誌記錄：** 在您的 `main.py` 中，按照配置範例所示將日誌層級設置為 `DEBUG`。

    ```python
    # 設定日誌等級為 DEBUG 以獲得詳細調試資訊
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```

2.  **運行您的代理：** 像往常一樣執行您的代理任務。

3.  **檢查日誌：** 在主控台輸出中查找來自 `google.adk.models.google_llm` 日誌記錄器的、以 `LLM Request:` 開頭的訊息。

    ```text
    ...
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - Sending out request, model: gemini-2.0-flash, backend: GoogleLLMVariant.GEMINI_API, stream: False
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm -
    LLM Request:
    -----------------------------------------------------------
    System Instruction:

          You roll dice and answer questions about the outcome of the dice rolls.
          You can roll dice of different sizes.
          You can use multiple tools in parallel by calling functions in parallel(in one request and in one round).
          It is ok to discuss previous dice roles, and comment on the dice rolls.
          When you are asked to roll a die, you must call the roll_die tool with the number of sides. Be sure to pass in an integer. Do not pass in a string.
          You should never roll a die on your own.
          When checking prime numbers, call the check_prime tool with a list of integers. Be sure to pass in a list of integers. You should never pass in a string.
          You should not check prime numbers before calling the tool.
          When you are asked to roll a die and check prime numbers, you should always make the following two function calls:
          1. You should first call the roll_die tool to get a roll. Wait for the function response before calling the check_prime tool.
          2. After you get the function response from roll_die tool, you should call the check_prime tool with the roll_die result.
            2.1 If user asks you to check primes based on previous rolls, make sure you include the previous rolls in the list.
          3. When you respond, you must include the roll_die result from step 1.
          You should always perform the previous 3 steps when asking for a roll and checking prime numbers.
          You should not rely on the previous history on prime results.


    You are an agent. Your internal name is "hello_world_agent".

    The description about you is "hello world agent that can roll a dice of 8 sides and check prime numbers."
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

    2025-07-10 15:26:13,779 - INFO - google_genai.models - AFC is enabled with max remote calls: 10.
    2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm -
    LLM Response:
    -----------------------------------------------------------
    Text:
    I have rolled a 6 sided die, and the result is 2.
    ...
    ```

4.  **分析提示詞：** 透過檢查記錄請求的 `System Instruction`、`contents`、`functions` 部分，您可以驗證：

    - 系統指令是否正確？
    - 對話歷史記錄（`user` 和 `model` 回合）是否準確？
    - 是否包含了最新的用戶查詢？
    - 是否向模型提供了正確的工具？
    - 模型是否正確調用了工具？
    - 模型回應需要多長時間？

這種詳細的輸出允許您直接從日誌文件中診斷各種問題，從錯誤的提示工程到工具定義的問題。
