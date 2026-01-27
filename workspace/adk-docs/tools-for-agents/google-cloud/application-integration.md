# ADK 的應用程式整合工具 (Application Integration Tools)

> 🔔 `更新日期：2026-01-25`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/application-integration/

[`ADK 支援`: `Python v0.1.0` | `Java v0.3.0`]

透過 **ApplicationIntegrationToolset**，您可以無縫地讓您的代理 (Agents) 安全且受控地存取企業應用程式。這得益於 Integration Connectors 提供超過 100 種針對 Salesforce、ServiceNow、JIRA、SAP 等系統的預建連接器。

它同時支援地端 (on-premise) 與軟體即服務 (SaaS) 應用程式。此外，您可以將現有的應用程式整合程序自動化轉化為代理工作流，方法是將應用程式整合工作流作為工具提供給您的 ADK 代理。

應用程式整合中的同盟搜尋 (Federated search) 功能讓您可以使用 ADK 代理同時查詢多個企業應用程式與資料來源。

## 影片說明：在應用程式整合中實作 ADK 聯合搜尋

**影片連結**：[See how ADK Federated Search in Application Integration works in this video walkthrough](https://www.youtube.com/watch?v=JdlWOQe5RgU)

### 影片概述

這份影片重點介紹了如何利用 **ADK (Agent Development Kit)** 與 **Google Cloud Application Integration** 實作「**聯合搜尋 (Federated Search)**」。這種技術讓 AI 代理程式能夠在不搬移資料、不建立索引的情況下，直接跨多個第三方平台進行即時檢索。

#### 1. 什麼是聯合搜尋 (Federated Search)？
*   **非索引式檢索**：與傳統的 RAG（檢索增強生成）或建立索引的方式不同，聯合搜尋**不會將資料複製到特定資料庫中**。
*   **直接連接**：AI 代理程式利用連接器（Connectors）直接連接到第三方平台（如 Salesforce、BigQuery）進行即時查詢。
*   **交易式搜尋**：這是一種直接由代理程式執行的「交易式」搜尋，能確保獲取最即時的權限與資料內容。

#### 2. 實作架構與資料來源
*   **核心工具**：使用 **ADK** 建立代理程式，並透過 **App Integration 連接器** 對接不同的資料源。
*   **多源整合範例**：
    *   **Salesforce**：包含客戶帳戶、產業別與營收資訊，但**沒有**客戶經理資訊。
    *   **BigQuery**：包含相同的帳戶資訊，且額外記錄了**客戶經理 (Account Manager)** 資訊。

#### 3. 身分驗證與安全性
*   **終端使用者驗證**：在連接 Salesforce 等敏感資料源時，代理程式會請求**使用者授權 (Consent)**，以確保符合權限管理規範。
*   **共用資料來源**：如 BigQuery 等內部共用資料則可設定為無需額外驗證即可搜尋。

#### 4. 強大的資料彙整與推理能力
*   **跨來源關聯 (Join)**：代理程式能自動識別資料分布，並將來自 Salesforce（營收）與 BigQuery（客戶經理）的資訊**合併成單一表格**呈現。
*   **進階問題處理**：
    *   當詢問「特定經理名下的總營收」時，代理程式會自動從兩邊獲取數據並進行加總計算。
    *   對於後續追蹤問題（如「這群人位於何處？」），即使資訊分散在不同系統，代理程式也能維持上下文的一致性並提供**統一的搜尋體驗**。



## 前提條件

### 1. 安裝 ADK

按照 [安裝指南](../../get-started/Installation/python.md) 中的步驟安裝代理開發套件 (Agent Development Kit)。

### 2. 安裝 CLI

安裝 [Google Cloud CLI](https://cloud.google.com/sdk/docs/install#installation_instructions)。
若要使用預設憑證運行該工具，請執行以下命令：

```shell
gcloud config set project <project-id>
gcloud auth application-default login
gcloud auth application-default set-quota-project <project-id>
```

將 `<project-id>` 替換為您的 Google Cloud 專案的唯一 ID。

### 3. 配置應用程式整合工作流並發布連接工具 (Connection Tool)

使用您想要在代理中使用的現有 [應用程式整合 (Application Integration)](https://cloud.google.com/application-integration/docs/overview) 工作流或 [整合連接器 (Integrations Connector)](https://cloud.google.com/integration-connectors/docs/overview) 連接。您也可以建立新的 [應用程式整合工作流](https://cloud.google.com/application-integration/docs/setup-application-integration) 或 [連接](https://cloud.google.com/integration-connectors/docs/connectors/neo4j/configure#configure-the-connector)。

從模板庫中導入並發布 [連接工具 (Connection Tool)](https://console.cloud.google.com/integrations/templates/connection-tool/locations/global)。

**注意**：若要使用來自 Integration Connectors 的連接器，您需要在與您的連接相同的區域中配置應用程式整合。

### 4. 建立專案結構

<details>
<summary>範例說明</summary>

> Python

```console
project_root_folder
├── .env
└── my_agent
    ├── __init__.py
    ├── agent.py
    └── tools.py
```

運行代理時，請確保從 `project_root_folder` 執行 `adk web`。

> Java

```console
project_root_folder
└── my_agent
    ├── agent.java
    └── pom.xml
```

運行代理時，請確保從 `project_root_folder` 執行命令。

</details>

### 5. 設定角色與權限

若要獲取設定 **ApplicationIntegrationToolset** 所需的權限，您必須在專案上擁有以下 IAM 角色（這適用於 Integration Connectors 和 Application Integration 工作流）：

    - roles/integrations.integrationEditor
    - roles/connectors.invoker
    - roles/secretmanager.secretAccessor

**注意：** 當使用 Agent Engine (AE) 進行部署時，請勿使用 `roles/integrations.integrationInvoker`，因為這可能導致 403 錯誤。請改用 `roles/integrations.integrationEditor`。

## 使用整合連接器 (Integration Connectors)

使用 [整合連接器 (Integration Connectors)](https://cloud.google.com/integration-connectors/docs/overview) 將您的代理連接到企業應用程式。

### 開始之前

**注意：** 當您在特定區域中配置應用程式整合時，通常會自動建立 *ExecuteConnection* 整合。如果 [整合清單](https://console.cloud.google.com/integrations/list) 中不存在 *ExecuteConnection*，您必須按照以下步驟建立它：

1. 若要使用來自 Integration Connectors 的連接器，點擊 **快速設定 (QUICK SETUP)** 並在與您的連接相同的區域中 [配置](https://console.cloud.google.com/integrations) 應用程式整合。

   ![Google Cloud 工具](https://google.github.io/adk-docs/assets/application-integration-overview.png)

2. 前往模板庫中的 [連接工具 (Connection Tool)](https://console.cloud.google.com/integrations/templates/connection-tool/locations/us-central1) 模板，然後點擊 **使用模板 (USE TEMPLATE)**。

    ![Google Cloud 工具](https://google.github.io/adk-docs/assets/use-connection-tool-template.png)

3. 輸入整合名稱為 *ExecuteConnection*（必須且只能使用此確切的整合名稱）。然後，選擇與您的連接區域相符的區域，並點擊 **建立 (CREATE)**。

4. 點擊 **發布 (PUBLISH)** 以在 <i>應用程式整合</i> 編輯器中發布該整合。

    ![Google Cloud 工具](https://google.github.io/adk-docs/assets/publish-integration.png)

### 建立應用程式整合工具集 (Application Integration Toolset)

若要為整合連接器建立應用程式整合工具集，請按照以下步驟操作：

1.  在 `tools.py` 檔案中建立一個使用 `ApplicationIntegrationToolset` 的工具：

    ```py
    from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 替換為連接的 GCP 專案
        location="us-central1", # TODO: 替換為連接的區域
        connection="test-connection", # TODO: 替換為連接名稱
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []}, # 操作的空清單表示支援實體上的所有操作。
        actions=["action1"], # TODO: 替換為操作
        service_account_json='{...}', # 選填。服務帳戶密鑰的字串化 JSON
        tool_name_prefix="tool_prefix2",
        tool_instructions="..."
    )
    ```

    **注意：**

    * 您可以透過產生 [服務帳戶密鑰 (Service Account Key)](https://cloud.google.com/iam/docs/keys-create-delete#creating)，並為該服務帳戶提供正確的 [應用程式整合與整合連接器 IAM 角色](#前提條件)，來提供用於替代預設憑證的服務帳戶。
    * 若要尋找連接支援的實體與操作清單，請使用連接器 API：[listActions](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listActions) 或 [listEntityTypes](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listEntityTypes)。

    `ApplicationIntegrationToolset` 針對整合連接器支援用於 **動態 OAuth2 驗證** 的 `auth_scheme` 與 `auth_credential`。若要使用它，請在 `tools.py` 檔案中建立一個如下所示的工具：

    ```py
    from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
    from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme
    from google.adk.auth import AuthCredential
    from google.adk.auth import AuthCredentialTypes
    from google.adk.auth import OAuth2Auth

    oauth2_data_google_cloud = {
      "type": "oauth2",
      "flows": {
          "authorizationCode": {
              "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
              "tokenUrl": "https://oauth2.googleapis.com/token",
              "scopes": {
                  "https://www.googleapis.com/auth/cloud-platform": (
                      "查看並管理您在 Google Cloud Platform 服務上的資料"
                  ),
                  "https://www.googleapis.com/auth/calendar.readonly": "查看您的日曆"
              },
          }
      },
    }

    oauth_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)

    auth_credential = AuthCredential(
      auth_type=AuthCredentialTypes.OAUTH2,
      oauth2=OAuth2Auth(
          client_id="...", # TODO: 替換為 client_id
          client_secret="...", # TODO: 替換為 client_secret
      ),
    )

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 替換為連接的 GCP 專案
        location="us-central1", # TODO: 替換為連接的區域
        connection="test-connection", # TODO: 替換為連接名稱
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []}, # 操作的空清單表示支援實體上的所有操作。
        actions=["GET_calendars/%7BcalendarId%7D/events"], # TODO: 替換為操作。此操作用於列出事件
        service_account_json='{...}', # 選填。服務帳戶密鑰的字串化 JSON
        tool_name_prefix="tool_prefix2",
        tool_instructions="...",
        auth_scheme=oauth_scheme,
        auth_credential=auth_credential
    )
    ```

2. 更新 `agent.py` 檔案並將工具新增到您的代理：

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import connector_tool

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='connector_agent',
        instruction="幫助使用者，利用您可以存取的工具",
        tools=[connector_tool],
    )
    ```

3. 設定 `__init__.py` 以公開您的代理：

    ```py
    from . import agent
    ```

4. 啟動 Google ADK Web UI 並使用您的代理：

    ```shell
    # 確保從您的 project_root_folder 執行 `adk web`
    adk web
    ```

完成上述步驟後，前往 [http://localhost:8000](http://localhost:8000)，並選擇 `my_agent` 代理（與代理資料夾名稱相同）。

## 使用應用程式整合工作流 (Application Integration Workflows)

將現有的 [應用程式整合 (Application Integration)](https://cloud.google.com/application-integration/docs/overview) 工作流作為代理工具使用，或建立一個新的工作流。

### 1. 建立工具

<details>
<summary>範例說明</summary>

> Python

若要在 `tools.py` 檔案中建立一個使用 `ApplicationIntegrationToolset` 的工具，請使用以下程式碼：

```py
    integration_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 替換為連接的 GCP 專案
        location="us-central1", # TODO: 替換為連接的區域
        integration="test-integration", # TODO: 替換為整合名稱
        triggers=["api_trigger/test_trigger"], # TODO: 替換為觸發器 ID。空清單表示考慮整合中的所有 API 觸發器。
        service_account_json='{...}', # 選填。服務帳戶密鑰的字串化 JSON
        tool_name_prefix="tool_prefix1",
        tool_instructions="..."
    )
```

**注意：** 您可以提供用於替代預設憑證的服務帳戶。若要執行此操作，請產生 [服務帳戶密鑰 (Service Account Key)](https://cloud.google.com/iam/docs/keys-create-delete#creating)，並為該服務帳戶提供正確的 [應用程式整合與整合連接器 IAM 角色](#前提條件)。有關 IAM 角色的更多詳細資訊，請參閱 [前提條件](#前提條件) 章節。

> Java

若要在 `tools.java` 檔案中建立一個使用 `ApplicationIntegrationToolset` 的工具，請使用以下程式碼：

```java
    import com.google.adk.tools.applicationintegrationtoolset.ApplicationIntegrationToolset;
    import com.google.common.collect.ImmutableList;
    import com.google.common.collect.ImmutableMap;

    public class Tools {
        private static ApplicationIntegrationToolset integrationTool;
        private static ApplicationIntegrationToolset connectionsTool;

        static {
            integrationTool = new ApplicationIntegrationToolset(
                    "test-project",
                    "us-central1",
                    "test-integration",
                    ImmutableList.of("api_trigger/test-api"),
                    null,
                    null,
                    null,
                    "{...}",
                    "tool_prefix1",
                    "...");

            connectionsTool = new ApplicationIntegrationToolset(
                    "test-project",
                    "us-central1",
                    null,
                    null,
                    "test-connection",
                    ImmutableMap.of("Issue", ImmutableList.of("GET")),
                    ImmutableList.of("ExecuteCustomQuery"),
                    "{...}",
                    "tool_prefix",
                    "...");
        }
    }
```

**注意：** 您可以提供用於替代預設憑證的服務帳戶。若要執行此操作，請產生 [服務帳戶密鑰 (Service Account Key)](https://cloud.google.com/iam/docs/keys-create-delete#creating)，並為該服務帳戶提供正確的 [應用程式整合與整合連接器 IAM 角色](#前提條件)。有關 IAM 角色的更多詳細資訊，請參閱 [前提條件](#前提條件) 章節。

</details>

### 2. 將工具新增到您的代理

<details>
<summary>範例說明</summary>

> Python

若要更新 `agent.py` 檔案並將工具新增到您的代理，請使用以下程式碼：

```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import integration_tool, connector_tool

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='integration_agent',
        instruction="幫助使用者，利用您可以存取的工具",
        tools=[integration_tool],
    )
```

> Java

若要更新 `agent.java` 檔案並將工具新增到您的代理，請使用以下程式碼：

```java
    import com.google.adk.agent.LlmAgent;
    import com.google.adk.tools.BaseTool;
    import com.google.common.collect.ImmutableList;

      public class MyAgent {
          public static void main(String[] args) {
              // 假設 Tools 類別的定義如前述步驟
              ImmutableList<BaseTool> tools = ImmutableList.<BaseTool>builder()
                      .add(Tools.integrationTool)
                      .add(Tools.connectionsTool)
                      .build();

              // 最後，使用自動產生的工具建立您的代理。
              LlmAgent rootAgent = LlmAgent.builder()
                      .name("science-teacher")
                      .description("科學老師代理")
                      .model("gemini-2.0-flash")
                      .instruction(
                              "幫助使用者，利用您可以存取的工具。"
                      )
                      .tools(tools)
                      .build();

              // 您現在可以使用 rootAgent 與 LLM 進行互動
              // 例如，您可以開始與代理對話。
          }
      }
```

</details>

**注意：** 若要尋找連接支援的實體與操作清單，請使用這些連接器 API：`listActions`、`listEntityTypes`。

### 3. 公開您的代理

<details>
<summary>範例說明</summary>

> Python

若要設定 `__init__.py` 以公開您的代理，請使用以下程式碼：

```py
    from . import agent
```

</details>

### 4. 使用您的代理

<details>
<summary>範例說明</summary>

> Python

若要啟動 Google ADK Web UI 並使用您的代理，請使用以下命令：

```shell
    # 確保從您的 project_root_folder 執行 `adk web`
    adk web
```
完成上述步驟後，前往 [http://localhost:8000](http://localhost:8000)，並選擇 `my_agent` 代理（與代理資料夾名稱相同）。

> Java

若要啟動 Google ADK Web UI 並使用您的代理，請使用以下命令：

```bash
    mvn install

    mvn exec:java \
        -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
        -Dexec.args="--adk.agents.source-dir=src/main/java" \
        -Dexec.classpathScope="compile"
```

完成上述步驟後，前往 [http://localhost:8000](http://localhost:8000)，並選擇 `my_agent` 代理（與代理資料夾名稱相同）。

</details>