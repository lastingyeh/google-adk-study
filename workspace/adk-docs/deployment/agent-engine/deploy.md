# 部署至 Vertex AI Agent Engine

🔔 `更新日期：2026 年 1 月 8 日`

本部署程序說明如何將 ADK 代理程式代碼標準部署至 Google Cloud
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)。
如果您已有現有的 Google Cloud 專案，且希望仔細管理將 ADK 代理程式部署到 Agent Engine 執行階段環境，則應遵循此部署路徑。這些說明使用 Cloud Console、gcloud 命令列介面和 ADK 命令列介面 (ADK CLI)。此路徑推薦給已熟悉配置 Google Cloud 專案的使用者，以及準備進行生產環境部署的使用者。

這些說明描述了如何將 ADK 專案部署到 Google Cloud Agent Engine 執行階段環境，其中包括以下階段：

*   [設定 Google Cloud 專案](#設定-google-cloud-專案)
*   [準備代理程式專案資料夾](#定義您的代理程式)
*   [部署代理程式](#部署代理程式)

## 設定 Google Cloud 專案

要將您的代理程式部署到 Agent Engine，您需要一個 Google Cloud 專案：

1. **登入 Google Cloud**：
    * 如果您是 Google Cloud 的**現有使用者**：
        * 請透過 [https://console.cloud.google.com](https://console.cloud.google.com) 登入。
        * 如果您之前使用的免費試用已過期，您可能需要升級到[付費帳單帳戶](https://docs.cloud.google.com/free/docs/free-cloud-features#how-to-upgrade)。
    * 如果您是 Google Cloud 的**新使用者**：
        * 您可以註冊[免費試用計畫](https://docs.cloud.google.com/free/docs/free-cloud-features)。免費試用可讓您獲得 300 美元的迎新抵用金，可在 91 天內用於各種 [Google Cloud 產品](https://docs.cloud.google.com/free/docs/free-cloud-features#during-free-trial)，且不會向您收費。在免費試用期間，您還可以存取 [Google Cloud 免費層級](https://docs.cloud.google.com/free/docs/free-cloud-features#free-tier)，這讓您可以在指定的每月限制內免費使用特定產品，並參與產品特定的免費試用。

2. **建立 Google Cloud 專案**
    * 如果您已有現有的 Google Cloud 專案，可以使用它，但請注意此過程可能會向專案添加新服務。
    * 如果您想建立新的 Google Cloud 專案，可以在 [建立專案](https://console.cloud.google.com/projectcreate) 頁面建立一個新專案。

3. **獲取您的 Google Cloud 專案 ID**
    * 您需要您的 Google Cloud 專案 ID，您可以在 GCP 首頁上找到它。請務必記錄專案 ID（包含連字號的字母數字），而非專案編號（純數字）。

    <img src="https://google.github.io/adk-docs/assets/project-id.png" alt="Google Cloud Project ID">

4. **在您的專案中啟用 Vertex AI**
    * 要使用 Agent Engine，您需要[啟用 Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)。點擊「啟用」按鈕以啟用該 API。啟用後，它應顯示為「API 已啟用」。

5. **在您的專案中啟用 Cloud Resource Manager API**
    * 要使用 Agent Engine，您需要[啟用 Cloud Resource Manager API](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview)。點擊「啟用」按鈕以啟用該 API。啟用後，它應顯示為「API 已啟用」。

6. **建立 Google Cloud Storage (GCS) Bucket**：
    * Agent Engine 需要一個 GCS bucket 來存放您代理程式的代碼和部署所需的依賴項。如果您已經有一個 GCS bucket，建議專門為部署用途建立一個新的。
    * 按照[說明](https://cloud.google.com/storage/docs/creating-buckets)建立 GCS bucket。建立第一個 bucket 時，您應該從預設設定開始。
    * 建立儲存 bucket 後，您應該可以在 [Cloud Storage Buckets 頁面](https://console.cloud.google.com/storage/browser) 上看到它。
    * 您需要 GCS bucket 路徑來設定為您的暫存 bucket（staging bucket）。例如，如果您的 GCS bucket 名稱為 "my-bucket"，則您的 bucket 路徑應為 "gs://my-bucket"。

> [!NOTE] "不使用 GCS bucket 進行部署"
    您可以使用不同的配置方法來避免在部署時使用 Google Cloud Storage bucket。有關此方法的詳細資訊，請參閱 Agent Engine 文件中的 [部署代理程式](https://docs.cloud.google.com/agent-builder/agent-engine/deploy#from-source-files)。

## 設定您的開發環境

現在您已經準備好了 Google Cloud 專案，可以回到您的開發環境。這些步驟需要訪問開發環境中的終端機以執行命令列指令。

### 使用 Google Cloud 驗證您的開發環境

*   您需要驗證您的開發環境，以便您和您的代碼可以與 Google Cloud 互動。為此，您需要 gcloud CLI。如果您從未使用的 gcloud CLI，則需要先[下載並安裝它](https://docs.cloud.google.com/sdk/docs/install-sdk)，然後再繼續執行以下步驟：

*   在您的終端機中運行以下命令，以使用者身份訪問您的 Google Cloud 專案：

    ```shell
    # 登入 Google Cloud 帳戶
    gcloud auth login
    ```

    驗證後，您應該會看到訊息 `You are now authenticated with the gcloud CLI!`。

*   運行以下命令來驗證您的代碼，以便它可以與 Google Cloud 協作：

    ```shell
    # 取得應用程式預設認證 (Application Default Credentials)
    gcloud auth application-default login
    ```

    驗證後，您應該會看到訊息 `You are now authenticated with the gcloud CLI!`。

*   （選用）如果您需要設定或更改 gcloud 中的預設專案，可以使用：

    ```shell
    # 設定預設專案 ID
    gcloud config set project MY-PROJECT-ID
    ```

### 定義您的代理程式

在準備好 Google Cloud 和開發環境後，您就可以部署代理程式了。這些說明假設您有一個代理程式專案資料夾，例如：

```shell
multi_tool_agent/
├── .env          # 環境變數設定
├── __init__.py   # 套件初始化文件
└── agent.py      # 代理程式核心邏輯
```

有關專案檔案和格式的更多詳細資訊，請參閱 [multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent) 代碼範例。

## 部署代理程式

您可以使用 `adk deploy` 命令列工具從終端機進行部署。此過程會封裝您的代碼，將其構建為容器，並將其部署到託管的 Agent Engine 服務。此過程可能需要幾分鐘。

以下範例部署命令使用 `multi_tool_agent` 範例代碼作為要部署的專案：

```shell
# 設定環境變數
PROJECT_ID=my-project-id
LOCATION_ID=us-central1
GCS_BUCKET=gs://MY-CLOUD-STORAGE-BUCKET

# 使用 ADK CLI 部署至 Agent Engine
adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --staging_bucket=$GCS_BUCKET \
        --display_name="My First Agent" \
        multi_tool_agent
```

對於 `region`（區域），您可以在 [Vertex AI Agent Builder 位置頁面](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine)上找到支援的區域列表。要了解 `adk deploy agent_engine` 命令的 CLI 選項，請參閱 [ADK CLI 參考](https://google.github.io/adk-docs/api-reference/cli/cli.html#adk-deploy-agent-engine)。

### 部署命令輸出

成功部署後，您應該會看到以下輸出：

```shell
# 正在建立 AgentEngine
Creating AgentEngine
# 建立 AgentEngine 後端 LRO (長期運行操作)
Create AgentEngine backing LRO: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944/operations/2356952072064073728
# 在指定的 URL 查看進度和日誌
View progress and logs at https://console.cloud.google.com/logs/query?project=hopeful-sunset-478017-q0
# AgentEngine 建立完成。資源名稱如下：
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
# 若要在另一個工作階段中使用此 AgentEngine：
To use this AgentEngine in another session:
agent_engine = vertexai.agent_engines.get('projects/123456789/locations/us-central1/reasoningEngines/751619551677906944')
# 清理暫存資料夾
Cleaning up the temp folder: /var/folders/k5/pv70z5m92s30k0n7hfkxszfr00mz24/T/agent_engine_deploy_src/20251219_134245
```

請注意，您現在擁有一個部署代理程式的 `RESOURCE_ID`（在上述範例中為 `751619551677906944`）。您需要此 ID 編號連同其他值，以便在 Agent Engine 上使用您的代理程式。

## 在 Agent Engine 上使用代理程式

完成 ADK 專案部署後，您可以使用 Vertex AI SDK、Python requests 函式庫或 REST API 用戶端來查詢代理程式。本節提供了有關與代理程式互動所需內容以及如何建構 URL 以與代理程式的 REST API 互動的一些資訊。

要與 Agent Engine 上的代理程式進行互動，您需要以下資訊：

*   **PROJECT_ID**（例如："my-project-id"）：您可以在[專案詳細資訊頁面](https://console.cloud.google.com/iam-admin/settings)上找到。
*   **LOCATION_ID**（例如："us-central1"）：您用於部署代理程式的區域。
*   **RESOURCE_ID**（例如："751619551677906944"）：您可以在 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) 上找到。

查詢 URL 的結構如下：

```shell
# Agent Engine 查詢 API 端點結構
https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query
```

您可以使用此 URL 結構從您的代理程式發送請求。有關如何發送請求的更多資訊，請參閱 Agent Engine 文件中的說明：[使用 Agent Development Kit 代理程式](https://docs.cloud.google.com/agent-builder/agent-engine/use/adk#rest-api)。您也可以查看 Agent Engine 文件以了解如何管理您的[已部署代理程式](https://docs.cloud.google.com/agent-builder/agent-engine/manage/overview)。有關測試和與已部署代理程式互動的更多資訊，請參閱[在 Agent Engine 中測試已部署的代理程式](/adk-docs/deploy/agent-engine/test/)。

### 監控與驗證

*   您可以在 Google Cloud Console 的 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) 中監控部署狀態。
*   有關更多詳細資訊，您可以訪問 Agent Engine 文件中關於[部署代理程式](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)和[管理已部署的代理程式](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)的部分。

## 測試已部署的代理程式

完成 ADK 代理程式部署後，您應該在新的代管環境中測試工作流程。有關測試部署到 Agent Engine 的 ADK 代理程式的更多資訊，請參閱[在 Agent Engine 中測試已部署的代理程式](test.md)。
