# 教學 23：生產部署

展示 ADK 代理部署策略和最佳實務的生產部署代理。

## 概述

此實作展示了生產級模式，包括：

- **本地 API 伺服器**：FastAPI 開發伺服器
- **Cloud Run 部署**：無伺服器自動擴展
- **Agent Engine 部署**：託管代理基礎設施
- **GKE 部署**：自訂 Kubernetes 控制
- **最佳實務**：安全性、監控、可擴展性

## 快速開始

### 1. 設定

```bash
# 安裝相依套件
make setup

# 設定環境
cp .env.example .env
# 編輯 .env 並新增您的 GOOGLE_API_KEY
```

### 2. 執行開發伺服器

```bash
# 設定 API 金鑰
export GOOGLE_API_KEY=your_api_key

# 啟動 ADK 網頁介面
make dev
```

開啟 http://localhost:8000 並從下拉式選單中選擇 `production_deployment_agent`。

### 3. 執行測試

```bash
make test
```

## 功能

### 代理工具

代理提供三個專用工具：

1. **check_deployment_status**：驗證部署健康狀態與狀態
2. **get_deployment_options**：取得可用的部署策略
3. **get_best_practices**：學習生產環境最佳實務

### 自訂 FastAPI 伺服器

此實作包含一個生產級 FastAPI 伺服器：

```bash
# 啟動自訂伺服器
python -m uvicorn production_agent.server:app --reload

# 訪問 API 文件
open http://localhost:8000/docs
```

功能：

- `/health` 的健康檢查端點
- `/invoke` 的代理調用
- 請求指標追蹤
- 錯誤處理與日誌記錄
- OpenAPI 文件

📖 **指南**：[FastAPI 最佳實務](./FASTAPI_BEST_PRACTICES.md) - 學習 7 個核心模式。

## 部署選項

### 1. 本地 API 伺服器

```bash
adk api_server
```

功能：

- 用於開發的熱重載 (Hot reload)
- 自動 API 文件
- 已啟用 CORS

### 2. Cloud Run

```bash
adk deploy cloud_run \
  --project your-project-id \
  --region us-central1
```

功能：

- 無伺服器自動擴展
- 按使用量付費定價
- 託管基礎設施

### 3. Agent Engine

```bash
adk deploy agent_engine \
  --project your-project-id \
  --region us-central1
```

功能：

- 託管代理基礎設施
- 內建監控
- 版本控制

### 4. GKE (Kubernetes)

```bash
adk deploy gke
```

功能：

- 完全 Kubernetes 控制
- 自訂擴展政策
- 進階網路

## 範例提示

嘗試使用以下提示與代理互動：

```
"What deployment options are available?" (有哪些部署選項？)
"How do I deploy to Cloud Run?" (如何部署到 Cloud Run？)
"What are the best practices for production?" (生產環境的最佳實務是什麼？)
"Show me security best practices" (顯示安全性最佳實務)
"How do I configure auto-scaling?" (如何設定自動擴展？)
"What's the difference between Cloud Run and Agent Engine?" (Cloud Run 和 Agent Engine 有什麼不同？)
```

## 安全性文件

生產部署的全面安全性指南：

- 📋 **[SECURITY_RESEARCH_SUMMARY.md](./SECURITY_RESEARCH_SUMMARY.md)** - 執行摘要
  - 決策者的 15 分鐘閱讀
  - 依平台的安全性概覽 (Local, Cloud Run, GKE, Agent Engine)
  - 關鍵發現與糾正誤解
  - 依使用案例的建議

- 📖 **[SECURITY_ANALYSIS_ALL_DEPLOYMENT_OPTIONS.md](./SECURITY_ANALYSIS_ALL_DEPLOYMENT_OPTIONS.md)** - 技術深入探討
  - 工程師和架構師的 45 分鐘閱讀
  - 詳細的各平台安全性分析
  - 威脅模型與實作模式
  - 安全性比較矩陣與決策架構

- ✅ **[SECURITY_VERIFICATION.md](./SECURITY_VERIFICATION.md)** - 逐步驗證
  - 部署前檢查清單
  - 各平台安全性驗證程序

## 最佳實務

### 安全性

- 使用 Google Secret Manager 管理秘密
- 絕不提交 API 金鑰
- 設定 CORS 搭配特定 origins
- 實作速率限制
- 審查您平台的安全性文件
- 遵循部署前安全性檢查清單

### 監控

- 新增健康檢查端點
- 使用結構化日誌 (JSON)
- 啟用 Cloud Trace
- 追蹤錯誤率與延遲

### 可擴展性

- 設定自動擴展
- 設定資源限制
- 使用連線池
- 最佳化記憶體使用

### 可靠性

- 實作優雅關機
- 新增存活/就緒探針 (liveness/readiness probes)
- 使用斷路器 (circuit breakers)
- 設定具有退避 (backoff) 的重試

## 專案結構

```
tutorial23/
├── production_agent/
│   ├── __init__.py          # 套件初始化
│   ├── agent.py             # 包含工具的代理定義
│   └── server.py            # 自訂 FastAPI 伺服器
├── tests/
│   ├── test_structure.py    # 專案結構測試
│   ├── test_imports.py      # 匯入驗證
│   ├── test_agent.py        # 代理設定測試
│   └── test_server.py       # 伺服器端點測試
├── pyproject.toml           # 專案設定
├── requirements.txt         # 相依套件
├── Makefile                 # 常用指令
├── .env.example            # 環境範本
└── README.md               # 本檔案
```

## 測試

執行全面測試套件：

```bash
# 所有測試
make test

# 特定測試檔案
pytest tests/test_agent.py -v

# 帶有覆蓋率報告
pytest tests/ -v --cov=production_agent --cov-report=html
```

測試覆蓋率包括：

- ✅ 專案結構驗證
- ✅ 匯入驗證
- ✅ 代理設定
- ✅ 工具功能
- ✅ 伺服器端點
- ✅ 請求/回應模型
- ✅ 健康檢查
- ✅ 指標追蹤

## 環境變數

請參閱 `.env.example` 以了解所有可用的設定選項：

```bash
# 必要
GOOGLE_API_KEY=your-api-key

# 選用 (用於 Vertex AI)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1

# 伺服器設定
PORT=8080
HOST=0.0.0.0
```

## 資源

- [教學 23 文件](../../docs/tutorial/23_production_deployment.md)
- [ADK 部署指南](https://google.github.io/adk-docs/deploy/)
- [Cloud Run 文件](https://cloud.google.com/run/docs)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/agent-engine)

## 故障排除

### "Agent not found in dropdown" (下拉式選單中找不到代理)

請確認您已安裝套件：

```bash
pip install -e .
```

### "GOOGLE_API_KEY not set" (未設定 GOOGLE_API_KEY)

匯出您的 API 金鑰：

```bash
export GOOGLE_API_KEY=your_key
```

### "Module not found" (找不到模組)

安裝相依套件：

```bash
make setup
```
---
## 專案結構說明

以下表格詳細說明了專案中各個檔案與目錄的用途，協助您快速了解專案結構：

| 分類           | 檔案/目錄名稱                                 | 說明                                                                         |
| :------------- | :-------------------------------------------- | :--------------------------------------------------------------------------- |
| **核心設定**   | `.env.example`                                | 環境變數設定範本，包含 API 金鑰與伺服器設定。                                |
|                | `Makefile`                                    | 專案自動化指令集，用於安裝、測試、開發與演示。                               |
|                | `pyproject.toml`                              | Python 專案設定檔，定義相依套件與建置系統。                                  |
|                | `requirements.txt`                            | 專案依賴套件清單。                                                           |
| **核心程式碼** | `production_agent/`                           | 包含代理實作 (`agent.py`) 與自訂 FastAPI 伺服器 (`server.py`) 的原始碼目錄。 |
|                | `tests/`                                      | 包含各項功能的測試程式碼。                                                   |
| **部署指南**   | `DEPLOYMENT_CHECKLIST.md`                     | 部署前後的詳細檢查清單，確保生產環境準備就緒。                               |
|                | `DEPLOYMENT_OPTIONS_EXPLAINED.md`             | 詳細比較 ADK 內建伺服器與自訂 FastAPI 伺服器的差異與選擇指南。               |
|                | `MIGRATION_GUIDE.md`                          | 跨平台遷移指南 (如從 Cloud Run 遷移至 GKE)。                                 |
|                | `QUICK_REFERENCE.md`                          | 快速參考卡，包含常用指令與決策樹。                                           |
| **安全性文件** | `SECURITY_RESEARCH_SUMMARY.md`                | 安全性研究執行摘要，適合決策者閱讀。                                         |
|                | `SECURITY_ANALYSIS_ALL_DEPLOYMENT_OPTIONS.md` | 所有部署選項的詳細安全性技術分析。                                           |
|                | `SECURITY_VERIFICATION.md`                    | 各平台安全性驗證的逐步指南。                                                 |
| **最佳實務**   | `FASTAPI_BEST_PRACTICES.md`                   | 關於生產級 FastAPI 伺服器的 7 個核心模式與最佳實務。                         |
|                | `COST_BREAKDOWN.md`                           | 各部署平台的詳細成本分析與估算。                                             |
| **專案說明**   | `README.md`                                   | 專案的主要說明文件（本檔案）。                                               |

