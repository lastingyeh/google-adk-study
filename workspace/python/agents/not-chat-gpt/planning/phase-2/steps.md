# Phase 2: 工具整合與 UI

## Week 3: 工具整合

### 步驟 1: Google Search Grounding
- [ ] 建立 `tools/google_search.py`
- [ ] 整合 Google Search Grounding API
- [ ] 實作 `groundingChunks` 提取與顯示
- [ ] 測試搜尋功能與引用來源

### 步驟 2: Code Execution
- [ ] 建立 `tools/code_executor.py`
- [ ] 整合 BuiltInCodeExecutor
- [ ] 實作程式碼執行與結果顯示
- [ ] 測試程式碼執行安全性

### 步驟 3: File Upload/Download
- [ ] 建立 `tools/file_handler.py`
- [ ] 實作 Artifact Tool
- [ ] 實作檔案上傳/下載功能
- [ ] 測試檔案處理流程

### 步驟 4: 工具整合測試
- [ ] 建立 `test_tools.py`
- [ ] 測試所有工具的整合
- [ ] 測試工具選擇準確率
- [ ] 調優工具使用策略

---

## Week 4: Web UI 建構

### 步驟 5: React Vite 專案設定
- [ ] 建立 `frontend/` 目錄
- [ ] 初始化 React Vite 專案
- [ ] 安裝必要套件（AG-UI, Markdown, Code Highlight）
- [ ] 設定 Vite 開發環境

### 步驟 6: AG-UI Protocol 整合
- [ ] 實作 API 服務層 (`services/api.ts`)
- [ ] 整合 AG-UI Protocol
- [ ] 測試前後端通訊

### 步驟 7: 對話介面實作
- [ ] 建立 `ConversationView.tsx`
- [ ] 建立 `MessageList.tsx`
- [ ] 建立 `InputBox.tsx`
- [ ] 實作 Markdown 渲染與程式碼高亮

### 步驟 8: SSE 串流顯示
- [ ] 實作 EventSource API
- [ ] 實作串流訊息顯示
- [ ] 實作載入與錯誤狀態處理

### 步驟 9: 模式切換控制
- [ ] 建立 `ModeSelector.tsx`
- [ ] 實作思考模式 / 標準模式切換
- [ ] 實作模式狀態指示器（💭 / 💬）
- [ ] 測試模式切換功能

### 步驟 10: 對話管理功能
- [ ] 實作新增對話功能
- [ ] 實作對話列表顯示
- [ ] 實作對話載入與刪除
- [ ] 實作對話歷史瀏覽

### 步驟 11: 文檔管理面板
- [ ] 建立 `DocumentPanel.tsx`
- [ ] 實作文檔上傳介面
- [ ] 實作文檔列表顯示
- [ ] 實作文檔刪除功能

### 步驟 12: 引用來源顯示
- [ ] 建立 `CitationBadge.tsx`
- [ ] 實作引用來源標籤顯示
- [ ] 實作引用來源點擊查看
- [ ] 美化引用樣式

### 步驟 13: UI 測試與優化
- [ ] 測試所有 UI 功能
- [ ] 優化使用者體驗
- [ ] 響應式設計調整
- [ ] 效能優化

---

## Phase 2 檢查點

- [ ] 所有工具整合完成
- [ ] Web UI 功能完整
- [ ] 串流回應順暢（> 95%）
- [ ] 工具選擇準確率 > 85%
- [ ] UI/UX 符合預期
