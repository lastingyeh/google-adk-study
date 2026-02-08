# 使用 AI 進行編碼

> 🔔 `更新日期：2026-02-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tutorials/coding-with-ai/

Agent Development Kit (ADK) 文件支援 [`/llms.txt` 標準](https://llmstxt.org/)，提供針對大型語言模型 (LLM) 最佳化的機器可讀文件索引。這讓您可以輕鬆地在 AI 驅動的開發環境中使用 ADK 文件作為上下文。

## 什麼是 llms.txt？

`llms.txt` 是一個標準化的文字檔案，作為 LLM 的地圖，列出最重要的文件頁面及其描述。這有助於 AI 工具理解 ADK 文件的結構，並檢索相關資訊以回答您的問題。

ADK 文件提供以下檔案，這些檔案會在每次更新時自動產生：

| 檔案 | 適用於... | URL |
| ------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **`llms.txt`**      | 能夠動態獲取連結的工具 | [`https://google.github.io/adk-docs/llms.txt`](https://google.github.io/adk-docs/llms.txt)           |
| **`llms-full.txt`** | 需要整個網站的單一靜態文字轉儲的工具 | [`https://google.github.io/adk-docs/llms-full.txt`](https://google.github.io/adk-docs/llms-full.txt) |

## 在開發工具中的使用方式

您可以使用這些檔案為您的 AI 編碼助理提供 ADK 知識。此功能允許您的代理在規劃任務和產生程式碼時，自主搜尋和閱讀 ADK 文件。

### Gemini CLI

[Gemini CLI](https://geminicli.com/) 可以設定為使用 [ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext) 來查詢 ADK 文件。

**安裝：**

要安裝擴充功能，請執行以下指令：

```bash
# 安裝 ADK Docs 擴充功能
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

**使用方式：**

安裝完成後，擴充功能會自動啟用。您可以直接在 Gemini CLI 中詢問有關 ADK 的問題，它將使用 `llms.txt` 檔案和 ADK 文件來提供準確的答案並產生程式碼。

例如，您可以在 Gemini CLI 中詢問以下問題：

> 如何使用 Agent Development Kit 建立功能工具？

---

### Antigravity

[Antigravity](https://antigravity.google/) IDE 可以透過執行指向 ADK 的 `llms.txt` 檔案的自訂 MCP 伺服器，設定為存取 ADK 文件。

**先決條件：**

請確保您已安裝 [`uv`](https://docs.astral.sh/uv/) 工具，因為此設定使用 `uvx` 來執行文件伺服器，無需手動安裝。

**設定：**

1. 透過編輯器代理面板頂部的 **...** (更多) 選單開啟 MCP 商店。

2. 點擊 **Manage MCP Servers** (管理 MCP 伺服器)。

3. 點擊 **View raw config** (查看原始設定)。

4. 將以下條目新增至 `mcp_config.json` 中的自訂 MCP 伺服器設定。如果這是您的第一個 MCP 伺服器，您可以貼上整個程式碼區塊：

   ```json
   {
     "mcpServers": {
       "adk-docs-mcp": {
         "command": "uvx",
         "args": [
           "--from",
           "mcpdoc",
           "mcpdoc",
           "--urls",
           "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
           "--transport",
           "stdio"
         ]
       }
     }
   }
   ```

有關管理 MCP 伺服器的更多資訊，請參閱 [Antigravity MCP 文件](https://antigravity.google/docs/mcp)。

**使用方式：**

設定完成後，您可以向編碼代理發出如下指令：

> 使用 ADK 文件建立一個多工具代理，該代理使用 Gemini 2.5 Pro 並包含模擬天氣查詢工具和自訂計算器工具。使用 `adk run` 驗證代理。

---

### Claude Code

[Claude Code](https://code.claude.com/docs/en/overview) 可以透過新增 [MCP 伺服器](https://code.claude.com/docs/en/mcp) 來設定查詢 ADK 文件。

**安裝：**

要將 ADK 文件的 MCP 伺服器新增至 Claude Code，請執行以下指令：

```bash
# 將 ADK 文件 MCP 伺服器新增至 Claude Code
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt --transport stdio
```

**使用方式：**

安裝完成後，MCP 伺服器會自動啟用。您可以直接在 Claude Code 中詢問有關 ADK 的問題，它將使用 `llms.txt` 檔案和 ADK 文件來提供準確的答案並產生程式碼。

例如，您可以在 Claude Code 中詢問以下問題：

> 如何使用 Agent Development Kit 建立功能工具？

---

### Cursor

[Cursor](https://cursor.com/) IDE 可以透過執行指向 ADK 的 `llms.txt` 檔案的自訂 MCP 伺服器，設定為存取 ADK 文件。

**先決條件：**

請確保您已安裝 [`uv`](https://docs.astral.sh/uv/) 工具，因為此設定使用 `uvx` 來執行文件伺服器，無需手動安裝。

**設定：**

1. 開啟 **Cursor Settings** (Cursor 設定) 並導航至 **Tools & MCP** 頁籤。

1. 點擊 **New MCP Server** (新增 MCP 伺服器)，這將開啟 `mcp.json` 進行編輯。

1. 將以下條目新增至 `mcp.json` 中的自訂 MCP 伺服器設定。如果這是您的第一個 MCP 伺服器，您可以貼上整個程式碼區塊：

   ```json
   {
     "mcpServers": {
       "adk-docs-mcp": {
         "command": "uvx",
         "args": [
           "--from",
           "mcpdoc",
           "mcpdoc",
           "--urls",
           "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
           "--transport",
           "stdio"
         ]
       }
     }
   }
   ```

有關管理 MCP 伺服器的更多資訊，請參閱 [Cursor MCP 文件](https://cursor.com/docs/context/mcp)。

**使用方式：**

設定完成後，您可以向編碼代理發出如下指令：

> 使用 ADK 文件建立一個多工具代理，該代理使用 Gemini 2.5 Pro 並包含模擬天氣查詢工具和自訂計算器工具。使用 `adk run` 驗證代理。

---

### 其他工具

任何支援 `llms.txt` 標準或可以從 URL 攝取文件的工具都可以從這些檔案中受益。您可以將 URL `https://google.github.io/adk-docs/llms.txt` (或 `llms-full.txt`) 提供給您工具的知識庫設定或 MCP 伺服器設定。
