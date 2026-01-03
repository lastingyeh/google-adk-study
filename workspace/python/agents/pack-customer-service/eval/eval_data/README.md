# 評估資料夾 (eval_data) 說明

此資料夾包含用於測試客戶服務 Agent 的 JSON 評估檔案。

### 檔案清單：
1. **simple.test.json**: 基本對話測試。
   - 包含簡單的問候語。
   - 包含基礎的工具調用驗證（例如：`access_cart_information`）。
2. **full_conversation.test.json**: 完整情境對話測試。
   - 用於驗證 Agent 在多輪對話中的表現。
3. **test_config.json**: 評估器的設定檔。

### JSON 結構重點：
- `query`: 使用者輸入的內容。
- `expected_tool_use`: 預期 Agent 應該使用的工具及其參數。這是評估 Agent 邏輯正確性的核心。
- `reference`: 預期的回覆內容（或其參考方向）。
