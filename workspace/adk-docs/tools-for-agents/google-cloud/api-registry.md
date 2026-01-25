# 從 Cloud API 登錄中心連接 MCP 工具

> 🔔 `更新日期：2026-01-25`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/api-registry/

[`ADK 支援`: `Python v1.20.0` | `預覽版`]

Agent 開發工具包 (ADK) 的 Google Cloud API 登錄中心 (API Registry) 連接器工具，讓您可以透過 [Google Cloud API 登錄中心](https://docs.cloud.google.com/api-registry/docs/overview) 將廣泛的 Google Cloud 服務作為 Model Context Protocol (MCP) 伺服器供您的 Agent 存取。您可以配置此工具將您的 Agent 連接到您的 Google Cloud 專案，並動態存取該專案中啟用的 Cloud 服務。

> [!NOTE] "預覽版發佈"
Google Cloud API 登錄中心功能為預覽版發佈。如需更多資訊，請參閱 [發佈階段說明](https://cloud.google.com/products#product-launch-stages)。

## 先決條件

在將 API 登錄中心與您的 Agent 搭配使用之前，您需要確保以下事項：

-   **Google Cloud 專案：** 配置您的 Agent 使用現有的 Google Cloud 專案來存取 AI 模型。

-   **API 登錄中心存取權限：** 執行 Agent 的環境需要具備 Google Cloud [應用程式預設認證 (Application Default Credentials)](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc) 以及 `apiregistry.viewer` 角色，以便列出可用的 MCP 伺服器。

-   **Cloud API：** 在您的 Google Cloud 專案中，啟用 *cloudapiregistry.googleapis.com* 和 *apihub.googleapis.com* Google Cloud API。

-   **MCP 伺服器與工具存取：** 確保您已在 API 登錄中心為您想要讓 Agent 存取的 Google Cloud 專案中的 Cloud 服務啟用了 MCP 伺服器。您可以在 Cloud 控制台啟用，或使用如下的 gcloud 命令：
    `gcloud beta api-registry mcp enable bigquery.googleapis.com --project={PROJECT_ID}`。
    Agent 使用的認證必須具備存取 MCP 伺服器以及工具所使用的底層服務之權限。例如，要使用 BigQuery 工具，服務帳戶需要具備 BigQuery 的 IAM 角色，如 `bigquery.dataViewer` 和 `bigquery.jobUser`。如需更多關於所需權限的資訊，請參閱 [驗證與存取](#驗證與存取)。

您可以使用以下 gcloud 命令檢查 API 登錄中心啟用了哪些 MCP 伺服器：

```console
# 列出指定專案中已啟用的 MCP 伺服器
gcloud beta api-registry mcp servers list --project={PROJECT_ID}.
```

## 與 Agent 搭配使用

在為 Agent 配置 API 登錄中心連接器工具時，您首先需要初始化 ***ApiRegistry*** 類別以建立與 Cloud 服務的連線，然後使用 `get_toolset()` 函式來獲取 API 登錄中心中註冊的特定 MCP 伺服器之工具集 (Toolset)。以下程式碼範例展示了如何建立一個使用 API 登錄中心所列 MCP 伺服器工具的 Agent。此 Agent 旨在與 BigQuery 進行互動：


```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.api_registry import ApiRegistry

# 使用您的 Google Cloud 專案 ID 和註冊的 MCP 伺服器名稱進行配置
PROJECT_ID = "your-google-cloud-project-id"
MCP_SERVER_NAME = "projects/your-google-cloud-project-id/locations/global/mcpServers/your-mcp-server-name"

# BigQuery 的範例標頭提供者，需要專案標頭。
def header_provider(context):
    # 回傳包含使用者專案 ID 的 HTTP 標頭
    return {"x-goog-user-project": PROJECT_ID}

# 初始化 ApiRegistry
api_registry = ApiRegistry(
    api_registry_project_id=PROJECT_ID,
    header_provider=header_provider
)

# 獲取特定 MCP 伺服器的工具集
registry_tools = api_registry.get_toolset(
    mcp_server_name=MCP_SERVER_NAME,
    # 可選擇性地過濾工具：
    #tool_filter=["list_datasets", "run_query"]
)

# 建立一個帶有工具的 Agent
root_agent = LlmAgent(
    model="gemini-1.5-flash", # 或您偏好的模型
    name="bigquery_assistant",
    instruction="""
幫助使用者透過可用工具存取其 BigQuery 資料。
    """,
    tools=[registry_tools],
)
```

有關此範例的完整程式碼，請參閱 [api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/) 範例。有關配置選項的資訊，請參閱 [配置](#配置)。有關此工具驗證的資訊，請參閱 [驗證與存取](#驗證與存取)。

## 驗證與存取

搭配 Agent 使用 API 登錄中心需要對 Agent 存取的服務進行驗證。預設情況下，該工具使用 Google Cloud [應用程式預設認證 (Application Default Credentials)](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc) 進行驗證。使用此工具時，請確保您的 Agent 具備以下權限與存取權限：

-   **API 登錄中心存取權限：** `ApiRegistry` 類別使用應用程式預設認證 (`google.auth.default()`) 來驗證對 Google Cloud API 登錄中心的請求，以列出可用的 MCP 伺服器。確保執行 Agent 的環境具備查看 API 登錄中心資源所需的權限，例如 `apiregistry.viewer`。

-   **MCP 伺服器與工具存取：** 由 `get_toolset` 回傳的 `McpToolset` 預設也使用 Google Cloud 應用程式預設認證來驗證對實際 MCP 伺服器端點的呼叫。使用的認證必須具備以下兩者的必要權限：
    1.  存取 MCP 伺服器本身。
    2.  使用工具與之互動的底層服務和資源。

-   **MCP 工具使用者角色：** 透過授予 MCP 工具使用者角色，允許您的 Agent 所使用的帳戶透過 API 登錄中心呼叫 MCP 工具：
    `gcloud projects add-iam-policy-binding {PROJECT_ID} --member={member} --role="roles/mcp.toolUser"`

例如，當使用與 BigQuery 互動的 MCP 伺服器工具時，與認證關聯的帳戶 (如服務帳戶) 必須在您的 Google Cloud 專案中被授予適當的 BigQuery IAM 角色，例如 `bigquery.dataViewer` 或 `bigquery.jobUser`，才能存取資料集並執行查詢。在 BigQuery MCP 伺服器的情況下，需要 `"x-goog-user-project": PROJECT_ID` 標頭才能使用其工具。用於驗證或專案上下文的其他標頭可以透過 `ApiRegistry` 建構函式中的 `header_provider` 引數注入。

## 配置

***APIRegistry*** 物件具有以下配置選項：

-   **`api_registry_project_id`** (str)：API 登錄中心所在的 Google Cloud 專案 ID。

-   **`location`** (str, 選填)：API 登錄中心資源的位置。預設為 `"global"`。

-   **`header_provider`** (Callable, 選填)：一個接收呼叫上下文並回傳要隨請求發送至 MCP 伺服器的額外 HTTP 標頭字典之函式。這通常用於動態驗證或專案特定標頭。

`get_toolset()` 函式具有以下配置選項：

-   **`mcp_server_name`** (str)：要從中載入工具的已註冊 MCP 伺服器的完整名稱，例如：
    `projects/my-project/locations/global/mcpServers/my-server`。

-   **`tool_filter`** (Union[ToolPredicate, List[str]], 選填)：指定要包含在工具集中的工具。
    -   如果是字串列表，則僅包含列表中名稱相符的工具。
    -   如果是 `ToolPredicate` 函式，則會為每個工具呼叫該函式，且僅包含其回傳為 `True` 的工具。
    -   如果為 `None`，則包含來自 MCP 伺服器的所有工具。

-   **`tool_name_prefix`** (str, 選填)：要添加到結果工具集中每個工具名稱的前綴。

## 其他資源

-   [api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/) ADK 程式碼範例
-   [Google Cloud API 登錄中心](https://docs.cloud.google.com/api-registry/docs/overview) 文件

## 下一步

如需如何使用`BigQuery API Registry Agent` 完整實作，請參閱以下範例：

- [BigQuery API Registry Agent 參考範例](../../python/agents/api-registry-agent/)