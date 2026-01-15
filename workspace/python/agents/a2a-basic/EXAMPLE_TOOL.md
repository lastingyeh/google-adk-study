# 範例工具 (Example Tool)

ExampleTool 是代理開發套件 (Agent Development Kit, ADK) 中的一個工具，其功能是透過在大型語言模型 (LLM) 的請求中加入少樣本範例 (few-shot examples) 來增強請求內容。它繼承自 `BaseTool`，主要專注於修改 `LlmRequest` 而非執行獨立操作，因此其 `name` 和 `description` 屬性並不會被用於外部互動。

## 主要特點

*   **目的**：為 LLM 提供少樣本範例，透過已提供的示範來幫助模型理解期望的輸出格式或行為。
*   **初始化**：在初始化時，它接受一個 `Example` 物件列表或一個 `BaseExampleProvider` 的實例。
*   **`process_llm_request` 方法**：這個非同步方法是 ExampleTool 的核心邏輯所在。它會從 `ToolContext` 中檢索使用者的內容，然後使用 `example_util.build_example_si` 將指令附加到 `LlmRequest` 中。這個函式會將已配置的範例與使用者的輸入整合，以供 LLM 使用。
*   **`from_config` 方法**：ExampleTool 可以透過其類別方法 `from_config` 從設定檔中實例化。此方法需要一個 `ExampleToolConfig`，其中可以將範例指定為 `Example` 物件列表，或是一個 `BaseExampleProvider` 物件的完整限定名稱。如果提供的是字串名稱，它會使用 `config_agent_utils.resolve_fully_qualified_name` 來動態載入 `BaseExampleProvider` 實例。
*   **`ExampleToolConfig`**：這個 Pydantic 模型定義了 ExampleTool 的設定結構，允許使用者將範例指定為列表或對 `BaseExampleProvider` 的字串引用。

## 使用範例

`a2a_basic/agent.py` 中展示了如何使用 ExampleTool：
```python
# 定義示例工具，用於引導模型理解對話流程
example_tool = ExampleTool(
    [
        {
            "input": {
                "role": "user",
                "parts": [{"text": "擲一個 6 面骰。"}],
            },
            "output": [{"role": "model", "parts": [{"text": "我為你擲出了 4。"}]}],
        },
        {
            "input": {
                "role": "user",
                "parts": [{"text": "7 是質數嗎？"}],
            },
            "output": [
                {
                    "role": "model",
                    "parts": [{"text": "是的，7 是一個質數。"}],
                }
            ],
        },
        {
            "input": {
                "role": "user",
                "parts": [{"text": "擲一個 10 面骰並檢查它是否為質數。"}],
            },
            "output": [
                {
                    "role": "model",
                    "parts": [{"text": "我為你擲出了 8。"}],
                },
                {
                    "role": "model",
                    "parts": [{"text": "8 不是質數。"}],
                },
            ],
        },
    ]
)
```

## 更多資訊

您可以在 `google/adk-python/src/google/adk/tools/example_tool.py` 中找到 ExampleTool 的定義。它透過 `google/adk-python/src/google/adk/tools/__init__.py` 進行延遲載入，作為工具整合與管理框架的一部分，詳細說明請參閱「核心工具抽象與管理」(Core Tool Abstraction and Management) 的 wiki 章節。
