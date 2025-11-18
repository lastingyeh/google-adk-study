# 教學 20：YAML 設定 - 宣告式代理人設定

**目標**：掌握使用 YAML 檔案進行宣告式代理人設定，定義代理人、工具和行為，而無需撰寫 Python 程式碼。

**您將學到**：
- 使用 `root_agent.yaml` 建立代理人設定
- 了解 `AgentConfig` 和 `LlmAgentConfig` 架構
- 在 YAML 中設定工具、模型和指令
- 設定檔中的多代理人系統
- 載入和驗證設定

## 專案結構

```
tutorial20/
├── root_agent.yaml      # 代理人設定
├── run_agent.py         # 執行腳本
├── tools/               # 工具實作
│   ├── __init__.py
│   └── customer_tools.py
├── tests/               # 綜合測試
│   ├── test_agent.py
│   ├── test_tools.py
│   ├── test_imports.py
│   └── test_structure.py
├── pyproject.toml       # 套件設定
├── requirements.txt     # 依賴項
└── Makefile            # 建置指令
```

## 流程圖
 ```mermaid
 sequenceDiagram
     participant User
     participant Runner
     participant Agent
     participant SessionService

     User->>Runner: 執行 main()
     Runner->>Agent: config_agent_utils.from_config('root_agent.yaml')
     activate Agent
     Agent-->>Runner: 代理人實例
     deactivate Agent

     Runner->>SessionService: 建立 InMemorySessionService
     Runner->>SessionService: create_session()

     loop 對於每個查詢
         User->>Runner: 發送查詢 (run_async)
         Runner->>Agent: 處理訊息
         activate Agent
         Agent->>Agent: 思考/調用工具
         Agent-->>Runner: 回應事件
         deactivate Agent
         Runner-->>User: 顯示結果
     end
```

## 快速開始

### 1. 安裝依賴項

```bash
make setup
```

### 2. 驗證設定

```bash
make validate-config
```

### 3. 執行代理人

```bash
make dev
```

在瀏覽器中開啟 http://localhost:8000 並從下拉選單中選擇 'customer_support'。

### 4. 執行演示查詢

在 ADK 網頁 UI 中嘗試這些提示：

- "我是客戶 CUST-001，我想查詢我的訂單 ORD-001"
- "我需要協助解決登入錯誤"
- "我想要訂單 ORD-002 的退款 $75"

## 設定概覽

`root_agent.yaml` 定義了一個客戶支援系統，包含：

- **單一代理人**：具有完整工具的客戶支援代理人
- **工具**：11 個用於客戶服務操作的功能

## 執行測試

```bash
make test
```

測試涵蓋：
- YAML 設定載入
- 工具功能實作
- 代理人建立和驗證
- 專案結構驗證

## 手動測試

使用測試查詢直接執行代理人：

```bash
python run_agent.py
```

## 設定詳情

### 代理人設定架構

```yaml
name: agent_name
model: gemini-2.0-flash
description: "代理人用途"
instruction: |
  代理人的
  多行指令

generate_content_config:
  temperature: 0.7
  max_output_tokens: 2048

tools:
  - type: function
    name: tool_name
    description: "工具描述"

sub_agents:
  - name: sub_agent_1
    model: gemini-2.0-flash
    # ... 子代理人設定
```

### 工具實作

工具是 Python 函數，回傳結構化的字典：

```python
def tool_name(param: Type) -> Dict[str, Any]:
    return {
        'status': 'success',
        'report': '人類可讀的訊息',
        'data': { ... }  # 工具特定資料
    }
```

## 環境設定

### API 金鑰驗證

```bash
export GOOGLE_API_KEY=您的_api_key
```

在此獲取免費金鑰：https://aistudio.google.com/app/apikey

### 服務帳戶驗證

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT=您的_project_id
```

## 疑難排解

### 設定錯誤

```bash
# 驗證 YAML 語法
python -c "import yaml; yaml.safe_load(open('root_agent.yaml'))"

# 測試代理人載入
python -c "from google.adk.agents import config_agent_utils; config_agent_utils.from_config('root_agent.yaml')"
```

### 匯入錯誤

```bash
# 測試工具匯入
python -c "from tools.customer_tools import check_customer_status; print('OK')"
```

### 驗證問題

確保您擁有：
- `GOOGLE_API_KEY` 環境變數，或
- `GOOGLE_APPLICATION_CREDENTIALS` 和 `GOOGLE_CLOUD_PROJECT` 變數

## 進階用法

### 自訂設定

編輯 `root_agent.yaml` 以：
- 更改模型參數
- 新增工具
- 修改代理人指令
- 新增子代理人

### 新增工具

1. 在 `tools/customer_tools.py` 中實作函數
2. 在 `tools/__init__.py` 匯出中新增
3. 在 `root_agent.yaml` 中引用

### 特定環境設定

建立多個 YAML 檔案：
- `config/dev/root_agent.yaml`
- `config/prod/root_agent.yaml`

載入方式：`config_agent_utils.from_config('config/dev/root_agent.yaml')`

## 核心概念

- **宣告式設定**：在 YAML 中定義代理人，而非程式碼
- **工具函數**：在 YAML 中按名稱引用的 Python 函數
- **多代理人系統**：協調器 + 專門的子代理人
- **設定驗證**：部署前測試設定
- **環境管理**：開發/預備/生產環境的分離設定

## 下一步

- **教學 21**：學習多模態與影像生成
- **教學 22**：掌握模型選擇與最佳化
- **教學 23**：探索生產部署

## 資源

- [ADK 設定文件](https://google.github.io/adk-docs/configuration/)
- [AgentConfig API 參考](https://google.github.io/adk-docs/api/agent-config/)
- [YAML 規範](https://yaml.org/spec/)

## 重點摘要

- **核心概念**：透過 YAML 檔案進行宣告式代理人設定 (Declarative Agent Configuration)，將代理人定義與程式碼實作分離。
- **關鍵技術**：YAML, `AgentConfig`, `LlmAgentConfig`, ADK Configuration Utils。
- **重要結論**：宣告式設定提高了代理人定義的可讀性和維護性，支援多環境配置，並簡化了多代理人系統的建構。
- **行動項目**：
    - 學習 YAML 設定語法。
    - 實作並註冊工具函數。
    - 建立與驗證 `root_agent.yaml`。
