# 使用命令列

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/runtime/command-line/

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

ADK 提供了一個互動式終端介面，用於測試您的代理。這對於快速測試、腳本化互動以及 CI/CD 流水線非常有用。

![ADK 執行](https://google.github.io/adk-docs/assets/adk-run.png)

## 執行代理

使用以下命令在 ADK 命令列介面中執行您的代理：

<details>
<summary>範例說明</summary>

> Python
```shell
# 執行名為 my_agent 的代理
adk run my_agent
```
> TypeScript
```shell
# 使用 npx 執行 TypeScript 版本的代理
npx @google/adk-devtools run agent.ts
```
> Go
```shell
# 直接執行 Go 語言的代理檔案
go run agent.go
```
> Java

建立一個 `AgentCliRunner` 類別 (請參閱 [Java 快速入門](../get-started/java.md) 並執行：

```shell
# 編譯並執行 Java 代理的 Main Class
mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
```
</details>

這將啟動一個互動式工作階段，您可以在終端中直接輸入查詢並查看代理回應：

```shell
代理執行中，輸入 exit 可退出。
[使用者輸入]：New York 的天氣如何？
[代理回應]：New York 的天氣晴朗，氣溫為 25°C。
[使用者輸入]：退出。
```

## 工作階段選項 (Session Options)

`adk run` 命令包含用於儲存、繼續和重播工作階段的選項。

### 儲存工作階段 (Save sessions)

要在退出時儲存工作階段：

```shell
# 執行代理並指定在退出時儲存工作階段到路徑
adk run --save_session path/to/my_agent
```

系統會提示您輸入工作階段 ID，工作階段將儲存至 `path/to/my_agent/<session_id>.session.json`。

您也可以預先指定工作階段 ID：

```shell
# 執行代理並預先指定工作階段 ID 進行儲存
adk run --save_session --session_id my_session path/to/my_agent
```

### 繼續工作階段 (Resume sessions)

要繼續先前儲存的工作階段：

```shell
# 載入指定的工作階段 JSON 檔案以繼續對話
adk run --resume path/to/my_agent/my_session.session.json path/to/my_agent
```

這會載入先前的工作階段狀態和事件歷史記錄，並顯示出來，讓您能夠繼續對話。

### 重播工作階段 (Replay sessions)

要重播工作階段檔案而不進行互動式輸入：

```shell
# 使用輸入檔案進行非互動式重播
adk run --replay path/to/input.json path/to/my_agent
```

輸入檔案應包含初始狀態和查詢：

```json
{
  "state": {"key": "value"},
  "queries": ["What is 2 + 2?", "What is the capital of France?"]
}
```

## 儲存選項 (Storage Options)

| 選項 | 描述 | 預設值 |
|--------|-------------|---------|
| `--session_service_uri` | 自訂工作階段儲存 URI | `.adk/session.db` 路徑下的 SQLite |
| `--artifact_service_uri` | 自訂 Artifact 儲存 URI | 本地 `.adk/artifacts` |

### 儲存選項範例

```shell
# 使用自訂的 SQLite 資料庫檔案儲存工作階段
adk run --session_service_uri "sqlite:///my_sessions.db" path/to/my_agent
```

## 所有選項 (All Options)

| 選項 | 描述 |
|--------|-------------|
| `--save_session` | 退出時將工作階段儲存至 JSON 檔案 |
| `--session_id` | 儲存時使用的工作階段 ID |
| `--resume` | 要繼續的工作階段檔案路徑 |
| `--replay` | 用於非互動式重播的輸入檔案路徑 |
| `--session_service_uri` | 自訂工作階段儲存 URI |
| `--artifact_service_uri` | 自訂 Artifact 儲存 URI |
