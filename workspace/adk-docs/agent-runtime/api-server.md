# 使用 API 伺服器
🔔 `更新日期：2026-01-22`

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

在部署您的代理之前，您應該測試它以確保其按預期運作。使用 ADK 中的 API 伺服器，透過 REST API 公開您的代理，以便進行程式化測試和整合。

![ADK API 伺服器](https://google.github.io/adk-docs/assets/adk-api-server.png)

## 啟動 API 伺服器

使用以下命令在 ADK API 伺服器中執行您的代理：

<details>
<summary>支援的語言和版本</summary>

> Python

```shell
adk api_server
```

> TypeScript

```shell
npx adk api_server
```

> Go

```shell
go run agent.go web api
```

<details>
<summary>Java</summary>
請務必更新連接埠號碼 (port number)。

> Maven

使用 Maven 編譯並執行 ADK 網頁伺服器：
  ```
  mvn compile exec:java \
    -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
  ```

> Gradle

  使用 Gradle 時，`build.gradle` 或 `build.gradle.kts` 建置檔案應在其 plugins 區段中包含以下 Java 外掛程式：

  ```groovy
  plugins {
      id('java')
      // 其他外掛程式
  }
  ```
  接著，在建置檔案的其他地方，於頂層建立一個新任務：

  ```groovy
  tasks.register('runADKWebServer', JavaExec) {
      dependsOn classes
      classpath = sourceSets.main.runtimeClasspath
      mainClass = 'com.google.adk.web.AdkWebServer'
      args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
  }
  ```

  最後，在命令列執行以下命令：
  ```
  gradle runADKWebServer
  ```
  在 Java 中，開發 UI 和 API 伺服器是綑綁在一起的。
</details >

</details>

此命令將啟動一個本地網頁伺服器，您可以在其中執行 cURL 命令或傳送 API 請求來測試您的代理。預設情況下，伺服器在 `http://localhost:8000` 上執行。

> [!NOTE] 進階用法與除錯
  有關所有可用端點、請求/回應格式以及除錯提示（包括如何使用互動式 API 文件）的完整參考，請參閱下方的 **ADK API 伺服器指南**。

## 本地測試 (Test locally)

本地測試涉及啟動本地網頁伺服器、建立工作階段並向您的代理傳送查詢。首先，請確保您位於正確的工作目錄中。

對於 TypeScript，您應該位於代理專案目錄本身。

```console
parent_folder/
└── my_sample_agent/  <-- 對於 TypeScript，請從此處執行命令
    └── agent.py (或 Agent.java 或 agent.ts)
```

**啟動本地伺服器**

接著，使用上面列出的命令啟動本地伺服器。

輸出應類似於：

<details>
<summary>輸出格式</summary>

> Python

```shell
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

> TypeScript

```shell
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+
```

> Java

```shell
2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
```
</details>

您的伺服器現在正在本地執行。請確保在後續所有命令中使用正確的 **_連接埠號碼 (port number)_**。

**建立新工作階段**

在 API 伺服器仍處於執行狀態下，開啟一個新的終端機視窗或分頁，並使用以下命令為代理建立新工作階段：

```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}'
```

讓我們分析一下發生了什麼：

* `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`：這會為您的代理 `my_sample_agent`（代理資料夾的名稱）建立一個新工作階段，包含使用者識別碼 (`u_123`) 和工作階段識別碼 (`s_123`)。您可以將 `my_sample_agent` 替換為您的代理資料夾名稱。您可以將 `u_123` 替換為特定的使用者識別碼，並將 `s_123` 替換為特定的工作階段識別碼。
* `{"key1": "value1", "key2": 42}`：這是選填的。您可以使用它在建立工作階段時自訂代理預先存在的狀態（字典）。

如果成功建立，這應該會傳回工作階段資訊。輸出應類似於：

```json
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"key1":"value1","key2":42},"events":[],"lastUpdateTime":1743711430.022186}
```

> [!TIP]
  您無法建立多個具有完全相同的使用者識別碼和工作階段識別碼的工作階段。如果您嘗試這樣做，可能會看到類似以下的回應：
  `{"detail":"Session already exists: s_123"}`。要修正此問題，您可以刪除該工作階段（例如 `s_123`），或選擇不同的工作階段識別碼。

**傳送查詢**

有兩種方法可以透過 POST 向代理傳送查詢，即透過 `/run` 或 `/run_sse` 路由。

* `POST http://localhost:8000/run`：將所有事件收集為清單並一次傳回整個清單。適合大多數使用者（如果您不確定，建議使用此方法）。
* `POST http://localhost:8000/run_sse`：以伺服器傳送事件 (Server-Sent-Events) 的形式傳回，這是一個事件物件流。適合想要在事件可用時立即收到通知的使用者。透過 `/run_sse`，您還可以將 `streaming` 設定為 `true` 以啟用權杖級 (token-level) 串流。

**使用 `/run`**

```shell
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"appName": "my_sample_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
  }
}'
```

在 TypeScript 中，目前僅支援 `camelCase` 欄位名稱（例如 `appName`、`userId`、`sessionId` 等）。

如果使用 `/run`，您將同時看到事件的完整輸出清單，應類似於：

```json
[
  {
    "content": {
      "parts": [
        {
          "functionCall": {
            "id": "af-e75e946d-c02a-4aad-931e-49e4ab859838",
            "args": { "city": "new york" },
            "name": "get_weather"
          }
        }
      ],
      "role": "model"
    },
    "invocationId": "e-71353f1e-aea1-4821-aa4b-46874a766853",
    "author": "weather_time_agent",
    "actions": {
      "stateDelta": {},
      "artifactDelta": {},
      "requestedAuthConfigs": {}
    },
    "longRunningToolIds": [],
    "id": "2Btee6zW",
    "timestamp": 1743712220.385936
  },
  {
    "content": {
      "parts": [
        {
          "functionResponse": {
            "id": "af-e75e946d-c02a-4aad-931e-49e4ab859838",
            "name": "get_weather",
            "response": {
              "status": "success",
              "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."
            }
          }
        }
      ],
      "role": "user"
    },
    "invocationId": "e-71353f1e-aea1-4821-aa4b-46874a766853",
    "author": "weather_time_agent",
    "actions": {
      "stateDelta": {},
      "artifactDelta": {},
      "requestedAuthConfigs": {}
    },
    "id": "PmWibL2m",
    "timestamp": 1743712221.895042
  },
  {
    "content": {
      "parts": [
        {
          "text": "OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"
        }
      ],
      "role": "model"
    },
    "invocationId": "e-71353f1e-aea1-4821-aa4b-46874a766853",
    "author": "weather_time_agent",
    "actions": {
      "stateDelta": {},
      "artifactDelta": {},
      "requestedAuthConfigs": {}
    },
    "id": "sYT42eVC",
    "timestamp": 1743712221.899018
  }
]
```

**使用 `/run_sse`**

```shell
curl -X POST http://localhost:8000/run_sse \
-H "Content-Type: application/json" \
-d '{
  "appName": "my_sample_agent",
  "userId": "u_123",
  "sessionId": "s_123",
  "newMessage": {
      "role": "user",
      "parts": [{
      "text": "Hey whats the weather in new york today"
      }]
  },
  "streaming": false
}'
```

您可以將 `streaming` 設定為 `true` 以啟用權杖級串流，這意味著回應將以多個區塊傳回給您，輸出應類似於：

```shell
data: {
  "content": {
    "parts": [
      {
        "functionCall": {
          "id": "af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d",
          "args": { "city": "new york" },
          "name": "get_weather"
        }
      }
    ],
    "role": "model"
  },
  "invocationId": "e-3f6d7765-5287-419e-9991-5fffa1a75565",
  "author": "weather_time_agent",
  "actions": {
    "stateDelta": {},
    "artifactDelta": {},
    "requestedAuthConfigs": {}
  },
  "longRunningToolIds": [],
  "id": "ptcjaZBa",
  "timestamp": 1743712255.313043
}

data: {
  "content": {
    "parts": [
      {
        "functionResponse": {
          "id": "af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d",
          "name": "get_weather",
          "response": {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."
          }
        }
      }
    ],
    "role": "user"
  },
  "invocationId": "e-3f6d7765-5287-419e-9991-5fffa1a75565",
  "author": "weather_time_agent",
  "actions": {
    "stateDelta": {},
    "artifactDelta": {},
    "requestedAuthConfigs": {}
  },
  "id": "5aocxjaq",
  "timestamp": 1743712257.387306
}

data: {
  "content": {
    "parts": [
      {
        "text": "OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"
      }
    ],
    "role": "model"
  },
  "invocationId": "e-3f6d7765-5287-419e-9991-5fffa1a75565",
  "author": "weather_time_agent",
  "actions": {
    "stateDelta": {},
    "artifactDelta": {},
    "requestedAuthConfigs": {}
  },
  "id": "rAnWGSiV",
  "timestamp": 1743712257.391317
}
```
**使用 `/run` 或 `/run_sse` 傳送包含 base64 編碼檔案的查詢**

```shell
curl -X POST http://localhost:8000/run \
-H 'Content-Type: application/json' \
-d '{
   "appName":"my_sample_agent",
   "userId":"u_123",
   "sessionId":"s_123",
   "newMessage":{
      "role":"user",
      "parts":[
         {
            "text":"Describe this image"
         },
         {
            "inlineData":{
               "displayName":"my_image.png",
               "data":"iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAACXBIWXMAAAsTAAALEwEAmpw...",
               "mimeType":"image/png"
            }
         }
      ]
   },
   "streaming":false
}'
```

> [!TIP]
  如果您正在使用 `/run_sse`，您應該會在每個事件可用時立即看到它。

## 整合

ADK 使用 [回呼 (Callbacks)](../callbacks/index.md) 與第三方觀測工具整合。這些整合會捕捉代理呼叫和互動的詳細追蹤，這對於理解行為、除錯問題和評估效能至關重要。

* [Comet Opik](https://github.com/comet-ml/opik) 是一個開源 LLM 觀測與評估平台，[原生支援 ADK](https://www.comet.com/docs/opik/tracing/integrations/adk)。

## 部署您的代理

既然您已經驗證了代理的本地運行，您就可以開始部署代理了！以下是您可以部署代理的一些方式：

* 部署到 [Agent Engine](../deployment/agent-engine/index.md)，這是在 Google Cloud 上的 Vertex AI 受管理服務中部署 ADK 代理的一種簡單方式。
* 部署到 [Cloud Run](../deployment/cloud-run.md)，並在 Google Cloud 上使用無伺服器架構完全控制如何擴充和管理您的代理。

## 互動式 API 文件

API 伺服器會使用 Swagger UI 自動產生互動式 API 文件。這是從瀏覽器直接探索端點、了解請求格式以及測試代理的寶貴工具。

要存取互動式文件，請啟動 API 伺服器並在網頁瀏覽器中導航至 [http://localhost:8000/docs](http://localhost:8000/docs)。

您將看到所有可用 API 端點的完整、互動式清單，您可以展開該清單以查看有關參數、請求主體和回應架構的詳細資訊。您甚至可以點擊 "Try it out" 向執行中的代理傳送即時請求。

## API 端點

以下章節詳細介紹了與代理互動的主要端點。

> [!NOTE] JSON 命名規範
> - **請求和回應主體** 都將對欄位名稱使用 `camelCase`（例如 `"appName"`）。

### 公用程式端點

#### 列出可用的代理

傳回伺服器發現的所有代理應用程式清單。

*   **方法：** `GET`
*   **路徑：** `/list-apps`

**範例請求**
```shell
curl -X GET http://localhost:8000/list-apps
```

**範例回應**
```json
["my_sample_agent", "another_agent"]
```

---

### 工作階段管理

工作階段儲存了特定使用者與代理互動的狀態和事件歷史記錄。

#### 更新工作階段

更新現有工作階段。

*   **方法：** `PATCH`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**請求主體**
```json
{
  "stateDelta": {
    "key1": "value1",
    "key2": 42
  }
}
```

**範例請求**
```shell
curl -X PATCH http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc \
  -H "Content-Type: application/json" \
  -d '{"stateDelta":{"visit_count": 5}}'
```

**範例回應**
```json
{
  "id": "s_abc",
  "appName": "my_sample_agent",
  "userId": "u_123",
  "state": { "visit_count": 5 },
  "events": [],
  "lastUpdateTime": 1743711430.022186
}
```

#### 取得工作階段

檢索特定工作階段的詳細資訊，包括其目前狀態和所有相關事件。

*   **方法：** `GET`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**範例請求**
```shell
curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**範例回應**
```json
{
  "id": "s_abc",
  "appName": "my_sample_agent",
  "userId": "u_123",
  "state": { "visit_count": 5 },
  "events": [...],
  "lastUpdateTime": 1743711430.022186
}
```

#### 刪除工作階段

刪除工作階段及其所有相關資料。

*   **方法：** `DELETE`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**範例請求**
```shell
curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**範例回應**
成功刪除會傳回一個帶有 `204 No Content` 狀態碼的空回應。

---

### 代理執行

這些端點用於向代理傳送新訊息並獲取回應。

#### 執行代理（單次回應）

執行代理並在執行完成後在單個 JSON 陣列中傳回所有產生的事件。

*   **方法：** `POST`
*   **路徑：** `/run`

**請求主體**
```json
{
  "appName": "my_sample_agent",
  "userId": "u_123",
  "sessionId": "s_abc",
  "newMessage": {
    "role": "user",
    "parts": [
      { "text": "What is the capital of France?" }
    ]
  }
}
```

在 TypeScript 中，目前僅支援 `camelCase` 欄位名稱（例如 `appName`、`userId`、`sessionId` 等）。

**範例請求**
```shell
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "my_sample_agent",
    "userId": "u_123",
    "sessionId": "s_abc",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the capital of France?"}]
    }
  }'
```

#### 執行代理（串流）

執行代理並使用 [伺服器傳送事件 (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) 在事件產生時將其串流回用戶端。

*   **方法：** `POST`
*   **路徑：** `/run_sse`

**請求主體**
請求主體與 `/run` 相同，並帶有一個額外的選填 `streaming` 旗標。
```json
{
  "appName": "my_sample_agent",
  "userId": "u_123",
  "sessionId": "s_abc",
  "newMessage": {
    "role": "user",
    "parts": [
      { "text": "What is the weather in New York?" }
    ]
  },
  "streaming": true
}
```
- `streaming`: （選填）設定為 `true` 以啟用模型回應的權杖級串流。預設為 `false`。

**範例請求**
```shell
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "my_sample_agent",
    "userId": "u_123",
    "sessionId": "s_abc",
    "newMessage": {
      "role": "user",
      "parts": [{"text": "What is the weather in New York?"}]
    },
    "streaming": false
  }'
```

## 整合說明

下表彙整了 ADK API 伺服器提供的完整端點說明：

| 功能類別 | 端點路徑 | 方法 | 說明 |
| :--- | :--- | :--- | :--- |
| 公用程式 | `/list-apps` | `GET` | 列出伺服器上所有可用的代理應用程式 |
| 工作階段管理 | `/apps/{app_name}/users/{user_id}/sessions/{session_id}` | `POST` | 建立新的代理工作階段，可初始化狀態 |
| 工作階段管理 | `/apps/{app_name}/users/{user_id}/sessions/{session_id}` | `GET` | 取得特定工作階段的詳細資訊與事件歷史 |
| 工作階段管理 | `/apps/{app_name}/users/{user_id}/sessions/{session_id}` | `PATCH` | 更新現有工作階段的狀態 (`stateDelta`) |
| 工作階段管理 | `/apps/{app_name}/users/{user_id}/sessions/{session_id}` | `DELETE` | 刪除工作階段及其相關資料 |
| 代理執行 | `/run` | `POST` | 執行代理並以單一 JSON 陣列傳回所有事件 |
| 代理執行 | `/run_sse` | `POST` | 執行代理並透過 SSE 串流傳回事件，支援權杖級串流 |
