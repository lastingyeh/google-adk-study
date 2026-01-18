# Reflect and Retry 工具外掛程式
🔔 `更新日期：2026-01-18`

[`ADK 支援`: `Python v1.16.0`]

Reflect and Retry 工具外掛程式可以協助您的代理程式從 ADK [工具](../custom-tools/index.md) 的錯誤回應中恢復，並自動重試工具請求。此外掛程式會攔截工具失敗，為 AI 模型提供結構化的引導以進行反思與修正，並在可配置的限制次數內重試操作。此外掛程式能協助您在代理程式工作流中建立更強的韌性，包括以下功能：

*   **並行安全**：使用鎖定機制安全地處理並行工具執行。
*   **可配置範圍**：追蹤每次呼叫的失敗（預設）或全域追蹤。
*   **細粒度追蹤**：按工具追蹤失敗次數。
*   **自定義錯誤提取**：支援在正常的工具回應中偵測錯誤。

## 新增 Reflect and Retry 外掛程式

將此外掛程式新增到您 ADK 專案 App 物件的 plugins 設定中，如下所示：

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin

# 初始化 App 並加入重試外掛程式
app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        # 設定最大重試次數為 3 次
        ReflectAndRetryToolPlugin(max_retries=3),
    ],
)
```

</details>

使用此配置，如果代理程式呼叫的任何工具傳回錯誤，請求將會更新並再次嘗試，每個工具最多重試 3 次。

## 配置設定

Reflect and Retry 外掛程式具有以下配置選項：

*   **`max_retries`**：（選填）系統為接收非錯誤回應而進行的額外嘗試總數。預設值為 3。
*   **`throw_exception_if_retry_exceeded`**：（選填）如果設定為 `False`，當最後一次重試嘗試失敗時，系統不會拋出錯誤。預設值為 `True`。
*   **`tracking_scope`**：（選填）
    *   **`TrackingScope.INVOCATION`**：跨單次呼叫和使用者追蹤工具失敗。此值為預設值。
    *   **`TrackingScope.GLOBAL`**：跨所有呼叫和所有使用者追蹤工具失敗。

### 進階配置

您可以透過擴展 `ReflectAndRetryToolPlugin` 類別來進一步修改此外掛程式的行為。以下程式碼範例展示了透過選擇具有錯誤狀態的回應來擴展行為的簡單示範：

<details>
<summary>範例說明</summary>

> Python

```python
class CustomRetryPlugin(ReflectAndRetryToolPlugin):
  async def extract_error_from_result(self, *, tool, tool_args, tool_context, result):
    # 根據回應內容偵測錯誤
    if result.get('status') == 'error':
        return result
    return None  # 未偵測到錯誤

# 將此修改後的外掛程式新增到您的 App 物件中：
# 設定最大重試次數為 5 次
error_handling_plugin = CustomRetryPlugin(max_retries=5)
```

</details>

## 後續步驟

有關使用 Reflect and Retry 外掛程式的完整程式碼範例，請參閱以下內容：

*   [基礎](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/basic) 程式碼範例
*   [虛假函式名稱 (Hallucinating function name)](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/hallucinating_func_name) 程式碼範例
