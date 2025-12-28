
# GEPA 最佳化代理

本文檔概述了 GEPA (近似遺傳演算法的提示分析) 最佳化代理的架構和工作流程，參考 [gepa_optimizer.py](./gepa_optimizer.py)。

## `RealGEPAOptimizer` 呼叫流程

`RealGEPAOptimizer` 類別透過一個包含「收集、反思、演化、評估、選擇」的迭代循環來自動最佳化 LLM 提示。

下面的序列圖展示了 `optimize` 方法的核心邏輯：

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Optimizer as RealGEPAOptimizer
    participant LLM_Reflect as 反思模型 (LLM)
    participant LLM_Evolve as 演化模型 (LLM)

    User->>Optimizer: optimize(初始提示, 測試情境)
    loop 每次迭代
        Optimizer->>Optimizer: collect_phase(目前提示, 測試情境)
        note right of Optimizer: 平行執行所有情境
        Optimizer-->>Optimizer: 執行結果, 失敗案例

        Optimizer->>LLM_Reflect: reflect_phase(提示, 失敗案例)
        LLM_Reflect-->>Optimizer: 改進建議

        Optimizer->>LLM_Evolve: evolve_phase(提示, 改進建議)
        LLM_Evolve-->>Optimizer: 演化後的提示

        Optimizer->>Optimizer: evaluate_phase(演化後的提示, 測試情境)
        note right of Optimizer: 再次執行所有情境
        Optimizer-->>Optimizer: 演化結果, 演化成功率

        Optimizer->>Optimizer: select_phase(目前版本, 演化版本)
        Optimizer-->>Optimizer: 選定的提示, 選定的成功率
    end
    Optimizer-->>User: 最佳化結果
```

## `BaseTool` 類別圖

此圖表說明了構成代理工具集基礎的 `BaseTool` 抽象類別及其各種具體實作。

```mermaid
classDiagram
    direction TB
    class BaseTool {
        <<abstract>>
        +name: str
        +description: str
        +is_long_running: bool
        +custom_metadata: Optional[dict]
        +__init__(name, description, is_long_running, custom_metadata)
        #_get_declaration(): Optional[FunctionDeclaration]
        +run_async(args, tool_context): Any
        +process_llm_request(tool_context, llm_request): None
        #_api_variant(): GoogleLLMVariant
        +from_config(config, config_abs_path): SelfTool
    }

    class BaseRetrievalTool {
        +__init__(name, description)
        +override _get_declaration(): FunctionDeclaration
    }

    class LlamaIndexRetrieval {
        +__init__(name, description, retriever)
        +override run_async(args, tool_context): Any
    }

    class VertexAiRagRetrieval {
        +__init__(name, description, rag_corpora, rag_resources, similarity_top_k, vector_distance_threshold)
        +override process_llm_request(tool_context, llm_request): None
        +override run_async(args, tool_context): Any
    }

    class SetModelResponseTool {
        +output_schema: type[BaseModel]
        +func: Callable
        +__init__(output_schema)
        +override _get_declaration(): Optional[FunctionDeclaration]
        +override run_async(args, tool_context): dict
    }

    class FunctionTool {
        #func: Callable
        #__init__(func, name, description, is_long_running, custom_metadata)
        #_get_declaration(): Optional[FunctionDeclaration]
        #run_async(args, tool_context): Any
    }

    class TransferToAgentTool {
        -agent_names: list[str]
        +__init__(agent_names)
        +override _get_declaration(): Optional[FunctionDeclaration]
    }

    class UrlContextTool {
        +__init__()
        +override process_llm_request(tool_context, llm_request): None
    }

    class VertexAiSearchTool {
        +data_store_id: Optional[str]
        +data_store_specs: Optional[list[VertexAISearchDataStoreSpec]]
        +search_engine_id: Optional[str]
        +filter: Optional[str]
        +max_results: Optional[int]
        +bypass_multi_tools_limit: bool
        +__init__(data_store_id, data_store_specs, search_engine_id, filter, max_results, bypass_multi_tools_limit)
        +override process_llm_request(tool_context, llm_request): None
    }

    BaseTool <|-- BaseRetrievalTool
    BaseRetrievalTool <|-- LlamaIndexRetrieval
    BaseRetrievalTool <|-- VertexAiRagRetrieval
    BaseTool <|-- SetModelResponseTool
    BaseTool <|-- FunctionTool
    FunctionTool <|-- TransferToAgentTool
    BaseTool <|-- UrlContextTool
    BaseTool <|-- VertexAiSearchTool

    FunctionDeclaration --o BaseTool : uses >
    ToolContext --o BaseTool : uses >
    LlmRequest --o BaseTool : uses >
    BaseModel --o SetModelResponseTool : uses >
    types.VertexRagStore --o VertexAiRagRetrieval : uses >
    types.VertexAISearch --o VertexAiSearchTool : uses >

```