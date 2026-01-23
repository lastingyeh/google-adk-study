# Go ADK 快速入門

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/get-started/go/

本指南將引導您快速上手使用 Go 語言的 Agent Development Kit (ADK)。在開始之前，請確保您已安裝以下軟體：

*   Go 1.24.4 或更新版本
*   ADK Go v0.2.0 或更新版本

---

## 建立 Agent 專案

首先，建立一個包含以下檔案和目錄結構的 Agent 專案：

```
my_agent/
├── agent.go    # 主要的 Agent 程式碼
└── .env        # 存放 API 金鑰或專案 ID
```

> **重點說明：**
> *   `agent.go`: 這是您 Agent 的核心邏輯所在。
> *   `.env`: 用於管理環境變數，特別是敏感資訊如 API 金鑰，這樣可以避免將其硬編碼在程式碼中。

您可以使用以下指令快速建立此專案結構：

**MacOS / Linux:**
```bash
mkdir -p my_agent/ &&
    touch my_agent/agent.go &&
    touch my_agent/.env
```

**Windows:**
```console
mkdir my_agent

type nul > my_agent\agent.go
type nul > my_agent\.env
```

---

### 定義 Agent 程式碼

接著，為您的 Agent 建立基本程式碼。這個範例將使用內建的 [Google 搜尋工具](https://google.github.io/adk-docs/tools/#google-search)。將以下程式碼新增到您的 `my_agent/agent.go` 檔案中：

```go title="my_agent/agent.go"
package main

import (
	"context"
	"log"
	"os"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher"
	"google.golang.org/adk/cmd/launcher/full"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/geminitool"
	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()

	// 初始化 Gemini 模型
	model, err := gemini.NewModel(ctx, "gemini-3-pro-preview", &genai.ClientConfig{
		APIKey: os.Getenv("GOOGLE_API_KEY"),
	})
	if err != nil {
		log.Fatalf("無法建立模型: %v", err)
	}

	// 建立一個 LLM Agent
	timeAgent, err := llmagent.New(llmagent.Config{
		Name:        "hello_time_agent",
		Model:       model,
		Description: "在指定城市提供目前時間。",
		Instruction: "你是一個樂於助人的助理，會在指定城市提供目前時間。",
		Tools: []tool.Tool{
			geminitool.GoogleSearch{}, // 使用 Google 搜尋工具
		},
	})
	if err != nil {
		log.Fatalf("無法建立 Agent: %v", err)
	}

	// 設定 Agent 啟動器
	config := &launcher.Config{
		AgentLoader: agent.NewSingleLoader(timeAgent),
	}

	// 執行 Agent
	l := full.NewLauncher()
	if err = l.Execute(ctx, config, os.Args[1:]); err != nil {
		log.Fatalf("執行失敗: %v\n\n%s", err, l.CommandLineSyntax())
	}
}
```

> **重點說明：**
> *   `gemini.NewModel`: 初始化語言模型，這裡是使用 Gemini Pro，並透過環境變數 `GOOGLE_API_KEY` 讀取 API 金鑰。
> *   `llmagent.New`: 這是建立 Agent 的核心部分，您可以在這裡定義 Agent 的名稱、描述、指令 (Prompt) 以及要使用的工具。
> *   `launcher`: ADK 提供了一個啟動器來執行您的 Agent，並處理命令列互動或 Web 介面。

---

### 設定專案與依賴套件

使用 `go mod` 指令來初始化專案模組，並根據 `agent.go` 檔案中的 `import` 語句安裝所需的套件：

```console
go mod init my-agent/main
go mod tidy
```

---

### 設定您的 API 金鑰

本專案使用 Gemini API，因此需要一組 API 金鑰。如果您還沒有，請在 Google AI Studio 的 [API 金鑰頁面](https://aistudio.google.com/app/apikey) 建立一組金鑰。

在終端機視窗中，將您的 API 金鑰寫入專案的 `.env` 檔案中以設定環境變數：

**MacOS / Linux:**
```bash
echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > my_agent/.env
```

**Windows:**
```console
echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > my_agent\.env
```

> **提示：** ADK 支援多種生成式 AI 模型。想了解如何在 ADK Agent 中設定其他模型，請參閱 [模型與驗證](/adk-docs/agents/models)。

---

## 執行您的 Agent

您可以使用定義好的互動式命令列介面或 ADK Go 命令列工具提供的 ADK Web 使用者介面來執行您的 ADK Agent。這兩種方式都可以讓您測試並與您的 Agent 互動。

### 使用命令列介面執行

使用以下 Go 指令來執行您的 Agent：

```console
# 執行前，請記得載入環境變數：
# MacOS/Linux: source .env
# Windows: env.bat
go run agent.go
```

![adk-run.png](https://google.github.io/adk-docs/assets/adk-run.png)

### 使用 Web 介面執行

使用以下 Go 指令來透過 ADK Web 介面執行您的 Agent：

```console
# 執行前，請記得載入環境變數
go run agent.go web api webui
```

此指令會啟動一個帶有聊天介面的 Web 伺服器。您可以透過 [http://localhost:8080](http://localhost:8080) 存取 Web 介面。在左上角選擇您的 Agent，然後輸入您的請求。

![adk-web-dev-ui-chat.png](https://google.github.io/adk-docs/assets/adk-web-dev-ui-chat.png)

> **注意：** ADK Web 僅供開發使用，不應用於生產環境部署。請僅在開發和除錯時使用 ADK Web。

## 下一步：建構您的 Agent

現在您已經安裝了 ADK 並執行了您的第一個 Agent，試著跟隨我們的建構指南來打造您自己的 Agent：
- [建立你的代理](https://google.github.io/adk-docs/tutorials/)

---

## 參考資源

*   [ADK Go 套件文件](https://pkg.go.dev/google.golang.org/adk)
*   [Gemini API 文件](https://ai.google.dev/docs)
*   [Google AI Studio](https://aistudio.google.com/)