# Events
🔔 `更新日期：2026-01-20`

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

事件是 Agent Development Kit (ADK) 內資訊流的基本單位。它們代表代理程式互動生命週期中發生的每一個重大事件，從最初的使用者輸入到最終的回應以及兩者之間的所有步驟。理解事件至關重要，因為它們是組件通訊、狀態管理和控制流引導的主要方式。

## 什麼是事件以及為什麼它們很重要

ADK 中的 `Event` 是一個不可變的記錄，代表代理程式執行中的特定點。它擷取了使用者訊息、代理程式回覆、使用工具的請求（函式呼叫）、工具結果、狀態變更、控制信號和錯誤。

<details>
<summary>範例說明</summary>

> Python

從技術上講，它是 `google.adk.events.Event` 類別的實例，它在基礎的 `LlmResponse` 結構上增加了必要的 ADK 特定元資料和 `actions` 酬載。

```python
# Event 的概念結構 (Python)
# from google.adk.events import Event, EventActions
# from google.genai import types

# class Event(LlmResponse): # 簡化視圖
#     # --- LlmResponse 欄位 ---
#     content: Optional[types.Content]
#     partial: Optional[bool]
#     # ... 其他回應欄位 ...

#     # --- ADK 特定新增內容 ---
#     author: str          # 'user' 或代理程式名稱
#     invocation_id: str   # 整個互動運行的 ID
#     id: str              # 此特定事件的唯一 ID
#     timestamp: float     # 建立時間
#     actions: EventActions # 對於副作用和控制很重要
#     branch: Optional[str] # 階層路徑
#     # ...
```

> Go

在 Go 中，這是一個 `google.golang.org/adk/session.Event` 類型的結構體。

```go
// Event 的概念結構 (Go - 參見 session/session.go)
// 基於 session.Event 結構體的簡化視圖
type Event struct {
    // --- 來自嵌入的 model.LLMResponse 的欄位 ---
    model.LLMResponse

    // --- ADK 特定新增內容 ---
    Author       string         // 'user' 或代理程式名稱
    InvocationID string         // 整個互動運行的 ID
    ID           string         // 此特定事件的唯一 ID
    Timestamp    time.Time      // 建立時間
    Actions      EventActions   // 對於副作用和控制很重要
    Branch       string         // 階層路徑
    // ... 其他欄位
}

// model.LLMResponse 包含 Content 欄位
type LLMResponse struct {
    Content *genai.Content
    // ... 其他欄位
}
```

> Java

在 Java 中，這是 `com.google.adk.events.Event` 類別的實例。它同樣在基礎回應結構上增加了必要的 ADK 特定元資料和 `actions` 酬載。

```java
// Event 的概念結構 (Java - 參見 com.google.adk.events.Event.java)
// 基於提供的 com.google.adk.events.Event.java 的簡化視圖
// public class Event extends JsonBaseModel {
//     // --- 類似於 LlmResponse 的欄位 ---
//     private Optional<Content> content;
//     private Optional<Boolean> partial;
//     // ... 其他回應欄位，如 errorCode, errorMessage ...

//     // --- ADK 特定新增內容 ---
//     private String author;         // 'user' 或代理程式名稱
//     private String invocationId;   // 整個互動運行的 ID
//     private String id;             // 此特定事件的唯一 ID
//     private long timestamp;        // 建立時間 (epoch 毫秒)
//     private EventActions actions;  // 對於副作用和控制很重要
//     private Optional<String> branch; // 階層路徑
//     // ... 其他欄位，如 turnComplete, longRunningToolIds 等
// }
```

</details>

事件對 ADK 的運作至關重要，原因有以下幾點：

1.  **通訊：** 它們作為使用者介面、`Runner`、代理程式、LLM 和工具之間的標準訊息格式。一切都以 `Event` 的形式流動。

2.  **發送信號狀態和 Artifact 變更：** 事件攜帶狀態修改的指令並追蹤構件更新。`SessionService` 使用這些信號來確保持久性。在 Python 中，變更透過 `event.actions.state_delta` 和 `event.actions.artifact_delta` 發送信號。

3.  **控制流：** 諸如 `event.actions.transfer_to_agent` 或 `event.actions.escalate` 之類的特定欄位充當引導框架的信號，決定下一個運行的代理程式或循環是否應該終止。

4.  **歷史記錄與可觀察性：** 記錄在 `session.events` 中的事件序列提供了一次互動的完整、按時間順序排列的歷史記錄，這對於偵錯、稽核和逐步了解代理程式行為非常有價值。

從本質上講，從使用者的查詢到代理程式的最終回答，整個過程都是透過 `Event` 物件的產生、解釋和處理來編排的。


## 理解與使用事件

作為開發人員，您主要會與 `Runner` 產出的事件流進行互動。以下是如何理解並從中提取資訊的方法：

> [!NOTE]
基本組件的特定參數或方法名稱可能會因 SDK 語言而略有不同（例如，Python 中的 `event.content()`，Java 中的 `event.content().get().parts()`）。有關詳細資訊，請參閱特定語言的 API 文件。

### 識別事件來源和類型

透過檢查以下內容快速確定事件代表什麼：

*   **是誰發送的？ (`event.author`)**
    *   `'user'`：表示直接來自終端使用者的輸入。
    *   `'AgentName'`：表示來自特定代理程式的輸出或操作（例如，`'WeatherAgent'`、`'SummarizerAgent'`）。
*   **主要酬載 (`payload`) 是什麼？ (`event.content` 和 `event.content.parts`)**
    *   **文字：** 表示對話訊息。對於 Python，檢查 `event.content.parts[0].text` 是否存在。對於 Java，檢查 `event.content()` 是否存在、其 `parts()` 是否存在且不為空，以及第一部分的 `text()` 是否存在。
    *   **工具呼叫請求：** 檢查 `event.get_function_calls()`。如果不為空，則 LLM 正在請求執行一個或多個工具。列表中的每個項目都有 `.name` 和 `.args`。
    *   **工具結果：** 檢查 `event.get_function_responses()`。如果不為空，則此事件攜帶工具執行的結果。每個項目都有 `.name` 和 `.response`（工具返回的字典）。*注意：* 對於歷史記錄結構，`content` 內部的 `role` 通常是 `'user'`，但事件 `author` 通常是請求工具呼叫的代理程式。

*   **是否為串流輸出？ (`event.partial`)**
    表示這是否為來自 LLM 的不完整文字塊。
    *   `True`：後續將有更多文字。
    *   `False` 或 `None`/`Optional.empty()`：這部分內容已完成（儘管如果 `turn_complete` 也為 false，則整個回合可能尚未結束）。

<details>
<summary>範例說明</summary>

> Python

```python
# 虛擬程式碼：基本事件識別 (Python)
# async for event in runner.run_async(...):
#     print(f"事件來自: {event.author}")
#
#     if event.content and event.content.parts:
#         if event.get_function_calls():
#             print("  類型: 工具呼叫請求")
#         elif event.get_function_responses():
#             print("  類型: 工具結果")
#         elif event.content.parts[0].text:
#             if event.partial:
#                 print("  類型: 串流文字塊")
#             else:
#                 print("  類型: 完整文字訊息")
#         else:
#             print("  類型: 其他內容 (例如，程式碼結果)")
#     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
#         print("  類型: 狀態/構件更新")
#     else:
#         print("  類型: 控制信號或其他")
```

> Go

```go
  // 虛擬程式碼：基本事件識別 (Go)
import (
  "fmt"
  "google.golang.org/adk/session"
  "google.golang.org/genai"
)

// hasFunctionCalls 檢查內容是否包含函式呼叫
func hasFunctionCalls(content *genai.Content) bool {
  if content == nil {
    return false
  }
  for _, part := range content.Parts {
    if part.FunctionCall != nil {
      return true
    }
  }
  return false
}

// hasFunctionResponses 檢查內容是否包含函式回應
func hasFunctionResponses(content *genai.Content) bool {
  if content == nil {
    return false
  }
  for _, part := range content.Parts {
    if part.FunctionResponse != nil {
      return true
    }
  }
  return false
}

// processEvents 處理事件流
func processEvents(events <-chan *session.Event) {
  for event := range events {
    fmt.Printf("事件來自: %s\n", event.Author)

    if event.LLMResponse != nil && event.LLMResponse.Content != nil {
      if hasFunctionCalls(event.LLMResponse.Content) {
        fmt.Println("  類型: 工具呼叫請求")
      } else if hasFunctionResponses(event.LLMResponse.Content) {
        fmt.Println("  類型: 工具結果")
      } else if len(event.LLMResponse.Content.Parts) > 0 {
        if event.LLMResponse.Content.Parts[0].Text != "" {
          if event.LLMResponse.Partial {
            fmt.Println("  類型: 串流文字塊")
          } else {
            fmt.Println("  類型: 完整文字訊息")
          }
        } else {
          fmt.Println("  類型: 其他內容 (例如，程式碼結果)")
        }
      }
    } else if len(event.Actions.StateDelta) > 0 {
      fmt.Println("  類型: 狀態更新")
    } else {
      fmt.Println("  類型: 控制信號或其他")
    }
  }
}
```

> Java

```java
// 虛擬程式碼：基本事件識別 (Java)
// import com.google.genai.types.Content;
// import com.google.adk.events.Event;
// import com.google.adk.events.EventActions;

// runner.runAsync(...).forEach(event -> { // 假設是同步流或反應式流
//     System.out.println("事件來自: " + event.author());
//
//     if (event.content().isPresent()) {
//         Content content = event.content().get();
//         if (!event.functionCalls().isEmpty()) {
//             System.out.println("  類型: 工具呼叫請求");
//         } else if (!event.functionResponses().isEmpty()) {
//             System.out.println("  類型: 工具結果");
//         } else if (content.parts().isPresent() && !content.parts().get().isEmpty() &&
//                    content.parts().get().get(0).text().isPresent()) {
//             if (event.partial().orElse(false)) {
//                 System.out.println("  類型: 串流文字塊");
//             } else {
//                 System.out.println("  類型: 完整文字訊息");
//             }
//         } else {
//             System.out.println("  類型: 其他內容 (例如，程式碼結果)");
//         }
//     } else if (event.actions() != null &&
//                ((event.actions().stateDelta() != null && !event.actions().stateDelta().isEmpty()) ||
//                 (event.actions().artifactDelta() != null && !event.actions().artifactDelta().isEmpty()))) {
//         System.out.println("  類型: 狀態/構件更新");
//     } else {
//         System.out.println("  類型: 控制信號或其他");
//     }
// });
```

</details>

### 提取關鍵資訊

一旦您知道了事件類型，就可以存取相關資料：

*   **文字內容：**
    在存取文字之前，請務必檢查內容和部分是否存在。在 Python 中為 `text = event.content.parts[0].text`。

*   **函式呼叫詳情：**

<details>
<summary>範例說明</summary>

> Python

```python
calls = event.get_function_calls()
if calls:
    for call in calls:
        tool_name = call.name
        arguments = call.args # 這通常是一個字典
        print(f"  工具: {tool_name}, 參數: {arguments}")
        # 應用程式可能會根據此分派執行
```

> Go

```go
import (
    "fmt"
    "google.golang.org/adk/session"
    "google.golang.org/genai"
)

// handleFunctionCalls 處理函式呼叫
func handleFunctionCalls(event *session.Event) {
    if event.LLMResponse == nil || event.LLMResponse.Content == nil {
        return
    }
    calls := event.Content.FunctionCalls()
    if len(calls) > 0 {
        for _, call := range calls {
            toolName := call.Name
            arguments := call.Args
            fmt.Printf("  工具: %s, 參數: %v\n", toolName, arguments)
            // 應用程式可能會根據此分派執行
        }
    }
}
```

> Java

```java
import com.google.genai.types.FunctionCall;
import com.google.common.collect.ImmutableList;
import java.util.Map;

// 從 Event.java 取得函式呼叫清單
ImmutableList<FunctionCall> calls = event.functionCalls();
if (!calls.isEmpty()) {
  for (FunctionCall call : calls) {
    String toolName = call.name().get();
    // args 是 Optional<Map<String, Object>>
    Map<String, Object> arguments = call.args().get();
           System.out.println("  工具: " + toolName + ", 參數: " + arguments);
    // 應用程式可能會根據此分派執行
  }
}
```

</details>

*   **函式回應詳情：**

<details>
<summary>範例說明</summary>

> Python

```python
responses = event.get_function_responses()
if responses:
    for response in responses:
        tool_name = response.name
        result_dict = response.response # 工具返回的字典
        print(f"  工具結果: {tool_name} -> {result_dict}")
```

> Go

```go
import (
    "fmt"
    "google.golang.org/adk/session"
    "google.golang.org/genai"
)

// handleFunctionResponses 處理函式回應
func handleFunctionResponses(event *session.Event) {
    if event.LLMResponse == nil || event.LLMResponse.Content == nil {
        return
    }
    responses := event.Content.FunctionResponses()
    if len(responses) > 0 {
        for _, response := range responses {
            toolName := response.Name
            result := response.Response
            fmt.Printf("  工具結果: %s -> %v\n", toolName, result)
        }
    }
}
```

> Java

```java
import com.google.genai.types.FunctionResponse;
import com.google.common.collect.ImmutableList;
import java.util.Map;

// 從 Event.java 取得函式回應清單
ImmutableList<FunctionResponse> responses = event.functionResponses();
if (!responses.isEmpty()) {
    for (FunctionResponse response : responses) {
        String toolName = response.name().get();
        Map<String, String> result= response.response().get(); // 在取得回應前先檢查
        System.out.println("  工具結果: " + toolName + " -> " + result);
    }
}
```

</details>

*   **識別碼：**
    *   `event.id`：此特定事件實例的唯一 ID。
    *   `event.invocation_id`：此事件所屬的整個「使用者請求到最終回應」週期的 ID。對於記錄和追蹤非常有用。

### 檢測操作與副作用

`event.actions` 物件發送已發生或應發生變更的信號。在存取 `event.actions` 及其欄位/方法之前，請務必檢查它們是否存在。

*   **狀態變更 (State Change)：** 提供在產生此事件的步驟期間，在對話狀態中修改的鍵值對集合。

<details>
<summary>範例說明</summary>

> Python

`delta = event.actions.state_delta` (`{key: value}` 對的字典)。
```python
if event.actions and event.actions.state_delta:
    print(f"  狀態變更: {event.actions.state_delta}")
    # 如有必要，更新本地 UI 或應用程式狀態
```

> Go

`delta := event.Actions.StateDelta` (一個 `map[string]any`)
```go
import (
    "fmt"
    "google.golang.org/adk/session"
)

// handleStateChanges 處理狀態變更
func handleStateChanges(event *session.Event) {
    if len(event.Actions.StateDelta) > 0 {
        fmt.Printf("  狀態變更: %v\n", event.Actions.StateDelta)
        // 如有必要，更新本地 UI 或應用程式狀態
    }
}
```

> Java

`ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

```java
import java.util.concurrent.ConcurrentMap;
import com.google.adk.events.EventActions;

EventActions actions = event.actions(); // 假設 event.actions() 不為 null
if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
    ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
    System.out.println("  狀態變更: " + stateChanges);
    // 如有必要，更新本地 UI 或應用程式狀態
}
```

</details>

*   **Artifact 儲存 (Artifact Saves)：** 提供一個集合，指示哪些 Artifacts 已儲存及其新的版本號（或相關的 `Part` 資訊）。

<details>
<summary>範例說明</summary>

> Python

`artifact_changes = event.actions.artifact_delta` (`{filename: version}` 的字典)。
```python
if event.actions and event.actions.artifact_delta:
    print(f"  Artifact 已儲存: {event.actions.artifact_delta}")
    # UI 可能會重新整理 Artifacts 清單
```

> Go

`artifactChanges := event.Actions.ArtifactDelta` (一個 `map[string]artifact.Artifact`)
```go
import (
    "fmt"
    "google.golang.org/adk/artifact"
    "google.golang.org/adk/session"
)

// handleArtifactChanges 處理 Artifact 變更
func handleArtifactChanges(event *session.Event) {
    if len(event.Actions.ArtifactDelta) > 0 {
        fmt.Printf("Artifact 已儲存: %v\n", event.Actions.ArtifactDelta)
        // UI 可能會重新整理 Artifact 清單
        // 遍歷 event.Actions.ArtifactDelta 以獲取檔名和 artifact.Artifact 詳情
        for filename, art := range event.Actions.ArtifactDelta {
            fmt.Printf("檔名: %s, 版本: %d, MIME 類型: %s\n", filename, art.Version, art.MIMEType)
        }
    }
}
```

> Java

`ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`

```java
import java.util.concurrent.ConcurrentMap;
import com.google.genai.types.Part;
import com.google.adk.events.EventActions;

EventActions actions = event.actions(); // 假設 event.actions() 不為 null
if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
    ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
    System.out.println("Artifact 已儲存: " + artifactChanges);
    // UI 可能會重新整理 Artifact 清單
    // 遍歷 artifactChanges.entrySet() 以獲取檔名和 Part 詳情
}
```

</details>

*   **控制流信號：** 檢查布林標記或字串值：

<details>
<summary>範例說明</summary>

> Python

*   `event.actions.transfer_to_agent` (字串)：控制權應移交給指定的代理程式。
*   `event.actions.escalate` (布林值)：循環應終止。
*   `event.actions.skip_summarization` (布林值)：LLM 不應總結工具結果。
```python
if event.actions:
    if event.actions.transfer_to_agent:
        print(f"  信號: 移交至 {event.actions.transfer_to_agent}")
    if event.actions.escalate:
        print("  信號: 提升 (終止循環)")
    if event.actions.skip_summarization:
        print("  信號: 跳過工具結果的總結")
```

> Go

*   `event.Actions.TransferToAgent` (字串)：控制權應移交給指定的代理程式。
*   `event.Actions.Escalate` (布林值)：循環應終止。
*   `event.Actions.SkipSummarization` (布林值)：LLM 不應總結工具結果。
```go
import (
    "fmt"
    "google.golang.org/adk/session"
)

// handleControlFlow 處理控制流
func handleControlFlow(event *session.Event) {
    if event.Actions.TransferToAgent != "" {
        fmt.Printf("  信號: 移交至 %s\n", event.Actions.TransferToAgent)
    }
    if event.Actions.Escalate {
        fmt.Println("  信號: 提升 (終止循環)")
    }
    if event.Actions.SkipSummarization {
        fmt.Println("  信號: 跳過工具結果的總結")
    }
}
```

> Java

*   `event.actions().transferToAgent()` (返回 `Optional<String>`)：控制權應移交給指定的代理程式。
*   `event.actions().escalate()` (返回 `Optional<Boolean>`)：循環應終止。
*   `event.actions().skipSummarization()` (返回 `Optional<Boolean>`)：LLM 不應總結工具結果。

```java
import com.google.adk.events.EventActions;
import java.util.Optional;

EventActions actions = event.actions(); // 假設 event.actions() 不為 null
if (actions != null) {
    Optional<String> transferAgent = actions.transferToAgent();
    if (transferAgent.isPresent()) {
        System.out.println("  信號: 移交至 " + transferAgent.get());
    }

    Optional<Boolean> escalate = actions.escalate();
    if (escalate.orElse(false)) { // 或 escalate.isPresent() && escalate.get()
        System.out.println("  信號: 提升 (終止循環)");
    }

    Optional<Boolean> skipSummarization = actions.skipSummarization();
    if (skipSummarization.orElse(false)) { // 或 skipSummarization.isPresent() && skipSummarization.get()
        System.out.println("  信號: 跳過工具結果的總結");
    }
}
```

</details>

### 確定事件是否為「最終」回應

使用內建的輔助方法 `event.is_final_response()` 來識別適合顯示為代理程式回合完整輸出的事件。

*   **目的：** 從最終面向使用者的訊息中過濾掉中間步驟（如工具呼叫、部分串流文字、內部狀態更新）。
*   **何時為 `True`？**
    1.  事件包含工具結果 (`function_response`) 且 `skip_summarization` 為 `True`。
    2.  事件包含針對標記為 `is_long_running=True` 的工具的工具呼叫 (`function_call`)。在 Java 中，檢查 `longRunningToolIds` 清單是否不為空：
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()` 為 `true`。
    3.  或者，滿足以下**所有**條件：
        *   沒有函式呼叫 (`get_function_calls()` 為空)。
        *   沒有函式回應 (`get_function_responses()` 為空)。
        *   不是部分串流塊 (`partial` 不為 `True`)。
        *   不以可能需要進一步處理/顯示的程式碼執行結果結尾。
*   **用法：** 在您的應用程式邏輯中過濾事件流。

<details>
<summary>範例說明</summary>

> Python

```python
# 虛擬程式碼：在應用程式中處理最終回應 (Python)
# full_response_text = ""
# async for event in runner.run_async(...):
#     # 如有需要，累積串流文字...
#     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
#         full_response_text += event.content.parts[0].text
#
#     # 檢查是否為最終的可顯示事件
#     if event.is_final_response():
#         print("\n--- 檢測到最終輸出 ---")
#         if event.content and event.content.parts and event.content.parts[0].text:
#              # 如果是串流的最後一部分，使用累積的文字
#              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
#              print(f"顯示給使用者: {final_text.strip()}")
#              full_response_text = "" # 重設累積器
#         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
#              # 如果需要，處理顯示原始工具結果
#              response_data = event.get_function_responses()[0].response
#              print(f"顯示原始工具結果: {response_data}")
#         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
#              print("顯示訊息: 工具正在背景運行...")
#         else:
#              # 如果適用，處理其他類型的最終回應
#              print("顯示: 最終非文字回應或信號。")
```

> Go

```go
// 虛擬程式碼：在應用程式中處理最終回應 (Go)
import (
    "fmt"
    "strings"
    "google.golang.org/adk/session"
    "google.golang.org/genai"
)

// isFinalResponse 檢查事件是否為適合顯示的最終回應。
func isFinalResponse(event *session.Event) bool {
    if event.LLMResponse != nil {
        // 條件 1：帶有跳過總結的工具結果。
        if event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 && event.Actions.SkipSummarization {
            return true
        }
        // 條件 2：長時間運行的工具呼叫。
        if len(event.LongRunningToolIDs) > 0 {
            return true
        }
        // 條件 3：不帶工具呼叫或回應的完整訊息。
        if (event.LLMResponse.Content == nil ||
            (len(event.LLMResponse.Content.FunctionCalls()) == 0 && len(event.LLMResponse.Content.FunctionResponses()) == 0)) &&
            !event.LLMResponse.Partial {
            return true
        }
    }
    return false
}

// handleFinalResponses 處理最終回應
func handleFinalResponses() {
    var fullResponseText strings.Builder
    // for event := range runner.Run(...) { // 範例循環
    // 	// 如有需要，累積串流文字...
    // 	if event.LLMResponse != nil && event.LLMResponse.Partial && event.LLMResponse.Content != nil {
    // 		if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
    // 			fullResponseText.WriteString(event.LLMResponse.Content.Parts[0].Text)
    // 		}
    // 	}
    //
    // 	// 檢查是否為最終的可顯示事件
    // 	if isFinalResponse(event) {
    // 		fmt.Println("\n--- 檢測到最終輸出 ---")
    // 		if event.LLMResponse != nil && event.LLMResponse.Content != nil {
    // 			if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
    // 				// 如果是串流的最後一部分，使用累積的文字
    // 				finalText := fullResponseText.String()
    // 				if !event.LLMResponse.Partial {
    // 					finalText += event.LLMResponse.Content.Parts[0].Text
    // 				}
    // 				fmt.Printf("顯示給使用者: %s\n", strings.TrimSpace(finalText))
    // 				fullResponseText.Reset() // 重設累積器
    // 			}
    // 		} else if event.Actions.SkipSummarization && event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 {
    // 			// 如果需要，處理顯示原始工具結果
    // 			responseData := event.LLMResponse.Content.FunctionResponses()[0].Response
    // 			fmt.Printf("顯示原始工具結果: %v\n", responseData)
    // 		} else if len(event.LongRunningToolIDs) > 0 {
    // 			fmt.Println("顯示訊息: 工具正在背景運行...")
    // 		} else {
    // 			// 如果適用，處理其他類型的最終回應
    // 			fmt.Println("顯示: 最終非文字回應或信號。")
    // 		}
    // 	}
    // }
}
```

> Java

```java
// 虛擬程式碼：在應用程式中處理最終回應 (Java)
import com.google.adk.events.Event;
import com.google.genai.types.Content;
import com.google.genai.types.FunctionResponse;
import java.util.Map;

StringBuilder fullResponseText = new StringBuilder();
runner.run(...).forEach(event -> { // 假設是事件流
     // 如有需要，累積串流文字...
     if (event.partial().orElse(false) && event.content().isPresent()) {
         event.content().flatMap(Content::parts).ifPresent(parts -> {
             if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                 fullResponseText.append(parts.get(0).text().get());
            }
         });
     }

     // 檢查是否為最終的可顯示事件
     if (event.finalResponse()) { // 使用來自 Event.java 的方法
         System.out.println("\n--- 檢測到最終輸出 ---");
         if (event.content().isPresent() &&
             event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
             // 如果是串流的最後一部分，使用累積的文字
             String eventText = event.content().get().parts().get().get(0).text().get();
             String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
             System.out.println("顯示給使用者: " + finalText.trim());
             fullResponseText.setLength(0); // 重設累積器
         } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                    && !event.functionResponses().isEmpty()) {
             // 如果需要，處理顯示原始工具結果，
             // 特別是如果 finalResponse() 由於其他條件而為 true
             // 或者如果您想不顧 finalResponse() 而顯示跳過的總結結果
             Map<String, Object> responseData = event.functionResponses().get(0).response().get();
             System.out.println("顯示原始工具結果: " + responseData);
         } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
             // 此情況已由 event.finalResponse() 涵蓋
             System.out.println("顯示訊息: 工具正在背景運行...");
         } else {
             // 如果適用，處理其他類型的最終回應
             System.out.println("顯示: 最終非文字回應或信號。");
         }
     }
 });
```

</details>

透過仔細檢查事件的這些方面，您可以建置健全的應用程式，對流經 ADK 系統的豐富資訊做出適當反應。

## 事件如何流動：產生與處理

事件在不同的時間點建立，並由框架系統地處理。了解此流程有助於釐清操作和歷史記錄是如何管理的。

*   **產生來源：**
    *   **使用者輸入：** `Runner` 通常會將最初的使用者訊息或對話中途的輸入封裝成一個 `author='user'` 的 `Event`。
    *   **代理程式邏輯：** 代理程式 (`BaseAgent`、`LlmAgent`) 明確地 `yield Event(...)` 物件（設定 `author=self.name`）以傳達回應或發送操作信號。
    *   **LLM 回應：** ADK 模型整合層將原始 LLM 輸出（文字、函式呼叫、錯誤）轉換為 `Event` 物件，作者為呼叫的代理程式。
    *   **工具結果：** 工具執行後，框架會產生一個包含 `function_response` 的 `Event`。`author` 通常是請求該工具的代理程式，而 `content` 內部的 `role` 則為 LLM 歷史記錄設定為 `'user'`。

*   **處理流程：**
    a.  **產出/返回 (Yield/Return)：** 事件由其來源產生並產出 (Python) 或返回/發出 (Java)。
    b.  **Runner 接收：** 執行代理程式的主 `Runner` 接收該事件。
    c.  **SessionService 處理：** `Runner` 將事件發送到配置的 `SessionService`。這是一個關鍵步驟：
        *   **應用差異 (Deltas)：** 服務將 `event.actions.state_delta` 合併到 `session.state` 中，並根據 `event.actions.artifact_delta` 更新內部記錄。（注意：實際的 Artifact *儲存*通常發生在更早呼叫 `context.save_artifact` 時）。
        *   **完成元資料 (Finalizes Metadata)：** 如果不存在，則分配唯一的 `event.id`；可能會更新 `event.timestamp`。
        *   **持久化到歷史記錄 (Persists to History)：** 將處理後的事件附加到 `session.events` 列表中。
    d.  **對外產出 (External Yield)：** `Runner` 將處理後的事件向外產出 (Python) 或返回/發出 (Java) 給呼叫應用程式（例如，調用 `runner.run_async` 的程式碼）。

此流程確保狀態變更和歷史記錄能與每個事件的通訊內容一致地被記錄。

## 常見事件範例（說明性模式）

以下是您在流中可能會看到的典型事件的簡明範例：

*   **使用者輸入：**
    ```json
    {
      "author": "user",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "預訂下週二飛往倫敦的航班"}]}
      // actions 通常為空
    }
    ```
*   **代理程式最終文字回應：** (`is_final_response() == True`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "好的，我可以幫忙。您能確認出發城市嗎？"}]},
      "partial": false,
      "turn_complete": true
      // actions 可能有狀態差異等。
    }
    ```
*   **代理程式串流文字回應：** (`is_final_response() == False`)
    ```json
    {
      "author": "SummaryAgent",
      "invocation_id": "e-abc...",
      "content": {"parts": [{"text": "該文件討論了三個重點："}]},
      "partial": true,
      "turn_complete": false
    }
    // ... 後續跟隨更多 partial=True 事件 ...
    ```
*   **工具呼叫請求 (由 LLM 發起)：** (`is_final_response() == False`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
      // actions 通常為空
    }
    ```
*   **提供的工具結果 (提供給 LLM)：** (`is_final_response()` 取決於 `skip_summarization`)
    ```json
    {
      "author": "TravelAgent", // 作者是請求該呼叫的代理程式
      "invocation_id": "e-xyz...",
      "content": {
        "role": "user", // 用於 LLM 歷史記錄的角色
        "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
      }
      // actions 可能有 skip_summarization=True
    }
    ```
*   **僅狀態/ Artifact 更新：** (`is_final_response() == False`)
    ```json
    {
      "author": "InternalUpdater",
      "invocation_id": "e-def...",
      "content": null,
      "actions": {
        "state_delta": {"user_status": "verified"},
        "artifact_delta": {"verification_doc.pdf": 2}
      }
    }
    ```
*   **代理程式移交信號：** (`is_final_response() == False`)
    ```json
    {
      "author": "OrchestratorAgent",
      "invocation_id": "e-789...",
      "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
      "actions": {"transfer_to_agent": "BillingAgent"} // 由框架添加
    }
    ```
*   **循環提升信號：** (`is_final_response() == False`)
    ```json
    {
      "author": "CheckerAgent",
      "invocation_id": "e-loop...",
      "content": {"parts": [{"text": "已達到最大重試次數。"}]}, // 選填內容
      "actions": {"escalate": true}
    }
    ```

## 補充背景與事件詳情

除了核心概念外，以下是關於背景與事件的一些特定細節，這對於某些使用案例很重要：

1.  **`ToolContext.function_call_id` (連結工具操作)：**
    *   當 LLM 請求工具 (FunctionCall) 時，該請求具有一個 ID。提供給您工具函式的 `ToolContext` 包含此 `function_call_id`。
    *   **重要性：** 此 ID 對於將身分驗證等操作連結回啟動它們的特定工具請求至關重要，尤其是在一回合中呼叫多個工具時。框架在內部使用此 ID。

2.  **狀態/Artifact變更如何被記錄：**
    *   當您使用 `CallbackContext` 或 `ToolContext` 修改狀態或儲存 Artifact 時，這些變更不會立即寫入持久儲存空間。
    *   相反地，它們會填充 `EventActions` 物件內的 `state_delta` 和 `artifact_delta` 欄位。
    *   此 `EventActions` 物件會附加到變更後產生的*下一個事件*（例如，代理程式的回應或工具結果事件）。
    *   `SessionService.append_event` 方法從傳入的事件中讀取這些差異，並將其應用於工作階段的持久狀態和 Artifact 記錄。這確保了變更在時間上與事件流連結。

3.  **狀態範圍前綴 (`app:`、`user:`、`temp:`)：**
    *   透過 `context.state` 管理狀態時，您可以選擇使用前綴：
        *   `app:my_setting`：建議與整個應用程式相關的狀態（需要持久化的 `SessionService`）。
        *   `user:user_preference`：建議跨工作階段與特定使用者相關的狀態（需要持久化的 `SessionService`）。
        *   `temp:intermediate_result` 或無前綴：通常是工作階段特定的或目前調用的暫時狀態。
    *   底層的 `SessionService` 決定如何處理這些前綴以進行持久化。

4.  **錯誤事件：**
    *   `Event` 可以代表一個錯誤。檢查 `event.error_code` 和 `event.error_message` 欄位（繼承自 `LlmResponse`）。
    *   錯誤可能源自 LLM（例如，安全過濾器、資源限制），或者在工具發生嚴重失敗時由框架封裝。檢查工具 `FunctionResponse` 內容以了解典型的工具特定錯誤。
    ```json
    // 範例錯誤事件 (概念性)
    {
      "author": "LLMAgent",
      "invocation_id": "e-err...",
      "content": null,
      "error_code": "SAFETY_FILTER_TRIGGERED",
      "error_message": "由於安全設定，回應被阻擋。",
      "actions": {}
    }
    ```

這些細節為涉及工具身分驗證、狀態持久化範圍以及事件流內錯誤處理的高級使用案例提供了更完整的圖像。

## 處理事件的最佳實踐

要在您的 ADK 應用程式中有效地使用事件：

*   **明確的作者歸屬：** 在建置自定義代理程式時，確保歷史記錄中代理程式操作的歸屬正確。框架通常會正確處理 LLM/工具事件的作者歸屬。

<details>
<summary>範例說明</summary>

> Python

在 `BaseAgent` 子類別中使用 `yield Event(author=self.name, ...)`。

> Go

在自定義代理程式的 `Run` 方法中，框架通常會處理作者歸屬。如果是手動建立事件，請設定作者：`yield(&session.Event{Author: a.name, ...}, nil)`

> Java

在自定義代理程式邏輯中建構 `Event` 時，請設定作者，例如：`Event.builder().author(this.getAgentName()) // ... .build();`

</details>

*   **語義化內容與操作：** 使用 `event.content` 處理核心訊息/資料（文字、函式呼叫/回應）。使用 `event.actions` 專門用於發送副作用（狀態/Artifact 差異）或控制流（`transfer`、`escalate`、`skip_summarization`）的信號。
*   **冪等性意識：** 了解 `SessionService` 負責應用 `event.actions` 中發送號信的狀態/Artifact 變更。雖然 ADK 服務旨在保持一致性，但如果您的應用程式邏輯重新處理事件，請考慮潛在的下游影響。
*   **使用 `is_final_response()`：** 在您的應用程式/UI 層依賴此輔助方法來識別完整的、面向使用者的文字回應。避免手動複製其邏輯。
*   **善用歷史記錄：** 工作階段的事件列表是您主要的偵錯工具。檢查作者、內容和操作的序列，以追蹤執行情況並診斷問題。
*   **使用元資料：** 使用 `invocation_id` 來關聯單次使用者互動中的所有事件。使用 `event.id` 來引用特定的、唯一的發生事件。

將事件視為具有明確內容與操作目的的結構化訊息，是建置、偵錯和管理 ADK 中複雜代理程式行為的關鍵。

## 更多說明

根據來源內容，以下將 **ADK 中的常見事件範例（說明性模式）** 整合，並加入您要求的 **關鍵 JSON 欄位與屬性內容**：

### 常見事件範例（說明性模式）整合表

| 事件類型 | 說明與特徵 | 關鍵 JSON 欄位 / 屬性 (Key Fields) | `is_final_response()` |
| :--- | :--- | :--- | :--- |
| **使用者輸入** | 初始訊息或對話中途輸入，代表終端使用者的請求。 | `author: 'user'`<br>`content.parts.text: "使用者文字內容"` | 通常不適用 (False) |
| **代理程式最終文字回應** | 完成的回覆，已過濾中間步驟，可直接顯示給使用者。 | `author: 'AgentName'`<br>`content.parts.text: "完整回覆內容"`<br>`partial: False` | **True** |
| **代理程式串流文字回應** | 來自 LLM 的不完整文字塊，表示後續還有更多文字。 | `author: 'AgentName'`<br>`partial: True` | **False** |
| **工具呼叫請求** | 由 LLM 發起，要求執行一個或多個特定工具（函式）。 | `get_function_calls()` 包含項目：<br>`.name`: 工具名稱<br>`.args`: 工具參數 | **False** (除非是長效工具) |
| **提供工具結果** | 框架產生，將工具執行的結果提供給 LLM 作為參考。 | `get_function_responses()` 包含項目：<br>`.name`: 工具名稱<br>`.response`: 返回的結果字典 | **取決於 `skip_summarization`** |
| **僅狀態 / Artifact 更新** | 發送 `state_delta` 或 `artifact_delta` 的信號，用於更新對話持久狀態。 | `actions.state_delta`: `{key: value}`<br>`actions.artifact_delta`: `{filename: version}` | **False** |
| **代理程式移交信號** | 指示控制權應移交給另一個特定的代理程式。 | `actions.transfer_to_agent: "TargetAgentName"` | **False** |
| **循環提升 (Escalate) 信號** | 指示目前的處理循環應該終止。 | `actions.escalate: True` | **False** |
| **錯誤事件** | 代表執行過程中發生的錯誤（如安全過濾或資源限制）。 | `error_code`: 錯誤代碼<br>`error_message`: 錯誤描述 | **False** |

#### 補充關鍵屬性說明

*   **唯一識別碼**：
    *   `event.id`：此特定事件實例的唯一 ID。
    *   `event.invocation_id`：整個「使用者請求到最終回應」週期的 ID，對於**追蹤與記錄**非常有用。
*   **動作與副作用 (`actions`)**：
    狀態與 Artifact 的變更並非立即寫入，而是封裝在 `EventActions` 物件中，附加在產生變更後的**下一個事件**裡，由 `SessionService` 負責處理並更新持久狀態。
*   **長效工具例外**：
    如果事件包含針對標記為 `is_long_running=True` 的工具呼叫，則 `is_final_response()` 會判定為 **True**，因為這通常需要向使用者顯示處理中的狀態。

在 Agent Development Kit (ADK) 的運作中，**事件 (Event)** 是資訊流的基本單位，擷取了代理程式執行過程中的特定時間點。以下是事件在 ADK 中的四大關鍵作用：

---
### 事件（Event）四大關鍵作用表

| 關鍵作用 | 核心說明 | 具體用途與範例 |
| :--- | :--- | :--- |
| **1. 標準化通訊 (Communication)** | 作為系統各組件間的**統一訊息格式**。 | 在 **UI、Runner、代理程式、LLM 與工具**之間傳遞資訊。一切資訊（訊息、工具請求、錯誤）皆以 Event 形式流動。 |
| **2. 狀態與構件變更信號 (Signaling Changes)** | 攜帶**狀態修改指令**並追蹤構件 (Artifact) 的更新。 | 透過 `actions` 欄位發送 `state_delta`（狀態差異）或 `artifact_delta`（構件版本更新）信號，供 **SessionService** 確保持久性。 |
| **3. 引導控制流 (Control Flow)** | 作為框架的「信號」，決定**下一步執行路徑**。 | 使用 `transfer_to_agent` 指示**移交控制權**給其他代理程式，或使用 `escalate` 標記**終止循環**。 |
| **4. 歷史記錄與可觀察性 (Observability)** | 提供按時間順序排列的**完整互動紀錄**。 | 所有事件會記錄在 `session.events` 中，對於**偵錯、稽核**以及逐步了解代理程式行為邏輯具有極高價值。 |

#### 補充細節
*   **不可變性**：事件是**不可變的記錄**，確保了歷史軌跡的可靠性。
*   **元資料追蹤**：每個事件都包含 `id`（唯一標識）與 `invocation_id`（追蹤整個請求週期），方便開發者進行關聯分析。
*   **最終回應判定**：透過 `is_final_response()` 方法，可以從事件流中過濾掉中間步驟（如工具呼叫或內部狀態更新），僅提取出適合顯示給使用者的**完整回覆**。