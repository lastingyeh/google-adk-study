# 教學 10：評估與測試 - 完整實作

這是來自 ADK 訓練儲存庫的 **教學 10：評估與測試** 的完整可運作實作。

## 概述

此實作展示了 ADK 代理的全面測試模式,包括:

- **單元測試 (Unit Tests)**: 使用 pytest 進行個別工具測試
- **整合測試 (Integration Tests)**: 多步驟工作流程驗證
- **評估測試 (Evaluation Tests)**: 軌跡與回應品質評估
- **配置測試 (Configuration Tests)**: 代理設定驗證

## 快速開始

```bash
# 安裝相依套件
make setup

# 在開發模式下執行代理
make dev

# 執行全面測試
make test
```

## 專案結構

```text
support-agent/
├── support_agent/           # 代理實作
│   ├── __init__.py         # 套件匯出
│   ├── agent.py            # 客戶支援代理
│   └── .env.example        # 環境變數範本
├── tests/                  # 全面測試套件
│   ├── test_agent.py       # pytest 測試套件
│   ├── test_config.json    # 評估標準
│   ├── simple.test.json    # 基本評估測試
│   ├── ticket_creation.test.json  # 工作流程測試
│   └── complex.evalset.json       # 多輪對話測試
├── requirements.txt        # Python 相依套件
├── Makefile               # 開發指令
└── README.md              # 本檔案
```

## 代理功能

**客戶支援代理 (Customer Support Agent)** 提供:

- **知識庫搜尋 (Knowledge Base Search)**: 回答常見客戶問題
- **工單建立 (Ticket Creation)**: 建立具有優先級別的支援工單
- **工單狀態查詢 (Ticket Status Checks)**: 監控現有工單進度

### 可用工具

1. `search_knowledge_base(query)` - 搜尋答案
2. `create_ticket(issue, priority)` - 建立支援工單
3. `check_ticket_status(ticket_id)` - 查詢工單狀態

## 測試

### 單元測試

執行個別工具與配置測試:

```bash
make test
```

**測試涵蓋範圍:**

- ✅ 工具函數行為 (16 個測試)
- ✅ 代理配置驗證 (6 個測試)
- ✅ 整合工作流程 (2 個測試)
- ✅ 評估框架測試 (3 個非同步測試)

### 評估測試

執行軌跡與回應品質評估:

```bash
make eval
```

**評估檔案:**

- `simple.test.json` - 基本知識庫搜尋
- `ticket_creation.test.json` - 多步驟工單工作流程
- `complex.evalset.json` - 多輪對話

## 示範提示

在 ADK 網頁介面中試試這些範例提示:

```bash
make demo
```

**互動範例:**

1. **密碼重設**: "How do I reset my password?" (如何重設密碼?)
2. **緊急問題**: "My account is completely locked!" (我的帳號完全被鎖定了!)
3. **政策問題**: "What's your refund policy?" (你們的退款政策是什麼?)
4. **狀態查詢**: "Check status of ticket TICK-ABC123" (查詢工單 TICK-ABC123 的狀態)

## 配置

1. **複製環境變數範本:**

   ```bash
   cp support_agent/.env.example support_agent/.env
   ```

2. **新增你的 API 金鑰:**

   ```bash
   # 編輯 support_agent/.env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## 開發指令

```bash
make setup      # 安裝相依套件
make dev        # 啟動 ADK 網頁介面
make test       # 執行所有測試
make test-cov   # 執行測試並產生涵蓋率報告
make eval       # 執行評估測試
make demo       # 顯示示範提示
make clean      # 清理快取檔案
```

## 測試結果

**預期測試輸出:**

```text
tests/test_agent.py::TestToolFunctions::test_search_knowledge_base_password_reset PASSED
tests/test_agent.py::TestToolFunctions::test_create_ticket_normal_priority PASSED
tests/test_agent.py::TestAgentConfiguration::test_agent_name PASSED
tests/test_agent.py::TestIntegration::test_ticket_creation_workflow PASSED
tests/test_agent.py::test_simple_kb_search PASSED
tests/test_agent.py::test_ticket_creation PASSED
tests/test_agent.py::test_multi_turn_conversation PASSED

=============== 28 passed in 8.43s ===============
```

## 評估指標

**軌跡分數 (Trajectory Score)**: 測量工具呼叫準確度 (0.0-1.0)

- 1.0 = 完美的工具序列匹配
- 0.8 = 良好匹配,有些微差異

**回應分數 (Response Score)**: 測量答案品質 (0.0-1.0)

- 0.9+ = 優秀匹配
- 0.7-0.8 = 良好匹配
- 0.5-0.6 = 可接受的匹配

## 疑難排解

### 常見問題

1. **匯入錯誤**: 確保使用 `make setup` 安裝相依套件

2. **API 金鑰問題**: 驗證 `GOOGLE_API_KEY` 已在 `.env` 中設定

3. **測試失敗**: 檢查所有相依套件是否相容

4. **評估錯誤**: 確保測試 JSON 檔案有效

### 除錯模式

使用詳細輸出執行測試:

```bash
pytest tests/ -v -s
```

## 連結

- **教學**: [Tutorial 10: Evaluation & Testing](../../../docs/tutorial/10_evaluation_testing.md)
- **ADK 文件**: <https://google.github.io/adk-docs/>
- **Google AI Studio**: <https://aistudio.google.com/>

## 貢獻

此實作遵循 ADK 訓練儲存庫中建立的模式。貢獻時:

1. 確保所有測試通過: `make test`
2. 為新功能新增測試案例
3. 更新 API 變更的文件
4. 遵循既定的程式碼模式
