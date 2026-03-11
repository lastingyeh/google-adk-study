# Plan: AI 代理防護系統 - 基於 Google ADK 的完整實作方案

基於 tasks.md 的四階段設計，使用 Google ADK 的 callbacks、tool confirmation、multi-agent 和 plugins 系統，建立企業級 AI 代理防護系統。

---

## Steps

### 階段一：靜態過濾機制（基礎防護層）

**Phase 1-A: 輸入內容過濾器**
1. 建立 `ContentFilterPlugin`（繼承 `BasePlugin`）實作 `before_model_callback` 檢查禁用關鍵字
2. 使用正則表達式多模式匹配，阻擋時返回 `LlmResponse` 並記錄到 `session.state`
3. 建立可配置的 YAML/JSON 格式黑名單檔案

**Phase 1-B: 敏感資訊偵測（*parallel with 1-A*）**
4. 建立 `PIIDetectionPlugin` 偵測 email、phone、SSN、credit card、API keys
5. 實作四種處理策略：完全遮蔽、部分掩碼、雜湊、直接攔截
6. 記錄偵測紀錄於 `session.state['security:pii_detections']`
7. 建立單元測試驗證 PII 偵測準確率（> 95%）

---

### 階段二：高風險操作人工審核（主動干預層）

**Phase 2-A: 風險工具分級（*depends on Phase 1*）**
8. 定義工具風險等級：`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
9. 建立 `RiskToolRegistry` 管理高風險工具清單
10. 使用 `FunctionTool` 包裝工具，設置 `require_confirmation=True`（CRITICAL）或條件確認函數（HIGH）

**Phase 2-B: 審核流程實作**
11. 實作 `before_tool_callback` 保存審核上下文到 `session.state['pending_approval']`
12. 建立審核 REST API 端點（/approval/pending, /approval/decision）
13. 實作 `request_confirmation` 進階模式，包含結構化 payload（action, risk_level, details）
14. 整合 ADK Resume 功能支援審核後恢復執行

---

### 階段三：智能安全審核層（語意防護層）

**Phase 3-A: 安全審核代理（*depends on Phase 2*）**
15. 建立 `SecurityReviewerAgent` (LlmAgent)，使用 `gemini-2.0-flash-lite`
16. 設計安全審核 system instruction，返回 JSON 格式評估結果
17. 建立 `SafetyReviewPlugin` 實作 `after_model_callback` 發送內容到審核代理

**Phase 3-B: 多代理協作架構**
18. 建立 `SequentialAgent` 結構：MainAgent → SecurityReviewerAgent → OutputGate
19. 實作 `OutputGate` 自定義代理根據審核結果決策（通過/阻擋/重新生成）
20. 實作審核結果快取避免重複審核
21. 建立降級機制處理審核代理失敗情況

---

### 階段四：維運監控與系統優化（持續改進層）

**Phase 4-A: 監控指標系統（*parallel with Phase 3-B*）**
22. 建立 `SecurityMetricsPlugin` 收集全域指標（請求數、阻擋數、工具調用數）
23. 將指標存儲到三層級：`temp:metrics.*`, `user:metrics.*`, `app:metrics.*`
24. 計算精準度指標：FPR < 5%, FNR < 1%

**Phase 4-B: 效能與成本監控**
25. 追蹤每層防護延遲時間，使用 Events 系統發送到觀測性平台
26. 實作成本追蹤記錄安全審核代理 token 使用量
27. 建立效能儀表板顯示延遲、阻擋率趨勢、成本分析

**Phase 4-C: 威脅情報與動態更新（*depends on 22-27*）**
28. 實作 `ThreatIntelligenceService` 定期更新黑名單
29. 建立異常檢測機制（阻擋率突增 > 3x baseline）
30. 實作告警與自動化報告生成

---

## Relevant files

**核心實作：**
- `workspace/python/agents/guarding-agent/plugins/content_filter_plugin.py` — 靜態關鍵字過濾
- `workspace/python/agents/guarding-agent/plugins/pii_detection_plugin.py` — 敏感資訊偵測和處理
- `workspace/python/agents/guarding-agent/plugins/security_metrics_plugin.py` — 全域指標收集
- `workspace/python/agents/guarding-agent/tools/risk_tool_registry.py` — 工具風險等級管理
- `workspace/python/agents/guarding-agent/agents/security_reviewer_agent.py` — 智能安全審核代理
- `workspace/python/agents/guarding-agent/agents/output_gate_agent.py` — 審核結果處理
- `workspace/python/agents/guarding-agent/agent.py` — 主代理整合（多代理系統）
- `workspace/python/agents/guarding-agent/config/security_config.yaml` — 安全配置檔案
- `workspace/python/agents/guarding-agent/services/threat_intelligence_service.py` — 威脅情報服務
- `workspace/python/agents/guarding-agent/api/approval_api.py` — 人工審核 REST API

**參考 ADK 文件：**
- `workspace/adk-docs/callbacks/types-of-callbacks.md` (L18-L87) — Callback 觸發時機和使用
- `workspace/adk-docs/callbacks/design-patterns-and-best-practices.md` (L14+) — 8 種 callback 設計模式
- `workspace/adk-docs/custom-tools/function-tools/confirmation.md` (L26-L150) — Tool Confirmation 機制
- `workspace/adk-docs/safety-and-security/index.md` (L1-L150) — 多層安全防護策略
- `workspace/adk-docs/plugins/index.md` (L1-L100) — Plugin 系統架構
- `workspace/adk-docs/agents/multi-agents.md` (L1-L200) — 多代理系統編排
- `workspace/adk-docs/sessions&memory/state.md` (L1-L150) — Session State 管理

**參考範例：**
- `workspace/notes/google-adk-training-hub/adk_training/09-callbacks_guardrails.md` (L1-L300) — 內容審核系統範例

---

## Verification

**階段一驗證：**
- ✅ 單元測試：關鍵字過濾準確率（FP < 5%, FN < 1%）
- ✅ PII 偵測準確率 > 95%（各類型）
- ✅ 性能測試：過濾延遲 < 10ms

**階段二驗證：**
- ✅ 高風險工具觸發確認流程測試
- ✅ 審核決策傳遞測試（核准/拒絕）
- ✅ Session 恢復功能測試

**階段三驗證：**
- ✅ 危險內容攔截率 > 95%
- ✅ 安全內容通過率 > 99%
- ✅ 審核延遲 < 500ms

**階段四驗證：**
- ✅ 所有指標正確收集和彙總
- ✅ 異常檢測準確性（模擬攻擊流量）
- ✅ 完整防護鏈延遲 < 600ms

---

## Decisions

### 架構決策

**1. 分層防禦策略**
- 採用四層獨立可測試防護：靜態過濾 → 人工確認 → 智能審核 → 監控優化
- 每層可獨立開關和配置，支援降級運行

**2. Plugin vs Callback 使用原則**
- **Plugin**：全域性功能（內容過濾、PII 偵測、指標收集）
- **Callback**：特定代理或工具的客製化邏輯
- 優點：Plugin 註冊一次即可應用於所有代理和工具

**3. Multi-Agent 架構模式**
- 使用 `SequentialAgent` 實現：MainAgent → SecurityReviewerAgent → OutputGate
- 而非在單一代理內處理所有邏輯，提升模組化和可測試性

**4. Session State 層級選擇**
- `temp:metrics.*` — 單次 invocation 的臨時數據（不持久化）
- `user:metrics.*` — 跨 session 的用戶行為分析（持久化）
- `app:metrics.*` — 全域配置和統計（持久化，所有用戶共享）

**5. 輕量審核模型選擇**
- 使用 `gemini-2.0-flash-lite` 而非 Pro 模型
- 目標：成本降低 80%，延遲 < 500ms
- 準確率目標：> 95%（透過 prompt engineering 優化）

### 安全策略

**1. 白名單優先原則**
- 明確定義允許的操作範圍
- 黑名單作為輔助，而非唯一防線

**2. 最小化資訊暴露**
- PII 偵測記錄不含原始敏感值
- 僅記錄類型、位置和雜湊值

**3. 審核決策可追溯**
- 所有阻擋/審核決策記錄：
  - `invocation_id`：調用唯一識別
  - `reason`：阻擋或審核原因
  - `timestamp`：決策時間
  - `layer`：哪一層防護觸發

### 效能目標

| 防護層 | 延遲目標 | 成本影響 |
|--------|----------|----------|
| 靜態過濾 | < 10ms | 無（本地處理） |
| 人工確認 | 人工決定 | 無（阻塞等待） |
| 智能審核 | < 500ms | +$0.001/請求 |
| **總體** | **< 600ms** | **+1-2%** |

**精準度目標：**
- False Positive Rate (誤報) < 5%
- False Negative Rate (漏報) < 1%

---

## Further Considerations

### 階段一：靜態過濾優化

**1. 詞彙庫管理策略**
- ❓ 是否整合 Google Cloud DLP API 取代正則表達式？
  - **優點**：更高準確率（> 98%）、更多 PII 類型支援
  - **缺點**：增加外部依賴、額外成本（$1/1000 請求）
  - **建議**：Phase 1 使用正則，Phase 4 評估升級

**2. 多語言支援**
- ❓ 中文、日文、韓文的關鍵字過濾如何實作？
  - 需要分詞處理？（jieba, MeCab）
  - Unicode 正規化處理（簡繁轉換）
  - **建議**：先支援英文，Phase 2 擴展多語言

**3. PII 處理策略選擇**
- ❓ 不同場景使用不同策略？
  - 客服系統：部分掩碼（保留上下文）
  - 日誌系統：完全遮蔽（安全優先）
  - 內部工具：僅提醒（保留原始數據）
  - **建議**：透過 `security_config.yaml` 配置各場景策略

---

### 階段二：人機協作優化

**1. 審核超時處理**
- ❓ 人工審核超過 X 分鐘未回應，執行哪種策略？
  - **選項 A**：自動拒絕（安全優先）
  - **選項 B**：通知升級（發送給 manager）
  - **選項 C**：降級處理（允許執行但記錄）
  - **建議**：依風險等級決定：
    - CRITICAL → 自動拒絕
    - HIGH → 通知升級

**2. 批量審核介面**
- ❓ 是否支援審核者一次審核多個待決操作？
  - 提升效率（減少切換成本）
  - 需要 UI 支援多選和批量決策
  - **建議**：Phase 2 實作單一審核，Phase 3 擴展批量

**3. 審核歷史與學習**
- ❓ 是否從歷史審核決策中學習？
  - 記錄：哪些操作經常被核准/拒絕
  - 自動調整：頻繁核准的操作降級風險等級
  - **建議**：Phase 4 實作，作為自動調優的一部分

---

### 階段三：智能審核深化

**1. 審核模型選擇權衡**
- ❓ Gemini Flash Lite vs Flash vs Pro？

| 模型 | 延遲 | 成本 | 準確率 | 建議場景 |
|------|------|------|--------|----------|
| Flash Lite | ~200ms | $0.0002/req | ~92% | 低風險內容 |
| Flash | ~400ms | $0.001/req | ~96% | 一般場景 |
| Pro | ~800ms | $0.005/req | ~98% | 高風險場景 |

- **建議策略**：動態選擇
  - 預過濾：Flash Lite 快速判斷
  - 可疑內容：升級到 Flash 或 Pro

**2. 安全標準可配置**
- ❓ 不同應用場景需要不同審核標準？
  - **客服代理**：寬鬆（避免誤報影響用戶體驗）
  - **內部工具**：中等（平衡效率與安全）
  - **金融交易**：嚴格（安全優先）
  - **建議**：在 `security_config.yaml` 定義場景配置檔

**3. Red Team 對抗性測試**
- ❓ 是否建立專門的對抗測試集？
  - **包含內容**：
    - Prompt injection 變體（100+ 案例）
    - Jailbreak 嘗試（50+ 案例）
    - 多語言繞過（30+ 案例）
  - **建議**：Phase 3 建立基礎集，Phase 4 持續擴充

---

### 階段四：監控與擴展

**1. 觀測性平台整合**
- ❓ 選擇哪個平台？

| 平台 | 優點 | 缺點 | 建議 |
|------|------|------|------|
| BigQuery Analytics | 強大查詢、低成本 | 需要 ETL 設置 | ✅ 首選 |
| Google Cloud Monitoring | 原生整合、即時告警 | 查詢能力受限 | ✅ 輔助 |
| Prometheus + Grafana | 開源、靈活 | 維護成本高 | ⚠️ 自建場景 |

- **建議架構**：
  - 即時監控 → Cloud Monitoring
  - 歷史分析 → BigQuery
  - 視覺化 → Looker Studio / Grafana

**2. 自動調優機制**
- ❓ 是否實作 ML 模型自動調整閾值？
  - **輸入特徵**：
    - 歷史阻擋率、誤報率
    - 用戶反饋（「這個阻擋是否正確？」）
    - 時間序列模式（工作時間 vs 夜間）
  - **輸出調整**：
    - 關鍵字權重
    - 審核閾值
    - 風險等級分類
  - **建議**：Phase 4 實作基礎版，持續優化

**3. 合規報告生成**
- ❓ 需要符合哪些法規？
  - **GDPR**（歐盟）：
    - 記錄所有 PII 處理操作
    - 提供用戶數據存取/刪除能力
  - **HIPAA**（美國醫療）：
    - 加密審計日誌
    - 最小權限存取控制
  - **建議格式**：
    - 日誌：結構化 JSON（Cloud Logging）
    - 報告：自動生成 PDF（每月/季度）

---

## Implementation Priority Matrix

基於影響力和實作複雜度的優先級矩陣：

```
高影響 │ P0: Phase 1-A      │ P1: Phase 2-A
       │ (靜態過濾)         │ (風險分級)
       │                    │
       │ P1: Phase 1-B      │ P2: Phase 3-A
       │ (PII 偵測)         │ (智能審核)
───────┼────────────────────┼──────────────────
低影響 │ P2: Phase 4-A      │ P3: Phase 4-C
       │ (基礎監控)         │ (威脅情報)
       │                    │
       └────────────────────┴──────────────────
         低複雜度              高複雜度
```

**優先級說明：**
- **P0**：必須實作（Phase 1-A 靜態過濾）— 立即防護
- **P1**：高優先級（Phase 1-B, 2-A）— 2 週內完成
- **P2**：中優先級（Phase 3-A, 4-A）— 1 個月內完成
- **P3**：低優先級（Phase 4-C）— 持續優化

---

## Success Metrics

### 技術指標

| 指標 | 目標值 | 測量方式 |
|------|--------|----------|
| **整體延遲** | < 600ms | P95 延遲（含所有防護層） |
| **誤報率 (FPR)** | < 5% | 被阻擋的安全請求 / 總安全請求 |
| **漏報率 (FNR)** | < 1% | 通過的危險請求 / 總危險請求 |
| **系統可用性** | > 99.9% | 月度正常運行時間 |
| **審核響應時間** | < 2 分鐘 | 人工審核平均處理時間 |

### 業務指標

| 指標 | 目標值 | 商業價值 |
|------|--------|----------|
| **安全事件減少** | -80% | 降低品牌風險 |
| **合規審計通過** | 100% | 避免罰款 |
| **用戶投訴減少** | -50% | 提升滿意度 |
| **人工審核成本** | -30% | 降低運營成本 |

### 持續改進指標

- **每月新威脅偵測數**：> 10 個新的攻擊模式
- **黑名單更新頻率**：每週 1 次
- **模型準確率提升**：每季 +2%

---

## Risk Management

### 技術風險

| 風險 | 影響 | 可能性 | 緩解策略 |
|------|------|--------|----------|
| **審核代理失敗** | 高 | 中 | 實作降級機制（使用規則引擎） |
| **性能瓶頸** | 中 | 中 | 實作快取層、非同步處理 |
| **誤報過多** | 高 | 高 | 持續調優、用戶反饋機制 |
| **API 配額耗盡** | 中 | 低 | 監控配額、實作限流 |

### 運營風險

| 風險 | 影響 | 可能性 | 緩解策略 |
|------|------|--------|----------|
| **審核人員不足** | 高 | 中 | 建立排程系統、升級機制 |
| **配置錯誤** | 高 | 中 | 配置驗證、版本控制 |
| **黑名單過時** | 中 | 高 | 自動更新、威脅情報整合 |
| **合規要求變更** | 低 | 低 | 模組化設計、易於調整 |

---

## Next Steps

### 立即行動（本週）
1. ✅ 建立專案結構：`workspace/python/agents/guarding-agent/`
2. ⬜ 實作 Phase 1-A：`ContentFilterPlugin` 基礎版本
3. ⬜ 建立單元測試框架和 CI/CD pipeline
4. ⬜ 編寫 `security_config.yaml` 配置檔案結構

### 短期目標（2 週）
5. ⬜ 完成 Phase 1-B：`PIIDetectionPlugin`
6. ⬜ 實作 Phase 2-A：`RiskToolRegistry` 和工具包裝
7. ⬜ 建立審核 API 端點原型
8. ⬜ 進行第一輪整合測試

### 中期目標（1 個月）
9. ⬜ 實作 Phase 3：智能審核代理和多代理架構
10. ⬜ 建立監控儀表板（Phase 4-A, 4-B）
11. ⬜ 進行壓力測試和性能優化
12. ⬜ 編寫使用文件和操作手冊

### 長期目標（持續）
13. ⬜ 實作 Phase 4-C：威脅情報和自動調優
14. ⬜ 建立 Red Team 測試集並持續擴充
15. ⬜ 根據用戶反饋和新威脅持續優化
16. ⬜ 探索 ML 模型輔助決策的可能性
