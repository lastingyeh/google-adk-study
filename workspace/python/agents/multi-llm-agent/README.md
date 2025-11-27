# 教學 28: 透過 LiteLLM 使用其他 LLM

一個透過 LiteLLM 整合支援 OpenAI、Claude、Ollama 等多種大型語言模型 (LLM) 的 multi-LLM agent。

## 🚀 快速入門

```bash
# 安裝依賴套件
make setup

# 設定 API 金鑰
export GOOGLE_API_KEY=your_google_key
export OPENAI_API_KEY=sk-your_openai_key
export ANTHROPIC_API_KEY=sk-ant-your_anthropic_key

# 啟動 agent
make dev

# 開啟 http://localhost:8000 並選擇 'multi_llm_agent'
```

## 💡 功能介紹

本教學示範如何在 ADK agent 中透過 LiteLLM 使用多個 LLM 供應商：

- **OpenAI GPT 模型**：GPT-4o 和 GPT-4o-mini 用於各種任務
- **Anthropic Claude**：Claude 3.7 Sonnet 用於詳細分析
- **Ollama 本地模型**：Llama 3.3 用於注重隱私的操作
- **Azure OpenAI**：企業級部署選項
- **多供應商策略**：跨供應商進行比較與優化

## 📁 專案結構

```
tutorial28/
├── multi_llm_agent/       # Agent 實作
│   ├── __init__.py        # 套件初始化
│   ├── agent.py           # Multi-LLM agent 定義
│   └── .env.example       # API 金鑰模板
├── tests/                 # 完整的測試套件
│   ├── test_agent.py      # Agent 設定測試
│   ├── test_imports.py    # 匯入驗證
│   └── test_structure.py  # 專案結構測試
├── requirements.txt       # Python 依賴套件
├── pyproject.toml         # 套件設定
├── Makefile              # 建置指令
└── README.md             # 本檔案
```

## 🔧 設定

### 先決條件

- Python 3.9+
- 來自 [AI Studio](https://aistudio.google.com/app/apikey) 的 Google API 金鑰
- 來自 [OpenAI Platform](https://platform.openai.com/api-keys) 的 OpenAI API 金鑰
- 來自 [Anthropic Console](https://console.anthropic.com/) 的 Anthropic API 金鑰
- 可選: [Ollama](https://ollama.com) 用於本地模型

### 安裝

```bash
# 1. 安裝依賴套件
make setup

# 2. 複製環境設定模板
cp multi_llm_agent/.env.example multi_llm_agent/.env

# 3. 編輯 .env 並加入您的 API 金鑰
# 4. 對於 Ollama：安裝 Ollama 並拉取模型
ollama pull llama3.3
```

## 🎯 可用的 Agents

### 1. Root Agent (預設)
- **模型**：OpenAI GPT-4o-mini
- **最適用於**：具成本效益的一般任務
- **用法**：可透過 `adk web` 存取的主要 agent

### 2. GPT-4o Agent
- **模型**：OpenAI GPT-4o (完整版)
- **最適用於**：複雜的推理與程式碼編寫
- **成本**：較高但能力更強

### 3. Claude Agent
- **模型**：Anthropic Claude 3.7 Sonnet
- **最適用於**：長篇內容、詳細分析
- **特色**：200K context window (上下文視窗)

### 4. Ollama Agent
- **模型**：Llama 3.3 (本地)
- **最適用於**：隱私、離線操作、無 API 成本
- **需求**：需在本地執行 Ollama

## 🧪 測試不同的 AI 模型

### 分步測試指南

#### 1. 使用 OpenAI GPT-4o-mini (預設) 進行測試

```bash
# 僅設定 OpenAI 金鑰
export OPENAI_API_KEY=sk-your_openai_key_here

# 執行範例
make demo

# 預期：所有範例都使用 GPT-4o-mini 成功執行
```

#### 2. 使用 Claude 3.7 Sonnet 進行測試

```bash
# 僅設定 Anthropic 金鑰
export ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# 執行範例
make demo

# 預期：所有範例都使用 Claude 成功執行
```

#### 3. 使用 Ollama (本地模型) 進行測試

```bash
# 如果尚未安裝 Ollama，請先安裝
# 請造訪: https://ollama.com

# 拉取 Granite 4 模型
ollama pull granite4:latest

# 啟動 Ollama 伺服器 (在另一個終端機中)
ollama serve

# 執行範例 (本地模型不需要 API 金鑰)
make demo

# 預期：Ollama 範例在本地執行，其他若無 API 金鑰則可能失敗
```

#### 4. 同時測試多個供應商

```bash
# 設定所有 API 金鑰
export OPENAI_API_KEY=sk-your_openai_key_here
export ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# 確保 Ollama 正在執行
ollama serve

# 執行範例
make demo

# 預期：所有 4 個模型都在所有範例情境中進行測試
```

### 測試特定的 Agents

#### 透過 ADK Web 介面執行個別 Agents

```bash
# 啟動 ADK web 介面
make dev

# 開啟 http://localhost:8000
# 從下拉選單中選擇：
# - multi_llm_agent (OpenAI GPT-4o-mini)
# - gpt4o_mini_agent (OpenAI GPT-4o-mini 替代方案)
# - claude_agent (Claude 3.7 Sonnet)
# - ollama_agent (Granite 4 本地)
```

#### 以程式化方式測試 Agents

```python
# 測試特定 agent
from multi_llm_agent.agent import root_agent, claude_agent, ollama_agent

# 測試 OpenAI agent
print("正在測試 OpenAI GPT-4o-mini...")
# 使用 agent.run() 或 Runner 模式

# 測試 Claude agent
print("正在測試 Claude 3.7 Sonnet...")
# 使用 agent.run() 或 Runner 模式

# 測試 Ollama agent
print("正在測試 Ollama Granite 4...")
# 使用 agent.run() 或 Runner 模式
```

### 新增更多 AI 模型

#### 1. 新增一個 LiteLLM 支援的新模型

```python
# 在 agent.py 中，新增新的 agent 設定
new_agent = Agent(
    name="new_model_agent",
    model=LiteLlm(model='provider/model-name'),  # 例如 'together/mistral-7b'
    description="由新模型驅動的 Agent",
    instruction="你是由新的 AI 模型驅動。",
    tools=[calculate_square, get_weather, analyze_sentiment]
)
```

#### 2. 支援的模型範例

```python
# 更多 OpenAI 模型
gpt4_turbo_agent = Agent(
    model=LiteLlm(model='openai/gpt-4-turbo'),
    # ... 其他設定
)

# 透過 LiteLLM 使用 Google 模型 (不建議，建議使用原生整合)
# gemini_pro_agent = Agent(
#     model=LiteLlm(model='gemini/gemini-pro'),
#     # ... 但最好使用原生整合: model='gemini-pro'
# )

# Together AI 模型
mistral_agent = Agent(
    model=LiteLlm(model='together/mistral-7b-instruct'),
    # ... 其他設定
)

# Hugging Face 模型
zephyr_agent = Agent(
    model=LiteLlm(model='huggingface/zephyr-7b-beta'),
    # ... 其他設定
)

# 更多 Ollama 模型
llama_agent = Agent(
    model=LiteLlm(model='ollama_chat/llama3.2'),
    # ... 其他設定
)
```

#### 3. 測試新模型

```bash
# 為新的供應商設定對應的 API 金鑰
export TOGETHER_API_KEY=your_together_key
export HUGGINGFACE_API_KEY=your_hf_key

# 將新 agent 加入 demo.py 的 agents 列表
agents.append((new_agent, "New Model Name"))

# 執行範例
make demo
```

### API 金鑰管理

#### 不同供應商的環境變數

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Together AI
export TOGETHER_API_KEY=...

# Hugging Face
export HUGGINGFACE_API_KEY=hf_...

# Replicate
export REPLICATE_API_TOKEN=...

# Azure OpenAI
export AZURE_API_KEY=...
export AZURE_API_BASE=...
export AZURE_API_VERSION=...
```

#### 測試 API 金鑰有效性

```bash
# 快速測試腳本
python -c "
import os
from litellm import completion

# 測試 OpenAI
try:
    response = completion(
        model='openai/gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello'}],
        api_key=os.getenv('OPENAI_API_KEY')
    )
    print('✅ OpenAI: 正常')
except Exception as e:
    print(f'❌ OpenAI: {e}')

# 測試 Anthropic
try:
    response = completion(
        model='anthropic/claude-3-haiku-20240307',
        messages=[{'role': 'user', 'content': 'Hello'}],
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    print('✅ Anthropic: 正常')
except Exception as e:
    print(f'❌ Anthropic: {e}')
"
```

### 效能比較測試

#### 執行基準測試

```bash
# 測試回應時間
python -c "
import time
from multi_llm_agent.examples.demo import run_query
from multi_llm_agent.agent import root_agent, claude_agent, ollama_agent

agents = [
    (root_agent, 'GPT-4o-mini'),
    (claude_agent, 'Claude 3.7'),
    (ollama_agent, 'Ollama Granite')
]

query = '15 的平方是多少？'
for agent, name in agents:
    start = time.time()
    result = await run_query(agent, query, name)
    elapsed = time.time() - start
    print(f'{name}: {elapsed:.2f}s')
"
```

#### 成本分析

```bash
# 估算成本 (需要 litellm)
python -c "
import litellm

# 獲取價格
pricing = litellm.get_model_cost('openai/gpt-4o-mini')
print('GPT-4o-mini 價格:', pricing)

pricing = litellm.get_model_cost('anthropic/claude-3-7-sonnet-20250219')
print('Claude 3.7 價格:', pricing)
"
```

## 💬 範例提示

請嘗試使用 agent 執行以下提示：

**數學運算**：

- "25 的平方是多少？"
- "計算 144 的平方"

**天氣查詢**：

- "舊金山的天氣如何？"
- "取得紐約的天氣"

**情緒分析**：

- "分析情緒：'這個產品真是太棒了！'"
- "「對服務感到失望」的情緒是什麼？"

**一般對話**：

- "解釋 LiteLLM 如何實現多模型支援"
- "比較 OpenAI GPT-4o 和 Claude 3.7 Sonnet"
- "使用 Ollama 的本地模型有什麼好處？"

## 🔑 API 金鑰設定

### Google (Gemini)

```bash
export GOOGLE_API_KEY=your_google_api_key
```

### OpenAI

```bash
export OPENAI_API_KEY=sk-your_openai_key
```

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY=sk-ant-your_anthropic_key
```

### Ollama (本地)

```bash
export OLLAMA_API_BASE=http://localhost:11434
```

## 📊 成本比較

| 供應商 | 模型 | 輸入成本 | 輸出成本 | 最適用於 |
|---|---|---|---|---|
| Google | gemini-2.5-flash | $0.075/1M | $0.30/1M | 最便宜的雲端模型 |
| OpenAI | gpt-4o-mini | $0.15/1M | $0.60/1M | 平衡型 |
| OpenAI | gpt-4o | $2.50/1M | $10/1M | 複雜任務 |
| Anthropic | claude-3-7-sonnet | $3/1M | $15/1M | 長篇內容 |
| Ollama | llama3.3 (本地) | $0 | $0 | 隱私/離線 |

## ⚠️ 重要注意事項

### 對於 Ollama 請使用 `ollama_chat`

```python
# ✅ 正確
model = LiteLlm(model='ollama_chat/llama3.3')

# ❌ 錯誤
model = LiteLlm(model='ollama/llama3.3')
```

### 不要為 Gemini 使用 LiteLLM

對於 Gemini 模型，請改用原生的 `GoogleGenAI`：

```python
# ✅ 對於 Gemini 正確的作法
agent = Agent(model='gemini-2.5-flash')

# ❌ 不要這樣做
agent = Agent(model=LiteLlm(model='gemini/gemini-2.5-flash'))
```

## 🛠️ 切換模型

要使用不同的模型，請修改 agent 設定：

```python
from google.adk.models import LiteLlm
from multi_llm_agent.agent import root_agent

# 切換到 GPT-4o
root_agent.model = LiteLlm(model='openai/gpt-4o')

# 切換到 Claude
root_agent.model = LiteLlm(model='anthropic/claude-3-7-sonnet-20250219')

# 切換到本地 Ollama
root_agent.model = LiteLlm(model='ollama_chat/llama3.3')
```

## 📚 資源

- [LiteLLM 文件](https://docs.litellm.ai/)
- [OpenAI API 參考](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude 文件](https://docs.anthropic.com/)
- [Ollama 模型庫](https://ollama.com/library)
- [ADK 官方文件](https://google.github.io/adk-docs/)

## 🐛 疑難排解

### "Module not found" 錯誤

```bash
pip install -e .
```

### "Authentication error" (驗證錯誤)

檢查 API 金鑰是否設定正確：

```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

### Ollama 連線錯誤

確保 Ollama 正在執行：

```bash
ollama serve
```

### Rate limits (速率限制)

實作指數退避 (exponential backoff) 或使用備用模型：

```python
try:
    # 嘗試主要模型
    result = await runner.run_async(...)
except RateLimitError:
    # 退回到替代模型
    agent.model = fallback_model
```

## 📝 授權

本教學是 ADK 訓練儲存庫的一部分。

---

## 本專案以 ❤️ 使用 Google ADK 和 LiteLLM 建置

### 重點摘要
- **核心概念**：本教學示範如何透過 `LiteLLM` 函式庫在 Google ADK (Agent Development Kit) 中整合並使用多種大型語言模型 (LLM)，包含 OpenAI、Anthropic Claude 及本地的 Ollama 模型。
- **關鍵技術**：
    - `LiteLLM`：作為一個中間層，統一了對不同 LLM 供應商的 API 呼叫。
    - `Google ADK`：用於建構、管理和執行 AI agent 的框架。
    - `Makefile`：提供快速入門指令，簡化了安裝、啟動、測試和清理流程。
    - `環境變數`：用於安全地管理不同服務的 API 金鑰。
- **重要結論**：開發者可以利用 LiteLLM 的彈性，輕鬆地在不同 LLM 模型之間切換，以比較其效能、成本和特定任務的適用性，同時也能夠整合注重隱私的本地模型。
- **行動項目**：
    1. 依照 `Makefile` 中的 `setup` 指令安裝所有必要的依賴套件。
    2. 建立 `.env` 檔案並填入所需的 API 金鑰 (Google, OpenAI, Anthropic)。
    3. (可選) 安裝並執行 Ollama 以下載並使用本地模型。
    4. 使用 `make dev` 啟動網頁介面，或 `make demo` 執行命令列範例來測試不同的 agent。

### Mermaid 流程圖

```mermaid
graph TD
    A[開始] --> B{設定環境};
    B --> C["安裝依賴 (make setup)"];
    B --> D["設定 API 金鑰 (export ...)"];
    C --> E{選擇操作};
    D --> E;

    subgraph "主要操作"
        E --> F["啟動網頁介面 (make dev)"];
        E --> G["執行命令列範例 (make demo)"];
        E --> H["執行測試 (make test)"];
    end

    F --> I[在瀏覽器開啟 localhost:8000];
    I --> J[從下拉選單選擇 Agent];
    J --> K[與 Agent 互動];

    G --> L[腳本自動測試多個 LLM];
    L --> M[在終端機查看結果];

    H --> N[執行 Pytest];
    N --> O[查看測試報告];

    K --> P[結束];
    M --> P;
    O --> P;
