# Runtime Configuration

🔔 `更新日期：2026 年 1 月 9 日`

`RunConfig` 定義了 ADK 中 Agent 的執行時行為與選項。它控制語音與串流設定、函式呼叫、Artifact 儲存以及 LLM 呼叫的限制。

建構 Agent 執行 (run) 時,您可以傳遞 `RunConfig` 來客製化 Agent 如何與模型互動、處理音訊以及串流回應。預設情況下,不會啟用串流,輸入也不會保留為 Artifact。使用 `RunConfig` 可覆寫這些預設值。

## 類別定義

`RunConfig` 類別包含 Agent 執行時行為的設定參數。

-   Python ADK 使用 Pydantic 進行此驗證。
-   Go ADK 預設使用可變結構 (mutable structs)。
-   Java ADK 通常使用不可變資料類別 (immutable data classes)。
-   TypeScript ADK 使用標準介面,並由 TypeScript 編譯器提供型別安全。

<details>
<summary>範例說明</summary>

> Python

```python
class RunConfig(BaseModel):
    """Agent 執行時行為的設定。"""

    model_config = ConfigDict(
        extra='forbid',
    )

    speech_config: Optional[types.SpeechConfig] = None
    response_modalities: Optional[list[str]] = None
    save_input_blobs_as_artifacts: bool = False
    support_cfc: bool = False
    streaming_mode: StreamingMode = StreamingMode.NONE
    output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
    max_llm_calls: int = 500
```

> TypeScript

```typescript
export interface RunConfig {
  speechConfig?: SpeechConfig;
  responseModalities?: Modality[];
  saveInputBlobsAsArtifacts: boolean;
  supportCfc: boolean;
  streamingMode: StreamingMode;
  outputAudioTranscription?: AudioTranscriptionConfig;
  maxLlmCalls: number;
  // ... 以及其他屬性
}

export enum StreamingMode {
  NONE = 'none',
  SSE = 'sse',
  BIDI = 'bidi',
}
```

> Go

```go
type StreamingMode string

const (
    StreamingModeNone StreamingMode = "none"
    StreamingModeSSE  StreamingMode = "sse"
)

// RunConfig 控制執行時行為。
type RunConfig struct {
    // 串流模式,None 或 StreamingMode.SSE。
    StreamingMode StreamingMode
    // 是否將輸入 Blob 儲存為 Artifact
    SaveInputBlobsAsArtifacts bool
}
```

> Java

```java
public abstract class RunConfig {

  public enum StreamingMode {
    NONE,
    SSE,
    BIDI
  }

  public abstract @Nullable SpeechConfig speechConfig();

  public abstract ImmutableList<Modality> responseModalities();

  public abstract boolean saveInputBlobsAsArtifacts();

  public abstract @Nullable AudioTranscriptionConfig outputAudioTranscription();

  public abstract int maxLlmCalls();

  // ...
}
```

</details>

## 執行時參數

| 參數 | Python 型別 | TypeScript 型別 | Go 型別 | Java 型別 | 預設值 (Py / TS / Go / Java) | 說明 |
| :--- | :--- | :--- |:--- |:--- | :--- |:--- |
| `speech_config` | `Optional[types.SpeechConfig]` | `SpeechConfig` (optional) | N/A | `SpeechConfig` (nullable via `@Nullable`) | `None` / `undefined`/ N/A / `null` | 使用 `SpeechConfig` 型別設定語音合成 (聲音、語言)。 |
| `response_modalities` | `Optional[list[str]]` | `Modality[]` (optional) | N/A | `ImmutableList<Modality>` | `None` / `undefined` / N/A / Empty `ImmutableList` | 預期的輸出模態列表 (例如 Python: `["TEXT", "AUDIO"]`; Java/TS: 使用結構化的 `Modality` 物件)。 |
| `save_input_blobs_as_artifacts` | `bool` | `boolean` | `bool` | `boolean` | `False` / `false` / `false` / `false` | 如果為 `true`,將輸入 Blob (例如上傳的檔案) 儲存為執行 Artifact 以供除錯/稽核。 |
| `streaming_mode` | `StreamingMode` | `StreamingMode` | `StreamingMode` | `StreamingMode` | `StreamingMode.NONE` / `StreamingMode.NONE` / `agent.StreamingModeNone` / `StreamingMode.NONE` | 設定串流行為:`NONE` (預設), `SSE` (Server-Sent Events), 或 `BIDI` (雙向)。 |
| `output_audio_transcription` | `Optional[types.AudioTranscriptionConfig]` | `AudioTranscriptionConfig` (optional) | N/A | `AudioTranscriptionConfig` (nullable via `@Nullable`) | `None` / `undefined` / N/A / `null` | 使用 `AudioTranscriptionConfig` 型別設定生成音訊輸出的轉錄。 |
| `max_llm_calls` | `int` | `number` | N/A | `int` | `500` / `500` / N/A / `500` | 限制每次執行的 LLM 呼叫總數。`0` 或負值表示不限制。超過語言限制 (例如 `sys.maxsize`, `Number.MAX_SAFE_INTEGER`) 會引發錯誤。 |
| `support_cfc` | `bool` | `boolean` | N/A | `bool` | `False` / `false` / N/A / `false` | **Python/TypeScript:** 啟用組合式函式呼叫 (Compositional Function Calling)。需要 `streaming_mode=SSE` 並使用 LIVE API。**實驗性功能。** |


### `speech_config`

[**ADK 支援**: `Python v0.1.0` | `Java v0.1.0`]

> [!Note]
    無論語言為何,`SpeechConfig` 的介面或定義皆相同。

具備音訊功能的 Live Agent 的語音設定。`SpeechConfig` 類別具有以下結構:

```python
class SpeechConfig(_common.BaseModel):
    """語音生成設定。"""

    voice_config: Optional[VoiceConfig] = Field(
        default=None,
        description="""使用的發話者設定。""",
    )
    language_code: Optional[str] = Field(
        default=None,
        description="""語音合成的語言代碼 (ISO 639,例如 en-US)。
        僅適用於 Live API。""",
    )
```

`voice_config` 參數使用 `VoiceConfig` 類別:

```python
class VoiceConfig(_common.BaseModel):
    """使用的聲音設定。"""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
        default=None,
        description="""使用的發話者設定。""",
    )
```

而 `PrebuiltVoiceConfig` 具有以下結構:

```python
class PrebuiltVoiceConfig(_common.BaseModel):
    """使用的預建發話者設定。"""

    voice_name: Optional[str] = Field(
        default=None,
        description="""使用的預建聲音名稱。""",
    )
```

這些巢狀設定類別允許您指定:

* `voice_config`: 使用的預建聲音名稱 (在 `PrebuiltVoiceConfig` 中)
* `language_code`: 語音合成的 ISO 639 語言代碼 (例如 "en-US")

實作支援語音的 Agent 時,設定這些參數以控制 Agent 說話時的聲音。

### `response_modalities`

[**ADK 支援**: `Python v0.1.0` | `Java v0.1.0`]

定義 Agent 的輸出模態。若未設定,預設為 AUDIO。回應模態決定 Agent 如何透過各種管道 (例如文字、音訊) 與使用者溝通。

### `save_input_blobs_as_artifacts`

[**ADK 支援**: `Python v0.1.0` | `Go v0.1.0` | `Java v0.1.0`]

啟用時,輸入 Blob 將在 Agent 執行期間儲存為 Artifact。這對於除錯和稽核用途非常有用,允許開發人員檢閱 Agent 接收到的確切資料。

### `support_cfc`

[**ADK 支援**: `Python v0.1.0` (實驗性)]

啟用組合式函式呼叫 (CFC) 支援。僅適用於使用 StreamingMode.SSE 時。啟用時,將呼叫 LIVE API,因為只有它支援 CFC 功能。

> [!TIP] "實驗性發布"
    `support_cfc` 功能為實驗性質,其 API 或行為可能會在未來版本中變更。

### `streaming_mode`

[**ADK 支援**: `Python v0.1.0` | `Go v0.1.0` (實驗性)]

設定 Agent 的串流行為。可能的值:

* `StreamingMode.NONE`: 不串流;回應以完整單元傳遞
* `StreamingMode.SSE`: Server-Sent Events 串流;從伺服器到用戶端的單向串流
* `StreamingMode.BIDI`: 雙向串流;雙向同時通訊

串流模式會影響效能和使用者體驗。SSE 串流讓使用者可以在回應生成時看到部分內容,而 BIDI 串流則啟用即時互動體驗。

### `output_audio_transcription`

[**ADK 支援**: `Python v0.1.0` | `Java v0.1.0`]

用於轉錄具備音訊回應功能的 Live Agent 音訊輸出的設定。這啟用了音訊回應的自動轉錄,以用於無障礙功能、記錄保存和多模態應用程式。

### `max_llm_calls`

[**ADK 支援**: `Python v0.1.0` | `Java v0.1.0`]

設定單次 Agent 執行的 LLM 呼叫總數限制。

* 大於 0 且小於 `sys.maxsize` 的值:強制執行 LLM 呼叫的上限
* 小於或等於 0 的值:允許無限次 LLM 呼叫 *(不建議用於生產環境)*

此參數可防止過度的 API 使用和潛在的失控程序。由於 LLM 呼叫通常會產生費用並消耗資源,因此設定適當的限制至關重要。

## 驗證規則

[**ADK 支援**: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

`RunConfig` 類別會驗證其參數以確保 Agent 正常運作。雖然 Python ADK 使用 `Pydantic` 進行自動型別驗證,但 Java 和 TypeScript ADK 依賴其靜態型別系統,並可能在 `RunConfig` 的建構函式中包含顯式檢查。
特別針對 `max_llm_calls` 參數:

1. 通常不允許極大的值 (如 Python 中的 `sys.maxsize`、Java 中的 `Integer.MAX_VALUE` 或 TypeScript 中的 `Number.MAX_SAFE_INTEGER`) 以防止問題。

2. 零或更小的值通常會觸發關於無限 LLM 互動的警告。

### 基本執行時設定

<details>
<summary>範例說明</summary>

> Python

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.NONE,
    max_llm_calls=100
)
```

> TypeScript

```typescript
import { RunConfig, StreamingMode } from '@google/adk';

const config: RunConfig = {
  streamingMode: StreamingMode.NONE,
  maxLlmCalls: 100,
};
```

> Go

```go
import "google.golang.org/adk/agent"

config := agent.RunConfig{
    StreamingMode: agent.StreamingModeNone,
}
```

> Java

```java
import com.google.adk.agents.RunConfig;
import com.google.adk.agents.RunConfig.StreamingMode;

RunConfig config = RunConfig.builder()
        .setStreamingMode(StreamingMode.NONE)
        .setMaxLlmCalls(100)
        .build();
```

</details>

此設定建立一個不串流的 Agent,限制 100 次 LLM 呼叫,適用於完整回應較佳的簡單任務導向 Agent。

### 啟用串流

<details>
<summary>範例說明</summary>

> Python

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    max_llm_calls=200
)
```

> TypeScript

```typescript
import { RunConfig, StreamingMode } from '@google/adk';

const config: RunConfig = {
  streamingMode: StreamingMode.SSE,
  maxLlmCalls: 200,
};
```

> Go

```go
import "google.golang.org/adk/agent"

config := agent.RunConfig{
    StreamingMode: agent.StreamingModeSSE,
}
```

> Java

```java
import com.google.adk.agents.RunConfig;
import com.google.adk.agents.RunConfig.StreamingMode;

RunConfig config = RunConfig.builder()
    .setStreamingMode(StreamingMode.SSE)
    .setMaxLlmCalls(200)
    .build();
```

</details>

使用 SSE 串流允許使用者在回應生成時看到內容,為聊天機器人和助理提供更靈敏的感覺。

### 啟用語音支援

<details>
<summary>範例說明</summary>

> Python

```python
from google.genai.adk import RunConfig, StreamingMode
from google.genai import types

config = RunConfig(
    speech_config=types.SpeechConfig(
        language_code="en-US",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"
            )
        ),
    ),
    response_modalities=["AUDIO", "TEXT"],
    save_input_blobs_as_artifacts=True,
    support_cfc=True,
    streaming_mode=StreamingMode.SSE,
    max_llm_calls=1000,
)
```

> TypeScript

```typescript
import { RunConfig, StreamingMode } from '@google/adk';

const config: RunConfig = {
    speechConfig: {
        languageCode: "en-US",
        voiceConfig: {
            prebuiltVoiceConfig: {
                voiceName: "Kore"
            }
        },
    },
    responseModalities: [
      { modality: "AUDIO" },
      { modality: "TEXT" }
    ],
    saveInputBlobsAsArtifacts: true,
    supportCfc: true,
    streamingMode: StreamingMode.SSE,
    maxLlmCalls: 1000,
    // ...
};
```

> Java

```java
import com.google.adk.agents.RunConfig;
import com.google.adk.agents.RunConfig.StreamingMode;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Modality;
import com.google.genai.types.Part;
import com.google.genai.types.PrebuiltVoiceConfig;
import com.google.genai.types.SpeechConfig;
import com.google.genai.types.VoiceConfig;

RunConfig runConfig =
    RunConfig.builder()
        .setStreamingMode(StreamingMode.SSE)
        .setMaxLlmCalls(1000)
        .setSaveInputBlobsAsArtifacts(true)
        .setResponseModalities(ImmutableList.of(new Modality("AUDIO"), new Modality("TEXT")))
        .setSpeechConfig(
            SpeechConfig.builder()
                .voiceConfig(
                    VoiceConfig.builder()
                        .prebuiltVoiceConfig(
                            PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                        .build())
                .languageCode("en-US")
                .build())
        .build();
```

</details>

這個綜合範例設定了一個 Agent,包含:

* 使用 "Kore" 聲音 (美式英語) 的語音功能
* 音訊和文字輸出模態
* 輸入 Blob 的 Artifact 儲存 (對除錯有用)
* 啟用實驗性 CFC 支援 **(Python 和 TypeScript)**
* 用於靈敏互動的 SSE 串流
* 1000 次 LLM 呼叫的限制

### 啟用 CFC 支援

[**ADK 支援**: `Python v0.1.0` | `Typescript v0.2.0` (實驗性)]

<details>
<summary>範例說明</summary>

> Python

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    support_cfc=True,
    max_llm_calls=150
)
```

> TypeScript

```typescript
import { RunConfig, StreamingMode } from '@google/adk';

const config: RunConfig = {
    streamingMode: StreamingMode.SSE,
    supportCfc: true,
    maxLlmCalls: 150,
};
```

</details>

啟用組合式函式呼叫 (CFC) 會建立一個可根據模型輸出動態執行函式的 Agent,這對於需要複雜工作流程的應用程式非常強大。

> [!TIP] "實驗性發布"
    組合式函式呼叫 (CFC) 串流功能為實驗性發布。
