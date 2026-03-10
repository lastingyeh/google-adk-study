# MCP 資料庫工具箱 (MCP Toolbox for Databases)

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/mcp-toolbox-for-databases/

[`ADK 支援`: `Python` | `Typescript` | `Go`]

[MCP 資料庫工具箱 (MCP Toolbox for Databases)](https://github.com/googleapis/genai-toolbox) 是一個開源的資料庫 MCP 伺服器。它的設計初衷是為了滿足企業級和生產環境的品質需求。透過處理連接池、身份驗證等複雜細節，它能讓您更輕鬆、更快速且更安全地開發工具。

Google 的 Agent 開發套件 (ADK) 內建支援 Toolbox。有關 [開始使用](https://googleapis.github.io/genai-toolbox/getting-started/) 或 [配置](https://googleapis.github.io/genai-toolbox/getting-started/configure/) Toolbox 的更多資訊，請參閱 [說明文件](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)。

![GenAI 工具箱](https://google.github.io/adk-docs/integrations/assets/mcp-db-toolbox.png)

## 支援的資料來源

MCP Toolbox 為以下資料庫和資料平台提供開箱即用的工具集：

### Google Cloud

*   [BigQuery](https://googleapis.github.io/genai-toolbox/resources/sources/bigquery/)（包括 SQL 執行、架構探索和 AI 驅動的時間序列預測工具）
*   [AlloyDB](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-pg/)（相容於 PostgreSQL，提供標準查詢和自然語言查詢工具）
*   [AlloyDB Admin](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-admin/)
*   [Spanner](https://googleapis.github.io/genai-toolbox/resources/sources/spanner/)（支援 GoogleSQL 和 PostgreSQL 方言）
*   Cloud SQL（專門支援 [Cloud SQL for PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-pg/)、[Cloud SQL for MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mysql/) 和 [Cloud SQL for SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mssql/)）
*   [Cloud SQL Admin](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-admin/)
*   [Firestore](https://googleapis.github.io/genai-toolbox/resources/sources/firestore/)
*   [Bigtable](https://googleapis.github.io/genai-toolbox/resources/sources/bigtable/)
*   [Dataplex](https://googleapis.github.io/genai-toolbox/resources/sources/dataplex/)（用於資料探索和元數據搜尋）
*   [Cloud Monitoring](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-monitoring/)

### 關聯式與 SQL 資料庫

*   [PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/postgres/)（通用型）
*   [MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/mysql/)（通用型）
*   [Microsoft SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/mssql/)（通用型）
*   [ClickHouse](https://googleapis.github.io/genai-toolbox/resources/sources/clickhouse/)
*   [TiDB](https://googleapis.github.io/genai-toolbox/resources/sources/tidb/)
*   [OceanBase](https://googleapis.github.io/genai-toolbox/resources/sources/oceanbase/)
*   [Firebird](https://googleapis.github.io/genai-toolbox/resources/sources/firebird/)
*   [SQLite](https://googleapis.github.io/genai-toolbox/resources/sources/sqlite/)
*   [YugabyteDB](https://googleapis.github.io/genai-toolbox/resources/sources/yugabytedb/)

### NoSQL 與 鍵值存儲 (Key-Value Stores)

*   [MongoDB](https://googleapis.github.io/genai-toolbox/resources/sources/mongodb/)
*   [Couchbase](https://googleapis.github.io/genai-toolbox/resources/sources/couchbase/)
*   [Redis](https://googleapis.github.io/genai-toolbox/resources/sources/redis/)
*   [Valkey](https://googleapis.github.io/genai-toolbox/resources/sources/valkey/)
*   [Cassandra](https://googleapis.github.io/genai-toolbox/resources/sources/cassandra/)

### 圖形資料庫 (Graph Databases)

*   [Neo4j](https://googleapis.github.io/genai-toolbox/resources/sources/neo4j/)（提供 Cypher 查詢和架構檢查工具）
*   [Dgraph](https://googleapis.github.io/genai-toolbox/resources/sources/dgraph/)

### 資料平台與聯邦 (Data Platforms & Federation)

*   [Looker](https://googleapis.github.io/genai-toolbox/resources/sources/looker/)（用於透過 Looker API 執行 Looks、查詢並建立儀表板）
*   [Trino](https://googleapis.github.io/genai-toolbox/resources/sources/trino/)（用於跨多個來源執行聯邦查詢）

### 其他

*   [HTTP](https://googleapis.github.io/genai-toolbox/resources/sources/http/)

## 配置與部署

Toolbox 是一個由您自行部署與管理的開源伺服器。有關部署和配置的更多說明，請參閱官方 Toolbox 說明文件：

* [安裝伺服器](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
* [配置 Toolbox](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

## 安裝適用於 ADK 的客戶端 SDK

<details>
<summary>Python</summary>

ADK 依賴 `toolbox-adk` Python 套件來使用 Toolbox。在開始之前請先安裝該套件：

```shell
pip install google-adk[toolbox]
```

### 載入 Toolbox 工具

一旦您的 Toolbox 伺服器配置完成並啟動運行，您就可以使用 ADK 從伺服器載入工具：

```python
from google.adk.agents import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

# 初始化 Toolbox 工具集
toolset = ToolboxToolset(
    server_url="http://127.0.0.1:5000"
)

# 建立 Agent 並提供工具集
root_agent = Agent(
    ...,
    tools=[toolset] # 將工具集提供給 Agent
)
```

### 身份驗證

`ToolboxToolset` 支援各種身份驗證策略，包括工作負載標識 (Workload Identity, ADC)、使用者標識 (User Identity, OAuth2) 和 API 金鑰。如需完整文件，請參閱 [Toolbox ADK 身份驗證指南](https://github.com/googleapis/mcp-toolbox-sdk-python/tree/main/packages/toolbox-adk#authentication)。

**範例：工作負載標識 (Workload Identity, ADC)**

建議用於 Cloud Run、GKE 或使用 `gcloud auth login` 進行本機開發。

```python
from google.adk.tools.toolbox_toolset import ToolboxToolset
from toolbox_adk import CredentialStrategy

# target_audience: 您的 Toolbox 伺服器 URL
creds = CredentialStrategy.workload_identity(target_audience="<TOOLBOX_URL>")

# 使用憑證初始化工具集
toolset = ToolboxToolset(
    server_url="<TOOLBOX_URL>",
    credentials=creds
)
```

### 進階配置

您可以配置參數綁定、請求掛鉤 (request hooks) 和額外的標頭。詳情請參閱 [Toolbox ADK 說明文件](https://github.com/googleapis/mcp-toolbox-sdk-python/tree/main/packages/toolbox-adk)。

#### 參數綁定 (Parameter Binding)

全域綁定工具參數的值。這些值對模型是隱藏的。

```python
toolset = ToolboxToolset(
    server_url="...",
    bound_params={
        "region": "us-central1",
        "api_key": lambda: get_api_key() # 可以是一個可呼叫物件
    }
)
```

#### 配合掛鉤 (Hooks) 使用

附加 `pre_hook` 和 `post_hook` 函式，以便在呼叫工具之前和之後執行邏輯。

```python
async def log_start(context, args):
    # 在工具啟動時記錄參數
    print(f"Starting tool with args: {args}")

toolset = ToolboxToolset(
    server_url="...",
    pre_hook=log_start
)
```
</details>

<details>
<summary>Typescript</summary>


ADK 依賴 `@toolbox-sdk/adk` TS 套件來使用 Toolbox。在開始之前請先安裝該套件：

```shell
npm install @toolbox-sdk/adk
```

### 載入 Toolbox 工具

一旦您的 Toolbox 伺服器配置完成並啟動運行，您就可以使用 ADK 從伺服器載入工具：

```typescript
import {InMemoryRunner, LlmAgent} from '@google/adk';
import {Content} from '@google/genai';
import {ToolboxClient} from '@toolbox-sdk/adk'

// 初始化 Toolbox 客戶端並載入工具集
const toolboxClient = new ToolboxClient("http://127.0.0.1:5000");
const loadedTools = await toolboxClient.loadToolset();

export const rootAgent = new LlmAgent({
  name: 'weather_time_agent',
  model: 'gemini-2.5-flash',
  description:
    '用於回答有關城市時間和天氣問題的 Agent。',
  instruction:
    '您是一個樂於助人的 Agent，可以回答使用者有關城市時間和天氣的問題。',
  tools: loadedTools,
});

async function main() {
  const userId = 'test_user';
  const appName = rootAgent.name;
  const runner = new InMemoryRunner({agent: rootAgent, appName});
  const session = await runner.sessionService.createSession({
    appName,
    userId,
  });

  const prompt = '紐約的天氣如何？現在幾點？';
  const content: Content = {
    role: 'user',
    parts: [{text: prompt}],
  };
  console.log(content);
  // 非同步執行 Runner 並處理事件
  for await (const e of runner.runAsync({
    userId,
    sessionId: session.id,
    newMessage: content,
  })) {
    if (e.content?.parts?.[0]?.text) {
      console.log(`${e.author}: ${JSON.stringify(e.content, null, 2)}`);
    }
  }
}

main().catch(console.error);
```
</details>

<details>
<summary>Go</summary>


ADK 依賴 `mcp-toolbox-sdk-go` Go 模組來使用 Toolbox。在開始之前請先安裝該模組：

```shell
go get github.com/googleapis/mcp-toolbox-sdk-go
```

### 載入 Toolbox 工具

一旦您的 Toolbox 伺服器配置完成並啟動運行，您就可以使用 ADK 從伺服器載入工具：

```go
package main

import (
	"context"
	"fmt"

	"github.com/googleapis/mcp-toolbox-sdk-go/tbadk"
	"google.golang.org/adk/agent/llmagent"
)

func main() {

  // 建立新的 MCP Toolbox 客戶端
  toolboxClient, err := tbadk.NewToolboxClient("https://127.0.0.1:5000")
	if err != nil {
		log.Fatalf("Failed to create MCP Toolbox client: %v", err)
	}

  // 載入特定的工具集
  toolboxtools, err := toolboxClient.LoadToolset("my-toolset-name", ctx)
  if err != nil {
    return fmt.Sprintln("Could not load Toolbox Toolset", err)
  }

  // 將載入的工具轉換為 ADK 工具清單
  toolsList := make([]tool.Tool, len(toolboxtools))
    for i := range toolboxtools {
      toolsList[i] = &toolboxtools[i]
    }

  // 初始化 LLM Agent 並提供工具清單
  llmagent, err := llmagent.New(llmagent.Config{
    ...,
    Tools:       toolsList,
  })

  // 載入單一工具
  tool, err := client.LoadTool("my-tool-name", ctx)
  if err != nil {
    return fmt.Sprintln("Could not load Toolbox Tool", err)
  }

  // 使用單一工具初始化 Agent
  llmagent, err := llmagent.New(llmagent.Config{
    ...,
    Tools:       []tool.Tool{&toolboxtool},
  })
}
```
</details>

## 進階 Toolbox 功能

Toolbox 具有多種功能，可讓您更輕鬆地為資料庫開發生成式 AI 工具。如需更多資訊，請閱讀以下功能的詳細介紹：

* [經過身份驗證的參數 (Authenticated Parameters)](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters)：自動將工具輸入與來自 OIDC 權杖的值綁定，從而輕鬆運行敏感查詢而不會有資料外洩的風險。
* [授權呼叫 (Authorized Invocations)](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations)：根據使用者的身份驗證權杖 (Auth token) 限制工具的使用權限。
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/)：透過 OpenTelemetry 從 Toolbox 獲取指標和追蹤資訊。
