# 適用於 ADK 的 AG-UI 使用者介面

> 🔔 `更新日期：2025-03-04`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/ag-ui/

[`ADK 支援`: `Python` | `TypeScript` | `Go` | `Java`]

讓您的 ADK 代理程式轉變為具備豐富、響應式 UI 的全功能應用程式。[AG-UI](https://docs.ag-ui.com/) 是一個開放協定，負責處理代理程式與使用者之間的串流事件、用戶端狀態以及雙向通訊。

[AG-UI](https://github.com/ag-ui-protocol/ag-ui) 提供一致的介面，為跨技術棧（從行動端到網頁端，甚至是命令列）的豐富用戶端提供支援。目前有多種不同的用戶端支援 AG-UI：

- [CopilotKit](https://copilotkit.ai) 提供工具和組件，將您的代理程式與網頁應用程式緊密整合
- 適用於 [Kotlin](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin)、[Java](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java)、[Go](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client) 的用戶端，以及使用 TypeScript 實作的 [CLI 版本](https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src)

本教學使用 CopilotKit 建立一個由 ADK 代理程式支援的範例應用程式，展示 AG-UI 支援的部分功能。

## 快速入門

首先，讓我們建立一個包含 ADK 代理程式和簡單網頁用戶端的範例應用程式：

1. 建立應用程式：

   ```bash
   # 使用 copilotkit 建立 ADK 範例專案
   npx copilotkit@latest create -f adk
   ```

1. 設定您的 Google API 金鑰：

   ```bash
   # 設定環境變數以使用 Google API
   export GOOGLE_API_KEY="your-api-key"
   ```

1. 安裝依賴項並執行：

   ```bash
   # 安裝套件並啟動開發伺服器
   npm install && npm run dev
   ```

這會啟動兩個伺服器：

- **http://localhost:3000** - 網頁 UI（在瀏覽器中開啟此連結）
- **http://localhost:8000** - ADK 代理程式 API（僅限後端）

在瀏覽器中開啟 <http://localhost:3000> 與您的代理程式進行對話。

## 功能

### 聊天 (Chat)

聊天是展示代理程式的常見介面，AG-UI 負責處理使用者與代理程式之間的訊息串流：

`src/app/page.tsx`
```tsx
<CopilotSidebar
  clickOutsideToClose={false} // 點擊外部不關閉
  defaultOpen={true} // 預設開啟
  labels={{
    title: "彈出式助手",
    initial: "👋 嗨，你好！你正在與代理程式聊天。此代理程式附帶一些工具可以幫助你開始..."
  }}
/>
```

在 [CopilotKit 文件](https://docs.copilotkit.ai/adk/agentic-chat-ui)中了解更多關於聊天 UI 的資訊。

### 生成式 UI (Generative UI)

AG-UI 讓您可以與生成式 UI 分享工具資訊，以便向使用者顯示：

`src/app/page.tsx`
```tsx
useRenderToolCall(
  {
    name: "get_weather", // 工具名稱：取得天氣
    description: "取得指定地點的天氣。", // 工具描述
    parameters: [{ name: "location", type: "string", required: true }], // 參數：地點
    render: ({ args }) => {
      // 渲染天氣卡片組件
      return <WeatherCard location={args.location} themeColor={themeColor} />;
    },
  },
  [themeColor],
);
```

在 [CopilotKit 文件](https://docs.copilotkit.ai/adk/generative-ui)中了解更多關於生成式 UI 的資訊。

### 共享狀態 (Shared State)

ADK 代理程式可以是具備狀態的，而在代理程式與 UI 之間同步該狀態可實現強大且流暢的使用者體驗。狀態可以雙向同步，因此代理程式會自動感知使用者或應用程式其他部分所做的變更：

`src/app/page.tsx`
```tsx
// 使用 useCoAgent 同步代理程式狀態
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent", // 代理程式名稱
  initialState: {
    proverbs: [
      "千里之行，始於足下。",
    ],
  },
})
```

在 [CopilotKit 文件](https://docs.copilotkit.ai/adk/shared-state)中了解更多關於共享狀態的資訊。

## 資源

若要查看您可以使用 AG-UI 在 UI 中構建的其他功能，請參考 CopilotKit 文件：

- [代理生成式 UI (Agentic Generative UI)](https://docs.copilotkit.ai/adk/generative-ui/agentic)
- [人機協作 (Human in the Loop)](https://docs.copilotkit.ai/adk/human-in-the-loop)
- [前端動作 (Frontend Actions)](https://docs.copilotkit.ai/adk/frontend-actions)

或者在 [AG-UI Dojo](https://dojo.ag-ui.com) 中嘗試。
