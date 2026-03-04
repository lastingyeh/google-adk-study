# ADK 的 Apigee API Hub 工具

> 🔔 `更新日期：2026-03-04`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/apigee-api-hub/

[`ADK 支援`: `Python v0.1.0`]

**ApiHubToolset** 讓您只需幾行程式碼，就能將 Apigee API Hub 中任何已編寫文件的 API 轉換為工具。本節將向您展示分步說明，包括為您的 API 設定安全連接的身份驗證。

**先決條件**

1. [安裝 ADK](../../get-started/Installation/python.md)
2. 安裝 [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?db=bigtable-docs#installation_instructions)。
3. 具有已編寫文件（即 OpenAPI 規範）API 的 [Apigee API Hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub) 執行個體
4. 設定您的專案結構並建立所需的檔案

```console
project_root_folder
 |
 `-- my_agent
     |-- .env
     |-- __init__.py
     |-- agent.py
     `__ tool.py
```

## 建立 API Hub 工具集 (Toolset)

注意：本教學包含代理程式 (Agent) 的建立。如果您已經有代理程式，您只需要遵循這些步驟的子集。

1. 獲取您的存取權杖 (access token)，以便 APIHubToolset 可以從 API Hub API 獲取規範。在您的終端機中執行以下命令：

    ```shell
    gcloud auth print-access-token
    # 列印您的存取權杖，例如 'ya29....'
    ```

2. 確保所使用的帳戶具有所需的權限。您可以使用預定義角色 `roles/apihub.viewer` 或分配以下權限：

    1. **apihub.specs.get (必要)**
    2. apihub.apis.get (選用)
    3. apihub.apis.list (選用)
    4. apihub.versions.get (選用)
    5. apihub.versions.list (選用)
    6. apihub.specs.list (選用)

3. 使用 `APIHubToolset` 建立工具。將以下內容新增到 `tools.py`

    如果您的 API 需要身份驗證，您必須為該工具配置身份驗證。以下程式碼範例演示了如何配置 API 金鑰。ADK 支援基於權杖的驗證（API 金鑰、Bearer 權杖）、服務帳戶和 OpenID Connect。我們很快將增加對各種 OAuth2 流程的支援。

    ```python
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
    from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset

    # 為您的 API 提供身份驗證。如果您的 API 不需要身份驗證，則不需要。
    auth_scheme, auth_credential = token_to_scheme_credential(
        "apikey", "query", "apikey", apikey_credential_str
    )

    sample_toolset = APIHubToolset(
        name="apihub-sample-tool",
        description="Sample Tool",
        access_token="...",  # 複製您在步驟 1 中生成的存取權杖
        apihub_resource_name="...", # API Hub 資源名稱
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

    對於正式環境部署，我們建議使用服務帳戶而不是存取權杖。在上面的程式碼片段中，使用 `service_account_json=service_account_cred_json_str` 並提供您的安全性帳戶憑據而不是權杖。

    對於 apihub_resource_name，如果您知道用於 API 的 OpenAPI 規範的特定 ID，請使用 `` `projects/my-project-id/locations/us-west1/apis/my-api-id/versions/version-id/specs/spec-id` ``。如果您希望工具集自動從 API 中拉取第一個可用的規範，請使用 `` `projects/my-project-id/locations/us-west1/apis/my-api-id` ``

4. 建立您的代理程式檔案 `Agent.py` 並將建立的工具新增到您的代理程式定義中：

    ```python
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import sample_toolset

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='enterprise_assistant',
        instruction='協助使用者，善用您可以存取的工具',
        tools=sample_toolset.get_tools(),
    )
    ```

5. 配置您的 `__init__.py` 以公開您的代理程式：

    ```python
    from . import agent
    ```

6. 啟動 Google ADK Web UI 並嘗試您的代理程式：

    ```shell
    # 確保從您的 project_root_folder 執行 `adk web`
    adk web
    ```

   然後前往 [http://localhost:8000](http://localhost:8000) 從 Web UI 嘗試您的代理程式。
