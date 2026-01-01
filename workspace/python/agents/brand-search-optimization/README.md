# 品牌搜尋優化（Brand Search Optimization）- 用於搜尋優化的 Web Browser Agent

## 概覽

此 Agent 的目標是協助零售網站強化商品資料。它會根據商品資料（例如：標題、描述、屬性）產生關鍵字，接著造訪網站進行搜尋，並分析前幾名結果，以提供「如何豐富商品標題」的建議。這能用來改善「Null & low recovery」或「Zero Results」等搜尋問題（通常代表商品資料與使用者搜尋意圖之間存在落差）。此 Agent 也可延伸至強化商品描述與屬性。

> **重點註解**
>
> * 這個流程的核心是：用「商品資料」產生查詢詞，再用「實際站內搜尋結果」回推應補強的商品內容。
> * 主要依賴的能力是：computer use（瀏覽器操作）與 BigQuery 資料連線。

## Agent 詳細資訊

此 Agent 示範了 Multi Agent 的設計，並包含 tool calling 與網頁爬取（web crawling）。

| Attribute                   | Detail                                               |
| --------------------------- | ---------------------------------------------------- |
| Interaction Type            | Workflow                                             |
| Complexity                  | Advanced                                             |
| Agent Type                  | Multi Agent                                          |
| Multi Agent Design Pattern: | Router Agent                                         |
| Components                  | BigQuery Connection, Computer use, Tools, Evaluation |
| Vertical                    | Retail                                               |

### Agent 架構

![Brand Search Optimization](./brand_search_optimization.png)

### 主要功能

* **Tools：**

  * `function_calling`：根據使用者提供的 brand，從商品目錄（例如 BigQuery table）取得資料。輸入為 brand 字串，輸出為資料庫紀錄清單。

  * `load_artifacts_tool`：將網頁原始碼載入為 artifact，以便分析頁面元件並決定後續動作（例如：點擊搜尋按鈕）。

  * `Website crawling`：透過多個獨立工具完成，例如 `go_to_url`、`take_screenshot`、`find_element_with_text`、`click_element_with_text`、`enter_text_into_element`、`scroll_down_screen`、`get_page_source`、`analyze_webpage_and_determine_action`。

* **Evaluation：** 使用 ADK 提供的 OOTB evaluation，可透過 `sh deployment/eval.sh` 執行。

> **重點註解**
>
> * `Website crawling` 相關工具多為「瀏覽器自動化」的操作原子（atomic actions），可靠性通常取決於目標網站的 UI 與反自動化策略。

## 設定與安裝

1. **先備條件：**
    * Python 3.11+
    * Poetry
        * 用於相依性管理與打包。請依照官方文件安裝：[Poetry website](https://python-poetry.org/docs/)
    * Google Cloud Platform 專案
    * 從 [here](https://aistudio.google.com) 取得 API key（若使用 Vertex AI 的 Gemini 則不需要）

2. **設定：**
    * Env 檔案設定
        * 複製範例 env 檔：`cp env.example .env`
        * 設定 `DISABLE_WEB_DRIVER=1`
        * 在 `.env` 填入下列變數值
            * `GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT>`
            * `GOOGLE_CLOUD_LOCATION=<YOUR_LOCATION>`

    * **API Keys：**
        * 將 API key 填入 `.env` 的 `GOOGLE_API_KEY`
        * Google API key 與 Vertex AI 設定不需要同時存在，兩者擇一即可

    * **BigQuery Setup：**
        * `.env` 內設定 `DATASET_ID`
        * `.env` 內設定 `TABLE_ID`
        * BigQuery table 可透過下方 `sh deployment/run.sh` 自動建立/填入樣本資料，或依照 `BigQuery Setup` 章節手動設定

    * **其他設定：**
        * 可在 `.env` 透過 `MODEL` 切換 Gemini Model
        * 當 `DISABLE_WEB_DRIVER=1` 時，會讓你可以跑 unit tests（詳見下方 `Unit Tests`）。**NOTE**：非測試情境時，建議預設保持為 0。

> **重點註解**
>
> * 安裝/測試期間先用 `DISABLE_WEB_DRIVER=1`（便於測試），實際跑 Agent 流程時再切回 `DISABLE_WEB_DRIVER=0`（啟用瀏覽器）。

3. **使用 Google Cloud 帳號進行驗證：**

    ```bash
    gcloud auth application-default login
    ```

4. **安裝：**

    * 使用 `deployment/run.sh` 安裝相依套件並填入資料庫

        `````bash
        # Clone this repository.
        git clone https://github.com/google/adk-samples.git
        cd adk-samples/python/agents/brand-search-optimization

        # Run This script
        # 1. Creates and activates a new virtual env
        # 2. Installs python packages
        # 3. Populates BigQuery data using variables set in `.env` file
        sh deployment/run.sh
        `````

    * 將 `DISABLE_WEB_DRIVER=0`

## 執行 Agent

你需要執行 `adk run brand_search_optimization` 來啟動 Agent。

你也可以用 `adk web` 啟動 Web App。

`adk web` 會在本機啟動一個 web server 並輸出 URL。你可以開啟該 URL，以聊天介面方式與 Agent 互動（UI 一開始會是空白）。

從下拉選單中選擇 "brand-search-optimization"。

> **NOTE**：此流程應會透過 web-driver 開啟新的 Chrome 視窗。若沒有開啟，請確認 `.env` 中 `DISABLE_WEB_DRIVER=0`。

### Brand Name

* 若你已執行 `deployment/run.sh`，Agent 會預先設定 brand 為 `BSOAgentTestBrand`。當 Agent 詢問 brand name 時，請輸入 `BSOAgentTestBrand`。
* 若使用自訂資料，請改成你的 brand name。
* 當你提供 brand name 後，Agent flow 會被觸發。

> **NOTE**
>
> * 請勿關閉 Agent 額外開啟的 Chrome 視窗。
> * 當 Agent 提供關鍵字清單後，請要求 Agent 去搜尋網站，例如："Can you search website?"、"Can you search of keywords on website?"、"Help me search for keywords on website" 等。
> * 第一次造訪 Google Shopping 時可能需要完成 captcha；完成後通常後續執行會更順。

> **重點註解**
>
> * 常見卡住點出現在「產生關鍵字」後未自動進入「網站搜尋」階段；此時直接請它搜尋 top keyword 通常可繼續流程。

### 範例互動

提供一個範例 session，示範 Brand Search Optimizer 如何針對 `BSOAgentTestBrand` 在 Google Shopping 上運作：[`example_interaction.md`](tests/example_interaction.md)

此檔案包含完整對話紀錄，涵蓋從找關鍵字到產出「top 3 搜尋結果標題」的比較報告。

> **Disclaimer**：此範例以 Google Shopping 做示範，但你必須自行確保符合目標網站的服務條款。

## 評估（Evaluating the Agent）

此範例使用 ADK 的 evaluation component，會以 `eval/data/` 內的 evalset 與 `eval/data/test_config.json` 的設定，來評估 brand search optimization agent。

你必須在 `brand-search-optimization` 目錄下執行：

```bash
sh deployment/eval.sh
```

## 單元測試（Unit Tests）

依下列步驟使用 `pytest` 執行單元測試：

1. 在 `.env` 設定 `DISABLE_WEB_DRIVER=1`

2. 執行 `sh deployment/test.sh`

此腳本會使用 BigQuery tool 的 mock BQ client，並執行 `tests/unit/test_tools.py` 中的單元測試。

> **重點註解**
>
> * 單元測試通常不依賴真實瀏覽器與真實 BigQuery 連線，目標是讓工具邏輯可被穩定驗證。

## 部署（Deploying the Agent）

可透過以下指令將 Agent 部署到 Vertex AI Agent Engine：

在 `.env` 設定 `DISABLE_WEB_DRIVER=1`

```bash
python deployment/deploy.py --create
```

你也可以依自身需求修改部署腳本。

## 客製化（Customization）

可客製化的方向包含：

* **調整對話流程：** 若要讓 Agent 比較「描述」而非「標題」，可修改 `brand_search_optimization/sub_agents/search_results/prompt.py`，特別是 `SEARCH_RESULT_AGENT_PROMPT` 中 `<Gather Information>` 段落。
* **更換資料來源：** 透過修改 `.env` 指向不同 BigQuery table。
* **更換網站：** 範例使用 Google Shopping；若改用你的網站，請同步調整相關程式碼。

### BigQuery Setup

#### 自動化

`sh deployment/run.sh` 會執行腳本，自動建立/填入 BigQuery table 的樣本資料。其背後會呼叫 `python tools/bq_populate_data.py`。

#### Dataset 與 Table 權限

若你要在「非你擁有」的 BigQuery Table 上執行 Agent，請參考 [here](./customization.md) 以授予必要權限。

#### 手動步驟

若要手動新增資料，請參考 `deployment/bq_data_setup.sql` 中的 SQL。

## 快速指南（Quickstart）

本專案提供 `Makefile` 來簡化常見操作。以下是快速開始步驟：

### 初始設定

1. **複製並設定環境檔：**
   ```bash
   cp env.example .env
   # 編輯 .env 並填入相關配置
   ```

2. **檢查環境：**
   ```bash
   make check-env
   ```

3. **Google Cloud 驗證：**
   ```bash
   gcloud auth application-default login
   ```

### 完整安裝流程

若要進行完整設定（安裝依賴 + 填入 BigQuery 資料）：

```bash
make setup
```

此命令等同於執行 `sh deployment/run.sh`，會自動：
- 使用 Poetry 安裝所有依賴套件
- 建立/填入 BigQuery 資料表的樣本資料

### 常用命令

| 命令           | 說明                           |
| -------------- | ------------------------------ |
| `make help`    | 顯示所有可用命令               |
| `make install` | 安裝專案依賴                   |
| `make setup`   | 完整設定：安裝 + BigQuery 資料 |
| `make test`    | 執行單元測試                   |
| `make eval`    | 執行評估測試                   |
| `make run`     | 執行主程式                     |
| `make clean`   | 清理編譯檔案和快取             |

### 執行 Agent

安裝完成後，使用以下命令執行 Agent：

```bash
# 啟動 Agent
adk run brand_search_optimization

# 或啟動 Web UI
adk web
```

在 Web UI 中：
- 從下拉選單選擇 "brand-search-optimization"
- 輸入 brand name（若使用預設資料，輸入 `BSOAgentTestBrand`）
- 根據提示進行互動

> **NOTE**：確保 `.env` 中設定 `DISABLE_WEB_DRIVER=0`（啟用瀏覽器）

### 測試

**執行單元測試：**
```bash
# 先在 .env 設定 DISABLE_WEB_DRIVER=1
make test
```

**執行評估：**
```bash
make eval
```

### 部署

部署到 Vertex AI Agent Engine：

```bash
make deploy-create PROJECT=<your-project> LOCATION=<location> BUCKET=<bucket-name>
```

刪除已部署的代理：

```bash
make deploy-delete PROJECT=<your-project> LOCATION=<location> RESOURCE_ID=<resource-id>
```

### 開發工具

```bash
# 進入 Poetry shell
make shell

# 顯示依賴列表
make show-deps

# 更新依賴
make update

# 新增開發依賴
make add-dev-pkg PKG=pytest-cov
```

> **提示**：執行 `make help` 可見完整命令列表及詳細說明

## 疑難排解與常見問題

### BigQuery data 不存在

此問題通常與以下原因相關：找不到 dataset、dataset 不在指定 location、或使用者缺少 BigQuery dataset 權限。

Error：

```bash
google.api_core.exceptions.NotFound: 404 Not found: Dataset ...:products_data_agent was not found in location US; reason: notFound, message: Not found: Dataset ...:products_data_agent was not found in location US
```

Fix：
請確認你已完整完成 `BigQuery Setup`。

### Selenium 問題

此問題與 Selenium / Webdriver 相關。

Error：

```bash
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: probably user data directory is already in use, please specify a unique value for --user-data-dir argument, or don't use --user-data-dir
```

Fix：移除資料目錄

```bash
rm -rf /tmp/selenium
```

### Agent flow 問題

#### 已知問題

* 若網站有強力的反 bot 檢查、或搜尋框被隱藏，Agent 可能無法穩定執行。
* Agent 沒有提示下一步：常發生在關鍵字產生階段之後。此時可要求 Agent 直接搜尋 top keyword，例如："can you search for keyword?"，或更明確地說 "transfer me to web browser agent"。
* Agent 再次詢問關鍵字：例如 `Okay, I will go to XYZ.com. What keyword do you want to search for on XYZ?`。請再提供一次關鍵字即可。

> **重點註解**
>
> * 只要流程已切換到網站搜尋，重點是讓「查詢詞」與「目標網站」明確；多補一句 keyword 往往比等待更有效。
>

## 免責聲明（Disclaimer）

此 Agent sample 僅供示範用途，並非用於正式生產環境。它提供一個基礎範例與起點，供個人或團隊在其上進一步開發自己的 agents。

此 sample 未經嚴格測試，可能包含錯誤或限制，且不包含生產環境通常需要的功能或最佳化（例如：健全的錯誤處理、安全性措施、可擴展性、效能考量、完整日誌、或進階設定選項）。

使用者需自行負責後續的開發、測試、安全強化與部署。我們建議在任何實際或關鍵情境使用前，先充分審查、測試並實作適當的防護措施。