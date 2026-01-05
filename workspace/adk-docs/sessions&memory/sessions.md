# 對話上下文簡介：Session、State 與 Memory
> 更新日期：2026 年 1 月 5 日

有意義的多輪對話需要代理（Agents）能夠理解上下文。就像人類一樣，它們需要記住對話歷史：了解已經說過和做過的事情，以維持連貫性並避免重複。Agent Development Kit (ADK) 透過 `Session`、`State` 和 `Memory` 提供結構化的方式來管理這些上下文。

> [!IMPORTANT]
> **重點說明**：ADK 區分了「當前互動」（Session/State）與「長期知識」（Memory），這讓代理能同時具備短期記憶與長期知識庫的能力。

## 核心概念

將您與代理的不同對話實例想像成不同的**對話執行緒 (Conversation Threads)**，並可能調用**長期知識 (Long-term Knowledge)**。

1.  **`Session`**：當前對話執行緒
    *   代表使用者與代理系統之間*單次、持續的互動*。
    *   包含該特定互動期間代理所採取的訊息和動作的時間序列（稱為 `Events`）。
    *   `Session` 還可以持有僅在*此對話期間*相關的臨時數據 (`State`)。

2.  **`State` (`session.state`)**：當前對話內的數據
    *   存儲在特定 `Session` 內的數據。
    *   用於管理*僅*與*當前活動*對話執行緒相關的信息（例如：*此次聊天中*購物車內的物品、*此會話中*提到的使用者偏好）。

3.  **`Memory`**：可搜索的跨會話信息
    *   代表可能跨越*多個過去會話*的信息存儲，或包含外部數據源。
    *   它充當一個知識庫，代理可以*搜索*該知識庫以召回超出立即對話範圍的信息或上下文。

## 管理上下文：服務 (Services)

ADK 提供多種服務來管理這些概念：

1.  **`SessionService`**：管理不同的對話執行緒（`Session` 對象）
    *   處理生命週期：建立、檢索、更新（附加 `Events`、修改 `State`）和刪除單個 `Session`。

2.  **`MemoryService`**：管理長期知識庫 (`Memory`)
    *   處理將信息（通常來自已完成的 `Session`）攝取到長期存儲中。
    *   提供根據查詢搜索這些存儲知識的方法。

> [!TIP]
> **開發提示**：ADK 為這兩種服務都提供了**內存中 (In-memory) 實作**，專為**本地測試和快速開發**設計。請記住，當應用程式重啟時，所有存儲在內存中的數據都會丟失。對於生產環境，請選擇雲端或資料庫後端。

### 總結比較：

| 概念 | 焦點 | 管理服務 |
| :--- | :--- | :--- |
| **`Session` & `State`** | **當前互動** – 單次活動對話的歷史與數據。 | `SessionService` |
| **`Memory`** | **過去與外部信息** – 可跨對話搜索的封存內容。 | `MemoryService` |

## 下一步

在接下來的章節中，我們將深入探討每個組件：

*   **`Session`**：理解其結構與 `Events`。
*   **`State`**：如何有效地讀取、寫入和管理會話特定數據。
*   **`SessionService`**：為您的會話選擇正確的存儲後端。
*   **`MemoryService`**：探索存儲和檢索更廣泛上下文的選項。

理解這些概念是構建能夠進行複雜、有狀態且具備上下文感知能力代理的基礎。

---

## 參考資源 (實作參考)
- [Tutorial 08: State and Memory - Persistent Agent Context (狀態與記憶體 - 持久化代理上下文)](../../../workspace/notes/google-adk-training-hub/adk_training/08-state_memory.md)
- [端對端實作 01：具備對話持久性的生產級商務代理 (End-to-End Implementation 01: Production Commerce Agent with Session Persistence)](../../../workspace/notes/google-adk-training-hub/adk_training/35-commerce_agent_e2e.md)
- [TIL: 在 Google ADK 1.17 中註冊自定義對話服務 (Registering Custom Session Services in Google ADK 1.17)](../../../workspace/notes/google-adk-training-hub/blog/2025-10-23-til-custom-session-services.md)