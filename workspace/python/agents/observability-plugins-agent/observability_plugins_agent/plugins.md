## 補充說明

### BASE PLUGIN 回呼方法詳解
[`BasePlugin`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L41) 類別定義於 `google/adk-python/src/google/adk/plugins/base_plugin.py`，作為 ADK 框架內所有外掛程式的基礎介面。它提供了一套全面的非同步回呼方法，允許外掛程式在代理程式、工具和大型語言模型（LLM）執行生命週期的各個點攔截和修改其行為。這些回呼包括：

### 回呼方法總覽
| 回呼方法                                                                                                  | 觸發時機                            | 目的                                                                                                                                                                                                                                                        | 回傳值                                                                                                                                                                                                                                                                            |
| :-------------------------------------------------------------------------------------------------------- | :---------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`on_user_message_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L114) | 在調用開始前收到使用者訊息時。      | 允許在執行器開始調用前，記錄或修改使用者訊息。                                                                                                                                                                                                              | 一個可選的 [`types.Content`](%2Fgoogle%2Fadk-python%2FCHANGELOG.md#L489)。如果回傳一個值，它將取代使用者訊息。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則正常進行。                                                                                                 |
| [`before_run_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L136)      | 在 ADK 執行器開始執行前。           | 生命週期中的第一個回呼，非常適合用於全域設定或初始化任務。                                                                                                                                                                                                  | 一個可選的 [`Event`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fevents%2Fevent.py#L30)。如果回傳一個值，它將停止執行器的執行，並以該事件結束運行。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則正常進行。                                                          |
| [`on_event_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L155)        | 從執行器產生事件後。                | 允許在事件被底層代理程式應用程式處理前修改事件。                                                                                                                                                                                                            | 一個可選值。非 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 的回傳值可能會修改或取代回應。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則使用原始回應。                                                                                                            |
| [`after_run_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L174)       | 在 ADK 執行器運行完成後。           | 最後一個回呼，適用於清理、最終記錄或報告任務。                                                                                                                                                                                                              | [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546)                                                                                                                                                                                                                                 |
| [`close`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Frunners.py#L1459)                                 | 當執行器關閉時。                    | 用於清理任務，如關閉網路連線或釋放資源。                                                                                                                                                                                                                    | [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546)                                                                                                                                                                                                                                 |
| [`before_agent_callback`](%2Fgoogle%2Fadk-python%2Fcontributing%2Fsamples%2Fcallbacks%2Fagent.py#L69)     | 在代理程式的主要邏輯被調用前。      | 用於記錄、設定或短路代理程式的執行。                                                                                                                                                                                                                        | 一個可選的 [`types.Content`](%2Fgoogle%2Fadk-python%2FCHANGELOG.md#L489)。如果回傳一個值，它將繞過代理程式回呼和執行，直接回傳該值。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則允許代理程式正常進行。                                                               |
| [`after_agent_callback`](%2Fgoogle%2Fadk-python%2Fcontributing%2Fsamples%2Fcallbacks%2Fagent.py#L74)      | 在代理程式的主要邏輯完成後。        | 允許檢查或修改代理程式的回應。                                                                                                                                                                                                                              | 一個可選的 [`types.Content`](%2Fgoogle%2Fadk-python%2FCHANGELOG.md#L489)。如果回傳一個值，它將被用作代理程式回應並附加到事件歷史記錄中。                                                                                                                                          |
| [`before_model_callback`](%2Fgoogle%2Fadk-python%2Fcontributing%2Fsamples%2Fcallbacks%2Fagent.py#L79)     | 在向大型語言模型（LLM）發送請求前。 | 提供一個機會來檢查、記錄或修改 [`LlmRequest`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fmodels%2Fllm_request.py#L49)。也可以通過回傳一個快取的 [`LlmResponse`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fmodels%2Fllm_response.py#L28) 來實現快取。 | 一個可選的 [`LlmResponse`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fmodels%2Fllm_response.py#L28)。非 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 的回傳會觸發提早退出並立即回傳回應。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則允許 LLM 請求正常進行。 |
| [`after_model_callback`](%2Fgoogle%2Fadk-python%2Fcontributing%2Fsamples%2Fcallbacks%2Fagent.py#L84)      | 從大型語言模型（LLM）收到回應後。   | 非常適合用於記錄模型回應、收集 token 使用量的指標，或對原始的 [`LlmResponse`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fmodels%2Fllm_response.py#L28) 進行後處理。                                                                                      | 一個可選的 [`LlmResponse`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fmodels%2Fllm_response.py#L28)。非 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 的回傳可能會修改或取代回應。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則允許使用原始回應。              |
| [`on_model_error_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L272)  | 當 LLM 呼叫遇到錯誤時。             | 提供一個機會來優雅地處理模型錯誤，可能提供替代回應或恢復機制。                                                                                                                                                                                              | 一個可選的 [`LlmResponse`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fmodels%2Fllm_response.py#L28)。如果回傳一個值，它將被用來取代傳播的錯誤。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則允許原始錯誤被引發。                                                   |
| [`before_tool_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L297)     | 在工具被呼叫前。                    | 用於記錄工具使用情況、輸入驗證或在將參數傳遞給工具前修改它們。                                                                                                                                                                                              | 一個可選的字典。如果回傳一個字典，它將停止工具執行並立即回傳此回應。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則使用原始參數。                                                                                                                                       |
| [`after_tool_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L321)      | 在工具被呼叫後。                    | 允許檢查、記錄或修改工具回傳的結果。                                                                                                                                                                                                                        | 一個可選的字典。如果回傳一個字典，它將取代工具的原始結果。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則使用原始、未修改的結果。                                                                                                                                       |
| [`on_tool_error_callback`](%2Fgoogle%2Fadk-python%2Fsrc%2Fgoogle%2Fadk%2Fplugins%2Fbase_plugin.py#L348)   | 當工具呼叫遇到錯誤時。              | 提供一個機會來優雅地處理工具錯誤，可能提供替代回應或恢復機制。                                                                                                                                                                                              | 一個可選的字典。如果回傳一個字典，它將被用作工具回應，而不是傳播錯誤。回傳 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 則允許原始錯誤被引發。                                                                                                                               |

如 [外掛程式架構](#plugin-architecture) 和 [核心外掛程式基礎設施與回呼機制](#plugin-architecture-core-plugin-infrastructure-and-callback-mechanism) 中所述，ADK 中的外掛程式會按照其註冊順序執行，如果回呼回傳非 [`None`](%2Fgoogle%2Fadk-python%2FAGENTS.md#L546) 值，則可以短路執行鏈。這允許外掛程式取得控制權或提供替代結果，繞過後續處理。由外掛程式對輸入參數所做的修改會傳播到鏈中的下一個回呼。

---
### BASE PLUGIN 類別圖
``` mermaid
classDiagram
    class BasePlugin {
        +name: str
        +on_user_message_callback()
        +before_run_callback()
        +on_event_callback()
        +after_run_callback()
        +close()
        +before_agent_callback()
        +after_agent_callback()
        +before_model_callback()
        +after_model_callback()
        +on_model_error_callback()
        +before_tool_callback()
        +after_tool_callback()
        +on_tool_error_callback()
    }
    class LoggingPlugin
    class BigQueryAgentAnalyticsPlugin
    class ContextFilterPlugin
    class GlobalInstructionPlugin
    class MultimodalToolResultsPlugin
    class ReflectAndRetryToolPlugin
    class SaveFilesAsArtifactsPlugin

    BasePlugin <|-- LoggingPlugin
    BasePlugin <|-- BigQueryAgentAnalyticsPlugin
    BasePlugin <|-- ContextFilterPlugin
    BasePlugin <|-- GlobalInstructionPlugin
    BasePlugin <|-- MultimodalToolResultsPlugin
    BasePlugin <|-- ReflectAndRetryToolPlugin
    BasePlugin <|-- SaveFilesAsArtifactsPlugin

```