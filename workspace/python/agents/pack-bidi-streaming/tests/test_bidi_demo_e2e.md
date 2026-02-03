# ADK 雙向串流 (Bidi-streaming) 範例應用程式端到端 (E2E) 測試程序

本文件提供使用 Chrome DevTools MCP 伺服器測試 ADK 雙向串流範例應用程式的逐步說明。

**注意：** 所有測試產出物（伺服器日誌、螢幕截圖、測試報告）都會保存在帶有時間戳記的目錄中，以便後續審查與分析。

> **重點註解：**
> 1. 本測試主要針對「雙向串流」特性，這意味著客戶端與伺服器端可以同時發送與接收數據。
> 2. 使用 Chrome DevTools MCP 可以自動化模擬用戶在瀏覽器上的操作。

## 1. 環境設定

### 將範例代碼複製到臨時目錄

為了測試目的，我們將範例代碼複製到一個帶有時間戳記的臨時目錄，並在其中運行。

```bash
# 建立唯一的帶時間戳記目錄
export TEST_DIR="/tmp/demo-$(date +%Y%m%d-%H%M%S)"
mkdir -p $TEST_DIR
cp -r src/demo/* $TEST_DIR
cd $TEST_DIR
```

### 運行範例應用程式

- 按照 `$TEST_DIR/README.md` 中的說明運行應用程式。
- 監控 `$TEST_DIR/app/server.log` 以確認伺服器已成功啟動。

> **重點註解：** 在啟動後務必確認 `server.log` 中沒有出現 `Error` 或 `Address already in use` 等錯誤訊息。

## 2. 使用 Chrome DevTools MCP 進行端到端 UI 測試

### 步驟 1：導航至應用程式

```yaml
mcp__chrome-devtools__navigate_page
url: http://localhost:8000
```

**預期結果：** 頁面成功加載。

### 步驟 2：獲取快照以驗證 UI

```yaml
mcp__chrome-devtools__take_snapshot
```

**預期元素：**

- 狀態指示器（應顯示 "● Disconnected"）
- 訊息與事件計數器（應顯示 "Messages: 0 | Events: 0"）
- API 後端單選按鈕 (Gemini API / Vertex AI)
- 憑證輸入欄位
- 模型下拉選單
- WebSocket URL 欄位（預填為 `ws://localhost:8000/ws`）
- SSE URL 欄位（預填為 `http://localhost:8000/sse`）
- 訊息輸入欄位
- 連接/斷開按鈕 (Connect/Disconnect)
- 發送/關閉按鈕 (Send/Close)（初始狀態應為禁用）
- 執行設定 (RunConfig) 核取方塊
- 日誌區域

> **重點註解：** 此步驟是為了確保所有 UI 組件都已正確渲染，避免後續操作因找不到元素而失敗。

### 步驟 3：在 UI 中配置憑證

從 `tests/e2e/.env` 複製適當的值到 UI。

**Gemini API 設定：**

```yaml
mcp__chrome-devtools__fill
uid: <api-key-field-uid>
value: your_api_key_here
```

**Vertex AI 設定：**

```yaml
mcp__chrome-devtools__click
uid: <vertex-radio-button-uid>

mcp__chrome-devtools__fill
uid: <gcp-project-field-uid>
value: your_project_id

mcp__chrome-devtools__fill
uid: <gcp-location-field-uid>
value: us-central1
```

### 步驟 4：連接 WebSocket

```yaml
mcp__chrome-devtools__click
uid: <connect-button-uid>
```

**預期結果：**

- 狀態變更為 "● Connected (WebSocket)"
- 日誌顯示：`[INFO] WebSocket connection established`
- "send_content()" 與 "close()" 按鈕變為可用狀態。

### 步驟 5：發送測試訊息

```yaml
mcp__chrome-devtools__fill
uid: <message-input-uid>
value: Hello! Can you explain what ADK streaming is?

mcp__chrome-devtools__click
uid: <send-button-uid>
```

**日誌預期輸出：**

1. `[SENT] Hello! Can you explain what ADK streaming is?`
2. 訊息計數器 (Messages counter) 增加至 1。
3. **工具執行事件** (JSON 對象)：
   - `executableCode` 對象顯示呼叫 Google Search 及其查詢內容。
   - `codeExecutionResult` 對象顯示結果為 "OUTCOME_OK"。
4. 多個 `[PARTIAL]` 事件，即時顯示串流文本片段。
5. 事件計數器 (Events counter) 增加（完整回應通常包含 10-15+ 個事件）。
6. `[COMPLETE]` 事件，包含完整回應。
7. `[TURN COMPLETE]` 事件，標記回應結束。

> **重點註解：**
> 1. 串流測試的關鍵在於觀察 `[PARTIAL]` 事件是否持續產生，這代表數據是分段即時傳輸的。
> 2. 在進行下一階段（截圖）前，請等待 2-3 秒以確保串流回應完全結束。

### 步驟 6：拍攝結果截圖

```yaml
mcp__chrome-devtools__take_screenshot
filePath: $TEST_DIR/streaming_results.png
```

**預期結果：** 截圖應顯示包含 partial 和 complete 事件的串流對話內容。

截圖將保存於 `$TEST_DIR/streaming_results.png`。

### 步驟 7：測試正常關閉 (Graceful close)

```yaml
mcp__chrome-devtools__click
uid: <close-button-uid>
```

**預期結果：**

- 日誌顯示：`[INFO] Sending graceful close signal via WebSocket`
- 連線正常關閉。
- 注意：UI 中的連線狀態可能仍顯示 "Connected"；請檢查伺服器日誌以確認連線已完全斷開。

### 步驟 8：檢查主控台 (Console) 錯誤

```yaml
mcp__chrome-devtools__list_console_messages
```

**預期結果：** 沒有嚴重的 JavaScript 錯誤。

- 可接受的警告：密碼欄位警告、favicon 的 404 錯誤。
- 任何與應用程式邏輯相關的錯誤都應進行調查。

### 步驟 9：檢查伺服器日誌錯誤

```bash
cat $TEST_DIR/app/server.log | grep -i error
```

**預期結果：** 無輸出（若無錯誤，grep 應不回傳任何內容）。

- 若出現錯誤，請審查其是否為非關鍵錯誤（例如棄用警告）。

## 3. 測試完成

### 3.1 停止伺服器

```bash
# 尋找並終止伺服器進程
pkill -f "uvicorn app.main"
```

**預期輸出 (來自 run.sh 清理腳本)：**

```text
Stopping server (PID: <process-id>)...
Server stopped
```

### 3.2 保存測試報告

完成所有測試步驟後，生成一份記錄結果的詳細測試報告。

測試報告將保存於：`$TEST_DIR/test_report.md`

**保存在 `$TEST_DIR` 中的測試產出物：**

- `app/server.log` - 測試運行的伺服器日誌
- `test_report.md` - 詳細測試報告
- 螢幕截圖（如果保存至此目錄）
- 其他測試相關文件

### 3.3 故障排除

#### 伺服器無法啟動
- 檢查連接埠 8000 是否已被佔用：`lsof -i :8000`
- 查看 server.log 中的啟動錯誤：`cat $TEST_DIR/app/server.log`
- 確保虛擬環境已正確設定。

#### WebSocket 連線失敗
- 驗證伺服器是否正在運行：`curl http://localhost:8000/healthz`
- 檢查瀏覽器主控台是否有連線錯誤。
- 確保憑證已正確配置。
- 查看伺服器日誌：`tail -f $TEST_DIR/app/server.log`

#### 未出現串流事件
- 驗證 API 金鑰是否有效。
- 檢查 server.log 中的 API 錯誤：`cat $TEST_DIR/app/server.log | grep -i error`
- 確保選取的模型支援 Live API（名稱中包含 "live" 的模型）。

#### 瀏覽器頁面意外關閉
- 使用 `mcp__chrome-devtools__new_page` 開啟新頁面。
- 重新導航至 `http://localhost:8000`。
- 從適當的步驟繼續測試。

## 4. 測試報告內容

生成一份綜合測試報告並保存至 `$TEST_DIR/test_report.md`。

測試報告應包含：

- **測試摘要**：總體狀態（通過/失敗）、日期、持續時間。
- **環境詳情**：測試目錄位置、伺服器配置。
- **逐步結果**：每個測試步驟的實際結果與預期結果對比。
- **串流指標**：發送的訊息數、接收的事件數、工具調用情況。
- **錯誤分析**：主控台錯誤、伺服器日誌錯誤（如有）。
- **螢幕截圖**：所擷取截圖的參考路徑。
- **觀察結果**：值得注意的行為、工具執行情況、串流效能。
- **結論**：總體評估及發現的任何問題。

**測試產出物位置**：所有產出物都保存在 `$TEST_DIR` 中供未來參考。

**查看測試結果的範例命令：**

```bash
echo "測試目錄: $TEST_DIR"
ls -lh $TEST_DIR/test_report.md
cat $TEST_DIR/test_report.md
```
