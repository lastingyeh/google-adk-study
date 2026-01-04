# Not ChatGPT

基於 **Google Gemini 2.0 Flash** 與 **Google ADK (Agent Development Kit)** 構建的智能對話助手，整合學習精華，實現安全、可追溯、具備文檔檢索能力的對話系統。

## 🏗️ 架構說明

### ⚠️ 重要：使用 Google ADK

本專案**完全基於 Google ADK 架構**開發，而非直接使用 `google-genai` SDK。

- ✅ 使用 `google.adk.agents.Agent` 定義 Agent
- ✅ 使用 `google.adk.runners.Runner` 執行 Agent
- ✅ 使用 `google.adk.sessions.SessionService` 管理狀態
- ❌ **不使用** `genai.Client()` 直接調用 LLM

**為什麼使用 ADK？**

- 標準化的 Agent 架構
- 內建會話管理和狀態持久化
- 易於添加工具、工作流程、回調
- 支援生產級部署
- 完整的評估和監控支援

📚 **參考文件**：
- [架構修正說明](./ARCHITECTURE_FIX.md)
- [ADK 快速參考](./ADK_QUICK_REFERENCE.md)
- [開發步驟](./planning/phase-1/steps.md)

## 🎯 專案目標

打造一個**生產級對話 AI 系統**，具備：

- 🧠 多輪對話記憶與上下文管理（基於 ADK SessionService）
- 💭 思考模式（深度推理）與標準模式切換
- 🛡️ 多層安全防護（PII 檢測、內容審核、AgentCallbacks）
- 📚 文檔檢索與引用來源追蹤 (RAG with Gemini Files)
- ⚡ 串流回應（基於 ADK Runner）
- 💾 對話持久化與 Session 管理
- 📊 完整的測試與評估體系（AgentEvaluator）

---

## ✅ Phase 1: 基礎對話系統（已完成）

### 核心功能

#### 1. 基礎對話能力

- ✅ Google Gemini 2.0 Flash 整合
- ✅ 多輪對話支援
- ✅ 上下文記憶 (Session State Management)
- ✅ 思考模式與標準模式切換

#### 2. 安全防護層 (Guardrails)

- ✅ PII 檢測與攔截（信用卡、email、電話、身份證）
- ✅ 敏感關鍵字過濾
- ✅ 輸入驗證與輸出清理
- ✅ 安全設定（SafetySettings）

#### 3. 對話持久化

- ✅ SQLite 資料庫整合
- ✅ Session 管理（建立、載入、列表、刪除）
- ✅ 對話歷史儲存與檢索
- ✅ 上下文狀態持久化（user/app/temp）

#### 4. 文檔管理與 RAG

- ✅ 文檔上傳到 Gemini Files API
- ✅ 文檔列表、查詢、刪除
- ✅ File Search Tool 實作
- ✅ 引用來源追蹤與顯示
- ✅ 多文檔聯合查詢

#### 5. CLI 互動介面

- ✅ 命令列對話介面
- ✅ 模式切換指令（/thinking, /standard）
- ✅ 安全防護開關（/safe on/off）
- ✅ Session 管理指令（/new, /list, /load, /history）
- ✅ 即時狀態顯示

#### 6. API 與串流

- ✅ FastAPI RESTful API
- ✅ SSE (Server-Sent Events) 串流回應
- ✅ 文檔管理 API 端點
- ✅ 對話 API 端點

#### 7. 測試與品質保證

- ✅ 單元測試（pytest）
- ✅ 整合測試
- ✅ 評估測試（AgentEvaluator 基礎版）
- ✅ 測試覆蓋率 > 70%
- ✅ 完整的測試數據集 (eval_set.json)

### 技術架構

```text
Backend (Python + FastAPI)
├── Agents         # 對話邏輯
│   ├── conversation_agent.py      # 基礎對話
│   ├── session_agent.py           # Session 管理
│   ├── rag_agent.py               # RAG 功能
│   └── safe_conversation_agent.py # 安全防護
├── Tools          # 工具集
│   └── file_search.py             # 文檔檢索
├── Services       # 服務層
│   ├── session_service.py         # Session 管理
│   └── document_service.py        # 文檔管理
├── Guardrails     # 安全防護
│   ├── pii_detector.py            # PII 檢測
│   └── safety_callbacks.py        # 安全回調
├── Config         # 配置
│   └── mode_config.py             # 模式配置
└── API            # HTTP API
    └── routes.py                  # RESTful 路由

Database: SQLite
├── conversations  # 對話記錄
└── messages       # 訊息記錄
```

### 快速開始

```bash
# 1. 安裝依賴
pip install -r backend/requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env，設定 GOOGLE_API_KEY

# 3. 啟動 CLI
python -m backend.cli

# 4. 啟動 API 伺服器
python -m backend.main
```

### 測試

```bash
# 執行所有測試
pytest tests/ -v

# 執行覆蓋率測試
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html --cov-report=term

# 執行特定測試
pytest tests/unit/backend/test_guardrails.py -v
pytest tests/integration/test_rag_citations.py -v
```

---

## 🚀 Phase 2: 工具整合與 UI（規劃中）

### 規劃功能

#### 1. 進階工具整合

- [ ] Code Execution Tool（程式碼執行）
- [ ] Google Search Tool（即時資訊檢索）
- [ ] Data Analysis Tool（資料分析）
- [ ] 自定義工具註冊機制

#### 2. 前端介面

- [ ] React + TypeScript Web UI
- [ ] 即時串流顯示
- [ ] 文檔管理面板
- [ ] 引用來源標籤
- [ ] 對話歷史介面
- [ ] 模式切換 UI

#### 3. 多模態支援

- [ ] 圖片上傳與分析
- [ ] 語音輸入（Speech-to-Text）
- [ ] 語音輸出（Text-to-Speech）

#### 4. 效能優化

- [ ] Redis Session 快取
- [ ] Context Compaction（對話壓縮）
- [ ] 分散式部署支援

---

## 🎓 Phase 3: 企業級功能（規劃中）

### 規劃功能

#### 1. 進階評估與監控

- [ ] AgentEvaluator 完整整合
- [ ] 自動化測試 Pipeline（CI/CD）
- [ ] 即時監控儀表板
- [ ] 品質趨勢分析

#### 2. 多租戶與權限

- [ ] 多使用者支援
- [ ] 角色權限管理（RBAC）
- [ ] 文檔存取控制
- [ ] 審計日誌

#### 3. 進階 RAG 功能

- [ ] Hybrid Search（關鍵字 + 語義）
- [ ] Reranking（結果重排序）
- [ ] 文檔分塊優化
- [ ] 查詢重寫（Query Rewriting）
- [ ] 引用準確度驗證

#### 4. 企業整合

- [ ] SSO 單點登入
- [ ] API Key 管理
- [ ] Webhook 通知
- [ ] 匯出對話記錄
- [ ] 自定義品牌化

#### 5. 生產環境部署

- [ ] Docker 容器化
- [ ] Kubernetes 部署
- [ ] 負載均衡
- [ ] 自動擴展
- [ ] 災難恢復

---

## 📝 常見問題 (FAQ)

### Q1: 為何不使用 LangChain？

**A**: ADK 是 Google 官方框架，與 Gemini 整合更深，且有以下優勢：

- 原生支援 Gemini 2.0 進階功能（Thinking、Grounding）
- 更好的 Agent Engine 整合
- 官方長期支援

### Q2: 如何處理長對話的 Context Window 限制？

**A**: 使用 Day 55 的 Context Compaction 技術：透過 LLM 自動摘要舊對話，可減少 80% Token 使用

### Q3: 如何估算使用成本？

**A**: Gemini 2.0 Flash 定價（2024）：

- Input: $0.075 / 1M tokens
- Output: $0.30 / 1M tokens

假設每次對話 1000 tokens：

- 每次成本 ≈ $0.000375
- 1000 次對話 ≈ $0.375

---

### Q4: 思考模式會增加多少成本？

**A**: 思考模式會產生額外的內部推理 tokens，實測數據：

#### 範例場景：複雜數學問題

- 標準模式：
  - Input: 100 tokens
  - Output: 500 tokens
  - 成本: $0.000375
  
- 思考模式：
  - Input: 100 tokens
  - Thinking: 300 tokens (內部推理，不計費)
  - Output: 500 tokens
  - 成本: $0.000375 (相同！)

**重點**: Gemini 2.0 的內建思考功能 **不額外收費**，僅計算最終輸出 tokens！

**建議策略**：

1. 預設使用標準模式（快速回應）
2. 複雜問題時自動提示切換思考模式
3. 允許使用者隨時切換模式

---

### Q5: 如何判斷何時該使用思考模式？

**A**: 提供三種判斷策略：

**1. 關鍵詞檢測（啟發式）**: 檢測「為什麼」、「如何」、「解釋」等關鍵詞

**2. 問題長度判斷**: 超過 50 字的問題通常較複雜

**3. 內容類型檢測**: 包含程式碼、數學公式或資料結構

**最佳實踐**：結合三種策略 + 使用者手動控制

---

### Q6: 思考模式的思考過程該如何顯示？

**A**: 提供三種顯示策略：

**1. 完整顯示（適合教學場景）**: 顯示完整思考過程

**2. 摘要顯示（適合一般使用）**: 僅顯示關鍵思考步驟

**3. 隱藏顯示（適合追求速度）**: 僅返回最終結果

---

### Q7: 如何確保代理不會產生違反公司政策的內容？

**A**: 使用 ADK 的 AgentCallbacks 機制實作多層安全防護：

**1. 請求前檢查 (before_model_request)**: 檢查惡意意圖與過濾敏感資訊

**2. 工具執行前驗證 (before_tool_execution)**: 檢查工具使用權限與參數安全性

**3. 回應後審核 (after_model_response)**: 內容審核與移除機密資訊

**最佳實踐**：

| 防護層級      | 檢查項目           | 實作位置              | 範例                      |
| ------------- | ------------------ | --------------------- | ----------------- |
| 🛡️ L1 請求過濾 | 惡意意圖、PII      | before_model_request  | "請提供管理員密碼" → 拒絕 |
| 🛡️ L2 工具管控 | 權限驗證、參數檢查 | before_tool_execution | 禁止存取 competitor.com   |
| 🛡️ L3 輸出審核 | 內容審核、資訊過濾 | after_model_response  | 自動移除內部文件編號      |
| 🛡️ L4 審計追蹤 | 所有安全事件記錄   | 全生命週期            | 記錄所有被攔截的請求      |

**實作範例**：參考 Day 18 (content-moderator) 的完整實作。

---

### Q8: 如何自訂公司專屬的安全規範？

**A**: 透過配置文件與規則引擎實現靈活的規範管理：

**1. YAML 配置（security_config.yaml）**: 定義禁止主題、PII 模式、工具白名單等

**2. 動態規則引擎**: 載入規則並評估是否違反規範

**3. 規範更新流程**:

- 透過 Git 版本控制規範配置
- 支援即時重載（無需重啟服務）
- 提供規範測試工具驗證規則有效性

---

### Q9: 如何有效測試 AI Agent 的品質？

**A**: 使用 Google ADK 的 AgentEvaluator 進行系統性評估：

**1. 建立評估數據集 (eval_set.json)**: 定義測試案例與預期行為

**2. 執行評估測試**: 使用 AgentEvaluator 分析準確率與工具使用正確率

**3. 整合 CI/CD**: 透過 GitHub Actions 自動執行評估

**測試層級**：

| 測試類型 | 覆蓋率目標 | 執行頻率 | 測試工具       |
| -------- | ---------- | -------- | -------------- |
| 單元測試 | > 70%      | 每次提交 | pytest         |
| 整合測試 | > 60%      | 每日     | pytest + ADK   |
| 評估測試 | 100%       | 每次發布 | AgentEvaluator |
| 效能測試 | N/A        | 每週     | locust/k6      |

---

### Q10: 如何確保 Agent 的回應品質穩定？

**A**: 建立完整的評估與監控機制：

**1. 自動化評估流程**: 測試回應準確度、思考模式品質、安全防護效果

**2. 生產環境監控**: 記錄關鍵指標（回應時間、Token 使用、工具呼叫、安全攔截、用戶反饋）

**3. 回歸測試**:

- 每次發布前執行完整評估數據集
- 確保新功能不影響既有品質
- 追蹤品質趨勢圖表

---

### Q11: Agentic RAG 與傳統 RAG 有何不同？

**A**: Agentic RAG 讓 AI 代理主動決定何時使用文檔知識：

#### 傳統 RAG 流程（被動）

```text
用戶問題 → 向量檢索 → 拼接上下文 → LLM 回答
```

**問題**：每次都檢索，即使問題不需要文檔

#### Agentic RAG 流程（主動）

```text
用戶問題 → Agent 判斷 → 需要文檔？
                         ├─ 是 → File Search Tool → 回答
                         └─ 否 → 直接回答 / Google Search
```

**優勢**：

- ✅ 智慧路由：結合即時資訊（Google Search）與私有知識（File Search）
- ✅ 成本優化：僅在需要時檢索文檔
- ✅ 更好的 UX：自動判斷，無需用戶手動切換模式

#### 實際應用範例

| 問題類型 | Agent 決策 | 使用工具 |
|---------|-----------|----------|
| "公司休假政策是什麼？" | 需要文檔 | File Search |
| "今天天氣如何？" | 需要即時資訊 | Google Search |
| "解釋一下量子力學" | 通用知識 | 直接回答（LLM 內建知識） |
| "比較文檔 A 和 B" | 需要多文檔 | File Search (Multi-Doc) |

---

### Q12: 如何優化 File Search 的查詢品質？

**A**: 提供三個層次的優化策略：

#### 1. 文檔準備階段

- 使用清晰的標題與章節結構
- 確保 PDF 可被文字提取（非掃描檔）
- 提供文檔摘要元資料

#### 2. 查詢優化

- 使用 Agent 重寫用戶問題（Query Rewriting）
- 設定相關性閾值（Relevance Threshold）
- 結合多輪對話上下文

#### 3. 結果後處理

- 驗證引用來源的準確性
- 提供原文摘錄（Snippets）
- 支援「查看完整文檔」功能

**進階技巧（P2 規劃）**：

- Reranking：使用 Cohere Rerank API 重新排序結果
- Hybrid Search：結合關鍵字與語義檢索
- 文檔分塊策略：針對長文檔優化切分
