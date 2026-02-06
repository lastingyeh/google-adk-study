# RAG Agent 單元測試

本目錄包含 RAG (Retrieval-Augmented Generation) Agent 的單元測試套件。

## 測試檔案結構

### 核心測試檔案

#### 1. `test_imports.py`
測試所有模組的匯入功能，確保：
- 所有套件和模組能正確匯入
- 沒有循環相依問題
- 必要的外部相依套件已安裝

**測試範圍：**
- rag 套件匯入
- agent、prompts、tracing 模組匯入
- Pydantic 模型匯入
- ADK、Vertex AI、Arize 相依套件匯入

#### 2. `test_structure.py`
測試專案檔案結構完整性，驗證：
- 必要的目錄和檔案存在
- 配置檔案格式正確
- 依賴項目已聲明

**測試範圍：**
- rag/ 模組結構
- tests/ 目錄結構
- 配置檔案（pyproject.toml, Makefile, .env.example 等）

#### 3. `test_agent.py`
測試 Agent 的配置與功能，包括：
- Agent 屬性（名稱、模型、指令）
- 工具配置（VertexAiRagRetrieval）
- App 配置

**測試範圍：**
- root_agent 配置
- ask_vertex_retrieval 工具
- ADK App 設定

#### 4. `test_prompts.py`
測試提示語（Prompts）模組，驗證：
- return_instructions_root() 函式
- 指令內容完整性
- RAG 與引用指引

**測試範圍：**
- 提示語函式存在性
- 指令內容與格式
- RAG 相關關鍵字

#### 5. `test_models.py`
測試 Pydantic 資料模型，確保：
- Request 和 Feedback 模型定義正確
- 欄位驗證邏輯
- 預設值生成（UUID）

**測試範圍：**
- Request 模型（message, events, user_id, session_id）
- Feedback 模型（score, text, log_type, service_name）
- 模型 schema 驗證

#### 6. `test_config.py`
測試環境配置與初始化邏輯：
- Google 認證設定
- 環境變數配置
- RAG Corpus 配置

**測試範圍：**
- 環境變數設定（GOOGLE_CLOUD_LOCATION, GOOGLE_GENAI_USE_VERTEXAI）
- RAG_CORPUS 環境變數
- dotenv 載入

#### 7. `test_tracing.py`
測試 Arize 追蹤與可觀察性功能：
- instrument_adk_with_arize() 函式
- 追蹤器初始化
- 環境變數處理

**測試範圍：**
- Arize 憑證檢查
- 追蹤器註冊
- GoogleADKInstrumentor 整合

#### 8. `test_telemetry.py`
測試遙測（Telemetry）配置：
- setup_telemetry() 函式
- OpenTelemetry 設定
- GCS 上傳配置

**測試範圍：**
- 遙測啟用/停用邏輯
- NO_CONTENT 模式強制執行
- 環境變數設定

#### 9. `test_fastapi.py`
測試 FastAPI 應用程式：
- FastAPI app 配置
- /feedback 端點
- 會話與構件服務配置

**測試範圍：**
- FastAPI app 實例
- 回饋收集端點
- 資料庫連線配置

#### 10. `test_dummy.py`
基礎測試檔案，用於驗證測試環境正常運作。

## 執行測試

### 執行所有單元測試
```bash
pytest tests/unit/ -v
```

### 執行特定測試檔案
```bash
pytest tests/unit/test_agent.py -v
```

### 執行特定測試類別
```bash
pytest tests/unit/test_agent.py::TestAgentConfiguration -v
```

### 執行特定測試函式
```bash
pytest tests/unit/test_agent.py::TestAgentConfiguration::test_root_agent_exists -v
```

### 查看測試涵蓋率
```bash
pytest tests/unit/ --cov=rag --cov-report=html --cov-report=term
```

### 顯示詳細輸出
```bash
pytest tests/unit/ -v -s
```

## 測試標記

使用 pytest 標記來選擇性執行測試：

```bash
# 執行快速測試
pytest -m "not slow"

# 執行需要外部相依的測試
pytest -m "integration"
```

## 測試最佳實踐

1. **獨立性**：每個測試應獨立運行，不依賴其他測試
2. **明確命名**：測試函式名稱應清楚描述測試內容
3. **AAA 模式**：Arrange（準備）、Act（執行）、Assert（驗證）
4. **Mock 外部服務**：使用 mock 隔離外部相依（API、資料庫等）
5. **涵蓋邊界條件**：測試正常情況、錯誤情況和邊界值

## 環境變數

測試時需要的環境變數（可透過 .env 或 pytest fixtures 設定）：

```bash
# RAG 配置
RAG_CORPUS=projects/{project}/locations/{location}/ragCorpora/{corpus_id}

# Arize 追蹤（選填）
ARIZE_SPACE_ID=your-space-id
ARIZE_API_KEY=your-api-key
ARIZE_PROJECT_NAME=adk-rag-agent

# 遙測配置（選填）
LOGS_BUCKET_NAME=your-bucket-name
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT

# 資料庫配置（選填）
DB_USER=postgres
DB_NAME=postgres
DB_PASS=your-password
INSTANCE_CONNECTION_NAME=project:region:instance
```

## 測試涵蓋率目標

- **核心模組**（agent.py, prompts.py）：≥ 90%
- **工具模組**（tracing.py, telemetry.py）：≥ 80%
- **整體專案**：≥ 75%

## 持續整合

測試會在以下情況自動執行：
- Push 到主分支
- 建立 Pull Request
- 定期排程（每日）

## 疑難排解

### 匯入錯誤
確保已安裝所有依賴：
```bash
pip install -e ".[dev]"
```

### 認證錯誤
設定 Google Cloud 認證：
```bash
gcloud auth application-default login
```

### 環境變數未設定
複製並編輯 .env 檔案：
```bash
cp .env.example .env
# 編輯 .env 填入真實值
```

## 參考資源

- [Pytest 官方文件](https://docs.pytest.org/)
- [Google ADK 文件](https://cloud.google.com/generative-ai-sdk)
- [Pydantic 文件](https://docs.pydantic.dev/)
- [FastAPI 測試指南](https://fastapi.tiangolo.com/tutorial/testing/)

---

**最後更新：** 2026-02-06
**測試檔案數量：** 10
**測試案例總數：** 150+
