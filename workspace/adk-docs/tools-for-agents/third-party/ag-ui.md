# 使用 AG-UI 和 CopilotKit 構建對話體驗

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/third-party/ag-ui/

作為一名代理構建者（agent builder），您希望用戶能透過豐富且響應迅速的介面與您的代理進行互動。從頭開始構建 UI 需要投入大量精力，特別是為了支援串流事件（streaming events）和客戶端狀態。這正是 [AG-UI](https://docs.ag-ui.com/) 的設計初衷 —— 直接連接到代理的豐富用戶體驗。

[AG-UI](https://github.com/ag-ui-protocol/ag-ui) 提供了一個一致的介面，以賦能跨技術棧（從行動端到網頁端，甚至是命令行）的豐富客戶端。目前有多種不同的客戶端支援 AG-UI：

- [CopilotKit](https://copilotkit.ai) 提供工具和組件，將您的代理與網頁應用程序緊密整合
- 適用於 [Kotlin](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin)、[Java](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java)、[Go](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client) 的客戶端，以及 TypeScript 中的 [CLI 實現](https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src)

本教學使用 CopilotKit 創建一個由 ADK 代理支援的範例應用程序，展示 AG-UI 支援的一些功能。

## 快速開始

首先，讓我們創建一個包含 ADK 代理和簡單網頁客戶端的範例應用程序：

```bash
# 使用 npx 創建一個帶有 ADK 代理的 ag-ui 應用程序
npx create-ag-ui-app@latest --adk
```

### 聊天 (Chat)

聊天是公開代理的熟悉介面，AG-UI 處理用戶與代理之間的串流訊息：

`src/app/page.txs`:
```tsx
// src/app/page.tsx
<CopilotSidebar
  clickOutsideToClose={false}
  defaultOpen={true}
  labels={{
    title: "彈出式助手",
    initial: "👋 嗨，你好！您正在與代理聊天。這個代理附帶了一些工具可以幫助您開始..."
  }}
/>
```


在 [CopilotKit 文件](https://docs.copilotkit.ai/adk/agentic-chat-ui) 中了解更多關於聊天 UI 的資訊。

### 基於工具的生成式 UI (渲染工具)

AG-UI 讓您與生成式 UI (Generative UI) 共享工具資訊，以便向用戶顯示：

`src/app/page.tsx`:
```tsx
// src/app/page.tsx
useCopilotAction({
  name: "get_weather", // 工具名稱：獲取天氣
  description: "獲取給定地點的天氣。", // 工具描述
  available: "disabled",
  parameters: [
    { name: "location", type: "string", required: true }, // 參數：地理位置，類型為字串，必填
  ],
  render: ({ args }) => {
    // 渲染天氣卡片組件，並傳入位置和主題顏色
    return <WeatherCard location={args.location} themeColor={themeColor} />
  },
});
```

在 [CopilotKit 文件](https://docs.copilotkit.ai/adk/generative-ui/tool-based) 中了解更多關於基於工具的生成式 UI 的資訊。

### 共享狀態 (Shared State)

ADK 代理可以是具有狀態的（stateful），在您的代理和 UI 之間同步該狀態可以實現強大且流暢的用戶體驗。狀態可以雙向同步，因此代理會自動察覺用戶或應用程序其他部分所做的更改：

`src/app/page.tsx`:
```tsx
// src/app/page.tsx
// 使用 useCoAgent 鉤子與名為 "my_agent" 的代理同步狀態
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: {
    proverbs: [
      "CopilotKit 可能很新，但它是最棒的發明之一 (sliced bread)。",
    ],
  },
})
```

</details>

在 [CopilotKit 文件](https://docs.copilotkit.ai/adk/shared-state) 中了解更多關於共享狀態的資訊。

### 試試看！

```bash
# 安裝依賴並啟動開發伺服器
npm install && npm run dev
```

## 資源

要查看您可以使用 AG-UI 在 UI 中構建的其他功能，請參考 CopilotKit 文件：

- [代理生成式 UI (Agentic Generative UI)](https://docs.copilotkit.ai/adk/generative-ui/agentic)
- [人機協同 (Human in the Loop)](https://docs.copilotkit.ai/adk/human-in-the-loop/agent)
- [前端動作 (Frontend Actions)](https://docs.copilotkit.ai/adk/frontend-actions)

或者在 [AG-UI Dojo](https://dojo.ag-ui.com) 中親自嘗試。
