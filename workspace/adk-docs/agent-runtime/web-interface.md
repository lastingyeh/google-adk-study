# 使用網頁介面
> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/runtime/web-interface/

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

ADK 網頁介面讓您可以直接在瀏覽器中測試您的代理程式 (agents)。此工具提供了一種簡單的方法來互動式地開發和偵錯您的代理程式。

![ADK 網頁介面](https://google.github.io/adk-docs/assets/adk-web-dev-ui-chat.png)

> [!WARNING] 注意：ADK Web 僅用於開發
ADK Web ***不適用於生產環境部署***。您應該僅將 ADK Web 用於開發和偵錯目的。

## 啟動網頁介面

使用以下命令在 ADK 網頁介面中執行您的代理程式：

<details>
<summary>範例說明</summary>

> Python

```shell
# 執行 ADK 網頁介面
adk web
```

> TypeScript

```shell
# 使用 npx 執行 ADK 網頁介面
npx adk web
```

> Go

```shell
# 執行 Go 代理程式並啟動網頁 UI
go run agent.go web api webui
```

<details>
<summary>Java</summary>

請確保更新連接埠號碼。

> Maven

使用 Maven 編譯並執行 ADK 網頁伺服器：
```console
# 編譯並執行，指定代理程式原始碼目錄與連接埠
mvn compile exec:java \
-Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
```

> Gradle

使用 Gradle 時，`build.gradle` 或 `build.gradle.kts` 建置檔案的 plugins 區段應包含以下 Java 外掛：

```groovy
// 引入 Java 外掛
plugins {
    id('java')
    // 其他外掛
}
```

然後，在建置檔案的其他地方（頂層），建立一個新任務：

```groovy
// 註冊執行 ADK 網頁伺服器的任務
tasks.register('runADKWebServer', JavaExec) {
    dependsOn classes
    classpath = sourceSets.main.runtimeClasspath
    mainClass = 'com.google.adk.web.AdkWebServer'
    args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
}
```

最後，在命令列執行以下命令：
```
# 執行自定義的 Gradle 任務來啟動伺服器
gradle runADKWebServer
```

在 Java 中，網頁介面和 API 伺服器是綑綁在一起的。
</details>

</details>

伺服器預設在 `http://localhost:8000` 啟動：

```shell
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+
```

## 功能

ADK 網頁介面的主要功能包括：

- **對話介面**：向您的代理程式發送訊息並即時查看回應
- **會話管理**：建立並在不同會話 (sessions) 之間切換
- **狀態檢視**：在開發過程中查看並修改會話狀態 (state)
- **事件歷史**：檢查代理程式執行期間產生的所有事件 (events)

## 常見選項

| 選項 | 描述 | 預設值 |
|--------|-------------|---------|
| `--port` | 執行伺服器的連接埠 | `8000` |
| `--host` | 主機綁定地址 | `127.0.0.1` |
| `--session_service_uri` | 自定義會話存儲 URI | In-memory |
| `--artifact_service_uri` | 自定義 artifact 存儲 URI | 本地 `.adk/artifacts` |
| `--reload/--no-reload` | 在程式碼變更時啟用自動重新載入 | `true` |

### 帶有選項的範例

```shell
# 指定連接埠與會話服務資料庫的範例
adk web --port 3000 --session_service_uri "sqlite:///sessions.db"
```
