# Interactions API 基礎範例

本範例展示了 Google Interactions API 的基礎功能，用於與 Gemini 模型建立有狀態的對話。

## 功能特色

- 與 Gemini 模型的基本文字互動
- 使用 `previous_interaction_id` 進行伺服器端狀態管理
- 用於即時輸出的串流回應 (Streaming responses)
- 使用工具進行 Function calling (函式呼叫)
- 內建工具 (Google Search, 程式碼執行)

## 先決條件

```bash
# 安裝依賴項
make setup

# 設定您的 API 金鑰
export GOOGLE_API_KEY="your-api-key-here"
```

## 快速開始

```bash
# 執行測試以驗證設定
make test

# 執行互動式演示
make demo

# 查看所有可用指令
make help
```

## 範例

### 基本互動

```python
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="Tell me a short joke about programming."
)

print(interaction.outputs[-1].text)
```

### 有狀態對話

```python
# 第一輪
interaction1 = client.interactions.create(
    model="gemini-2.5-flash",
    input="My favorite color is blue."
)

# 第二輪 - 保留上下文！
interaction2 = client.interactions.create(
    model="gemini-2.5-flash",
    input="What is my favorite color?",
    previous_interaction_id=interaction1.id
)
# 輸出: "Your favorite color is blue."
```

### 串流 (Streaming)

```python
stream = client.interactions.create(
    model="gemini-2.5-flash",
    input="Explain quantum entanglement simply.",
    stream=True
)

for chunk in stream:
    if chunk.event_type == "content.delta":
        print(chunk.delta.text, end="", flush=True)
```

### 函式呼叫 (Function Calling)

```python
weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "Gets weather for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="What's the weather in Paris?",
    tools=[weather_tool]
)
```

## 專案結構

```
interactions_api_basic/
├── Makefile                    # 建置與執行指令
├── README.md                   # 本文件
├── pyproject.toml             # 專案設定
├── requirements.txt           # 依賴項
├── interactions_basic_agent/  # 主要代理模組
│   ├── __init__.py
│   ├── agent.py               # 代理實作
│   ├── tools.py               # 工具定義
│   └── .env.example           # 環境變數範本
└── tests/                     # 測試套件
    ├── test_agent.py          # 代理測試
    ├── test_imports.py        # 匯入測試
    └── test_interactions.py   # Interactions API 測試
```

## 執行測試

```bash
# 執行所有測試
make test

# 使用詳細輸出執行
pytest tests/ -v

# 執行特定測試檔案
pytest tests/test_interactions.py -v
```

## 了解更多

- [Interactions API 文件](https://ai.google.dev/gemini-api/docs/interactions)
- [部落格文章：精通 Interactions API](../../../notes/google-adk-training-hub/blog/2025-12-12-interactions-api-deep-research.md)
- [Google AI Studio](https://aistudio.google.com/apikey)

## 重點摘要

- **核心概念**：Interactions API 提供了一個統一的介面來管理與 Gemini 模型的有狀態對話，簡化了上下文維護的複雜性。
- **關鍵技術**：
    - `previous_interaction_id`：用於在伺服器端維持對話狀態的關鍵參數。
    - **Streaming**：支援即時內容生成的串流回應。
    - **Function Calling**：整合自定義工具與內建工具（如 Google Search）。
- **重要結論**：Interactions API 特別適合需要長時間運行、多輪對話且需要維護狀態的 AI 應用程式，它比傳統的 `generateContent` API 提供了更高級別的抽象與便利性。
- **行動項目**：
    - 設定 `GOOGLE_API_KEY` 環境變數。
    - 執行 `make demo` 體驗完整功能。
    - 參考測試代碼了解 API 的具體用法。
