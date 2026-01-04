# ADK TypeScript 快速入門

> 更新日期：2026 年 1 月 4 日

本指南將說明如何開始使用 Agent Development Kit (ADK) for TypeScript。在開始之前，請確認您已安裝以下項目：

*   Node.js 20.12.7 或更高版本
*   Node Package Manager (npm) 9.2.0 或更高版本

## 建立 Agent 專案

建立包含以下檔案和目錄結構的 Agent 專案：

```none
my-agent/
    agent.ts        # 主要 agent 程式碼
    package.json    # 專案設定檔
    tsconfig.json   # TypeScript 設定檔
    .env            # API 金鑰或專案 ID
```

### 使用命令列建立專案結構

**MacOS / Linux**

```bash
mkdir -p my-agent/ && \
    touch my-agent/agent.ts \
    touch my-agent/package.json \
    touch my-agent/.env
```

**Windows**

```console
mkdir my-agent\
type nul > my-agent\agent.ts
type nul > my-agent\package.json
type nul > my-agent\.env
```

**注意：** 請勿建立 `tsconfig.json`，您將在稍後的步驟中產生該檔案。

### 定義 Agent 程式碼

為基本 Agent 建立程式碼，包含一個名為 `getCurrentTime` 的 ADK [Function Tool](https://google.github.io/adk-docs/tools-custom/function-tools/) 簡單實作。
將以下程式碼新增至專案目錄中的 `agent.ts` 檔案：

```typescript title="my-agent/agent.ts"
import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

/* 模擬工具實作 */
// 定義一個獲取當前時間的工具
const getCurrentTime = new FunctionTool({
  name: 'get_current_time',
  description: 'Returns the current time in a specified city.', // 返回指定城市的當前時間
  parameters: z.object({
    city: z.string().describe("The name of the city for which to retrieve the current time."), // 要檢索當前時間的城市名稱
  }),
  // 執行邏輯
  execute: ({city}) => {
    return {status: 'success', report: `The current time in ${city} is 10:30 AM`};
  },
});

// 定義主要 Agent
export const rootAgent = new LlmAgent({
  name: 'hello_time_agent',
  model: 'gemini-2.5-flash', // 使用的模型
  description: 'Tells the current time in a specified city.', // Agent 描述
  instruction: `You are a helpful assistant that tells the current time in a city.
                Use the 'getCurrentTime' tool for this purpose.`, // Agent 指令：告知城市時間，使用 getCurrentTime 工具
  tools: [getCurrentTime], // 註冊工具
});
```

### 設定專案與相依套件

使用 `npm` 工具安裝並設定專案的相依套件，包括 package 檔案、TypeScript 設定、ADK TypeScript 主要函式庫和開發者工具。在您的 `my-agent/` 目錄中執行以下命令：

```console
cd my-agent/
# 初始化專案使用預設值
npm init --yes
# 設定 TypeScript
npm install -D typescript
npx tsc --init
# 安裝 ADK 函式庫
npm install @google/adk
npm install @google/adk-devtools
```

完成這些安裝和設定步驟後，開啟 `package.json` 專案檔案，並確認 `main:` 值已設定為 `agent.ts`，且 TypeScript 相依套件以及 ADK 函式庫相依套件已設定，如下例所示：

`my-agent/package.json`
```json
{
  "name": "my-agent",
  "version": "1.0.0",
  "description": "My ADK Agent",
  "main": "agent.ts",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "devDependencies": {
    "typescript": "^5.9.3"
  },
  "dependencies": {
    "@google/adk": "^0.2.0",
    "@google/adk-devtools": "^0.2.0"
  }
}
```

為了開發方便，請在 `tsconfig.json` 檔案中，將 `verbatimModuleSyntax` 設定更新為 `false`，以允許在新增模組時使用較簡單的語法：

`my-agent/tsconfig.json`
```json
    // 設定為 false 以允許 CommonJS 模組語法：
    "verbatimModuleSyntax": false,
```

### 編譯專案

完成專案設定後，編譯專案以準備執行您的 ADK Agent：

```console
npx tsc
```

### 設定您的 API 金鑰

本專案使用 Gemini API，需要 API 金鑰。如果您還沒有 Gemini API 金鑰，請在 Google AI Studio 的 [API Keys](https://aistudio.google.com/app/apikey) 頁面建立一個金鑰。

在終端機視窗中，將您的 API 金鑰寫入專案的 `.env` 檔案以設定環境變數：

```bash title="更新: my-agent/.env"
echo 'GEMINI_API_KEY="YOUR_API_KEY"' > .env
```

> **提示：在 ADK 中使用其他 AI 模型**
> ADK 支援使用多種生成式 AI 模型。如需有關在 ADK Agent 中設定其他模型的更多資訊，請參閱 [Models & Authentication](https://google.github.io/adk-docs/agents/models/)。

## 執行您的 Agent

您可以使用 `@google/adk-devtools` 函式庫作為互動式命令列介面（使用 `run` 命令），或使用 ADK 網頁使用者介面（使用 `web` 命令）來執行您的 ADK Agent。這兩個選項都允許您測試並與您的 Agent 互動。

### 使用命令列介面執行

使用以下命令透過 ADK TypeScript 命令列介面工具執行您的 Agent：

```console
npx @google/adk-devtools run agent.ts
```

![adk-run.png](https://google.github.io/adk-docs/assets/adk-run.png)

### 使用網頁介面執行

使用以下命令透過 ADK 網頁介面執行您的 Agent：

```console
npx @google/adk-devtools web
```

此命令會啟動一個網頁伺服器，並為您的 Agent 提供聊天介面。您可以透過 (http://localhost:8000) 存取網頁介面。在右上角選擇您的 Agent 並輸入請求。

![adk-web-dev-ui-chat.png](https://google.github.io/adk-docs/assets/adk-web-dev-ui-chat.png)

> **警告：ADK Web 僅供開發使用**
> ADK Web ***不適合用於正式生產部署***。您應僅將 ADK Web 用於開發和除錯目的。

## 參考資源

*   [Function Tool](https://google.github.io/adk-docs/tools-custom/function-tools/)
*   [API Keys](https://aistudio.google.com/app/apikey)
*   [Models & Authentication](https://google.github.io/adk-docs/agents/models/)
