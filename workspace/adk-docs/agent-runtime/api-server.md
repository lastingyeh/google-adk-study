# 使用 API 伺服器

🔔 `更新日期：2026 年 1 月 9 日`

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

在部署 Agent 之前，您應該對其進行測試，以確保其按預期運作。在開發環境中測試 Agent 最簡單的方法是使用 ADK API 伺服器。

<details>
<summary>範例說明</summary>

> Python

```py
# 啟動 Python 版 ADK API 伺服器
adk api_server
```

> TypeScript

```shell
# 啟動 TypeScript 版 ADK API 伺服器
npx adk api_server
```

> Go

```go
// 啟動 Go 版 ADK API 伺服器
go run agent.go web api
```

> Java

請確保更新連接埠號。

  - Maven
    ```console
    # 使用 Maven 編譯並執行 ADK 網頁伺服器
    mvn compile exec:java \
    -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
    ```
  - Gradle

    使用 Gradle 時，`build.gradle` 或 `build.gradle.kts` 建置檔案的 plugins 部分應包含以下 Java 外掛：

    ```groovy
    plugins {
        id('java')
        // 其他外掛
    }
    ```

    接著，在建置檔案的其他地方（頂層），建立一個新任務：

    ```groovy
    // 註冊執行 ADK 網頁伺服器的任務
    tasks.register('runADKWebServer', JavaExec) {
        dependsOn classes
        classpath = sourceSets.main.runtimeClasspath
        mainClass = 'com.google.adk.web.AdkWebServer'
        args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
    }
    ```

    最後，在命令列執行以下指令：

    ```console
    # 執行自定義的 Gradle 任務來啟動伺服器
    gradle runADKWebServer
    ```

在 Java 中，開發 UI（Dev UI）和 API 伺服器是綑綁在一起的。

</details>

此指令將啟動一個本地網頁伺服器，您可以在其中執行 cURL 指令或發送 API 請求來測試您的 Agent。

> [!TIP] 進階用法與除錯
    有關所有可用端點、請求/回應格式以及除錯提示（包括如何使用互動式 API 文件）的完整參考，請參閱下方的 **ADK API 伺服器指南**。

## 本地測試

本地測試涉及啟動本地網頁伺服器、建立工作階段（session）以及向您的 Agent 發送查詢。首先，請確保您位於正確的工作目錄中。

對於 TypeScript，您應該位於 Agent 專案目錄本身。

```console
parent_folder/
└── my_sample_agent/  <-- 對於 TypeScript，請從此處執行指令
    └── agent.py (或 Agent.java 或 agent.ts)
```

**啟動本地伺服器**

接下來，使用上方列出的指令啟動本地伺服器。

輸出應如下所示：

<details>
<summary>範例說明</summary>

> Python

```shell
# 伺服器啟動訊息範例
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

> TypeScript

```shell
# 伺服器啟動成功橫幅
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+
```

> Java

```shell
# Spring Boot 啟動記錄範例
2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
```

</details>

您的伺服器現在正在本地運行。請確保在所有後續指令中使用正確的 **_連接埠號_**。

**建立新工作階段**

在 API 伺服器仍運行的情況下，開啟一個新的終端機視窗或分頁，並使用以下指令為 Agent 建立一個新工作階段：

```shell
# 使用 cURL 發送 POST 請求以建立工作階段
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}'
```

讓我們分解一下發生了什麼：

* `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`：這會為您的 Agent `my_sample_agent`（這是 Agent 資料夾的名稱）、使用者 ID (`u_123`) 和工作階段 ID (`s_123`) 建立一個新工作階段。您可以將 `my_sample_agent` 替換為您的 Agent 資料夾名稱。您可以將 `u_123` 替換為特定的使用者 ID，並將 `s_123` 替換為特定的工作階段 ID。
* `{"key1": "value1", "key2": 42}`：這是選填的。您可以使用它在建立工作階段時自定義 Agent 現有的狀態 (dict)。

如果建立成功，這應該會傳回工作階段資訊。輸出應如下所示：

```json
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"key1":"value1","key2":42},"events":[],"lastUpdateTime":1743711430.022186}
```

> [!NOTE]
    您無法使用完全相同的使用者 ID 和工作階段 ID 建立多個工作階段。如果您嘗試這樣做，可能會看到類似以下的回應：
    `{"detail":"Session already exists: s_123"}`。要解決此問題，您可以刪除該工作階段（例如 `s_123`），或選擇不同的工作階段 ID。

**發送查詢**

有兩種方法可以透過 POST 向您的 Agent 發送查詢，分別是透過 `/run` 或 `/run_sse` 路由。

* `POST http://localhost:8000/run`：將所有事件收集為清單並一次傳回整個清單。適合大多數使用者（如果您不確定，我們建議使用此方法）。
* `POST http://localhost:8000/run_sse`：作為伺服器發送事件 (Server-Sent-Events) 傳回，這是一個事件物件流。適合希望在事件可用時立即收到通知的人。使用 `/run_sse`，您還可以將 `streaming` 設置為 `true` 以啟用權杖級（token-level）串流。

**使用 `/run`**

```shell
# 發送同步查詢請求並等待完整回應
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

在 TypeScript 中，目前僅支援 `camelCase` 欄位名稱（例如 `appName`、`userId`、`sessionId` 等），近期將支援 `snake_case`。

如果使用 `/run`，您將同時看到事件的完整輸出（以清單形式），輸出應如下所示：

```json
[
  {
    "content": {
      "parts": [
        {
          "functionCall": {
            "id": "af-e75e946d-c02a-4aad-931e-49e4ab859838",
            "args": {
              "city": "new york"
            },
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
# 發送串流查詢請求
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

您可以將 `streaming` 設置為 `true` 以啟用權杖級串流，這意味著回應將以多個區塊的形式傳回給您，輸出應如下所示：

`data:`
```json
{
  "content": {
    "parts": [
      {
        "functionCall": {
          "id": "af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d",
          "args": {
            "city": "new york"
          },
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
```

`data:`
```json
{
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
```
`data:`
```json
{
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
**使用 `/run` 或 `/run_sse` 發送帶有 base64 編碼檔案的查詢**

```shell
# 發送包含圖片資料的請求
curl -X POST http://localhost:8000/run \
--H 'Content-Type: application/json' \
--d '{
   "appName":"my_sample_agent",
   "userId":"u_123",
   "sessionId":"s_123",
   "newMessage":{
      "role":"user",
      "parts":[{
            "text":"Describe this image"
         },{
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

> [!NOTE]
    如果您使用的是 `/run_sse`，您應該在每個事件可用時立即看到它。

## 整合

ADK 使用 [回呼 (Callbacks)](https://google.github.io/adk-docs/callbacks/) 與第三方觀測工具整合。這些整合可以擷取 Agent 呼叫和互動的詳細追蹤，這對於了解行為、除錯問題和評估效能至關重要。

* [Comet Opik](https://github.com/comet-ml/opik) 是一個開源 LLM 觀測與評估平台，[原生支援 ADK](https://www.comet.com/docs/opik/tracing/integrations/adk)。

## 部署您的 Agent

既然您已經驗證了 Agent 的本地操作，就可以開始部署 Agent 了！以下是您可以部署 Agent 的一些方式：

* 部署到 [Agent Engine](../deployment/agent-engine/index.md)，這是在 Google Cloud 上的 Vertex AI 受管理服務中部署 ADK Agent 最簡單的方法。
* 部署到 [Cloud Run](../deployment/cloud-run.md)，並使用 Google Cloud 上的無伺服器架構完全控制如何擴充和管理您的 Agent。


## ADK API 伺服器

ADK API 伺服器是一個預先封裝的 [FastAPI](https://fastapi.tiangolo.com/) 網頁伺服器，透過 RESTful API 公開您的 Agent。它是本地測試和開發的主要工具，讓您可以在部署 Agent 之前以程式化方式與其進行互動。

## 執行伺服器

要啟動伺服器，請從專案的根目錄執行以下指令：

```shell
# 啟動預設的 ADK API 伺服器
adk api_server
```

預設情況下，伺服器在 `http://localhost:8000` 上執行。您將看到確認伺服器已啟動的輸出：

```shell
# 伺服器執行中的訊息
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

## 使用互動式 API 文件進行除錯

API 伺服器會使用 Swagger UI 自動產生互動式 API 文件。這是一個非常有價值的工具，可用於探索端點、了解請求格式，以及直接從瀏覽器測試您的 Agent。

要訪問互動式文件，請啟動 API 伺服器並在網頁瀏覽器中導航至 [http://localhost:8000/docs](http://localhost:8000/docs)。

您將看到所有可用 API 端點的完整互動式清單，您可以展開該清單以查看有關參數、請求主體（request bodies）和回應結構（response schemas）的詳細資訊。您甚至可以點擊 "Try it out" 向運作中的 Agent 發送即時請求。

在 TypeScript 中，互動式 API 文件支援即將推出。

## API 端點

以下章節詳細介紹了與您的 Agent 互動的主要端點。

> [!NOTE] "JSON 命名規範"
    - **請求和回應主體** 中的欄位名稱都將使用 `camelCase`（例如 `"appName"`）。

### 公用端點

#### 列出可用的 Agent

傳回伺服器發現的所有 Agent 應用程式清單。

*   **方法：** `GET`
*   **路徑：** `/list-apps`

**請求範例**
```shell
# 獲取所有應用程式清單
curl -X GET http://localhost:8000/list-apps
```

**回應範例**
```json
["my_sample_agent", "another_agent"]
```

---

### 工作階段管理 (Session Management)

工作階段儲存特定使用者與 Agent 互動的狀態和事件歷史記錄。

#### 更新工作階段

更新現有的工作階段。

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

**請求範例**
```shell
# 更新特定工作階段的狀態
curl -X PATCH http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc \
  -H "Content-Type: application/json" \
  -d '{"stateDelta":{"visit_count": 5}}'
```

**回應範例**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[],"lastUpdateTime":1743711430.022186}
```

#### 獲取工作階段

擷取特定工作階段的詳細資訊，包括其當前狀態和所有相關事件。

*   **方法：** `GET`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**請求範例**
```shell
# 取得工作階段的詳細內容
curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**回應範例**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[...],"lastUpdateTime":1743711430.022186}
```

#### 刪除工作階段

刪除工作階段及其所有相關資料。

*   **方法：** `DELETE`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**請求範例**
```shell
# 刪除指定的工作階段
curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**回應範例**
成功刪除會傳回一個狀態碼為 `204 No Content` 的空回應。

---

### Agent 執行

這些端點用於向 Agent 發送新訊息並獲取回應。

#### 執行 Agent (單次回應)

執行 Agent 並在執行完成後在單個 JSON 陣列中傳回所有產生的事件。

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

在 TypeScript 中，目前僅支援 `camelCase` 欄位名稱（例如 `appName`、`userId`、`sessionId` 等），近期將支援 `snake_case`。

**請求範例**
```shell
# 發送請求並獲取單次完整回應
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

#### 執行 Agent (串流)

執行 Agent，並使用 [伺服器發送事件 (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) 在事件產生時將其串流回用戶端。

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
- `streaming`：(選填) 設置為 `true` 以啟用模型回應的權杖級串流。預設為 `false`。

**請求範例**
```shell
# 發送請求並啟用串流輸出
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
---
### API 整理表格

以下表格總結了 ADK API 伺服器提供的所有端點：

| 類別 | 端點名稱 | HTTP 方法 | 路徑 | 主要功能 | 請求參數 |
|------|---------|----------|------|---------|---------|
| **公用端點** | 列出可用的 Agent | `GET` | `/list-apps` | 傳回所有 Agent 應用程式清單 | 無 |
| **工作階段管理** | 更新工作階段 | `PATCH` | `/apps/{app_name}/users/{user_id}/sessions/{session_id}` | 更新現有工作階段的狀態 | `stateDelta`: 狀態變更物件 |
| **工作階段管理** | 獲取工作階段 | `GET` | `/apps/{app_name}/users/{user_id}/sessions/{session_id}` | 擷取工作階段詳細資訊 | 無 |
| **工作階段管理** | 刪除工作階段 | `DELETE` | `/apps/{app_name}/users/{user_id}/sessions/{session_id}` | 刪除工作階段及其資料 | 無 |
| **Agent 執行** | 執行 Agent (單次) | `POST` | `/run` | 執行 Agent 並傳回完整事件陣列 | `appName`, `userId`, `sessionId`, `newMessage` |
| **Agent 執行** | 執行 Agent (串流) | `POST` | `/run_sse` | 執行 Agent 並以 SSE 串流傳回事件 | `appName`, `userId`, `sessionId`, `newMessage`, `streaming`(選填) |

#### 路徑參數說明

- `{app_name}`: Agent 應用程式名稱（對應 Agent 資料夾名稱）
- `{user_id}`: 使用者識別碼（例如：`u_123`）
- `{session_id}`: 工作階段識別碼（例如：`s_abc`）

#### 通用請求結構

執行 Agent 時的 `newMessage` 物件結構：
```json
{
  "role": "user",
  "parts": [
    { "text": "您的訊息內容" }
  ]
}
```

支援多模態輸入（文字 + 圖片）時可使用 `inlineData` 欄位傳遞 base64 編碼的檔案資料。
