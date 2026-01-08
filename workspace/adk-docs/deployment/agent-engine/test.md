# 在 Agent Engine 中測試已部署的代理

這些說明解釋了如何測試部署到 [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) 執行環境的 ADK 代理。在使用這些說明之前，您需要先使用[可用方法](./index.md)之一，完成將代理部署到 Agent Engine 執行環境的操作。本指南將向您展示如何透過 Google Cloud 控制台查看、互動和測試您部署的代理，並使用 REST API 呼叫或適用於 Python 的 Vertex AI SDK 與代理進行互動。

## 測試模式整合說明

以下表格整合了本文件涵蓋的所有測試模式，協助您根據需求選擇適合的測試方法：

| 測試模式 | 適用場景 | 所需工具/環境 | 認證方式 | 主要功能 | 相關章節 |
|---------|---------|--------------|---------|---------|---------|
| **Cloud 控制台查看** | 快速檢視已部署代理清單與基本資訊 | Google Cloud 控制台 | Google Cloud 帳號登入 | 查看代理清單、獲取 API URL | [在 Cloud 控制台中查看](#在-cloud-控制台中查看已部署的代理) |
| **REST API - 連線檢查** | 驗證代理部署狀態與存取權限 | `curl`、終端機 | `gcloud auth` / API Key | 發送 GET 請求列出 reasoningEngines | [檢查與代理的連線](#檢查與代理的連線) |
| **REST API - 互動測試** | 簡單的命令列測試與除錯 | `curl`、終端機 | `gcloud auth` / API Key | 建立工作階段、發送查詢、接收回應 | [發送代理請求](#發送代理請求) |
| **Python SDK - 基本測試** | 可重複的自動化測試與複雜互動 | Python、Vertex AI SDK | 專案認證 | 建立遠端工作階段、串流查詢 | [使用 Python 進行測試](#使用-python-進行測試) |
| **Python SDK - 多模態** | 測試包含圖片的多模態查詢 | Python、Vertex AI SDK、GCS | 專案認證 | 發送文字+圖片查詢 | [發送多模態查詢](#發送多模態查詢) |
| **資源清理** | 測試完成後刪除雲端資源 | Python SDK / Cloud 控制台 | 專案認證 | 刪除代理及相關資源 | [清理部署](#清理部署) |

### 測試模式選擇建議

- **快速驗證**：使用 Cloud 控制台查看 + REST API 連線檢查
- **功能測試**：使用 REST API 互動測試或 Python SDK 基本測試
- **整合測試**：使用 Python SDK 編寫自動化測試腳本
- **多模態功能**：使用 Python SDK 多模態測試
- **成本控制**：測試完成後務必執行資源清理

### 認證模式比較

| 認證方式 | 使用場景 | 設定方式 |
|---------|---------|---------|
| **gcloud auth** | Google Cloud 專案環境 | `gcloud auth print-access-token` |
| **API Key** | Vertex AI 快速模式 | 在請求 header 中使用 `x-goog-api-key` |
| **專案認證** | Python SDK | 透過 ADK 專案設定或環境變數 |

## 在 Cloud 控制台中查看已部署的代理

要在 Cloud 控制台中查看您部署的代理：

- 導覽至 Google Cloud 控制台中的 Agent Engine 頁面：
  [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

此頁面列出了您當前選定的 Google Cloud 專案中所有已部署的代理。如果您沒有看到列出的代理，請確保您已在 Google Cloud 控制台中選取了目標專案。有關選取現有 Google Cloud 專案的更多資訊，請參閱[建立和管理專案](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)。

## 尋找 Google Cloud 專案資訊

您需要專案的位址和資源識別資訊（`PROJECT_ID`、`LOCATION_ID`、`RESOURCE_ID`）才能測試您的部署。您可以使用 Cloud 控制台或 `gcloud` 命令列工具來尋找這些資訊。

> [!NOTE] Vertex AI 快速模式 (express mode) API 金鑰
    如果您使用的是 Vertex AI 快速模式，您可以跳過此步驟並使用您的 API 金鑰。

要使用 Google Cloud 控制台尋找您的專案資訊：

1.  在 Google Cloud 控制台中，導覽至 Agent Engine 頁面：
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

2.  在頁面頂部，選取 **API URL**，然後複製部署代理的 **查詢 URL (Query URL)** 字串，格式應如下所示：

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

要使用 `gcloud` 命令列工具尋找您的專案資訊：

1.  在您的開發環境中，確保您已通過 Google Cloud 驗證，並執行以下命令來列出您的專案：

    ```shell
    # 列出所有 Google Cloud 專案
    gcloud projects list
    ```

2.  使用部署時使用的專案 ID，執行此命令以獲取更多詳細資訊：

    ```shell
    # 搜尋 ReasoningEngine 資源以獲取部署詳細資訊
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

## 使用 REST 呼叫進行測試

與部署在 Agent Engine 中的代理進行互動的一種簡單方法是使用 `curl` 工具進行 REST 呼叫。本節介紹如何檢查與代理的連線，以及如何測試部署代理對請求的處理。

### 檢查與代理的連線

您可以使用 Cloud 控制台 Agent Engine 區塊中提供的 **查詢 URL (Query URL)** 檢查與執行中代理的連線。此檢查不會執行已部署的代理，而是傳回有關代理的資訊。

要發送 REST 呼叫並從部署的代理獲取回應：

- 在開發環境的終端機視窗中，建立一個請求並執行它：

  > Google Cloud 專案

    ```shell
    # 發送 GET 請求以列出 reasoningEngines，驗證連線與權限
    curl -X GET \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        "https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines"
    ```

  > Vertex AI 快速模式

    ```shell
    # 使用 API 金鑰在快速模式下發送 GET 請求
    curl -X GET \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        "https://aiplatform.googleapis.com/v1/reasoningEngines"
    ```

如果部署成功，此請求將回應有效請求清單和預期的資料格式。

> [!TIP] 移除連線 URL 的 `:query` 參數
    如果您使用 Cloud 控制台 Agent Engine 區塊中提供的 **查詢 URL (Query URL)**，請確保從位址結尾移除 `:query` 參數。

> [!TIP] 代理連線的存取權限
    此連線測試要求呼叫使用者具有已部署代理的有效存取權杖 (access token)。從其他環境進行測試時，請確保呼叫使用者具有連線到您 Google Cloud 專案中代理的權限。

### 發送代理請求

從代理專案獲取回應時，您必須先建立一個工作階段 (session)，獲取工作階段 ID (Session ID)，然後使用該工作階段 ID 發送請求。以下說明描述了此過程。

要透過 REST 測試與已部署代理的互動：

1.  在開發環境的終端機視窗中，使用此範本建立請求來建立工作階段：

    > Google Cloud 專案

    ```shell
    # 呼叫 async_create_session 方法來建立新的工作階段
    curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query \
        -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
    ```

    > Vertex AI 快速模式

    ```shell
    # 在快速模式下使用 API 金鑰建立工作階段
    curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
        -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
    ```

1.  在上述命令的回應中，從 **id** 欄位提取建立的 **工作階段 ID (Session ID)**：

    ```json
    {
      "output": {
        "userId": "u_123",
        "lastUpdateTime": 1757690426.337745,
        "state": {},
        "id": "4857885913439920384", // 工作階段 ID (Session ID)
        "appName": "9888888855577777776",
        "events": []
      }
    }
    ```

2.  在開發環境的終端機視窗中，使用此範本和上一步中建立的工作階段 ID 建立請求，向您的代理發送訊息：

    > Google Cloud 專案

    ```
    # 使用工作階段 ID 向代理發送串流查詢請求
    curl \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "嘿，今天紐約的天氣如何？",
        }
    }'
    ```

    > Vertex AI 快速模式

    ```shell
    # 在快速模式下向代理發送串流查詢請求
    curl \
    -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
    -H "Content-Type: application/json" \
    https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
    "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "嘿，今天紐約的天氣如何？",
        }
    }'
    ```

此請求應會以 JSON 格式從您部署的代理程式碼生成回應。有關使用 REST 呼叫與 Agent Engine 中部署的 ADK 代理進行互動的更多資訊，請參閱 Agent Engine 說明文件中的[管理已部署的代理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)和[使用 Agent Development Kit 代理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)。

## 使用 Python 進行測試

您可以使用 Python 程式碼對部署在 Agent Engine 中的代理進行更複雜且可重複的測試。這些說明描述了如何與部署的代理建立工作階段，然後將請求發送給代理進行處理。

### 建立遠端工作階段

使用 `remote_app` 物件建立與已部署的遠端代理的連線：

```python
# 如果您是在新腳本中或使用 ADK CLI 進行部署，可以像這樣進行連線：
# remote_app = agent_engines.get("您的代理資源名稱")

# 建立一個遠端工作階段
remote_session = await remote_app.async_create_session(user_id="u_456")
# 打印工作階段資訊
print(remote_session)
```

`create_session`（遠端）的預期輸出：

```json
{
    'events': [],
    'user_id': 'u_456',
    'state': {},
    'id': '7543472750996750336',
    'app_name': '7917477678498709504',
    'last_update_time': 1743683353.030133
}
```

`id` 值是工作階段 ID，而 `app_name` 是 Agent Engine 上部署代理的資源 ID。

#### 向您的遠端代理發送查詢

```python
# 使用工作階段 ID 向遠端代理發送串流查詢
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="紐約的天氣如何",
):
    # 打印每個串流事件
    print(event)
```

`async_stream_query`（遠端）的預期輸出：

```jsonl
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}

{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': '紐約天氣晴朗，氣溫為攝氏 25 度（華氏 41 度）。'}}}], 'role': 'user'}

{'parts': [{'text': '紐約天氣晴朗，氣溫為攝氏 25 度（華氏 41 度）。'}], 'role': 'model'}
```

有關與部署在 Agent Engine 中的 ADK 代理進行互動的更多資訊，請參閱 Agent Engine 說明文件中的[管理已部署的代理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)和[使用 Agent Development Kit 代理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)。

### 發送多模態查詢

要向您的代理發送多模態查詢（例如，包含圖片），您可以使用 `types.Part` 物件列表來構建 `async_stream_query` 的 `message` 參數。每個部分可以是文字或圖片。

要包含圖片，您可以使用 `types.Part.from_uri`，並為圖片提供 Google Cloud Storage (GCS) URI。

```python
from google.genai import types

# 從 GCS URI 建立圖片部分
image_part = types.Part.from_uri(
    file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
    mime_type="image/jpeg",
)
# 建立文字部分
text_part = types.Part.from_text(
    text="這張圖片裡有什麼？",
)

# 發送包含文字和圖片的多模態查詢
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=[text_part, image_part],
):
    # 打印回應事件
    print(event)
```

> [!NOTE]
    雖然與模型的底層通訊可能涉及圖片的 Base64 編碼，但將圖片資料發送到部署在 Agent Engine 上的代理的推薦且受支援的方法是提供 GCS URI。

## 清理部署

如果您已執行部署作為測試，建議在完成後清理雲端資源。您可以刪除部署的 Agent Engine 執行個體，以避免 Google Cloud 帳戶產生任何非預期的費用。

```python
# 強制刪除遠端應用程式及其關聯資源（如工作階段）
remote_app.delete(force=True)
```

`force=True` 參數還會刪除從部署代理生成的任何子資源（例如工作階段）。您也可以透過 Google Cloud 上的 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) 刪除已部署的代理。
