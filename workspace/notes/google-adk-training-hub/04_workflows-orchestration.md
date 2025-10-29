# Workflows & Orchestration

**🎯 目的**: 掌握工作流程模式，以協調複雜的代理行為和多步驟流程。

**📚 真實來源**: [google/adk-python/src/google/adk/agents/workflow\_agents/](https://github.com/google/adk-python/tree/main/src/google/adk/agents/workflow_agents/) (ADK 1.15)

---

## [FLOW] 工作流程模式概覽

**心智模型**: 工作流程就像代理協調的 **裝配線策略**：

```
┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW PATTERNS                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ [INSTR] SEQUENTIAL (Assembly Line)                           │
│    "One step after another, in order order"                  │
│                                                              │
│    Step 1  →  Step 2  →  Step 3  →  Step 4                   │
│    Write      Review     Refactor    Test                    │
│                                                              │
│    Use: Pipelines, dependencies, order matters               │
│    Pattern: Each step uses output from previous              │
│    Source: agents/workflow_agents/sequential_agent.py        │
│                                                              │
│ [PARALLEL] PARALLEL (Fan-out/Gather)                         │
│    "Multiple tasks at once, then combine"                    │
│                                                              │
│         ┌─── Task A ───┐                                     │
│         ├─── Task B ───┤  →  Merge Results                   │
│         └─── Task C ───┘                                     │
│       Research      Research   Synthesis                     │
│       Source 1      Source 2                                 │
│                                                              │
│    Use: Independent tasks, speed critical                    │
│    Pattern: Fan-out → Execute → Gather                       │
│    Source: agents/workflow_agents/parallel_agent.py          │
│                                                              │
│ [LOOP] LOOP (Iterative Refinement)                           │
│    "Repeat until good enough or max iterations"              │
│                                                              │
│    ┌──────────────────┐                                      │
│    │  ┌──► Critic ───┐│                                      │
│    │  │              ││                                      │
│    │  └─── Refiner ◄─┘│                                      │
│    └──────────────────┘                                      │
│         (Repeat 5x or until exit_loop)                       │
│                                                              │
│    Use: Quality improvement, retry logic                     │
│    Pattern: Generate → Critique → Improve → Repeat           │
│    Source: agents/workflow_agents/loop_agent.py              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## [INSTR] 序列工作流程 (裝配線)

### 基本序列模式

**心智模型**: 步驟按順序執行，每個步驟都使用前一個步驟的輸出：

```python
from google.adk.agents import SequentialAgent

# Define individual agents
research_agent = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Research the given topic thoroughly",
    output_key="research_results"
)
writer_agent = Agent(
    name="writer",
    model="gemini-2.5-flash",
    instruction="Write a comprehensive article based on the research: {research_results}",
    output_key="article_draft"
)
editor_agent = Agent(
    name="editor",
    model="gemini-2.5-flash",
    instruction="Edit and improve the article: {article_draft}",
    output_key="final_article"
)

# Create sequential workflow
content_pipeline = SequentialAgent(
    name="content_creation_pipeline",
    sub_agents=[research_agent, writer_agent, editor_agent],
    description="Complete content creation from research to publication"
)
```

### 序列工作流程執行

**執行流程**:

    User Query → Research Agent → Writer Agent → Editor Agent → Final Result
    1. Research agent gets user query
    2. Research agent saves results to state['research_results']
    3. Writer agent reads {research_results} from instruction
    4. Writer agent saves draft to state['article_draft']
    5. Editor agent reads {article_draft} from instruction
    6. Editor agent produces final output

### 進階序列模式

**條件分支**:

```python
# Dynamic routing based on content type
def route_by_topic(context, result):
    topic = result.get('topic', '').lower()
    if 'technical' in topic:
        return 'tech_writer'
    elif 'business' in topic:
        return 'business_writer'
    else:
        return 'general_writer'

routing_agent = Agent(
    name="router",
    model="gemini-2.5-flash",
    instruction="Analyze the topic and determine content type",
    output_key="topic_analysis"
)
tech_writer = Agent(name="tech_writer", ...)
business_writer = Agent(name="business_writer", ...)
general_writer = Agent(name="general_writer", ...)

# Sequential with dynamic agent selection
content_workflow = SequentialAgent(
    sub_agents=[routing_agent],  # Start with router
    dynamic_agents={
        'tech_writer': tech_writer,
        'business_writer': business_writer,
        'general_writer': general_writer
    },
    routing_function=route_by_topic
)
```

---

## ⚡ 平行工作流程 (Fan-out/Gather)

### 基本平行模式

**心智模型**: 獨立任務同時執行，然後合併結果：

```python
from google.adk.agents import ParallelAgent

# Research different aspects in parallel
web_research_agent = Agent(
    name="web_researcher",
    model="gemini-2.5-flash",
    tools=[google_search],
    instruction="Research topic using web search",
    output_key="web_findings"
)
database_research_agent = Agent(
    name="db_researcher",
    model="gemini-2.5-flash",
    tools=[database_tool],
    instruction="Search internal database for relevant data",
    output_key="db_findings"
)
expert_opinion_agent = Agent(
    name="expert_consultant",
    model="gemini-2.5-flash",
    tools=[expert_tool],
    instruction="Consult domain experts on the topic",
    output_key="expert_insights"
)

# Execute all research in parallel
parallel_research = ParallelAgent(
    name="comprehensive_research",
    sub_agents=[web_research_agent, database_research_agent, expert_opinion_agent],
    description="Research topic from multiple sources simultaneously"
)
```

### 平行執行流程

Fan-out → Execute → Gather:

    User Query
        │
    ┌─── Fan-out ───┐
    │               │
┌───▼──┐  ┌───▼──┐  ┌───▼───┐
│ Web  │  │  DB  │  │Expert │
│Search│  │Search│  │Consult│
└───┬──┘  └───┬──┘  └───┬───┘
    │         │         │
    └─── Gather ────────┘
         │
    Merge Results
         │
    Final Synthesis

### 平行與序列合併

**完整的調查流程**:

```python
# Parallel research phase
parallel_research = ParallelAgent(
    sub_agents=[web_agent, db_agent, expert_agent]
)

# Sequential synthesis phase
synthesis_agent = Agent(
    name="synthesizer",
    model="gemini-2.5-flash",
    instruction="""
    Synthesize findings from multiple sources:
    Web: {web_findings}
    Database: {db_findings}
    Experts: {expert_insights}
    Create a comprehensive report.
    """,
    output_key="final_report"
)

# Complete workflow: Parallel → Sequential
research_pipeline = SequentialAgent(
    sub_agents=[parallel_research, synthesis_agent]
)
```

---

## 🔁 循環工作流程 (迭代優化)

### 基本循環模式

**心智模型**: 重複直到滿足品質標準或達到最大迭代次數：

```python
from google.adk.agents import LoopAgent

# Content generator
writer_agent = Agent(
    name="content_writer",
    model="gemini-2.5-flash",
    instruction="Write content on the topic: {topic}",
    output_key="content_draft"
)

# Quality critic
critic_agent = Agent(
    name="content_critic",
    model="gemini-2.5-flash",
    instruction="""
    Evaluate the content quality: {content_draft}
    Rate on scale 1-10 for:
    - Accuracy
    - Completeness
    - Clarity
    - Engagement
    If score < 8, provide specific improvement suggestions.
    """,
    output_key="critique"
)

# Improvement refiner
refiner_agent = Agent(
    name="content_refiner",
    model="gemini-2.5-flash",
    instruction="""
    Improve the content based on critique: {critique}
    Original: {content_draft}
    Address all the critic's suggestions.
    """,
    output_key="improved_content"
)

# Iterative refinement loop
quality_loop = LoopAgent(
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=5,
    description="Iteratively improve content until quality standards are met"
)
```

### 循環執行流程

**Generate → Critique → Refine → Repeat**:

    Initial Content
           │
        ┌──▼──┐
        │Critic│ ←──┐
        └─────┘     │
           │       │
        Critique    │
           │       │
        ┌──▼───┐    │
        │Refine│    │
        └──────┘    │
           │       │
      Improved      │
    Quality Check   │
       ├─ Good ─────┘
       └─ Poor ──────┐
              │
     Continue Loop
 (up to max_iterations)

### 進階循環模式

**條件退出**:

```python
def should_continue_loop(context, result):
    """Custom exit condition"""
    critique = result.get('critique', '')
    score = extract_score_from_critique(critique)
    return score < 8  # Continue if quality < 8/10

quality_loop = LoopAgent(
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=5,
    exit_condition=should_continue_loop,
    description="Iterative refinement with quality threshold"
)
```

**多代理循環**:

```python
# Complex iterative process
brainstorm_agent = Agent(name="brainstormer", ...)
designer_agent = Agent(name="designer", ...)
developer_agent = Agent(name="developer", ...)
tester_agent = Agent(name="tester", ...)

# Development cycle
development_loop = LoopAgent(
    sub_agents=[designer_agent, developer_agent, tester_agent],
    max_iterations=10,
    description="Iterative product development cycle"
)
```

---

## [FLOW] 複雜工作流程組合

### 巢狀工作流程

**心智模型**: 工作流程可以包含其他工作流程，以進行分層組織：

```python
# Level 1: Individual research tasks
web_agent = Agent(name="web_researcher", ...)
api_agent = Agent(name="api_researcher", ...)
file_agent = Agent(name="file_analyzer", ...)

# Level 2: Parallel research
research_team = ParallelAgent(
    sub_agents=[web_agent, api_agent, file_agent]
)

# Level 3: Sequential processing
processing_pipeline = SequentialAgent(
    sub_agents=[
        research_team,      # Parallel research
        data_cleaner,       # Sequential processing
        analyzer,           # Sequential processing
        reporter            # Sequential processing
    ]
)

# Level 4: Quality loop
quality_assurance = LoopAgent(
    sub_agents=[processing_pipeline, quality_checker, improver],
    max_iterations=3
)
```

### 真實世界範例：內容創作流程

```python
# 1. Research Phase (Parallel)
research_sources = ParallelAgent(
    sub_agents=[
        web_research_agent,
        academic_search_agent,
        social_media_monitor
    ]
)

# 2. Content Generation (Sequential)
content_creation = SequentialAgent(
    sub_agents=[
        outline_writer,
        draft_writer,
        fact_checker
    ]
)

# 3. Review & Editing (Loop)
editing_cycle = LoopAgent(
    sub_agents=[
        editor_agent,
        proofreader_agent,
        final_reviewer
    ],
    max_iterations=3
)

# 4. Publication (Sequential)
publication_pipeline = SequentialAgent(
    sub_agents=[
        seo_optimizer,
        formatter_agent,
        publisher_agent
    ]
)

# Complete Content Pipeline
content_workflow = SequentialAgent(
    sub_agents=[
        research_sources,      # Parallel
        content_creation,      # Sequential
        editing_cycle,         # Loop
        publication_pipeline   # Sequential
    ]
)
```

---

## 🎯 工作流程決策框架

### 何時使用每種模式

| 場景 | 序列 | 平行 | 循環 |
| :--- | :--- | :--- | :--- |
| 順序重要 | ✅ 是 | ❌ 否 | ❌ 否 |
| 獨立任務 | ❌ 否 | ✅ 是 | ❌ 否 |
| 需要速度 | ❌ 否 | ✅ 是 | ❌ 否 |
| 迭代優化 | ❌ 否 | ❌ 否 | ✅ 是 |
| 品質 > 速度 | ❌ 否 | ❌ 否 | ✅ 是 |
| 依賴性 | ✅ 是 | ❌ 否 | 🤔 可能 |

### 工作流程選擇指南

    Need to orchestrate multiple agents?
    │
    ├─ Steps depend on each other?
    │  ├─ Simple dependency chain?
    │  │  └─ SequentialAgent
    │  └─ Complex dependencies?
    │     └─ SequentialAgent + state routing
    │
    ├─ Steps are independent?
    │  ├─ Need results combined?
    │  │  └─ ParallelAgent + Sequential merger
    │  └─ Can process separately?
    │     └─ ParallelAgent (fire and forget)
    │
    ├─ Need iterative improvement?
    │  ├─ Quality refinement?
    │  │  └─ LoopAgent (critic + refiner)
    │  └─ Progressive enhancement?
    │     └─ LoopAgent (multi-stage improvement)
    │
    └─ Complex combination?
        └─ Nested workflows (Parallel + Sequential + Loop)

---

## ⚡ 性能優化

### 平行執行的好處

**速度提升**:

*   **獨立任務**: 3 個平行代理速度提升 3 倍
*   **I/O 綁定**: 網路請求、API 呼叫、文件操作
*   **CPU 綁定**: 分配給具有不同模型的代理

**成本考量**:

*   **Token 效率**: 總 Token 相同，執行速度更快
*   **模型選擇**: 為平行任務使用較小的模型
*   **快取**: 快取中間結果以避免重新計算

### 優化策略

**批次處理**:

```python
# Process multiple items in parallel
batch_processor = ParallelAgent(
    sub_agents=[
        Agent(name="item_1_processor", ...),
        Agent(name="item_2_processor", ...),
        Agent(name="item_3_processor", ...)
    ]
)

# More efficient than sequential processing
sequential_processor = SequentialAgent(
    sub_agents=[item_1_processor, item_2_processor, item_3_processor]
)
```

**提早退出優化**:

```python
# Stop when good enough
quality_loop = LoopAgent(
    sub_agents=[generator, critic, improver],
    max_iterations=10,
    exit_condition=lambda ctx, res: res.get('quality_score', 0) >= 9
)
```

---

## 🔍 調試工作流程

### 狀態檢查

**追蹤數據流**:

```python
# Enable state logging
import logging
logging.getLogger('google.adk.agents').setLevel(logging.DEBUG)

# Inspect state at each step
result = await runner.run_async(query)
for event in result.events:
    if 'state' in event:
        print(f"Step: {event.step}")
        print(f"State: {event.state}")
```

### 工作流程可視化

**執行圖**:

```python
# Generate workflow diagram
workflow_graph = content_pipeline.get_execution_graph()
print(workflow_graph)  # Mermaid diagram

# Analyze bottlenecks
performance_report = content_pipeline.analyze_performance()
print(performance_report)  # Timing, bottlenecks, optimization suggestions
```

### 常見問題與解決方案

| 問題 | 症狀 | 解決方案 |
| :--- | :--- | :--- |
| 狀態未傳遞 | 代理無法訪問先前結果 | 檢查 `output_key` 和狀態插值 |
| 平行減速 | 序列執行而非平行 | 驗證代理是否真正獨立 |
| 循環永不退出 | 無限優化循環 | 設置 `max_iterations`，添加退出條件 |
| 記憶體膨脹 | 狀態變得過大 | 使用 `temp:` 範圍，清理中間數據 |
| 競爭條件 | 非確定性結果 | 確保適當的狀態同步 |

---

## 📚 相關主題

*   **[代理架構 →](/adk_training/docs/agent-architecture)**: 個別代理設計
*   **[工具與能力 →](/adk_training/docs/tools-capabilities)**: 代理能做什麼
*   **[LLM 整合 →](/adk_training/docs/llm-integration)**: LLM 如何驅動工作流程

### 🎓 實作教學

*   **[教學 04: 序列工作流程](/adk_training/docs/sequential_workflows)**: 建立有序的代理流程
*   **[教學 05: 平行處理](/adk_training/docs/parallel_processing)**: 同時運行代理以提高速度
*   **[教學 06: 多代理系統](/adk_training/docs/multi_agent_systems)**: 複雜的代理協調
*   **[教學 07: 循環代理](/adk_training/docs/loop_agents)**: 迭代優化模式

## 🎯 關鍵要點

1.  **序列**: 用於有序、依賴的步驟 (裝配線)
2.  **平行**: 用於獨立任務 (fan-out/gather)
3.  **循環**: 用於迭代優化 (critic/refiner 模式)
4.  **組合**: 巢狀工作流程以實現複雜的層次結構
5.  **性能**: 平行執行以提高速度，序列執行以處理依賴性
6.  **狀態流**: 使用 `output_key` 和插值進行數據傳遞

**🔗 下一步**: 學習 [LLM 整合](/adk_training/docs/llm-integration) 以了解語言模型如何驅動這些工作流程。
