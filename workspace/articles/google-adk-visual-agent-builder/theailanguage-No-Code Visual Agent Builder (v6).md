您的查詢是關於**Google ADK 可視化構建器**（Visual Agent Developer by Google ADK）的**重點**。這是一個新的**無程式碼**（no-code）工具，用於使用 Google ADK 框架構建 AI 代理（Agent）。

以下是根據來源內容，對此工具的功能、設置流程、代理類型和當前限制的全面總結：

### 一、 ADK 可視化構建器概述與核心功能

1.  **性質與目的**
    *   ADK 可視化構建器是 Google ADK 的一部分，它提供了一個**可視化的無程式碼構建器**，用於創建代理工作流程。
    *   它的功能與 OpenAI Agent Builder 和 NATN 類似。
    *   該工具作為 **ADK web** 介面的一部分提供。

2.  **介面與操作**
    *   核心介面是一個**畫布**（canvas）。
    *   用戶可以從左側面板拖曳組件來創建工作流程。
    *   操作方式包括拖曳節點來移動，以及使用 `Shift + 點擊` 來連接節點。
    *   構建完成後，可以點擊底部的「**儲存**」（save）或「取消」（cancel）按鈕來保存或放棄工作流程。

3.  **支援的代理與配置**
    *   左側邊欄提供配置選項，允許用戶添加不同類型的代理和回調（callbacks）。
    *   可添加的代理工作流程類型包括：
        *   **LLM 代理**（LLM agent）：用於執行基於指令的單純任務，是基礎類別。
        *   **順序代理**（sequential agent）。
        *   **循環代理**（loop agent）。
        *   **並行代理**（parallel agent）。
    *   可添加的回調選項包括 `before agent` 和 `after agent`。
    *   配置時可選擇模型，例如 **Gemini 2.5 Flash**（較快，適用於測試）或 2.5 Pro。

4.  **Gemini 構建器助手（Builder Assistant）**
    *   這是 ADK 可視化構建器的一項重要功能，它利用 **Gemini** 提供幫助。
    *   用戶可以在聊天框中輸入提示，描述想要的代理類型。
    *   助手隨後會詢問澄清問題，例如想使用的模型或是否需要子代理。
    *   確認後，助手會為用戶**自動構建整個代理**，並將相關檔案寫入本地資料夾。
    *   助手甚至可以提供更精細的設計，例如創建一個空的 `tools` 目錄和一個 `web_page_writer.py` 腳本，作為代理可以調用的自定義工具。

5.  **底層結構**
    *   該無程式碼構建器在後端生成的檔案是 **YML 檔案**。
    *   這些 YML 檔案類似於 ADK 的代理配置（agent config）功能，這表明可視化構建器可能是基於現有的代理配置功能集之上構建的。

### 二、 環境設置與運行步驟

要運行 ADK 可視化構建器，需要進行以下設置：

1.  **專案準備**
    *   創建一個新的資料夾（例如 `version 6 ADK no code`）。
    *   必須有一個程式碼資料夾，因為無程式碼構建器會將生成的代理配置檔案寫入其中。
    *   在該目錄下，初始化一個新的 Python 專案（使用 `uv init`）。
    *   創建並啟動虛擬環境（使用 `uv venv`，然後 `source .venv/bin/activate`）。
    *   添加 Google ADK 套件（使用 `uv add google-adk`）。

2.  **API 密鑰設置**
    *   創建一個 `.env` 檔案。
    *   獲取 **Google API Key**，需要訪問 `aistudio.google.com/api-keys`。
    *   將密鑰添加到 `.env` 檔案中，格式為 `GOOGLE_API_KEY=您的密鑰`。
    *   **ADK web 會自動查找並使用此密鑰**。
    *   建議將 `.env` 檔案添加到 `.gitignore` 以確保密鑰安全。

3.  **運行與訪問**
    *   在設置好的目錄中，執行命令 `adk web`。
    *   這將在 `http://localhost:8000` 上啟動 ADK web 介面。
    *   在介面中，點擊「Select an agent」下方的「**+**」按鈕，選擇「create new agent in builder mode」來開始構建新的代理。

### 三、 實作範例：網頁生成器代理

在來源中，建立了一個簡單的單一代理系統來生成網頁：

1.  **代理目標**
    *   該代理（`root website builder`）接收一個主題作為用戶輸入。
    *   其指令是基於查詢，**構建一個統一的 HTML + CSS + JS 網頁文件**。

2.  **手動構建步驟**
    *   創建名為 `webpage generator 2` 的新代理。
    *   將代理類型設置為 **LLM agent**。
    *   選擇模型為 **Gemini 2.5 Flash**。
    *   輸入指令：「Build a single unified HTML + CSS + JS document that is a web page as per the user query」（根據用戶查詢，構建一個單一、統一的 HTML+CSS+JS 文件，作為一個網頁）。
    *   測試時，向代理發送查詢「build a generic landing page template」，代理成功輸出了完整的 HTML 文件。

### 四、 當前限制與注意事項

由於該工具非常新，用戶在使用時需要保持「**容忍**」（tolerant）：

*   **初期版本與錯誤**：目前它是早期版本（影片錄製時 ADK 版本為 1.18.0），存在許多小故障（glitches）和錯誤，例如節點可能錯位。
*   **文檔不足**：目前還沒有完善的使用文檔。
*   **創建代理的穩定性**：有時創建第一個代理時不會自動進入構建器模式，或編輯選項會變灰，需要重試。
*   **助手輸出的問題**：雖然 Gemini 構建器助手可以設計代理並生成 YML 檔案的內容，但在當前版本中，**UI 介面可能無法成功接收並保存這些詳細的檔案輸出**到本地資料夾，導致生成的 `root_agent.yml` 檔案內容是空的預設值。

總而言之，Google ADK 可視化構建器是一個**非常有前景**的工具，它將 ADK 的強大功能（如多代理協調和工具添加）帶入了無程式碼的視覺化環境中，一旦完全開發，將極大地簡化工作流程構建。