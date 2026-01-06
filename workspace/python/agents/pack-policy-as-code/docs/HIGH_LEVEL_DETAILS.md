# Policy-as-Code Agent：高階細節說明

## 目的

Policy-as-Code Agent旨在自動化並簡化資料治理，讓使用者能以自然語言定義與驗證資料政策。它解決了人工治理檢查的困難與傳統規則式系統的僵化問題。


## 價值主張

### 技術面（CEs/SAs）
*   **Agentic AI**：以生成式邏輯取代靜態規則。LLM可即時產生Python政策檢查程式，展現高階推理能力。
*   **混合執行**：結合LLM意圖解析與確定性Python執行，消除執行時的幻覺（hallucinations）。
*   **智慧記憶體**：向量搜尋記憶體（Firestore）快取並學習成功政策，最佳化延遲與成本，是關鍵的生產模式。
*   **雙模式**：可彈性針對離線GCS匯出或即時Dataplex API執行，展現多元整合能力。

### 商業面（Sales/FSRs）
*   **民主化治理**：讓非技術人員也能以自然語言稽核資料，消除工程瓶頸。
*   **主動風險控管**：以「合規即程式」即時測試政策（如保存規則），降低法規罰款風險。
*   **效率提升**：自動化人工資料集檢查，將數天工作縮短為數秒。
*   **自我修復**：不僅監控，更主動建議違規修正方案，實現主動治理。


## 1. 運作流程：從查詢到報告

Agent遵循簡單且強大的六步驟流程：

1.  **搜尋記憶體**：當使用者提供政策時，Agent會先語意搜尋內部記憶體，檢查是否已有類似政策的程式碼。搜尋可依作者與日期篩選。
2.  **理解政策**：若未找到快取政策，使用者以自然語言輸入政策，例如*「所有 'finance' 領域的資料集都必須有 'data_owner' 標籤。」*
3.  **產生並快取邏輯**：Agent核心（Gemini LLM）動態產生對應的Python檢查程式，並將新政策儲存至記憶體，支援版本控管。
4.  **執行與回報**：Agent執行快取或新產生的Python程式，針對選定的中繼資料來源（GCS匯出或Dataplex即時查詢），回報違規資源。
5.  **建議修正**：如有違規，Agent可應使用者要求，利用LLM針對每項違規提出可行修正建議。
6.  **回饋與排名**：政策執行後，使用者可評分，回饋將用於政策排名，優先推薦最佳政策。

## 2. 主要功能

*   **自然語言介面**：無需撰寫程式或特殊查詢語言。
*   **智慧且具版本控管的記憶體**：Agent會快取成功產生的政策。收到新查詢時，會先搜尋記憶體是否有可重用的類似政策，節省時間與成本，確保政策一致執行。記憶體支援：
    *   **版本控管**：政策可更新，Agent會追蹤不同版本。
    *   **自動修剪**：可自動移除舊的或未使用的政策。
    *   **增強搜尋**：可依作者與日期篩選政策。
    *   **排名**：根據使用者回饋對政策排名，優先推薦最有效政策。
*   **動態且彈性**：可即時產生程式碼，支援複雜與細緻的政策需求。
*   **彈性資料來源**：可針對GCS離線匯出或Dataplex即時查詢進行分析。
*   **可行性報告**：精確指出違規項目，便於快速修正。
*   **可行性修正建議**：提供明確且可執行的違規修正步驟。

## 3. 技術深度解析

*   **大型語言模型（LLM）**：Agent採用雙模型架構，兼顧效能與成本：
    *   **Gemini 2.5 Flash**：負責對話邏輯與將用戶請求導向正確工具。
    *   **Gemini 2.5 Pro**：負責最複雜的任務：將自然語言政策轉換為精確可執行的Python程式碼。
*   **Agentic AI架構**：本Agent屬於**Agentic AI**，比傳統**AI Agent**更進階。
    *   **AI Agent vs. Agentic AI：**
        *   **AI Agent**：通常依照預先編寫的規則或狹義模型執行特定任務。
        *   **Agentic AI**：可自主推理、規劃並執行多步驟以達成高階目標，能適應、學習並運用工具解決複雜問題，無需每步指令。
    *   **為何屬於Agentic AI：**
        *   **動態程式碼產生**：Agent不是執行預寫檢查器，而是**即時產生**Python檢查程式，展現高度推理與自主性。
        *   **適應性**：不限於固定政策，可即時支援新型政策需求，無需重寫程式。
        *   **自主工具鏈結**：Agent自動串接工具，先產生政策程式碼再執行，無縫滿足用戶需求。
    *   **規劃與執行：**
        *   **規劃**：LLM首先將用戶英文查詢轉換為邏輯且可執行的Python函式，並依據精心設計的提示模板（`prompts/v4.md`）提供上下文、中繼資料結構與動態範例。
        *   **執行**：Agent將產生的程式碼以Python `exec()`執行，完成實際驗證。
*   **核心組件：**
    *   **`llm_generate_policy_code`**：Agent「大腦」，將用戶查詢包裝成詳細提示，送至Gemini LLM取得Python驗證程式碼。
    *   **`run_simulation`**：Agent「引擎室」，將LLM產生的Python程式碼執行於中繼資料，收集並格式化違規項目。
    *   **中繼資料來源**：Agent可從兩種來源取得中繼資料：
        *   **GCS Loader**：讀取Google Cloud Storage（GCS）匯出的中繼資料。
        *   **Dataplex Search**：即時查詢Dataplex Universal Catalog並取得完整細節。
*   **技術堆疊：**
    *   **主要語言**：Python
    *   **關鍵函式庫：**
        *   `vertexai`：與Gemini LLM互動。
        *   `google-cloud-firestore`：與Firestore資料庫互動，作為記憶體。
        *   `google-cloud-storage`：讀取GCS中的中繼資料檔案。
        *   `google-cloud-dataplex`：與Dataplex API互動。
        *   `google-adk`：Agent開發框架。
    *   **資料格式**：支援**JSONL**（JSON Lines）格式的中繼資料匯出，為Dataplex標準輸出。
*   **安全性：**
    *   **AST分析**：執行程式碼前，Agent會用Python AST模組靜態分析，偵測並阻擋危險匯入（如`os`、`sys`、`subprocess`）與不安全呼叫（如`eval`、`open`）。
    *   **受限執行**：動態程式碼僅在受限環境下以`exec()`執行，僅允許安全函式庫（如`json`、`re`、`datetime`）與標準內建。
*   **可擴充性：**
    *   新型政策可即時支援，無需修改底層程式，LLM可隨需產生所需邏輯。

## 4. 使用範例

1.  **使用者輸入（自然語言）：**
    > 「所有public_data資料集中的表格都必須有'sensitivity'標籤」

2.  **Agent產生的程式碼（簡化版）：**
    ```python
        # 檢查政策：所有 public_data 資料集中的表格都必須有 'sensitivity' 標籤
        def check_policy(metadata: list) -> list:
            violations = []  # 儲存所有違規項目
            for resource in metadata:
                # 判斷該資源是否屬於 'public_data' 資料集且類型為表格
                is_in_public_data_dataset = resource.get('dataset') == 'public_data' and resource.get('type') == 'table'
                # 判斷該資源是否缺少 'sensitivity' 標籤
                sensitivity_label_is_missing = 'sensitivity' not in resource.get('labels', {})
                # 若同時符合上述條件，則記錄違規
                if is_in_public_data_dataset and sensitivity_label_is_missing:
                    violations.append({
                        "resource_name": resource['fullyQualifiedName'],  # 資源名稱
                        "violation": "表格屬於 'public_data' 資料集但缺少 'sensitivity' 標籤。"  # 違規原因
                    })
            return violations  # 回傳所有違規項目
    ```

3.  **最終輸出給使用者：**
    > **發現政策違規：**
    > *   **資源：** `bigquery:data-governance-agent-dev.public_data.daily_active_users`
    >     *   **違規：** 表格屬於'public_data'資料集但缺少'sensitivity'標籤。
    > *   **資源：** `bigquery:data-governance-agent-dev.public_data.website_commenters`
    >     *   **違規：** 表格屬於'public_data'資料集但缺少'sensitivity'標籤。


## 5. 進階功能

### 📋 合規評分卡與報告
Agent提供強大的高階治理報告工具：
*   **合規評分卡**：可對資料進行「健康檢查」（如：`「為我的dataplex資產產生合規評分卡」`），Agent會執行一系列**核心政策**並計算合規分數。
*   **可設定核心政策**：可自訂組織的「合規」定義，檢視、增刪並儲存專屬核心政策至Agent記憶體。
*   **豐富報告**：違規報告可匯出為**CSV**或**HTML**，便於離線分享，或直接上傳至Google Cloud Storage。

### 📊 政策分析與歷史紀錄
Agent追蹤所有政策執行，支援進階分析：
*   **執行歷史**：可查詢過去執行情形（如：`「昨天哪些政策失敗？」`）。
*   **違規排行**：找出最常違規的政策。
*   **資源搜尋**：可用部分名稱查詢特定資源的所有違規紀錄。
*   **違規資源排行**：找出最不合規的資產。

### 🔌 Model Context Protocol (MCP) 整合
Agent相容於**Model Context Protocol (MCP)**。
*   **Dataplex MCP**：可連接Dataplex MCP伺服器，取得更多互動工具。
*   **可擴充性**：可連接其他MCP相容伺服器，擴展Agent功能。
