# Pack Deep Search - 單元測試文件

## 簡介

此文件提供 `pack-deep-search` 專案的完整單元測試案例說明，旨在建立清晰、一致且全面的測試文件。這些測試確保 Deep Search Agent 的核心功能、配置和整合都得到充分的驗證。

---

## 測試架構概覽

```
tests/unit/
├── __init__.py
├── README.md
├── test_agent.py          # Agent 配置與功能測試
├── test_callbacks.py      # 回調函式測試
├── test_config.py         # 配置模組測試
├── test_imports.py        # 匯入與結構驗證測試
├── test_models.py         # Pydantic 模型測試
└── test_structure.py      # 專案結構與檔案存在性測試
```

---

## 測試分類與內容

### 1. 匯入與結構驗證測試 (`test_imports.py`)

**測試類別：** `TestImports`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-IMPORT-001** | 驗證 Agent 模組可被匯入 | `from app import agent` |
| **TC-IMPORT-002** | 驗證 Root Agent 可從模組匯入 | `from app import root_agent` |
| **TC-IMPORT-003** | 驗證 Root Agent 具備基本屬性 | `name`, `model` 屬性 |
| **TC-IMPORT-004** | 驗證 Config 模組可被匯入 | `from app.config import config` |
| **TC-IMPORT-005** | 驗證 Pydantic 模型可被匯入 | `SearchQuery`, `Feedback` |
| **TC-IMPORT-006** | 驗證回調函式存在且可被呼叫 | 所有回調函式 |
| **TC-IMPORT-007** | 驗證 Agent 擁有必要屬性 | 核心屬性檢查 |
| **TC-IMPORT-008** | 驗證自訂 Agent 類別存在 | `EscalationChecker` |
| **TC-IMPORT-009** | 驗證所有子 Agent 可被匯入 | 全部 8 個子 Agent |

**測試數量：** 9 個測試案例

---

### 2. 專案結構與檔案存在性測試 (`test_structure.py`)

#### **測試類別 A：** `TestProjectStructure`

**檔案結構測試：**

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-STRUCT-001** | App 模組目錄存在 | `app/` |
| **TC-STRUCT-002** | `__init__.py` 存在 | `app/__init__.py` |
| **TC-STRUCT-003** | `agent.py` 存在 | `app/agent.py` |
| **TC-STRUCT-004** | `config.py` 存在 | `app/config.py` |
| **TC-STRUCT-005** | `fast_api_app.py` 存在 | `app/fast_api_app.py` |
| **TC-STRUCT-006** | Tests 目錄存在 | `tests/` |
| **TC-STRUCT-007** | Unit tests 目錄存在 | `tests/unit/` |
| **TC-STRUCT-008** | 測試檔案存在 | 所有測試檔案 |
| **TC-STRUCT-009** | 設定檔存在 | `pyproject.toml`, `Makefile` |
| **TC-STRUCT-010** | 環境範本檔存在 | `.env.example` |
| **TC-STRUCT-011** | README 存在 | `README.md` |
| **TC-STRUCT-012** | Dockerfile 存在 | `Dockerfile` |
| **TC-STRUCT-013** | pyproject.toml 內容驗證 | 包含專案資訊 |
| **TC-STRUCT-014** | 依賴項目驗證 | `google-adk`, `pytest` |

#### **測試類別 B：** `TestEnvironmentConfiguration`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-ENV-001** | 環境範本與實際環境分離 | `.env.example` vs `.env` |
| **TC-ENV-002** | 環境範本包含必要變數 | `GOOGLE_API_KEY` |
| **TC-ENV-003** | Makefile 包含必要 targets | 基本 targets |

#### **測試類別 C：** `TestCodeQuality`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-QUALITY-001** | Agent 模組包含 docstrings | agent.py 文件化 |
| **TC-QUALITY-002** | Config 模組包含 docstrings | config.py 文件化 |
| **TC-QUALITY-003** | 檔案包含授權標頭 | Copyright/License |
| **TC-QUALITY-004** | 類別包含 docstrings | 主要類別文件化 |

#### **測試類別 D：** `TestAppUtilsStructure`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-UTILS-001** | app_utils 目錄存在 | `app/app_utils/` |
| **TC-UTILS-002** | telemetry 模組存在 | `telemetry.py` |
| **TC-UTILS-003** | typing 模組存在 | `typing.py` |

**測試數量：** 24 個測試案例

---

### 3. Agent 配置與功能測試 (`test_agent.py`)

#### **測試類別 A：** `TestAgentConfiguration`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-AGENT-001** | Root Agent 正確定義 | `root_agent` 存在 |
| **TC-AGENT-002** | Agent 名稱驗證 | `interactive_planner_agent` |
| **TC-AGENT-003** | Agent 模型驗證 | `gemini-3-pro-preview` |
| **TC-AGENT-004** | Agent 描述存在 | description 屬性 |
| **TC-AGENT-005** | Agent 指令存在 | instruction 屬性 |
| **TC-AGENT-006** | Agent 子 Agent 配置 | sub_agents 屬性 |
| **TC-AGENT-007** | Agent 工具配置 | tools 屬性 |

#### **測試類別 B：** `TestSubAgents`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-SUB-001** | plan_generator 配置 | 名稱、模型、工具 |
| **TC-SUB-002** | section_planner 配置 | 輸出鍵配置 |
| **TC-SUB-003** | section_researcher 配置 | 工具與輸出鍵 |
| **TC-SUB-004** | research_evaluator 配置 | 評估功能 |
| **TC-SUB-005** | enhanced_search_executor 配置 | 搜尋增強 |
| **TC-SUB-006** | report_composer 配置 | 報告生成 |
| **TC-SUB-007** | research_pipeline 結構 | 流程配置 |

#### **測試類別 C：** `TestCustomAgents`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-CUSTOM-001** | EscalationChecker 類別定義 | 類別存在 |
| **TC-CUSTOM-002** | EscalationChecker 實例化 | 可建立實例 |
| **TC-CUSTOM-003** | EscalationChecker 執行方法 | `_run_async_impl` |

#### **測試類別 D-G：** 其他 Agent 測試

- `TestAgentCallbacks`: 回調配置測試 (5 個案例)
- `TestAgentTools`: 工具配置測試 (4 個案例)
- `TestAgentOutputKeys`: 輸出鍵測試 (5 個案例)
- `TestAgentHierarchy`: 層級結構測試 (3 個案例)

**測試數量：** 31 個測試案例

---

### 4. 配置模組測試 (`test_config.py`)

#### **測試類別 A：** `TestConfiguration`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-CONFIG-001** | Config 實例存在 | `config` 物件 |
| **TC-CONFIG-002** | Critic model 設定 | `critic_model` 屬性 |
| **TC-CONFIG-003** | Worker model 設定 | `worker_model` 屬性 |
| **TC-CONFIG-004** | 最大迭代次數設定 | `max_search_iterations` |
| **TC-CONFIG-005** | 預設值驗證 | 所有預設配置 |

#### **測試類別 B：** `TestConfigurationClass`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-CLASS-001** | ResearchConfiguration 類別 | 類別定義 |
| **TC-CLASS-002** | 類別實例化 | 可建立實例 |
| **TC-CLASS-003** | 自訂值支援 | 參數化配置 |
| **TC-CLASS-004** | Dataclass 驗證 | 是否為 dataclass |

#### **測試類別 C：** `TestEnvironmentVariables`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-ENV-VAR-001** | dotenv 載入驗證 | 環境變數存在 |
| **TC-ENV-VAR-002** | Vertex AI 配置 | 配置邏輯正確 |

**測試數量：** 11 個測試案例

---

### 5. Pydantic 模型測試 (`test_models.py`)

#### **測試類別 A：** `TestSearchQueryModel`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-MODEL-SQ-001** | SearchQuery 模型存在 | 模型定義 |
| **TC-MODEL-SQ-002** | 模型建立 | 實例化功能 |
| **TC-MODEL-SQ-003** | 必要欄位驗證 | 欄位驗證 |
| **TC-MODEL-SQ-004** | 欄位類型驗證 | 類型檢查 |
| **TC-MODEL-SQ-005** | Schema 驗證 | JSON schema |

#### **測試類別 B：** `TestFeedbackModel`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-MODEL-FB-001** | Feedback 模型存在 | 模型定義 |
| **TC-MODEL-FB-002** | Pass 狀態建立 | grade="pass" |
| **TC-MODEL-FB-003** | Fail 狀態建立 | grade="fail" |
| **TC-MODEL-FB-004** | Grade literal 驗證 | 只接受 pass/fail |
| **TC-MODEL-FB-005** | 必要欄位驗證 | 欄位驗證 |
| **TC-MODEL-FB-006** | 選填欄位驗證 | follow_up_queries |
| **TC-MODEL-FB-007** | 多個 queries 處理 | 陣列處理 |
| **TC-MODEL-FB-008** | Schema 驗證 | JSON schema |
| **TC-MODEL-FB-009** | 模型序列化 | to_dict |
| **TC-MODEL-FB-010** | 模型反序列化 | from_dict |

#### **測試類別 C：** `TestModelIntegration`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-INTEGRATION-001** | Feedback 與 SearchQuery 整合 | 模型組合 |
| **TC-INTEGRATION-002** | 模型 JSON 序列化 | JSON 輸出 |

**測試數量：** 17 個測試案例

---

### 6. 回調函式測試 (`test_callbacks.py`)

#### **測試類別 A：** `TestCollectResearchSourcesCallback`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-CB-CRS-001** | 回調函式存在 | 函式定義 |
| **TC-CB-CRS-002** | 空狀態處理 | 初始化邏輯 |
| **TC-CB-CRS-003** | 狀態初始化 | state 物件建立 |

#### **測試類別 B：** `TestCitationReplacementCallback`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-CB-CR-001** | 回調函式存在 | 函式定義 |
| **TC-CB-CR-002** | 空報告處理 | 空字串處理 |
| **TC-CB-CR-003** | 引用標籤替換 | Citation tag 轉換 |
| **TC-CB-CR-004** | 無效引用處理 | 錯誤處理 |
| **TC-CB-CR-005** | 標點符號修正 | 間距調整 |
| **TC-CB-CR-006** | 返回類型驗證 | Content 類型 |
| **TC-CB-CR-007** | 多個引用處理 | 批次處理 |

#### **測試類別 C：** `TestCallbackIntegration`

| 測試案例編號 | 描述 | 驗證項目 |
|------------|------|---------|
| **TC-CB-INT-001** | 回調分配驗證 | Agent 綁定 |
| **TC-CB-INT-002** | 正確回調分配 | 對應關係 |

**測試數量：** 12 個測試案例

---

## 測試執行

### 執行所有測試

```bash
# 使用 pytest
pytest tests/unit/ -v

# 使用 Make
make test
```

### 執行特定測試檔案

```bash
pytest tests/unit/test_agent.py -v
pytest tests/unit/test_models.py -v
pytest tests/unit/test_callbacks.py -v
```

### 執行特定測試類別

```bash
pytest tests/unit/test_agent.py::TestAgentConfiguration -v
pytest tests/unit/test_models.py::TestFeedbackModel -v
```

### 執行涵蓋率測試

```bash
pytest tests/unit/ --cov=app --cov-report=html
pytest tests/unit/ --cov=app --cov-report=term-missing
```

---

## 測試統計摘要

| 測試檔案 | 測試類別數 | 測試案例數 | 涵蓋範圍 |
|---------|----------|----------|---------|
| `test_imports.py` | 1 | 9 | 模組匯入 |
| `test_structure.py` | 4 | 24 | 專案結構 |
| `test_agent.py` | 7 | 31 | Agent 功能 |
| `test_config.py` | 3 | 11 | 配置管理 |
| `test_models.py` | 3 | 17 | 資料模型 |
| `test_callbacks.py` | 3 | 12 | 回調函式 |
| **總計** | **21** | **104** | **完整覆蓋** |

---

## 測試品質指標

| 指標 | 狀態 | 說明 |
|-----|------|------|
| 測試命名清晰度 | ✅ 優秀 | 描述性命名 |
| Docstring 完整性 | ✅ 100% | 所有測試含文件 |
| 邊界測試覆蓋 | ✅ 完整 | 異常情況處理 |
| Mock 使用 | ✅ 適當 | 回調測試使用 Mock |
| 測試獨立性 | ✅ 符合規範 | 無依賴關係 |
| AAA 模式 | ✅ 遵循 | Arrange-Act-Assert |

---

## 測試設計原則

### 1. **分層測試架構**
- **Layer 1**: 匯入測試（最基礎）
- **Layer 2**: 結構測試（檔案系統）
- **Layer 3**: 配置測試（設定驗證）
- **Layer 4**: 模型測試（資料驗證）
- **Layer 5**: 功能測試（業務邏輯）
- **Layer 6**: 整合測試（組件互動）

### 2. **AAA 測試模式**
所有測試遵循 Arrange-Act-Assert 結構

### 3. **邊界條件覆蓋**
- 空值處理
- 無效輸入
- 異常情況
- 極端值測試

### 4. **單一職責原則**
每個測試案例只驗證一個功能點

---

## 維護指南

### 新增測試時
1. 遵循現有命名慣例
2. 添加清晰的 docstring
3. 更新此 README 文件
4. 確保測試獨立性

### 測試失敗時
1. 檢查測試邏輯
2. 驗證環境配置
3. 查看依賴版本
4. 檢查程式碼變更

---

## 相關資源

- [pytest 文件](https://docs.pytest.org/)
- [Google ADK 文件](https://github.com/google/adk)
- [Pydantic 文件](https://docs.pydantic.dev/)
- [測試最佳實踐](https://docs.python.org/3/library/unittest.html)

---

**最後更新：** 2026-01-16
**測試框架：** pytest 9.0.1
**Python 版本：** >=3.10, <3.13
