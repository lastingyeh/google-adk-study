# Google ADK Agents 分析報告

> 本報告分析 Google ADK 代理目錄中的所有主要代理程式，提供詳細的功能、工具使用和技術特色分析。

## 代理分析表格

| 代理名稱                    | 描述                                                 | 使用工具                                                                                                                      | 特色                                                                       | 外部工具                                 | 標籤                                    |
| --------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------- | --------------------------------------- |
| hello-agent                 | 簡單的友善對話代理，作為入門教學                     | -                                                                                                                             | 基礎對話                                                                   | -                                        | 教學, 入門, Gemini 2.0 Flash            |
| finance-assistant           | 財務計算助理，提供複利和貸款計算功能                 | FunctionTool (calculate_compound_interest, calculate_loan_payment)                                                            | 工具呼叫, 財務計算                                                         | -                                        | 財務, 計算, 複利, 貸款                  |
| chuck-norris-agent          | Chuck Norris 笑話代理，展示 OpenAPI 工具整合         | OpenAPIToolset (Chuck Norris API)                                                                                             | OpenAPI 整合                                                               | Chuck Norris API                         | OpenAPI, API 整合, 娛樂                 |
| blog-pipeline               | 部落格創建流水線，展示循序代理工作流程               | -                                                                                                                             | SequentialAgent, 多代理協作, 狀態共享                                      | -                                        | 工作流程, 序列代理, 內容創作            |
| travel-planner              | 旅遊規劃系統，展示並行處理與扇出/聚合模式            | -                                                                                                                             | ParallelAgent, SequentialAgent, 並發執行                                   | -                                        | 並行處理, 旅遊, 多代理                  |
| content-publisher           | 內容發布系統，結合並行研究與循序精煉                 | google_search                                                                                                                 | ParallelAgent, SequentialAgent, 多重管線                                   | Google Search                            | 內容發布, 研究, 多代理系統              |
| essay-refiner               | 論文精煉系統，展示迴圈代理與退出條件                 | FunctionTool (exit_loop)                                                                                                      | LoopAgent, SequentialAgent, 迭代精煉                                       | -                                        | 迴圈代理, 論文寫作, 迭代優化            |
| personal-tutor              | 個人化學習導師，展示狀態與記憶管理                   | FunctionTool (set_user_preferences, record_topic_completion, get_user_progress, start_learning_session, calculate_quiz_grade) | 狀態管理, 記憶服務, 使用者偏好                                             | -                                        | 教育, 狀態管理, 個人化, 記憶            |
| content-moderator           | 內容審查助理，展示回呼與防護措施                     | -                                                                                                                             | Callbacks, Guardrails, PII 過濾, 速率限制                                  | -                                        | 內容審查, 安全, 回呼, 防護              |
| support-agent               | 客戶支援代理，展示可測試模式                         | FunctionTool (search_knowledge_base, create_ticket, check_ticket_status)                                                      | 結構化輸出, 知識庫                                                         | -                                        | 客戶支援, 工單系統, 測試                |
| grounding-agent             | 接地代理，展示 Google Search 和 Maps Grounding       | google_search, google_maps_grounding, FunctionTool (analyze_search_results, save_research_findings)                           | Grounding, 搜尋增強                                                        | Google Search, Google Maps (Vertex AI)   | 接地, 搜尋, 地圖, 研究                  |
| strategic-solver            | 策略問題解決器，展示規劃器與思考配置                 | FunctionTool (analyze_market, calculate_roi, assess_risk, generate_strategy)                                                  | BuiltInPlanner, PlanReActPlanner, BasePlanner, 進階推理                    | -                                        | 規劃器, 策略, 商業分析, 推理            |
| code-calculator             | 金融計算器，展示程式碼執行能力                       | -                                                                                                                             | BuiltInCodeExecutor, Python 程式碼執行                                     | -                                        | 程式碼執行, 財務, 計算, Gemini 2.0      |
| streaming-agent             | 串流代理，展示 SSE 即時回應                          | -                                                                                                                             | Streaming, SSE, 即時輸出                                                   | -                                        | 串流, SSE, 即時                         |
| voice-assistant             | 語音助理，展示 Live API 雙向串流                     | -                                                                                                                             | Live API, 雙向串流, 音訊處理, 語音輸入輸出                                 | PyAudio                                  | 語音, Live API, 音訊, 即時對話          |
| mcp-agent                   | MCP 代理，展示 Model Context Protocol 整合與人工介入 | McpToolset (檔案系統操作)                                                                                                     | MCP 整合, Human-in-the-Loop, 檔案操作                                      | MCP 檔案系統伺服器                       | MCP, HITL, 檔案系統, 安全               |
| a2a-orchestrator            | 代理對代理協調器，展示 A2A 通訊                      | FunctionTool (check_agent_availability, log_coordination_step)                                                                | RemoteA2aAgent, 分散式代理, 協調                                           | -                                        | A2A, 協調, 分散式, 遠端代理             |
| observability-agent         | 可觀測性代理，展示事件追蹤與監控                     | FunctionTool (check_order_status, process_refund, check_inventory)                                                            | Events, EventActions, 指標收集, 監控                                       | -                                        | 可觀測性, 事件, 監控, 指標              |
| artifact-agent              | Artifacts 代理，展示檔案管理與版本控制               | FunctionTool (extract_text_tool, summarize_document_tool, translate_document_tool), load_artifacts_tool                       | Artifacts 儲存, 版本控制, 文件處理                                         | -                                        | Artifacts, 文件, 版本控制, 翻譯         |
| customer-support            | 客戶支援代理，從 YAML 設定載入                       | -                                                                                                                             | YAML 設定                                                                  | -                                        | 客戶支援, YAML, 設定                    |
| vision-catalog-agent        | 視覺目錄代理，展示多模態與影像處理                   | FunctionTool (圖片工具)                                                                                                       | MultiModal, 影像處理, 產品分析                                             | PIL/Pillow                               | 視覺, 多模態, 影像, 產品目錄            |
| model-selector              | 模型選擇器，展示模型評測與比較                       | FunctionTool (recommend_model_for_use_case, get_model_info)                                                                   | 模型評測, 基準測試, 並行測試                                               | -                                        | 模型選擇, 評測, 效能, 成本分析          |
| software-bug-assistant      | 軟體錯誤助理，整合多種工具                           | FunctionTool (get_current_date), search_tool, langchain_tool, toolbox_tools, mcp_tools                                        | LangChain 整合, MCP 整合                                                   | LangChain, MCP, Toolbox                  | 除錯, 軟體開發, 工具整合                |
| youtube-shorts-assistant    | YouTube Shorts 助理，多代理影片創作系統              | AgentTool (scriptwriter_agent, visualizer_agent, formatter_agent)                                                             | LlmAgent, 多代理工作流                                                     | -                                        | 影片創作, YouTube, 多代理               |
| production-agent            | 生產環境部署代理，展示部署策略                       | FunctionTool (check_deployment_status, get_deployment_options, get_best_practices)                                            | 部署指導, 最佳實踐                                                         | FastAPI, Cloud Run, Agent Engine, GKE    | 部署, 生產環境, DevOps, 最佳實踐        |
| observability-plugins-agent | 進階可觀測性代理，展示外掛程式架構                   | -                                                                                                                             | Plugins, MetricsCollectorPlugin, AlertingPlugin, PerformanceProfilerPlugin | -                                        | 可觀測性, 外掛, 監控, 警報              |
| best-practices-agent        | 最佳實踐代理，展示生產就緒模式                       | 使用 Pydantic 驗證的多種工具                                                                                                  | Pydantic 驗證, 斷路器, 重試邏輯, 快取                                      | -                                        | 最佳實踐, 驗證, 錯誤處理, 效能          |
| enterprise-agent            | 企業級代理，展示 Gemini Enterprise 部署              | FunctionTool (check_company_size, score_lead, get_competitive_intel)                                                          | 企業部署, 潛在客戶評分                                                     | CRM 系統, 企業資料庫                     | 企業, 銷售, 合規, Gemini Enterprise     |
| third-party-agent           | 第三方工具整合代理，展示外部框架整合                 | LangchainTool (Wikipedia, DuckDuckGo), CrewAI 工具                                                                            | LangChain 整合, CrewAI 整合                                                | LangChain, CrewAI, Wikipedia, DuckDuckGo | 第三方整合, LangChain, CrewAI           |
| multi-llm-agent             | 多 LLM 代理，展示透過 LiteLLM 使用多種模型           | FunctionTool (calculate_square, get_weather, analyze_sentiment)                                                               | LiteLLM 整合, 多模型支援                                                   | LiteLLM, OpenAI, Anthropic, Ollama       | 多模型, LiteLLM, OpenAI, Claude, Ollama |
| data-analysis-dashboard     | 資料分析儀表板，整合 AG-UI 與 pandas                 | FunctionTool (load_csv_data, analyze_data, visualize_data)                                                                    | AG-UI 整合, 資料分析, 視覺化                                               | AG-UI, pandas, FastAPI                   | 資料分析, 視覺化, AG-UI, 儀表板         |
| data-analysis-agent         | 資料分析代理，多代理數據分析系統                     | FunctionTool (analyze_column, calculate_correlation, filter_data), AgentTool (visualization_agent)                            | 多代理協作, 資料分析                                                       | -                                        | 資料分析, 統計, 視覺化                  |
| support-bot                 | 團隊支援機器人，提供知識庫與工單功能                 | FunctionTool (search_knowledge_base, create_ticket)                                                                           | 知識庫, 工單系統                                                           | -                                        | 支援, 知識庫, 工單                      |
| pubsub-agent                | 文件處理代理，展示 Pydantic 結構化輸出               | AgentTool (多個專門文件處理子代理)                                                                                            | Pydantic Schema, 結構化輸出, 多代理                                        | -                                        | 文件處理, Pydantic, 結構化輸出          |
| policy-navigator            | 企業合規與政策導航器，多代理系統                     | FunctionTool (upload_policy_documents, search_policies, check_compliance_risk, generate_policy_summary)                       | 多代理協調, File Search, 合規檢查                                          | File Search stores                       | 合規, 政策, 企業, 搜尋                  |
| context-compaction-agent    | 上下文壓縮代理，展示長對話優化                       | FunctionTool (summarize_text, calculate_complexity)                                                                           | Context Compaction, Token 優化                                             | -                                        | 上下文壓縮, 長對話, 優化                |
| pause-resume-agent          | 暫停恢復代理，展示長期執行工作流                     | FunctionTool (process_data_chunk, validate_checkpoint, get_resumption_hint)                                                   | Resumability, 檢查點, 狀態保存                                             | -                                        | 暫停恢復, 檢查點, 長期任務              |
| tool-use-evaluator          | 工具使用評估代理，展示工具排序與品質                 | FunctionTool (analyze_data, extract_features, validate_quality, apply_model)                                                  | 工具排序評估, 品質檢查                                                     | -                                        | 評估, 工具使用, 品質                    |
| custom-session-agent        | 自定義會話服務代理，展示 Redis 會話管理              | -                                                                                                                             | Redis 整合, 服務註冊, 會話管理                                             | Redis                                    | 會話, Redis, 服務註冊                   |
| commerce-agent-e2e          | 商務代理，運動產品搜尋與推薦                         | FunctionTool (search_products, save_preferences, get_preferences)                                                             | Grounding Callback, 使用者偏好                                             | Google Search                            | 電商, 產品搜尋, 推薦                    |
| deep-research-agent         | 深度研究代理，使用 Deep Research API                 | -                                                                                                                             | Deep Research API, 長時間研究, 引用提取                                    | Google Deep Research API, Vertex AI      | 研究, 深度分析, 引用                    |
| customer-support-agent      | 客戶支援代理，整合 AG-UI 的 Next.js 應用             | FunctionTool (search_knowledge_base, lookup_order_status, create_support_ticket)                                              | AG-UI 整合, Next.js 前端                                                   | AG-UI, Next.js, FastAPI                  | 客戶支援, AG-UI, Web 應用               |

## 分類統計

### 按功能分類

- **基礎教學**: hello-agent
- **工具整合**: finance-assistant, chuck-norris-agent, code-calculator, grounding-agent
- **工作流程**: blog-pipeline, travel-planner, content-publisher, essay-refiner
- **狀態與記憶**: personal-tutor, artifact-agent, custom-session-agent
- **控制與測試**: content-moderator, support-agent, observability-agent, tool-use-evaluator
- **規劃與推理**: strategic-solver
- **進階互動**: streaming-agent, voice-assistant, interactions-api-basic
- **多模態**: vision-catalog-agent
- **整合**: mcp-agent, a2a-orchestrator, enterprise-agent, third-party-agent, multi-llm-agent, customer-support-agent, data-analysis-dashboard, data-analysis-agent, adk-interactions-integration, mcp-a2a-master, pack-adk-a2a-agent
- **核心架構**: customer-support, model-selector, production-agent, best-practices-agent, context-compaction-agent, pause-resume-agent
- **應用**: software-bug-assistant, youtube-shorts-assistant, support-bot, pubsub-agent, commerce-agent-e2e, policy-navigator, deep-research-agent
- **可觀測性**: observability-plugins-agent, math-agent-otel

### 主要技術特色

1. **代理類型**

   - SequentialAgent: 循序執行代理
   - ParallelAgent: 並行執行代理
   - LoopAgent: 迴圈代理
   - RemoteA2aAgent: 遠端代理對代理通訊

2. **工具整合**

   - FunctionTool: 自定義函數工具
   - OpenAPIToolset: OpenAPI 規範工具
   - McpToolset: Model Context Protocol 工具
   - AgentTool: 代理工具（用於多代理協作）
   - LangchainTool: LangChain 工具整合

3. **進階功能**

   - Grounding: 搜尋增強（Google Search, Google Maps）
   - Code Execution: 程式碼執行能力
   - Streaming: 串流輸出
   - Live API: 即時雙向通訊
   - Multimodal: 多模態處理（文字、圖片、語音）
   - Context Compaction: 上下文壓縮
   - Resumability: 暫停與恢復

4. **生產功能**

   - Callbacks: 回呼機制
   - Guardrails: 防護措施
   - Events: 事件追蹤
   - Plugins: 外掛程式架構
   - Pydantic 驗證: 結構化輸出與驗證
   - YAML 設定: 宣告式配置

5. **外部整合**
   - LiteLLM: 多 LLM 支援（OpenAI, Claude, Ollama）
   - LangChain/CrewAI: 第三方框架
   - AG-UI: 生成式 UI 整合
   - Redis: 會話管理
   - Cloud Services: Cloud Run, GKE, Vertex AI

## 學習路徑建議

### 初學者

1. hello-agent - 了解基礎
2. finance-assistant - 學習工具使用
3. streaming-agent - 理解串流輸出

### 中級

4. blog-pipeline - 循序工作流程
5. travel-planner - 並行處理
6. personal-tutor - 狀態管理
7. grounding-agent - 搜尋增強

### 進階

8. a2a-orchestrator - 分散式代理
9. mcp-agent - MCP 協議整合
10. multi-llm-agent - 多模型整合
11. best-practices-agent - 生產最佳實踐

### 專業應用

12. commerce-agent-e2e - 端到端電商應用
13. policy-navigator - 企業合規系統
14. production-agent - 生產環境部署
15. deep-research-agent - 深度研究應用

---

**生成時間**: 2025 年 12 月 24 日
**分析範圍**: /Users/cfh00543956/Desktop/Labs/google-adk-study/workspace/python/agents
**代理總數**: 42 個主要代理
