# Agent Structure Analysis

This document provides a hierarchical analysis of all agents found in `workspace/python/agents`.

## 1. hello-agent
- **Root Agent:** `hello_assistant`
  - **Type:** Agent
  - **Description:** A friendly AI assistant for general conversation.
  - **Tools:** None

## 2. finance-assistant
- **Root Agent:** `finance_assistant`
  - **Type:** Agent
  - **Description:** A financial calculation assistant.
  - **Tools:**
    - `calculate_compound_interest(principal: float, annual_rate: float, years: int, compounds_per_year: int) -> dict`
    - `calculate_loan_payment(loan_amount: float, annual_rate: float, years: int) -> dict`
    - `calculate_monthly_savings(target_amount: float, years: int, annual_return: float) -> dict`

## 3. blog-pipeline
- **Root Agent:** `BlogCreationPipeline`
  - **Type:** SequentialAgent
  - **Description:** Complete blog post creation pipeline from research to publishing.
  - **Sub-Agents:**
    1. `researcher` (Agent) - Researches topic and gathers key facts.
    2. `writer` (Agent) - Writes blog post draft based on research.
    3. `editor` (Agent) - Reviews blog post draft and provides feedback.
    4. `formatter` (Agent) - Applies editorial feedback and formats final post.

## 4. chuck-norris-agent
- **Root Agent:** `chuck_norris_agent`
  - **Type:** Agent
  - **Description:** Chuck Norris fact assistant using OpenAPI tools.
  - **Toolsets:**
    - `chuck_norris_toolset` (OpenAPIToolset) - Provides tools from Chuck Norris API (`get_random_joke`, `search_jokes`, `get_categories`).

## 5. code-calculator
- **Root Agent:** `FinancialCalculator`
  - **Type:** Agent
  - **Description:** Expert financial calculator with Python code execution.
  - **Capabilities:**
    - `BuiltInCodeExecutor` - Allows execution of Python code for calculations.

## 6. content-moderator
- **Root Agent:** `content_moderator`
  - **Type:** Agent
  - **Description:** Content moderation assistant with safety guardrails.
  - **Tools:**
    - `generate_text(topic: str, word_count: int, tool_context: ToolContext) -> Dict[str, Any]`
    - `check_grammar(text: str, tool_context: ToolContext) -> Dict[str, Any]`
    - `get_usage_stats(tool_context: ToolContext) -> Dict[str, Any]`
  - **Callbacks:**
    - `before_agent_callback`
    - `after_agent_callback`
    - `before_model_callback`
    - `after_model_callback`
    - `before_tool_callback`
    - `after_tool_callback`

## 7. content-publisher
- **Root Agent:** `ContentPublishingSystem`
  - **Type:** SequentialAgent
  - **Description:** Complete content publishing system with parallel research and sequential creation.
  - **Sub-Agents:**
    1. `ParallelResearch` (ParallelAgent)
       - `NewsPipeline` (SequentialAgent) -> [`news_fetcher`, `news_summarizer`]
       - `SocialPipeline` (SequentialAgent) -> [`social_monitor`, `sentiment_analyzer`]
       - `ExpertPipeline` (SequentialAgent) -> [`expert_finder`, `quote_extractor`]
    2. `article_writer` (Agent)
    3. `article_editor` (Agent)
    4. `article_formatter` (Agent)

## 8. customer-support
- **Root Agent:** `customer_support`
  - **Type:** Agent (Configured via YAML)
  - **Description:** Customer support agent with various tools.
  - **Tools:**
    - `check_customer_status`
    - `log_interaction`
    - `get_order_status`
    - `track_shipment`
    - `cancel_order`
    - `search_knowledge_base`
    - `run_diagnostic`
    - `create_ticket`
    - `get_billing_history`
    - `process_refund`
    - `update_payment_method`

## 9. enterprise-agent
- **Root Agent:** `lead_qualifier`
  - **Type:** Agent
  - **Description:** Enterprise sales lead qualification agent.
  - **Tools:**
    - `check_company_size(company_name: str) -> Dict[str, Any]`
    - `score_lead(company_size: int, industry: str, budget: str) -> Dict[str, Any]`
    - `get_competitive_intel(company_name: str, competitor: str) -> Dict[str, Any]`

## 10. essay-refiner
- **Root Agent:** `EssayRefinementSystem`
  - **Type:** SequentialAgent
  - **Description:** Complete essay writing and refinement system.
  - **Sub-Agents:**
    1. `InitialWriter` (Agent) - Writes first draft.
    2. `RefinementLoop` (LoopAgent)
       - `Critic` (Agent) - Reviews essay.
       - `Refiner` (Agent) - Refines essay or exits.
         - Tools: `exit_loop(tool_context: ToolContext)`

## 11. grounding-agent
- **Root Agent:** `advanced_grounding_agent` (or `basic_grounding_agent` if VertexAI disabled)
  - **Type:** Agent
  - **Description:** Advanced grounding agent with search, analysis and conditional map tools.
  - **Tools:**
    - `google_search`
    - `google_maps_grounding` (Conditional on VertexAI)
    - `analyze_search_results(query: str, search_content: str, tool_context: ToolContext) -> Dict[str, Any]`
    - `save_research_findings(topic: str, findings: str, tool_context: ToolContext) -> Dict[str, Any]`

## 12. mcp-agent
- **Root Agent:** `mcp_file_assistant`
  - **Type:** Agent
  - **Description:** AI assistant with filesystem access via MCP.
  - **Tools:**
    - `McpToolset` - Connects to filesystem MCP server (tools: `read_file`, `list_directory`, `write_file`, etc.).
  - **Features:** Human-in-the-loop (HITL) approval for destructive operations.

## 13. model-selector
- **Root Agent:** `model_selector_agent`
  - **Type:** Agent
  - **Description:** Expert agent for selecting and comparing AI models.
  - **Tools:**
    - `recommend_model_for_use_case(use_case: str, tool_context: ToolContext) -> Dict[str, Any]`
    - `get_model_info(model_name: str, tool_context: ToolContext) -> Dict[str, Any]`

## 14. multi-llm-agent
- **Root Agent:** `multi_llm_agent`
  - **Type:** Agent
  - **Description:** Multi-LLM agent via LiteLLM supporting OpenAI, Claude, etc.
  - **Model:** LiteLLM (default: `openai/gpt-4o-mini`)
  - **Tools:**
    - `calculate_square(number: int) -> int`
    - `get_weather(city: str) -> dict`
    - `analyze_sentiment(text: str) -> dict`

## 15. observability-agent
- **Root Agent:** `customer_service`
  - **Type:** Agent
  - **Description:** Customer service agent with event tracking.
  - **Tools:**
    - `check_order_status(order_id: str) -> Dict[str, Any]`
    - `process_refund(order_id: str, amount: float) -> Dict[str, Any]`
    - `check_inventory(product_id: str) -> Dict[str, Any]`

## 16. observability-plugins-agent
- **Root Agent:** `observability_plugins_agent`
  - **Type:** Agent
  - **Description:** Production assistant with comprehensive observability plugins.
  - **Plugins:**
    - `MetricsCollectorPlugin`
    - `AlertingPlugin`
    - `PerformanceProfilerPlugin`

## 17. personal-tutor
- **Root Agent:** `personal_tutor`
  - **Type:** Agent
  - **Description:** Personal tutor tracking user progress and preferences.
  - **Tools:**
    - `set_user_preferences`
    - `record_topic_completion`
    - `get_user_progress`
    - `start_learning_session`
    - `calculate_quiz_grade`
    - `search_past_lessons`

## 18. production-agent
- **Root Agent:** `production_deployment_agent`
  - **Type:** Agent
  - **Description:** Expert on production deployment strategies.
  - **Tools:**
    - `check_deployment_status() -> dict`
    - `get_deployment_options() -> dict`
    - `get_best_practices() -> dict`

## 19. software-bug-assistant
- **Root Agent:** `software_bug_assistant`
  - **Type:** Agent
  - **Description:** Software bug assistant.
  - **Tools:**
    - `get_current_date`
    - `search_tool` (AgentTool wrapping `search_agent`)
    - `langchain_tool` (StackExchangeTool)
    - `toolbox_tools` (Google Cloud Toolbox)
    - `mcp_tools` (GitHub MCP)

## 20. strategic-solver
- **Root Agent:** `plan_react_strategic_solver` (Default Root)
  - **Type:** Agent
  - **Description:** Strategic business consultant using PlanReActPlanner.
  - **Planner:** `PlanReActPlanner`
  - **Tools:**
    - `analyze_market`
    - `calculate_roi`
    - `assess_risk`
    - `save_strategy_report`

## 21. streaming-agent
- **Root Agent:** `streaming_assistant`
  - **Type:** Agent
  - **Description:** Helpful assistant providing real-time streaming responses.
  - **Tools:**
    - `format_streaming_info`
    - `analyze_streaming_performance`

## 22. support-agent
- **Root Agent:** `support_agent`
  - **Type:** Agent
  - **Description:** Customer support agent with KB search and ticket creation.
  - **Tools:**
    - `search_knowledge_base(query: str, tool_context: ToolContext) -> Dict[str, Any]`
    - `create_ticket(issue: str, tool_context: ToolContext, priority: str) -> Dict[str, Any]`
    - `check_ticket_status(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]`

## 23. third-party-agent
- **Root Agent:** `third_party_agent`
  - **Type:** Agent
  - **Description:** Agent integrating third-party tools (LangChain, CrewAI).
  - **Tools:**
    - `create_wikipedia_tool` (LangChain)
    - `create_web_search_tool` (LangChain DuckDuckGo)
    - `create_directory_read_tool` (CrewAI)
    - `create_file_read_tool` (CrewAI)

## 24. a2a-orchestrator
- **Root Agent:** `a2a_orchestrator`
  - **Type:** Agent
  - **Description:** Orchestrator agent using ADK A2A to coordinate remote agents.
  - **Sub-Agents:**
    - `research_specialist` (RemoteA2aAgent)
    - `data_analyst` (RemoteA2aAgent)
    - `content_writer` (RemoteA2aAgent)
  - **Tools:**
    - `check_agent_availability`
    - `log_coordination_step`

## 25. artifact-agent
- **Root Agent:** `artifact_agent`
  - **Type:** Agent
  - **Description:** Document processing agent with artifact storage and versioning.
  - **Tools:**
    - `extract_text_tool`
    - `summarize_document_tool`
    - `translate_document_tool`
    - `create_final_report_tool`
    - `list_artifacts_tool`
    - `load_artifact_tool`
    - `load_artifacts_tool` (Built-in)

## 26. best-practices-agent
- **Root Agent:** `best_practices_agent`
  - **Type:** Agent
  - **Description:** Production-ready agent demonstrating best practices.
  - **Tools:**
    - `validate_input_tool`
    - `retry_with_backoff_tool`
    - `circuit_breaker_call_tool`
    - `cache_operation_tool`
    - `batch_process_tool`
    - `health_check_tool`
    - `get_metrics_tool`

## 27. travel-planner
- **Root Agent:** `TravelPlanningSystem`
  - **Type:** SequentialAgent
  - **Description:** Complete travel planning system with parallel search.
  - **Sub-Agents:**
    1. `ParallelSearch` (ParallelAgent)
       - `flight_finder`
       - `hotel_finder`
       - `activity_finder`
    2. `itinerary_builder` (Agent)

## 28. vision-catalog-agent
- **Root Agent:** `vision_catalog_coordinator`
  - **Type:** Agent
  - **Description:** Multimodal visual product catalog coordinator.
  - **Tools:**
    - `list_sample_images`
    - `generate_product_mockup`
    - `analyze_uploaded_image`
    - `analyze_product_image`
    - `compare_product_images`

## 29. voice-assistant
- **Root Agent:** `voice_assistant`
  - **Type:** Agent
  - **Description:** Real-time voice assistant supporting Live API.
  - **Capabilities:** Audio Recording/Playback, Live API Streaming.

## 30. youtube-shorts-assistant
- **Root Agent:** `youtube_shorts_agent`
  - **Type:** LlmAgent
  - **Description:** Agent for creating YouTube Short videos.
  - **Tools:**
    - `scriptwriter_agent` (AgentTool)
    - `visualizer_agent` (AgentTool)
    - `formatter_agent` (AgentTool)
