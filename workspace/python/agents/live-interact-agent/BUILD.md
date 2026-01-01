# 前端專案建構詳解：從零打造 Multimodal Live Client

本文件將專案拆解為詳細的建構步驟，深入至**單一檔案**層級，說明每個核心檔案的生成目的與實作邏輯。透過依序理解這些檔案的建立過程，您將能掌握整個專案的資料流向與架構原理。

---

## 第一階段：專案初始化與設定 (Initialization)

在撰寫業務邏輯前，我們先建立專案骨架與基礎設定。

### 步驟 1：建立 React TypeScript 專案
-   **生成檔案**: `package.json`, `tsconfig.json`
-   **說明**: 使用 Create React App (CRA) 搭配 TypeScript 模版初始化專案。
    -   `package.json`: 定義了 `react`, `sass`, `eventemitter3` 等關鍵依賴。
    -   `tsconfig.json`: 設定 TypeScript 編譯選項，確保型別安全。

---

## 第二階段：定義核心型別 (Core Types)

為了確保前後端溝通順暢，我們首先定義資料的「規格書」。

### 步驟 2：定義共用介面
-   **生成檔案**: `src/multimodal-live-types.ts`
-   **說明**: 定義 WebSocket 通訊協定所需的 Type 介面。
    -   `MultimodalLiveAPIClientConnection`: 定義連線相關的型別。
    -   `ServerContent`, `ToolCall`: 定義從伺服器接收的訊息結構。
    -   **目的**: 讓後續開發的所有檔案都能引用統一的型別定義，避免資料結構混亂。

---

## 第三階段：建構底層工具庫 (Utilities)

這一階段我們建立不依賴 React 的純 TypeScript 類別，負責處理瀏覽器底層 API (Audio/WebSocket)。

### 步驟 3：實作音訊處理模組
-   **生成檔案**:
    -   `src/utils/audio-recorder.ts`: 封裝 `MediaRecorder` API，負責擷取麥克風音訊並轉換為適合傳輸的 Base64 格式。
    -   `src/utils/audio-streamer.ts`: 管理 `AudioContext`，負責將從 WebSocket 收到的 PCM 音訊數據排入佇列並播放。
    -   `src/utils/worklets/audio-processing.ts`: 定義 Audio Worklet，用於高效能的音訊處理。

### 步驟 4：實作 WebSocket 通訊核心
-   **生成檔案**: `src/utils/multimodal-live-client.ts`
-   **說明**: 這是本專案的**核心引擎**。
    -   繼承自 `EventEmitter`，實作觀察者模式。
    -   管理 WebSocket 的 `connect`, `disconnect`, `send` 方法。
    -   解析伺服器訊息 (`turnComplete`, `audio`, `content`) 並觸發對應事件。
    -   **目的**: 將複雜的 WebSocket 狀態機封裝在此，讓 UI 層只需呼叫簡單的 API。

---

## 第四階段：開發 React Hooks 與 Context (Logic Layer)

現在我們將底層工具庫與 React 的生命週期結合。

### 步驟 5：封裝功能 Hooks
-   **生成檔案**:
    -   `src/hooks/use-live-api.ts`: 初始化 `MultimodalLiveClient` 與 `AudioStreamer`，並將 Client 的事件 (`open`, `close`, `audio`) 綁定到 React state。
    -   `src/hooks/use-webcam.ts`: 封裝 `navigator.mediaDevices.getUserMedia`，提供視訊串流 (`MediaStream`) 給 UI 顯示。
    -   `src/hooks/use-screen-capture.ts`: 處理螢幕分享的邏輯。

### 步驟 6：建立全域狀態 Context
-   **生成檔案**: `src/contexts/LiveAPIContext.tsx`
-   **說明**: 建立 `LiveAPIContext` 與 `LiveAPIProvider`。
    -   **目的**: 將 `useLiveAPI` 產生的 `client` 實例、`connected` 狀態、`volume` 音量資訊，透過 Context API 注入到元件樹中。這樣深層的子元件就不需要透過層層 Props 傳遞也能存取 Client。

---

## 第五階段：建構 UI 元件 (Component Layer)

有了邏輯層，我們開始製作使用者看得到的介面元件。

### 步驟 7：開發視覺化元件
-   **生成檔案**: `src/components/audio-pulse/AudioPulse.tsx`
-   **說明**: 接收音量 (`volume`) props，使用 CSS 動畫繪製出動態的聲波圖形，提供視覺回饋。

### 步驟 8：開發日誌元件
-   **生成檔案**: `src/components/logger/Logger.tsx`
-   **說明**: 訂閱 Client 的訊息事件，將 JSON 格式的溝通紀錄渲染在畫面上，方便開發者除錯。

### 步驟 9：開發側邊控制面板
-   **生成檔案**: `src/components/side-panel/SidePanel.tsx`
-   **說明**: 這是主要的使用者互動介面。
    -   使用 `useLiveAPIContext()` 取得 Client。
    -   包含「Connect/Disconnect」按鈕。
    -   包含「麥克風/攝影機」開關控制。
    -   整合 `Logger` 與文字輸入框。

---

## 第六階段：應用程式組裝 (App Assembly)

最後，我們將所有積木組裝起來。

### 步驟 10：整合主頁面
-   **生成檔案**: `src/App.tsx`
-   **說明**:
    1.  使用 `LiveAPIProvider` 包覆最外層，確保 Context 生效。
    2.  佈局 `<div className="video-container">` 放置 `<video>` 元素，並將 `useWebcam` 的串流綁定至此。
    3.  放置 `<SidePanel>` 於側邊。
    4.  引用 `App.scss` 處理整體版面配置 (Flex/Grid)。

### 步驟 11：掛載應用程式
-   **生成檔案**: `src/index.tsx`
-   **說明**: 將 `<App />` 掛載到 HTML 的 `root` 節點，啟動 React 應用程式。

---

## 總結 (Summary)

透過上述流程，我們完成了一個功能完整的即時多模態 AI 前端：

1.  **Types** 定義了通訊標準。
2.  **Utils** 處理了底層 I/O。
3.  **Hooks/Context** 連接了 React 狀態。
4.  **Components** 呈現了視覺介面。
5.  **App** 完成了最終組裝。

依循此架構進行開發，能確保程式碼的高內聚與低耦合，便於未來的維護與擴充。
