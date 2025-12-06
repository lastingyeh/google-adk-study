# 商務代理人測試指南 (Commerce Agent Testing Guide)

## ✅ 所有修正已完成

以下問題已獲得解決：

1. ✅ **TypedDict 回傳型別**：已修正 - 現在於簽名中使用 `Dict[str, Any]` 並在內部使用 TypedDict 提示
2. ✅ **接地回調 (Grounding Callback)**：實作了基於函式的回調 (而非基於類別)
3. ✅ **Agent.after_model 參數**：已移除 - 回調現在位於 Runner 中，而非 Agent
4. ✅ **提示重寫**：完整的禮賓人員 (Concierge) 角色，具備明確的偏好工作流程
5. ✅ **套件安裝**：`pip install -e .` 已成功完成
6. ✅ **伺服器啟動**：ADK 網頁伺服器執行無錯誤

## 🧪 測試說明

### 步驟 1：啟動伺服器

伺服器已經在運作中！如果沒有，請執行：

```bash
cd /Users/raphaelmansuy/Github/03-working/adk_training/tutorial_implementation/commerce_agent_e2e
make dev
```

### 步驟 2：打開網頁介面

打開您的瀏覽器並訪問：**http://localhost:8000**

### 步驟 3：選擇正確的代理人

⚠️ **關鍵**：在頁面頂部的代理人下拉選單中，請選擇 **`commerce_agent`** (不是 `context_engineering` 或其他代理人)

### 步驟 4：測試禮賓人員 (Concierge) 工作流程

#### 測試案例 1：基本偏好儲存

**使用者訊息 1：**
```
I want running shoes
(我想要慢跑鞋)
```

**預期代理人行為：**
- ✅ 代理人首先呼叫 `get_preferences` 工具
- ✅ 代理人詢問："What's your budget?" (你的預算多少？) 和 "Are you a beginner or experienced?" (你是初學者還是有經驗者？)
- ✅ 溫暖、友善的語氣

**使用者訊息 2：**
```
Under 150 euros, I'm a beginner
(150 歐元以下，我是初學者)
```

**預期代理人行為：**
- ✅ 代理人呼叫 `save_preferences` 工具，參數為：sport="running", budget=150, experience="beginner"
- ✅ 代理人確認："✓ I've saved your preferences..." (✓ 我已儲存您的偏好...)
- ✅ 代理人呼叫 `search_products` 工具以尋找慢跑鞋
- ✅ 代理人解釋「為什麼」這些產品適合初學者
- ✅ 帶有專家指導的個人化推薦

#### 測試案例 2：既有偏好

**使用者訊息 (新會話)：**
```
Find me some cycling gear
(幫我找些騎行裝備)
```

**預期代理人行為：**
- ✅ 代理人呼叫 `get_preferences` 工具
- ✅ 如果先前會話的偏好存在，代理人會引用它們："I see you prefer products under €150..." (我看到您偏好 150 歐元以下的產品...)
- ✅ 代理人詢問這些偏好是否也適用於騎行
- ✅ 如果使用者提供新資訊，則更新偏好

#### 測試案例 3：專家使用者

**使用者訊息：**
```
I'm looking for trail running shoes, budget around 180, I've been running for 5 years
(我在找越野跑鞋，預算約 180，我已經跑了 5 年)
```

**預期代理人行為：**
- ✅ 代理人儲存：sport="trail running", budget=180, experience="experienced"
- ✅ 代理人推薦進階功能："As an experienced runner, you'll appreciate..." (身為一位經驗豐富的跑者，您會欣賞...)
- ✅ 關於緩衝、抓地力、耐用性的技術解釋

### 步驟 5：驗證接地元數據 (Grounding Metadata) (可選)

接地回調會從 Google Search 結果中提取元數據。要查看它：

1. 查看執行 `make dev` 的 **終端機輸出 (terminal output)**
2. 在代理人呼叫 `search_products` 之後，您應該會看到類似以下的日誌：

```
Grounding Sources:
  • decathlon.fr (confidence: 0.85)
  • nike.com (confidence: 0.90)
  • amazon.fr (confidence: 0.75)
```

**注意**：此元數據目前僅記錄到伺服器主控台。尚未在 UI 中顯示 (這需要自定義前端整合)。

### 步驟 6：驗證狀態持久性

要測試偏好是否在不同會話間儲存：

1. 完成上述測試案例 1 (儲存偏好)
2. 重新整理瀏覽器頁面 (建立新會話)
3. 發送訊息："Show me tennis rackets" (給我看網球拍)
4. 驗證代理人使用 `get_preferences` 檢索先前的偏好

### 步驟 7：檢查錯誤

監控終端機是否出現：
- ❌ `ValidationError` → 不應出現 (已修正)
- ❌ `Extra inputs are not permitted` → 不應出現 (已修正)
- ✅ 正常的 INFO 日誌 → 預期中
- ✅ 實驗性警告 (Experimental warnings) → 預期中 (可安全忽略)

## 🐛 故障排除

### 問題：代理人下拉選單顯示錯誤的代理人

**解決方案**：確保您位於正確的目錄且套件已安裝：

```bash
cd /Users/raphaelmansuy/Github/03-working/adk_training/tutorial_implementation/commerce_agent_e2e
pip install -e .
make dev
```

### 問題："No root_agent found for 'commerce_agent'"

**解決方案**：清除 Python 快取並重新安裝：

```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
pip install -e .
```

### 問題：代理人未儲存偏好

**檢查**：
1. 驗證提示 (prompt) 是否有明確的 "ALWAYS call save_preferences" 指令
2. 檢查終端機日誌中的工具呼叫
3. 確保 `.env` 檔案具有 `GOOGLE_API_KEY` 或 Google Cloud 憑證

### 問題：接地元數據未顯示

**預期行為**：接地元數據出現在 **伺服器日誌** (終端機) 中，而非 UI 中。這是設計使然。要查看它：

```bash
# 測試時觀察終端機輸出
# 在 search_products 呼叫後尋找 "Grounding Sources:"
```

## 📊 成功標準

如果符合以下條件，則您的測試成功：

- ✅ 代理人啟動無錯誤
- ✅ 代理人在對話開始時呼叫 `get_preferences`
- ✅ 當使用者提供資訊時，代理人呼叫 `save_preferences`
- ✅ 代理人用友善的訊息確認偏好儲存
- ✅ 代理人使用 Google Search 搜尋產品
- ✅ 代理人解釋產品推薦及其理由
- ✅ 代理人使用溫暖、專家的禮賓人員語氣
- ✅ 偏好在瀏覽器重新整理後仍然存在
- ✅ 接地元數據出現在伺服器日誌中

## 🔍 進階測試 (可選)

### 使用 Runner 和 Callback 進行測試

如果您想以程式設計方式測試回調：

```python
from commerce_agent import root_agent, create_grounding_callback
from google.adk.runners import Runner

# 建立帶有接地回調的 runner
runner = Runner(
    agent=root_agent,
    after_model_callbacks=[create_grounding_callback(verbose=True)]
)

# 執行測試對話
response = runner.run("Find me running shoes under 150 for beginners")
print(response)
```

### 執行測試

```bash
cd /Users/raphaelmansuy/Github/03-working/adk_training/tutorial_implementation/commerce_agent_e2e
make test
```

預期：**14/14 tests passing**

## 📝 已修正 vs 未實作

### ✅ 本次會話已修正

- TypedDict 與 ADK 函式呼叫的相容性
- 基於函式的接地回調 (非基於類別)
- 代理人設定 (移除了無效的 `after_model` 參數)
- 重寫提示以符合禮賓人員行為
- 指令中明確的偏好工作流程
- 套件安裝與發現

### ⚠️ 未實作 (超出範圍)

- **SQLite 資料庫**：使用 ADK 狀態代替 (較簡單，足以應付偏好)
- **UI 接地顯示**：僅記錄回調至主控台 (UI 整合需要自定義前端)
- **產品目錄快取**：目前規模不需要
- **分析儀表板**：未來增強功能

### 🎯 已知限制

1. **接地元數據位置**：出現在伺服器日誌中，而非 UI (需要 CopilotKit 或自定義 React 元件)
2. **狀態持久性**：使用 ADK 狀態，而非 SQLite (權衡：簡單性 vs 查詢能力)
3. **Agent 中的 Callback**：必須使用 Runner 進行回調 (ADK 設計決策)

## 📚 下一步

測試後，您可以：

1. **自定義提示**：編輯 `commerce_agent/prompt.py` 以更改代理人個性
2. **新增工具**：在 `commerce_agent/tools/` 中建立新工具
3. **整合 UI**：使用 CopilotKit 建置自定義前端並顯示接地來源
4. **新增資料庫**：從 ADK 狀態切換到 SQLite 以進行複雜查詢 (見教學範例)
5. **部署**：使用 `adk deploy cloud_run` 進行生產環境部署 (見教學 32-34)

## 🤝 支援

如果您遇到問題：

1. 檢查終端機日誌以獲取詳細錯誤訊息
2. 驗證 `.env` 檔案具有正確的 API 金鑰
3. 執行 `make test` 以檢查設定問題
4. 檢閱 `README.md` 以了解架構細節
5. 查看 `copilot-instructions.md` 以了解 ADK 模式

---
# 重點摘要

- **核心概念**：
    - **測試流程**：涵蓋從伺服器啟動到 UI 互動的完整步驟。
    - **禮賓人員角色 (Concierge Persona)**：驗證代理人是否表現出預期的溫暖、專業語氣並主動管理偏好。
    - **接地驗證**：確認搜尋來源元數據正確提取並記錄。

- **關鍵技術**：
    - **ADK Runner**：用於執行代理人並附加回調。
    - **Grounding Callback**：攔截並記錄搜尋來源資訊。
    - **TypedDict**：確保工具輸入輸出的型別正確性。

- **重要結論**：
    - 測試不僅要驗證功能 (如搜尋)，還要驗證行為 (如語氣、確認偏好)。
    - 接地資訊目前僅在後端日誌可見，這是驗證搜尋真實性的關鍵。
    - 狀態持久性測試需要跨會話 (重新整理頁面) 進行驗證。

- **行動項目**：
    - 按照指南步驟 1-7 執行手動測試。
    - 觀察終端機輸出以驗證接地元數據。
    - 如果遇到錯誤，參考故障排除章節。
