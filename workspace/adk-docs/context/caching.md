# 使用 Gemini 進行快取 (Context caching)
🔔 `更新日期：2026-01-10`

[`ADK 支援`: `Python v1.15.0`]

在與代理 (agent) 合作完成任務時，您可能希望在對生成式 AI 模型的多次請求中重複使用擴展指令或大型資料集。為每個代理請求重新發送這些資料既緩慢、低效且可能耗費成本。在生成式 AI 模型中使用內容快取 (context caching) 功能可以顯著加快回應速度，並減少每次請求發送到模型的權杖 (token) 數量。

ADK 內容快取功能允許您在支援此功能的生成式 AI 模型（包括 Gemini 2.0 及更高版本模型）中快取請求資料。本文件說明如何設定及使用此功能。

## 設定內容快取

您可以在包裝代理的 ADK `App` 物件層級設定內容快取功能。請使用 `ContextCacheConfig` 類別來設定這些設定，如以下程式碼範例所示：

```python
from google.adk import Agent
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

# 設定一個使用 Gemini 2.0 或更高版本模型的代理
root_agent = Agent(
  # configure an agent using Gemini 2.0 or higher
)

# 建立具有內容快取配置的應用程式
app = App(
    name='my-caching-agent-app',
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,    # 觸發快取的最小權杖數
        ttl_seconds=600,    # 儲存時間最長達 10 分鐘
        cache_intervals=5,  # 使用 5 次後重新整理
    ),
)
```

## 配置設定

`ContextCacheConfig` 類別具有以下設定，用於控制代理的快取運作方式。當您配置這些設定時，它們將套用於應用程式中的所有代理。

-   **`min_tokens`** (int)：啟用快取所需的最小權杖數。此設定可讓您避免在效能提升微不足道的小型請求中產生快取開銷。預設值為 `0`。
-   **`ttl_seconds`** (int)：快取的存活時間 (TTL)，以秒為單位。此設定決定快取內容在重新整理前儲存的時間。預設值為 `1800`（30 分鐘）。
-   **`cache_intervals`** (int)：相同快取內容在過期前可使用的最大次數。此設定可讓您控制快取更新的頻率，即使 TTL 尚未過期。預設值為 `10`。

### 實作範例

- [`Cache Analysis`](../../python/agents/cache-analysis/)：展示如何分析內容快取效能的程式碼範例。

- [`Static Instruction`](../../python/agents/static-instruction/)：使用靜態指令實作數位寵物代理，更多資訊[參考](#static_instruction-vs-instructions)。

---
## 更多資訊

### `static_instruction` V.S. `instructions`

1. `static_instruction` (靜態指令)

    定義：這是在代理（Agent）層級設定的基礎指令。

    特性：

    - 持久性：它是代理程式的「靈魂」，在整個會話（Session）或多次對話轉向（Turns）中保持不變。
    - 用途：通常用於定義代理的角色（Persona）、核心任務、回覆風格或必須遵守的全局規則。
    - 快取友好：由於內容固定，非常適合用於 Context Caching（內容快取），能有效降低重複處理長文本的成本。

2. `instruction` (即時/單次指令)

    定義：通常指在特定對話轉向（Turn）中提供的動態指令。

    特性：
    - 即時性：針對當下特定的請求或任務進行補充。
    - 用途：用於處理需要根據上下文變化的指令，例如「請根據這份新上傳的 PDF 總結內容」。
    - 優先權：在某些子代理（Sub-agent）架構中，instruction 會與代理描述結合，用於導引模型在運行時進行任務分配。

**快速對比表**
| 特性     | static_instruction                      | instruction                           |
| -------- | --------------------------------------- | ------------------------------------- |
| 生效範圍 | 整個代理的生命週期 (Global)             | 單次請求或特定任務 (Context-specific) |
| 角色定義 | 適合定義角色、語氣、安全準則            | 適合定義當下的具體動作                |
| 變動頻率 | 極低                                    | 高 (隨對話上下文變動)                 |
| 底層機制 | 類似於 Gemini API 的 system_instruction | 類似於 User Prompt 或 Turn-based 指令 |

**開發建議：**

在構建多代理（Multi-agent）系統時，應將通用的行為規範寫在 static_instruction。如果 static_instruction 太長導致效能下降，建議將功能拆分到不同的子代理，並利用子代理的 description 來引導任務分發.
單一代理的細節控制和多代理轉接流程是不同的開發情境.
