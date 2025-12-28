# 策略問題解決器 - 教學 12 實作

此實作展示了使用 BuiltInPlanner、PlanReActPlanner 和自訂 BasePlanner 實作的**進階推理能力**，用於解決複雜的商業問題。

## 概述

策略問題解決器展示了三種不同的規劃方法：

- **BuiltInPlanner**：使用 Gemini 2.0+ 的原生思考能力，具有透明的推理過程
- **PlanReActPlanner**：實作結構化的 計劃 → 推理 → 行動 → 觀察 → 重新規劃 工作流程
- **StrategicPlanner**：用於特定領域商業策略分析的自訂 BasePlanner 子類別

## 功能特色

### 🤖 多重規劃策略

- 使用 BuiltInPlanner 進行透明思考
- 使用 PlanReActPlanner 進行結構化推理
- 使用自訂規劃器處理特定領域工作流程

### 🛠️ 商業分析工具

- **市場分析**：產業研究和趨勢識別
- **ROI 計算器**：財務預測和投資分析
- **風險評估**：商業風險評估和緩解策略
- **策略報告**：記錄並儲存策略建議

### 📊 完整測試

- 30+ 單元測試涵蓋所有功能
- 完整工作流程的整合測試
- 錯誤處理和邊界情況涵蓋

## 快速開始

### 1. 設定環境

```bash
# 複製並導航到實作目錄
cd tutorial_implementation/tutorial12

# 安裝相依套件
make setup

# 複製環境範本
cp strategic_solver/.env.example strategic_solver/.env

# 編輯 .env 並加入您的 Google AI API 金鑰
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 2. 執行開發伺服器

```bash
# 啟動 ADK 網頁介面
make dev

# 在瀏覽器開啟 http://localhost:8000
# 從代理下拉選單選擇 "strategic_solver"
```

### 3. 測試實作

```bash
# 執行完整測試套件
make test

# 查看可測試的範例查詢
make examples

# 執行示範範例
make demo
```

## 專案結構

```
strategic-solver/
├── strategic_solver/           # 代理實作
│   ├── __init__.py            # 套件標記
│   ├── agent.py               # 主代理，包含規劃器和工具
│   └── .env.example           # 環境配置範本
├── tests/                     # 完整測試套件
│   ├── __init__.py
│   ├── test_imports.py        # 匯入和結構測試
│   ├── test_tools.py          # 工具功能測試
│   ├── test_agents.py         # 代理和規劃器測試
│   └── test_integration.py    # 整合和工作流程測試
├── pyproject.toml             # 現代 Python 打包配置
├── requirements.txt           # 執行時相依套件
├── Makefile                  # 開發指令
└── README.md                 # 本檔案
```

## 代理變體，參考 [base_planner.py](./strategic_solver/agent.py)

### BuiltInPlanner 代理 (`builtin_planner_agent`)

- **目的**：展示透明的思考能力
- **特色**：向使用者顯示內部推理過程
- **使用情境**：教育應用程式、除錯、建立信任
- **配置**：`ThinkingConfig(include_thoughts=True)`

### PlanReActPlanner 代理 (`plan_react_agent`)

- **目的**：具有明確規劃階段的結構化問題解決
- **特色**：計劃 → 推理 → 行動 → 觀察 → 重新規劃 工作流程
- **使用情境**：需要系統化方法的複雜多步驟問題
- **配置**：標準 PlanReActPlanner，使用 XML 標籤

### StrategicPlanner 代理 (`strategic_planner_agent`)

- **目的**：特定領域的商業策略分析
- **特色**：自訂工作流程：分析 → 評估 → 策略 → 驗證
- **使用情境**：商業諮詢和策略規劃
- **配置**：自訂 BasePlanner 子類別

## 商業分析工具

### 市場分析工具

```python
result = analyze_market("healthcare", "North America", tool_context)
# 返回：growth_rate（成長率）、competition（競爭）、trends（趨勢）、
#       opportunities（機會）、threats（威脅）
```

### ROI 計算器工具

```python
result = calculate_roi(100000, 8.5, 5, tool_context)
# 返回：final_value（最終價值）、total_profit（總利潤）、
#       roi_percentage（ROI 百分比）、annual_breakdown（年度細分）
```

### 風險評估工具

```python
result = assess_risk(["competition", "regulatory_changes"], tool_context)
# 返回：risk_level（風險等級）、mitigation_suggestions（緩解建議）、
#       factor_scores（因素評分）
```

### 策略報告工具

```python
result = await save_strategy_report(problem, strategy, tool_context)
# 儲存帶時間戳記的格式化 markdown 報告
```

## 使用範例

### 基本策略分析

```
使用者："我們應該擴展到亞洲醫療保健市場嗎？"

代理回應：
[思考中]
這是一個複雜的策略決策，需要市場分析、
財務預測和風險評估...

市場分析：醫療保健領域年成長率 8.5%
財務預測：50 萬美元投資的 5 年 ROI 為 46.8%
風險評估：中等風險，需要法規緩解

建議：採用分階段方法進行...
```

### 結構化規劃範例

```
使用者："我們應該如何減輕網路安全風險？"

代理回應：
<PLANNING>
1. 評估當前風險態勢
2. 識別關鍵漏洞
3. 評估緩解策略
4. 建立實施時間表
</PLANNING>

<ACTION>
正在分析風險因素...
</ACTION>

<OBSERVATION>
已識別高風險因素：網路釣魚、資料外洩、內部威脅
</OBSERVATION>

<FINAL_ANSWER>
實施全面的網路安全框架：
1. 員工培訓計畫
2. 多因素驗證
3. 定期安全稽核
4. 事件應變計畫
</FINAL_ANSWER>
```

## 測試

### 執行所有測試

```bash
make test
```

### 測試涵蓋範圍

- **匯入測試**：模組載入和結構驗證
- **工具測試**：個別工具功能（25+ 測試案例）
- **代理測試**：規劃器配置和代理設定
- **整合測試**：完整工作流程測試

### 測試類別

#### 單元測試

- 工具輸入驗證和錯誤處理
- 計算準確性（ROI、風險評分）
- 資料結構正確性

#### 整合測試

- 多工具工作流程執行
- 錯誤傳播處理
- 規劃器比較和驗證

## 配置

### 環境變數

```bash
# 必要
GOOGLE_API_KEY=your_google_ai_api_key

# 選用
GOOGLE_GENAI_USE_VERTEXAI=0  # 設為 1 以使用 VertexAI
GOOGLE_CLOUD_PROJECT=your_project
GOOGLE_CLOUD_LOCATION=us-central1
```

### 模型配置

- **模型**：`gemini-2.0-flash`（支援思考能力）
- **溫度**：0.3-0.4（平衡策略分析）
- **最大 Token 數**：3000（足以進行詳細分析）

## 開發指令

```bash
# 設定和安裝
make setup          # 安裝相依套件並以開發模式安裝套件
make dev           # 啟動 ADK 網頁介面 (http://localhost:8000)

# 測試和範例
make test          # 執行完整測試套件（60+ 測試）
make examples      # 顯示可測試的範例查詢
make demo          # 執行自動化策略問題解決範例

# 程式碼品質
make lint          # 使用 flake8 檢查程式碼風格
make format        # 使用 black 格式化程式碼

# 清理
make clean         # 移除快取檔案和產出物
```

## 疑難排解

### 常見問題

#### "規劃器未顯示思考過程"

- 確保使用 Gemini 2.0+ 模型
- 檢查 BuiltInPlanner 的 `ThinkingConfig(include_thoughts=True)`
- 驗證 API 金鑰可存取啟用思考功能的模型

#### "PlanReAct 標籤未出現"

- 檢查 PlanReActPlanner 是否正確實例化
- 確保代理指示不會覆蓋規劃格式
- 嘗試稍微提高溫度以獲得更結構化的輸出

#### "工具執行失敗"

- 驗證工具函式是否正確匯入
- 檢查工具上下文是否正確傳遞
- 確保非同步工具已正確等待

#### "匯入錯誤"

- 執行 `make setup` 安裝相依套件
- 檢查 Python 路徑是否包含 strategic_solver 目錄
- 驗證所有必要套件是否已安裝

### 除錯模式

透過設定環境變數啟用詳細日誌記錄：

```bash
export ADK_DEBUG=1
```

## API 參考

### 規劃器類別

- `BuiltInPlanner(thinking_config)` - 原生模型思考
- `PlanReActPlanner()` - 結構化規劃工作流程
- `StrategicPlanner()` - 自訂商業策略規劃器

### 工具函式

- `analyze_market(industry, region, context)` - 市場研究
- `calculate_roi(investment, return_rate, years, context)` - 財務分析
- `assess_risk(factors, context)` - 風險評估
- `save_strategy_report(problem, strategy, context)` - 報告生成

## 效能考量

### 規劃器開銷

- **BuiltInPlanner**：4-6 秒（思考透明度）
- **PlanReActPlanner**：5-8 秒（結構化工作流程）
- **StrategicPlanner**：5-7 秒（特定領域分析）

### 最佳化技巧

- 使用 BuiltInPlanner 滿足透明度需求
- 選擇 PlanReActPlanner 處理複雜的結構化問題
- 保留 StrategicPlanner 用於商業諮詢場景
- 考慮使用串流處理長回應

## 貢獻

### 新增工具

1. 在 `agent.py` 中建立工具函式
2. 在 `test_tools.py` 中加入完整測試
3. 更新代理工具列表
4. 加入文件和範例

### 新增規劃器

1. 擴展 `BasePlanner` 類別
2. 實作 `build_planning_instruction` 和 `process_planning_response`
3. 加入代理配置
4. 建立完整測試

## 連結

- **教學**：[教學 12：規劃器與思維 (Planners and Thinking) - 策略性代理規劃 (Strategic Agent Planning)](../../../notes/google-adk-training-hub/adk_training/12-planners_thinking.md)
- **ADK 文件**：https://google.github.io/adk-docs/
- **Gemini 模型**：https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini

## 授權

此實作遵循與 ADK 訓練儲存庫相同的授權。
