# Advanced Patterns (進階模式)

**目的**: 探索尖端的 ADK 功能，以實現即時互動、標準化協定和分散式代理系統。

**資料來源**: [google/adk-python/src/google/adk/agents/live_request_queue.py](https://github.com/google/adk-python/tree/main/src/google/adk/agents/live_request_queue.py) (ADK 1.15) + MCP/A2A 實作

---

## 目錄

1.  [Streaming & Real-Time Interaction (串流與即時互動)](#streaming--real-time-interaction-串流與即時互動)
    *   與使用者進行即時對話
2.  [MCP (Model Context Protocol) (模型上下文協定)](#mcp-model-context-protocol-模型上下文協定)
    *   通用工具標準
3.  [A2A (Agent-to-Agent Communication) (代理對代理通訊)](#a2a-agent-to-agent-communication-代理對代理通訊)
    *   分散式代理系統

---

## Streaming & Real-Time Interaction (串流與即時互動)

### SSE (Server-Sent Events) (伺服器發送事件)

用於向使用者進行文字串流。

```python
# 向使用者進行文字串流
async def stream_response(query):
    runner = Runner()
    # 以 SSE 方式非同步執行
    async for event in runner.run_async(streaming=SSE):
        # 如果事件類型為 'content'，則發送內容
        if event.type == 'content':
            yield f"data: {event.content}\n\n"
        # 如果事件類型為 'done'，表示串流結束
        elif event.type == 'done':
            yield "data: [DONE]\n\n"
```

### BIDI (Bidirectional Streaming) (雙向串流)

用於語音或視訊對話。

```python
# 語音/視訊對話
queue = LiveRequestQueue()
runner = Runner()

async def live_conversation():
    # 執行即時對話
    async for event in runner.run_live(queue):
        # 如果事件類型為 'audio_response'，則播放音訊
        if event.type == 'audio_response':
            play_audio(event.audio_data)

        # 發送使用者輸入
        queue.send_realtime(audio_blob)
```

**適用模型**: `gemini-2.0-flash-live-*`, `gemini-live-2.5-*`

---

## 🔌 MCP (Model Context Protocol) (模型上下文協定)

### Universal Tool Standard (通用工具標準)

提供一個標準化的工具介面。

```python
# 標準化工具介面
mcp_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-filesystem', '/data']
    )
)

# 可與任何相容 MCP 的伺服器協作
# - 檔案系統操作
# - 資料庫查詢
# - Git 操作
# - Slack/Teams 整合
```

### MCP Benefits (MCP 的優點)

*   **Interoperability (互通性)**: 一個協定，多種工具。
*   **Security (安全性)**: 內建身份驗證。
*   **Discovery (探索性)**: 自動偵測功能。
*   **Community (社群)**: 提供超過 100 個 MCP 伺服器。

---

## 🤝 A2A (Agent-to-Agent Communication) (代理對代理通訊)

### Microservices Architecture (微服務架構)

允許遠端代理的整合。

```python
# 遠端代理整合
youtube_agent = RemoteA2aAgent(
    name='youtube_expert',
    base_url='https://youtube-agent.company.com'
)

# 本地代理使用遠端專業知識
orchestrator = Agent(
    name="content_strategist",
    tools=[AgentTool(youtube_agent)],
    instruction="使用 YouTube 分析數據建立策略"
)
```

### A2A vs Local Multi-Agent (A2A 與本地多代理比較)

*   **Distribution (分散式)**: 代理位於不同的服務上。
*   **Scaling (擴展性)**: 獨立部署與擴展。
*   **Teams (團隊合作)**: 跨團隊協作。
*   **Specialization (專業化)**: 特定領域的專家。

---

## 🚀 Next-Level Capabilities (新世代功能)

### Multimodal Integration (多模態整合)

*   **Images (圖片)**: 視覺分析與生成。
*   **Audio (音訊)**: 語音辨識與合成。
*   **Video (視訊)**: 即時視訊處理。
*   **Documents (文件)**: PDF/文字擷取與分析。

### Code Execution (程式碼執行)

內建 Python 直譯器。

```python
# 內建 Python 直譯器
code_agent = Agent(
    name="programmer",
    model="gemini-2.0-flash",  # 啟用程式碼執行
    instruction="編寫並測試 Python 程式碼"
)
```

### Custom Planners (自訂規劃器)

用於進階的推理策略。

```python
# 進階推理策略
reasoning_planner = CustomPlanner(
    strategy="tree_of_thought",
    max_depth=5
)

agent = Agent(
    name="deep_reasoner",
    planner=reasoning_planner
)
```

---

## 🎯 Key Takeaways (重點摘要)

1.  **Streaming (串流)**: 即時文字 (SSE) 和語音/視訊 (BIDI)。
2.  **MCP (模型上下文協定)**: 用於互通性的通用工具協定。
3.  **A2A (代理對代理通訊)**: 分散式代理通訊。
4.  **Multimodal (多模態)**: 圖片、音訊、視訊、文件。
5.  **Code Execution (程式碼執行)**: 內建 Python 直譯器。
6.  **Custom Planners (自訂規劃器)**: 進階推理策略。

**🔗 下一步**: 掌握 [Decision Frameworks (決策框架)](/adk_training/docs/decision-frameworks) 以選擇合適的模式。
