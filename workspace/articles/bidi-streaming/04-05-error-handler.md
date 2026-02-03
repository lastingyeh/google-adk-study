歡迎來到這份深度技術實戰筆記。我是你們的資深技術導師。

在 **ADK 雙向串流 (Bidi-streaming)** 的開發過程中，處理「開心路徑（Happy Path）」只是基礎，真正的資深開發者是在**下游（Downstream）事件處理**的脈絡下，如何精準地應對安全攔截（Safety）、速率限制（Rate Limit）與連線逾時（Timeout）。這不僅關乎系統的穩定性，更直接影響使用者的信任感。

---

### 📌 ADK 下游錯誤處理學習地圖

1.  **錯誤事件模型**：解構 `error_code` 與 `finish_reason`。
2.  **核心決策矩陣**：何時該 `break` 終止，何時該 `continue` 重試？
3.  **三大實戰場景**：
    *   安全原則（Safety）與內容過濾。
    *   暫時性網路抖動與逾時處理。
    *   資源枯竭（Rate Limit）與配額管理。
4.  **連線生命週期管理**：會話恢復（Session Resumption）如何解決 10 分鐘超時。
5.  **最後的防線**：`finally` 區塊與資源釋放。

---

### 一、 錯誤事件解碼：當模型「說不」的時候

在下游處理中，錯誤並非總是透過 Python 異常（Exception）拋出，更多時候是以 **錯誤事件（Error Events）** 的形式出現在 `run_live()` 的非同步產生器中。

**這代表什麼？**
當模型停止產生，可能是因為完成任務，也可能是因為觸發了安全過濾器（Safety Filter）。我們必須監控 `Event` 中的兩個關鍵欄位：
*   **`error_code` / `error_message`**：提供失敗的診斷資訊。
*   **`finish_reason`**：識別模型停止的原因，例如 `SAFETY`（觸發安全原則）或 `MAX_TOKENS`（達到長度限制）。

---

### 二、 場景驅動教學：錯誤處理的實戰對話

身為導師，我將透過三個實際開發場景，帶領大家掌握應對邏輯。

#### 💡 場景一：觸發內容安全原則 (Safety Violation)
**提問：** 「如果使用者問了不恰當的問題，導致模型回應到一半突然中斷，我該如何處理？」
**解析：** 關鍵在於判斷模型是否還能「有意義地繼續」。
*   **技術行為**：此時會收到 `error_code="SAFETY"` 或 `finish_reason="SAFETY"`。
*   **導師建議**：**請直接使用 `break`**。因為模型已經徹底終止該回應，繼續等待只會浪費資源。
*   **使用者體驗**：請優雅地通知使用者：「內容違反安全原則，無法繼續生成」。

#### 💡 場景二：暫時性網路抖動或逾時 (Timeout)
**提問：** 「在語音對話中，如果網路發生 0.5 秒的閃斷（`UNAVAILABLE`），我該立刻關閉連線嗎？」
**解析：** 絕對不要。
*   **關鍵在於**：這屬於暫時性錯誤。連線可能會自動恢復，模型可能繼續串流逐字稿。
*   **導師建議**：**請使用 `continue`**。配合指數退避（Exponential Backoff）重試機制，直到確認無法修復為止。

#### 💡 場景三：配額耗盡 (Rate Limit / Resource Exhausted)
**提問：** 「當我收到 `RESOURCE_EXHAUSTED` 錯誤時，代表我被封鎖了嗎？」
**解析：** 這代表你達到了 API 的速率限制或並行會話配額。
*   **決策路徑**：這通常是暫時的。你可以先嘗試 `continue` 帶重試邏輯；但若多次失敗，則需 `break` 並引導使用者稍後再試。

---

### 三、 邏輯具象化：錯誤處理決策矩陣

根據來源資料，我為大家整理了這份生產級的應對表：

| 錯誤類型 (Error Code)               | 建議動作                | 核心原因                     |
| :---------------------------------- | :---------------------- | :--------------------------- |
| **SAFETY / PROHIBITED_CONTENT**     | **`break`**             | 模型已終止回應，且不應重試   |
| **MAX_TOKENS**                      | **`break`**             | 模型已達到輸出上限，完成產生 |
| **UNAVAILABLE / DEADLINE_EXCEEDED** | **`continue`**          | 暫時性網路問題，連線可能恢復 |
| **RESOURCE_EXHAUSTED (速率限制)**   | **`continue` (帶重試)** | 等待配額釋放後可能恢復       |
| **CANCELLED**                       | **`break`**             | 用戶端主動取消，需清理資源   |

---

### 四、 代碼即真理：生產級錯誤處理模版

以下是來源資料中具備實戰價值的錯誤處理邏輯註解。請特別注意 `try-except-finally` 的結構：

```python
# [導師點評]：在 Phase 3 的下游任務中，我們必須對 Event 進行防禦性檢查
async for event in runner.run_live(...):
    # 1. 優先檢查錯誤代碼，避免處理無效內容
    if event.error_code:
        if event.error_code in ["SAFETY", "MAX_TOKENS"]:
            logger.warning(f"終端錯誤: {event.error_message}")
            break # 模型已停止回應，退出循環

        elif event.error_code == "RESOURCE_EXHAUSTED":
            logger.info("達到速率限制，嘗試等待...")
            await asyncio.sleep(2)
            continue # 暫時性問題，嘗試繼續

# [關鍵實作]：並行任務的異常擷取與資源清理
try:
    await asyncio.gather(upstream_task(), downstream_task())
except WebSocketDisconnect:
    logger.debug("用戶端正常斷開連線")
except Exception as e:
    # 包含 session_id 以便日後除錯
    logger.error(f"工作階段 {session_id} 發生意外錯誤: {e}", exc_info=True)
finally:
    # [核心原則]：Phase 4 - 終止會話
    # 務必呼叫 close()，否則會產生「殭屍會話」消耗配額
    live_request_queue.close()
```

---

### 五、 知識延伸：解決「10 分鐘斷線」的技術深度

在處理逾時（Timeout）時，我們必須理解 Live API 的原生限制。

**關鍵在於：**
1.  **連線持續時間限制**：Gemini Live API 的 WebSocket 連線通常在約 10 分鐘後會自動終止。
2.  **會話恢復 (Session Resumption)**：這代表什麼？這是一項能跨連線遷移會話的功能。
3.  **ADK 的自動化**：只要在 `RunConfig` 中啟動 `session_resumption=types.SessionResumptionConfig()`，ADK 就會自動快取恢復句柄（Resumption Handle），在斷線時「透明地」重新連線，使用者完全不會察覺。

---

### 💡 實戰導向總結

在下游事件處理的脈絡下，錯誤處理不只是抓取 Exception，而是對模型狀態的精準判斷。
*   **安全性 (Safety)** 是硬限制，遇到就 `break`。
*   **逾時與暫時錯誤** 應透過「會話恢復」與 `continue` 來優雅地自癒。
*   **配額 (Rate Limit)** 需要透過「會話池」或增加配額請求來提前規劃。
*   **最後的禮儀**：無論發生什麼錯誤，`finally` 區塊中的 `live_request_queue.close()` 是你唯一的資源守護神。

#ADKErrorHandling #BidiStreaming #SafetyPolicy #SessionResumption #RateLimitManagement

**更多資源**：
*   關於 `finish_reason` 的完整清單，請參考 Google AI for Developers 官方文件。
*   關於配額增加流程，請至 Google Cloud 控制台的「配額」頁面搜尋 `Bidi generate content concurrent requests`。