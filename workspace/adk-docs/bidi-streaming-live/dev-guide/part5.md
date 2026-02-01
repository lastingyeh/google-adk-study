# 第 5 部分：如何使用音訊、圖片與影片

> 🔔 `更新日期：2026-02-01`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/streaming/dev-guide/part5/

本節涵蓋 ADK Live API 整合中的音訊、圖片與影片功能，包括支援的模型、音訊模型架構、規格，以及實作語音與影片功能的最佳實踐。

## 如何使用音訊

Live API 的音訊功能透過雙向音訊串流，實現亞秒級延遲的自然語音對話。本節介紹如何向模型發送音訊輸入以及如何接收音訊回應，包括格式要求、串流最佳實踐和用戶端實作模式。

### 發送音訊輸入

**音訊格式要求：**

在呼叫 `send_realtime()` 之前，請確保您的音訊數據已符合正確格式：

- **格式**：16 位元 PCM（有符號整數）
- **採樣率**：16,000 Hz (16kHz)
- **聲道**：單聲道 (Mono)

ADK 不執行音訊格式轉換。發送格式不正確的音訊將導致品質不佳或錯誤。

示範實作：[main.py:181-184](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L181-L184)


```python
# 建立音訊 Blob 對象
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000", # 設定 MIME 類型為 16kHz 的 PCM 音訊
    data=audio_data # 音訊原始數據
)
# 透過 LiveRequestQueue 發送即時音訊數據
live_request_queue.send_realtime(audio_blob)
```

#### 發送音訊輸入的最佳實踐

1. **分段串流 (Chunked Streaming)**：以小塊發送音訊以實現低延遲。根據您的延遲要求選擇分段大小：

   - **超低延遲**（即時對話）：10-20ms 分段（@ 16kHz 約 320-640 位元組）
   - **平衡**（建議）：50-100ms 分段（@ 16kHz 約 1600-3200 位元組）
   - **較低開銷**：100-200ms 分段（@ 16kHz 約 3200-6400 位元組）

   在整個工作階段中使用一致的分段大小以獲得最佳效能。例如：100ms @ 16kHz = 16000 採樣/秒 × 0.1 秒 × 2 位元組/採樣 = 3200 位元組。

2. **即時轉發 (Prompt Forwarding)**：ADK 的 `LiveRequestQueue` 會立即轉發每個分段，而不進行合併或批次處理。請選擇符合您延遲與頻寬要求的分段大小。不要等待模型回應才發送下一個分段。

3. **連續處理**：模型會連續處理音訊，而不是按回合處理。在啟用自動語音活動偵測 (VAD) 的情況下（預設值），只需持續串流音訊，讓 API 偵測語音即可。

4. **活動訊號**：僅在您明確停用 VAD 以進行手動回合控制時，才使用 `send_activity_start()` / `send_activity_end()`。由於 VAD 預設為啟用，因此大多數應用程式不需要活動訊號。

#### 在用戶端處理音訊輸入

在基於瀏覽器的應用程式中，擷取麥克風音訊並發送到伺服器需要使用 Web Audio API 配合 AudioWorklet 處理器。bidi-demo 展示了如何擷取麥克風輸入、將其轉換為所需的 16 位元 PCM 16kHz 格式，並持續串流至 WebSocket 伺服器。

**架構：**

1. **音訊擷取**：使用 Web Audio API 以 16kHz 採樣率存取麥克風
1. **音訊處理**：AudioWorklet 處理器即時擷取音訊影格
1. **格式轉換**：將 Float32Array 採樣轉換為 16 位元 PCM
1. **WebSocket 串流**：透過 WebSocket 將 PCM 分段發送到伺服器

示範實作：[audio-recorder.js:7-58](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-recorder.js#L7-L58)

```javascript
// 啟動音訊錄製工作線程 (AudioWorklet)
export async function startAudioRecorderWorklet(audioRecorderHandler) {
    // 建立一個 16kHz 採樣率的 AudioContext
    // 這符合 Live API 要求的輸入格式 (16-bit PCM @ 16kHz)
    const audioRecorderContext = new AudioContext({ sampleRate: 16000 });

    // 載入將即時處理音訊的 AudioWorklet 模組
    // AudioWorklet 在獨立線程上執行，以實現低延遲、無卡頓的音訊處理
    const workletURL = new URL("./pcm-recorder-processor.js", import.meta.url);
    await audioRecorderContext.audioWorklet.addModule(workletURL);

    // 請求存取使用者的麥克風
    // channelCount: 1 請求單聲道音訊，這是 Live API 所要求的
    micStream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1 }
    });
    const source = audioRecorderContext.createMediaStreamSource(micStream);

    // 建立使用自定義 PCM 錄音處理器的 AudioWorkletNode
    // 此節點將擷取音訊影格並將其發送給我們的處理函式
    const audioRecorderNode = new AudioWorkletNode(
        audioRecorderContext,
        "pcm-recorder-processor"
    );

    // 將麥克風來源連接到工作線程處理器
    // 處理器將接收音訊影格並透過 port.postMessage 發送出去
    source.connect(audioRecorderNode);
    audioRecorderNode.port.onmessage = (event) => {
        // 將 Float32Array 轉換為 Live API 要求的 16 位元 PCM 格式
        const pcmData = convertFloat32ToPCM(event.data);

        // 將 PCM 數據發送給處理函式（該函式將轉發至 WebSocket）
        audioRecorderHandler(pcmData);
    };
    return [audioRecorderNode, audioRecorderContext, micStream];
}

// 將 Float32 採樣轉換為 16 位元 PCM
function convertFloat32ToPCM(inputData) {
    // 建立一個相同長度的 Int16Array
    const pcm16 = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
        // Web Audio API 提供 [-1.0, 1.0] 範圍內的 Float32 採樣
        // 乘以 0x7fff (32767) 以轉換為 16 位元有符號整數範圍 [-32768, 32767]
        pcm16[i] = inputData[i] * 0x7fff;
    }
    // 返回底層的 ArrayBuffer（二進制數據）以便高效傳輸
    return pcm16.buffer;
}
```

示範實作：[pcm-recorder-processor.js:1-18](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/pcm-recorder-processor.js#L1-L18)

```javascript
// pcm-recorder-processor.js - 用於擷取音訊的 AudioWorklet 處理器
class PCMProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    process(inputs, outputs, parameters) {
        if (inputs.length > 0 && inputs[0].length > 0) {
            // 使用第一個聲道（單聲道）
            const inputChannel = inputs[0][0];
            // 複製緩衝區以避免記憶體回收再利用的問題
            const inputCopy = new Float32Array(inputChannel);
            this.port.postMessage(inputCopy);
        }
        return true;
    }
}

// 註冊處理器名稱
registerProcessor("pcm-recorder-processor", PCMProcessor);
```

示範實作：[app.js:977-986](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L979-L988)

```javascript
// 音訊錄製處理函式 - 針對每個音訊分段呼叫
function audioRecorderHandler(pcmData) {
    if (websocket && websocket.readyState === WebSocket.OPEN && is_audio) {
        // 以二進制 WebSocket 影格發送音訊（比 base64 JSON 更高效）
        websocket.send(pcmData);
        console.log("[CLIENT TO AGENT] Sent audio chunk: %s bytes", pcmData.byteLength);
    }
}
```

**關鍵實作細節：**

1. **16kHz 採樣率**：AudioContext 必須以 `sampleRate: 16000` 建立，以符合 Live API 要求。現代瀏覽器支援此採樣率。
2. **單聲道音訊**：請求單聲道音訊 (`channelCount: 1`)，因為 Live API 預期單聲道輸入。這可以減少頻寬和處理開銷。
3. **AudioWorklet 處理**：AudioWorklet 在獨立於主 JavaScript 線程的線程上執行，確保低延遲且不阻塞 UI 的音訊處理。
4. **Float32 到 PCM16 轉換**：Web Audio API 提供範圍為 [-1.0, 1.0] 的 Float32Array 音訊數據。乘以 32767 (0x7fff) 即可轉換為 16 位元有符號整數 PCM。
5. **二進制 WebSocket 影格**：直接透過 WebSocket 二進制影格發送 PCM 數據（ArrayBuffer），而不是在 JSON 中進行 base64 編碼。這可減少約 33% 的頻寬並消除編碼/解碼開銷。
6. **連續串流**：AudioWorklet 的 `process()` 方法會定期自動呼叫（對於 16kHz，通常一次處理 128 個採樣）。這為串流提供了穩定的大小分段。

這種架構確保了低延遲的音訊擷取和高效的傳輸，隨後伺服器透過 `LiveRequestQueue.send_realtime()` 將其轉發給 ADK Live API。

### 接收音訊輸出

當配置了 `response_modalities=["AUDIO"]` 時，模型會在事件串流中以 `inline_data` 組件返回音訊數據。

**音訊格式要求：**

模型輸出的音訊格式如下：

- **格式**：16 位元 PCM（有符號整數）
- **採樣率**：原生音訊模型為 24,000 Hz (24kHz)
- **聲道**：單聲道 (Mono)
- **MIME 類型**：`audio/pcm;rate=24000`

音訊數據以原始 PCM 位元組形式到達，可直接用於播放或進一步處理。除非您需要不同的採樣率或格式，否則不需要額外的轉換。

**接收音訊輸出：**

```python
from google.adk.agents.run_config import RunConfig, StreamingMode

# 配置音訊輸出
run_config = RunConfig(
    response_modalities=["AUDIO"],  # 音訊回應所需
    streaming_mode=StreamingMode.BIDI
)

# 處理來自模型的音訊輸出
async for event in runner.run_live(
    user_id="user_123",
    session_id="session_456",
    live_request_queue=live_request_queue,
    run_config=run_config
):
    # 事件可能包含多個部分（文字、音訊等）
    if event.content and event.content.parts:
        for part in event.content.parts:
            # 音訊數據以 MIME 類型為 audio/pcm 的 inline_data 形式到達
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                # 數據已經解碼為原始位元組 (24kHz, 16-bit PCM, mono)
                audio_bytes = part.inline_data.data

                # 將音訊串流發送至用戶端的邏輯
                await stream_audio_to_client(audio_bytes)

                # 或者儲存到檔案
                # with open("output.pcm", "ab") as f:
                #     f.write(audio_bytes)
```

> [!NOTE] 自動 Base64 解碼
Live API 傳輸協定將音訊數據作為 base64 編碼字串進行傳輸。google.genai 類型系統使用 Pydantic 的 base64 序列化功能 (`val_json_bytes='base64'`)，在反序列化 API 回應時自動將 base64 字串解碼為位元組。當您存取 `part.inline_data.data` 時，您收到的是即用型位元組，無需手動進行 base64 解碼。

#### 在用戶端處理音訊事件

bidi-demo 採用了不同的架構方法：它不直接在伺服器上處理音訊，而是將所有事件（包括音訊數據）轉發給 WebSocket 用戶端，並在瀏覽器中處理音訊播放。這種模式實現了關注點分離——伺服器專注於 ADK 事件串流，而用戶端則使用 Web Audio API 處理媒體播放。

示範實作：[main.py:225-233](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L225-L233)

```python
# bidi-demo 將所有事件（包括音訊）轉發給 WebSocket 用戶端
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    # 將事件轉換為 JSON 格式
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    # 透過 WebSocket 發送文字消息
    await websocket.send_text(event_json)
```

**示範實作（用戶端 - JavaScript）：**

用戶端實作涉及三個組件：WebSocket 訊息處理、使用 AudioWorklet 的音訊播放器設定，以及 AudioWorklet 處理器本身。

示範實作：[app.js:638-688](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L640-L690)

```javascript
// 1. WebSocket 訊息處理器
// 處理內容事件（文字或音訊）
if (adkEvent.content && adkEvent.content.parts) {
    const parts = adkEvent.content.parts;

    for (const part of parts) {
        // 處理內嵌數據（音訊）
        if (part.inlineData) {
            const mimeType = part.inlineData.mimeType;
            const data = part.inlineData.data;

            // 檢查是否為音訊 PCM 數據且音訊播放器已就緒
            if (mimeType && mimeType.startsWith("audio/pcm") && audioPlayerNode) {
                // 將 base64 解碼為 ArrayBuffer 並發送至 AudioWorklet 進行播放
                audioPlayerNode.port.postMessage(base64ToArray(data));
            }
        }
    }
}

// 將 base64 音訊數據解碼為 ArrayBuffer
function base64ToArray(base64) {
    // 將 base64url 轉換為標準 base64 (符合 RFC 4648)
    // base64url 使用 '-' 和 '_' 代替 '+' 和 '/'
    let standardBase64 = base64.replace(/-/g, '+').replace(/_/g, '/');

    // 如果需要，添加填充字元 '='
    // Base64 字串必須是 4 的倍數
    while (standardBase64.length % 4) {
        standardBase64 += '=';
    }

    // 使用瀏覽器 API 將 base64 字串解碼為二進制字串
    const binaryString = window.atob(standardBase64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    // 將每個字元代碼 (0-255) 轉換為位元組
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    // 返回底層 ArrayBuffer
    return bytes.buffer;
}
```

示範實作：[audio-player.js:5-24](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-player.js#L5-L24)

```javascript
// 2. 音訊播放器設定
// 啟動音訊播放器工作線程
export async function startAudioPlayerWorklet() {
    // 建立一個 24kHz 採樣率的 AudioContext
    // 這符合 Live API 的輸出音訊格式 (16-bit PCM @ 24kHz)
    // 注意：與輸入頻率 (16kHz) 不同 - Live API 以更高品質輸出
    const audioContext = new AudioContext({
        sampleRate: 24000
    });

    // 載入處理音訊播放的 AudioWorklet 模組
    // AudioWorklet 在音訊渲染線程執行，實現流暢且低延遲的播放
    const workletURL = new URL('./pcm-player-processor.js', import.meta.url);
    await audioContext.audioWorklet.addModule(workletURL);

    // 使用自定義 PCM 播放處理器建立 AudioWorkletNode
    // 此節點將透過 postMessage 接收音訊數據並透過揚聲器播放
    const audioPlayerNode = new AudioWorkletNode(audioContext, 'pcm-player-processor');

    // 將播放節點連接到音訊目的地（揚聲器/耳機）
    // 建立音訊圖：AudioWorklet → AudioContext.destination
    audioPlayerNode.connect(audioContext.destination);

    return [audioPlayerNode, audioContext];
}
```

示範實作：[pcm-player-processor.js:5-76](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/pcm-player-processor.js#L5-L76)


```javascript
// 3. AudioWorklet 處理器（環狀緩衝區 Ring Buffer）
// 緩衝並播放 PCM 音訊的 AudioWorklet 處理器
class PCMPlayerProcessor extends AudioWorkletProcessor {
    constructor() {
        super();

        // 初始化環狀緩衝區 (24kHz x 180 秒 = 約 430 萬個採樣)
        // 環狀緩衝區可吸收網路抖動並確保流暢播放
        this.bufferSize = 24000 * 180;
        this.buffer = new Float32Array(this.bufferSize);
        this.writeIndex = 0;  // 寫入新音訊數據的位置
        this.readIndex = 0;   // 讀取播放數據的位置

        // 處理來自主要線程的訊息
        this.port.onmessage = (event) => {
            // 中斷時重設緩衝區（例如使用者打斷模型回應）
            if (event.data.command === 'endOfAudio') {
                this.readIndex = this.writeIndex; // 透過將讀取位置跳至寫入位置來清除緩衝區
                return;
            }

            // 從傳入的 ArrayBuffer 解碼 Int16 陣列
            // Live API 發送的是 16 位元 PCM 音訊數據
            const int16Samples = new Int16Array(event.data);

            // 將音訊數據加入環狀緩衝區以供播放
            this._enqueue(int16Samples);
        };
    }

    // 將傳入的 Int16 數據推入環狀緩衝區
    _enqueue(int16Samples) {
        for (let i = 0; i < int16Samples.length; i++) {
            // 將 16 位元整數轉換為 Web Audio API 要求的 [-1.0, 1.0] 浮點數
            // 除以 32768 (有符號 16 位元整數的最大正值)
            const floatVal = int16Samples[i] / 32768;

            // 儲存在環狀緩衝區的當前寫入位置
            this.buffer[this.writeIndex] = floatVal;
            // 寫入索引向前移動，在緩衝區末端繞回（循環緩衝區）
            this.writeIndex = (this.writeIndex + 1) % this.bufferSize;

            // 溢位處理：如果寫入趕上讀取，則將讀取索引向前移動
            // 這會覆蓋最舊的未播放採樣（少見，僅在極端網路延遲下發生）
            if (this.writeIndex === this.readIndex) {
                this.readIndex = (this.readIndex + 1) % this.bufferSize;
            }
        }
    }

    // 由 Web Audio 系統自動呼叫，每次約處理 128 個採樣
    // 此函式在音訊渲染線程上執行以獲取精確時序
    process(inputs, outputs, parameters) {
        const output = outputs[0];
        const framesPerBlock = output[0].length;

        for (let frame = 0; frame < framesPerBlock; frame++) {
            // 將採樣寫入輸出緩衝區（單聲道轉雙聲道）
            output[0][frame] = this.buffer[this.readIndex]; // 左聲道
            if (output.length > 1) {
                output[1][frame] = this.buffer[this.readIndex]; // 右聲道（複製以實現立體聲）
            }

            // 除非緩衝區為空（下溢保護），否則向前移動讀取索引
            if (this.readIndex != this.writeIndex) {
                this.readIndex = (this.readIndex + 1) % this.bufferSize;
            }
            // 如果 readIndex == writeIndex，表示沒有數據 - 輸出靜音 (0.0)
        }

        return true; // 保持處理器運作（返回 false 則終止）
    }
}

// 註冊處理器
registerProcessor('pcm-player-processor', PCMPlayerProcessor);
```

**關鍵實作模式：**

1. **Base64 解碼**：伺服器在 JSON 中將音訊數據作為 base64 編碼字串發送。用戶端必須先解碼為 ArrayBuffer 才能傳遞給 AudioWorklet。需處理標準 base64 和 base64url 編碼。
2. **24kHz 採樣率**：AudioContext 必須以 `sampleRate: 24000` 建立，以符合 Live API 輸出格式（與 16kHz 輸入不同）。
3. **環狀緩衝區架構**：使用循環緩衝區處理多變的網路延遲並確保流暢播放。緩衝區儲存 Float32 採樣，並透過覆蓋最舊數據處理溢位。
4. **PCM16 到 Float32 轉換**：Live API 發送 16 位元有符號整數。除以 32768 即可轉換為 Web Audio API 要求的 [-1.0, 1.0] 範圍內的 Float32。
5. **單聲道轉雙聲道**：處理器將單聲道音訊複製到左、右聲道進行立體聲輸出，確保與所有音訊裝置相容。
6. **中斷處理**：發生中斷事件時，發送 `endOfAudio` 指令，透過設定 `readIndex = writeIndex` 來清除緩衝區，防止播放過時音訊。

此架構可確保流暢、低延遲的音訊播放，同時優雅地處理網路抖動和中斷。

## 如何使用圖片與影片

在 ADK 雙向串流中，圖片和影片都被處理為 JPEG 影格。與使用 HLS、mp4 或 H.264 的典型影片串流不同，ADK 使用簡單的逐影格圖片處理方法，靜態圖片和影片影格都作為單個 JPEG 圖片發送。

**圖片/影片規格：**

- **格式**：JPEG (`image/jpeg`)
- **影格率**：建議最高每秒 1 影格 (1 FPS)
- **解析度**：建議 768x768 像素

示範實作：[main.py:202-217](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L202-L217)

```python
# 解碼 base64 圖片數據
image_data = base64.b64decode(json_message["data"])
mime_type = json_message.get("mimeType", "image/jpeg")

# 將圖片作為 Blob 發送
image_blob = types.Blob(
    mime_type=mime_type,
    data=image_data
)
# 發送即時圖片數據
live_request_queue.send_realtime(image_blob)
```

**不適用於：**

- **即時影片動作識別** - 1 FPS 太慢，無法捕捉快速動作
- **即時體育分析或運動追蹤** - 對於快速移動的主體，時間解析度不足

**圖片處理範例用例：**

在 [Shopper's Concierge 示範](https://youtu.be/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&t=40)中，應用程式使用 `send_realtime()` 發送使用者上傳的圖片。代理程式辨識圖片背景並在電子商務網站上搜尋相關商品。

### 在用戶端處理圖片輸入

在基於瀏覽器的應用程式中，從使用者網路攝影機擷取圖片並發送至伺服器需要使用 MediaDevices API 存取攝影機、將影格擷取到畫布 (canvas) 並轉換為 JPEG 格式。bidi-demo 展示了如何開啟攝影機預覽視窗、擷取單個影格並將其作為 base64 編碼的 JPEG 發送至 WebSocket 伺服器。

**架構：**

1. **攝影機存取**：使用 `navigator.mediaDevices.getUserMedia()` 存取網路攝影機
1. **影片預覽**：在 `<video>` 元素中顯示即時攝影機畫面
1. **影格擷取**：將影片影格繪製到 `<canvas>` 並轉換為 JPEG
1. **Base64 編碼**：將畫布轉換為 base64 資料 URL 進行傳輸
1. **WebSocket 傳輸**：作為 JSON 訊息發送至伺服器

示範實作：[app.js:801-843](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L803-L845)

```javascript
// 1. 開啟攝影機預覽
// 開啟攝影機彈窗並開始預覽
async function openCameraPreview() {
    try {
        // 請求以 768x768 解析度存取使用者網路攝影機
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 768 },
                height: { ideal: 768 },
                facingMode: 'user'
            }
        });

        // 將串流設定給影片元素
        cameraPreview.srcObject = cameraStream;

        // 顯示彈窗
        cameraModal.classList.add('show');

    } catch (error) {
        console.error('存取攝影機錯誤:', error);
        addSystemMessage(`無法存取攝影機: ${error.message}`);
    }
}

// 關閉攝影機預覽並停止
function closeCameraPreview() {
    // 停止攝影機串流
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    // 清除影片來源
    cameraPreview.srcObject = null;

    // 隱藏彈窗
    cameraModal.classList.remove('show');
}
```

示範實作：[app.js:846-914](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L848-L916)

```javascript
// 2. 擷取並發送圖片
// 從即時預覽中擷取圖片
function captureImageFromPreview() {
    if (!cameraStream) {
        addSystemMessage('無可用的攝影機串流');
        return;
    }

    try {
        // 建立畫布以擷取影格
        const canvas = document.createElement('canvas');
        canvas.width = cameraPreview.videoWidth;
        canvas.height = cameraPreview.videoHeight;
        const context = canvas.getContext('2d');

        // 將當前影片影格繪製到畫布
        context.drawImage(cameraPreview, 0, 0, canvas.width, canvas.height);

        // 將畫布轉換為資料 URL 以供顯示
        const imageDataUrl = canvas.toDataURL('image/jpeg', 0.85);

        // 在聊天室中顯示擷取的圖片
        const imageBubble = createImageBubble(imageDataUrl, true);
        messagesDiv.appendChild(imageBubble);

        // 將畫布轉換為 blob 以發送至伺服器
        canvas.toBlob((blob) => {
            // 將 blob 轉換為 base64
            const reader = new FileReader();
            reader.onloadend = () => {
                // 移除 data:image/jpeg;base64, 前綴
                const base64data = reader.result.split(',')[1];
                sendImage(base64data);
            };
            reader.readAsDataURL(blob);
        }, 'image/jpeg', 0.85);

        // 關閉攝影機彈窗
        closeCameraPreview();

    } catch (error) {
        console.error('擷取圖片錯誤:', error);
        addSystemMessage(`無法擷取圖片: ${error.message}`);
    }
}

// 發送圖片至伺服器
function sendImage(base64Image) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        const jsonMessage = JSON.stringify({
            type: "image",
            data: base64Image,
            mimeType: "image/jpeg"
        });
        websocket.send(jsonMessage);
        console.log("[CLIENT TO AGENT] Sent image");
    }
}
```

**關鍵實作細節：**

1. **768x768 解析度**：請求理想解析度為 768x768，以符合建議規格。瀏覽器將提供最接近的可用解析度。
2. **面向使用者的攝影機**：`facingMode: 'user'` 約束選擇行動裝置的前置攝影機，適用於自拍。
3. **畫布影格擷取**：使用 `canvas.getContext('2d').drawImage()` 從即時影片串流中擷取單個影格。這會建立當前影片影格的靜態快照。
4. **JPEG 壓縮**：`toDataURL()` 和 `toBlob()` 的第二個參數是品質（0.0 到 1.0）。使用 0.85 可提供良好品質，同時保持檔案大小在可控範圍內。
5. **雙重輸出**：程式碼同時建立了用於即時 UI 顯示的資料 URL，以及用於高效 base64 編碼的 blob，展示了回應式使用者回饋的模式。
6. **資源清理**：關閉攝影機時務必呼叫 `getTracks().forEach(track => track.stop())` 以釋放硬體資源並關閉攝影機指示燈。
7. **Base64 編碼**：FileReader 將 blob 轉換為資料 URL (`data:image/jpeg;base64,<data>`)。在逗號處分割並取第二部分，即可獲得不含前綴的純 base64 數據。

此實作提供了具備預覽、單影格擷取功能的友善攝影機介面，並能高效地將數據傳輸至伺服器供 Live API 處理。

### 自定義影片串流工具支援

ADK 為在串流工作階段期間處理影片影格提供了特殊的工具支援。與同步執行的常規工具不同，串流工具可以在模型繼續生成回應時，非同步地產出影片影格。

**串流工具生命週期：**

1. **開始**：模型呼叫時，ADK 啟動您的異步產生器 (async generator) 函式
1. **串流**：您的函式透過 `AsyncGenerator` 持續產出結果
1. **停止**：當發生以下情況時，ADK 取消產生器任務：
1. 模型呼叫您提供的 `stop_streaming()` 函式
1. 工作階段結束
1. 發生錯誤

**重要**：您必須提供一個 `stop_streaming(function_name: str)` 函式作為工具，以便模型能明確停止串流操作。

有關實作處理影片影格並將其產出給模型的自定義影片串流工具，請參閱 [串流工具說明文件](../streaming-tools.md)。

## 了解音訊模型架構

使用 Live API 建構語音應用程式時，最重要的決定之一是選擇正確的音訊模型架構。Live API 支援兩種根本不同的音訊處理模型：**原生(端到端)音訊 (Native Audio)** 和 **半串聯 (Half-Cascade)**。這些模型架構在處理音訊輸入和生成音訊輸出的方式上有所不同，這直接影響回應的自然度、工具執行可靠性、延遲特性以及整體用例適用性。

了解這些架構有助於您根據應用程式要求（例如優先考慮自然對話 AI、生產環境可靠性或特定功能可用性）做出明智的模型選擇。

### 原生音訊模型 (Native Audio Models)

一種完全整合的端到端音訊模型架構，模型直接處理音訊輸入並直接生成音訊輸出，不經過中間文字轉換。這種方法可實現更具自然語調的類人語音。

| 音訊模型架構 | 平台               | 模型                                                                                                                         | 備註       |
| ------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------- | ---------- |
| 原生音訊     | Gemini Live API    | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-live)          | 公開可用   |
| 原生音訊     | Vertex AI Live API | [gemini-live-2.5-flash-native-audio](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api) | 公開預覽版 |

**關鍵特性：**

- **端到端音訊處理**：直接處理音訊輸入並生成音訊輸出，無需中間轉換為文字
- **自然語調**：產生更具類人的語音模式、語調和情感表現力
- **擴展語音庫**：支援所有半串聯語音，以及來自文字轉語音 (TTS) 服務的額外語音
- **自動語言偵測**：從對話背景中判斷語言，無需明確配置
- **進階對話功能**：
- **[情感對話](#主動性與情感對話)**：根據輸入的表情和語氣調整回應風格，偵測情緒線索
- **[主動音訊](#主動性與情感對話)**：可以主動決定何時回應、提供建議或忽略無關輸入
- **動態思考**：支援思考摘要和動態思考預算
- **僅限音訊 (AUDIO-only) 回應模式**：不支援 `RunConfig` 的 TEXT 回應模式，導致初始回應時間較慢

### 半串聯模型 (Half-Cascade Models)

一種混合架構，結合了原生音訊輸入處理與文字轉語音 (TTS) 輸出生成。在某些文件中也被稱為「級聯」模型。

音訊輸入是原生處理的，但回應首先生成為文字，然後轉換為語音。這種分離在生產環境中提供了更好的可靠性和更穩健的工具執行。

| 音訊模型架構 | 平台               | 模型                                                                                                             | 備註                     |
| ------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------- | ------------------------ |
| 半串聯       | Gemini Live API    | [gemini-2.0-flash-live-001](https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash-live)                  | 2025 年 12 月 9 日起棄用 |
| 半串聯       | Vertex AI Live API | [gemini-live-2.5-flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash#2.5-flash) | 私人 GA 版，不公開提供   |

**關鍵特性：**

- **混合架構**：結合原生音訊輸入處理與基於 TTS 的音訊輸出生成
- **支援文字回應模式**：除了 AUDIO 外，還支援 `RunConfig` 的 TEXT 回應模式，在僅限文字的用例中可實現更快的響應
- **明確語言控制**：支援透過 `speech_config.language_code` 手動配置語言代碼
- **成熟的 TTS 品質**：利用經驗證的文字轉語音技術，獲得穩定一致的音訊輸出
- **支援的語音**：Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr（8 種內建語音）

### 如何處理模型名稱

建構 ADK 應用程式時，您需要指定要使用的模型。建議的方法是使用環境變數來配置模型，這樣可以隨著模型可用性和命名的變化而保持靈活性。

**建議模式：**

```python
import os
from google.adk.agents import Agent

# 使用環境變數，並提供一個合理的預設值
agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[...],
    instruction="..."
)
```

**為什麼要使用環境變數：**

- **模型可用性變化**：模型會定期發佈、更新和棄用（例如 `gemini-2.0-flash-live-001` 於 2025 年 12 月 9 日被棄用）
- **平台專屬名稱**：Gemini Live API 和 Vertex AI Live API 對於相同功能使用不同的模型命名約定
- **切換方便**：只需更新 `.env` 檔案即可更換模型，無需修改代碼
- **環境特定配置**：在開發、測試和生產環境中使用不同的模型

**在 `.env` 檔案中配置：**

```bash
# 用於 Gemini Live API（公開可用）
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# 用於 Vertex AI Live API（如果使用 Vertex AI）
# DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

> [!NOTE] 環境變數載入順序
> 在配合 `python-dotenv` 使用 `.env` 檔案時，您必須在匯入任何讀取環境變數的模組**之前**呼叫 `load_dotenv()`。否則 `os.getenv()` 會返回 `None` 並回退到預設值，忽視您的 `.env` 配置。
>
> **`main.py` 中的正確順序：**
>
> ```python
> from dotenv import load_dotenv
> from pathlib import Path
>
> # 在匯入代理程式之前載入 .env 檔案
> load_dotenv(Path(__file__).parent / ".env")
>
> # 現在可以安全地匯入使用環境變數的模組
> from google_search_agent.agent import agent
> ```
>
> **錯誤順序（無效）：**
>
>```python
> from dotenv import load_dotenv
> from google_search_agent.agent import agent  # 代理程式在此處讀取環境變數
>
> # 太晚了！代理程式已使用預設模型初始化
> load_dotenv(Path(__file__).parent / ".env")
> ```
>
> 這是 Python 的匯入行為：當您匯入模組時，其頂層代碼會立即執行。如果您的代理程式模組在匯入時呼叫 `os.getenv("DEMO_AGENT_MODEL")`，那麼 `.env` 檔案必須已經載入完成。

**選擇正確的模型：**

1. **選擇平台**：決定使用 Gemini Live API（公開）或 Vertex AI Live API（企業）
2. **選擇架構**：
3. 原生音訊用於具備進階功能的自然對話 AI
4. 半串聯用於具備工具執行能力的生產環境可靠性
5. **檢查當前可用性**：參考上面的模型表格和官方文件
6. **配置環境變數**：在 `.env` 檔案中設置 `DEMO_AGENT_MODEL`（參見 [`agent.py:11-16`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/google_search_agent/agent.py#L11-L16) 和 [`main.py:99-152`](https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L99-L152)）

### Live API 模型相容性與可用性

有關 Live API 模型相容性與可用性的最新資訊：

- **Gemini Live API 模型**：請參閱 [Gemini 模型文件](https://ai.google.dev/gemini-api/docs/models/gemini)
- **Vertex AI Live API 模型**：請參閱 [Vertex AI 模型文件](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

在部署到生產環境之前，請務必在官方文件中確認模型的可用性和功能支援。

## 音訊逐字稿 (Audio Transcription)

Live API 提供內建的音訊逐字稿功能，可自動將使用者輸入和模型輸出的語音轉換為文字。這消除了對外部逐字稿服務的需求，並能實現即時字幕、對話記錄和無障礙功能。ADK 透過 `RunConfig` 公開了這些功能，允許您為其中一個或兩個音訊方向啟用逐字稿。

> [!NOTE] 資料來源
[Gemini Live API - 音訊逐字稿](https://ai.google.dev/gemini-api/docs/live-guide#audio-transcriptions)

**配置：**

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# 預設行為：音訊逐字稿預設為「啟用」
# 輸入和輸出逐字稿都會自動配置
run_config = RunConfig(
    response_modalities=["AUDIO"]
    # input_audio_transcription 預設為 AudioTranscriptionConfig()
    # output_audio_transcription 預設為 AudioTranscriptionConfig()
)

# 要明確停用語音逐字稿：
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,   # 明確停用使用者輸入逐字稿
    output_audio_transcription=None   # 明確停用模型輸出逐字稿
)

# 僅啟用輸入逐字稿（停用輸出）：
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=types.AudioTranscriptionConfig(),  # 明確啟用（與預設相同，屬多餘）
    output_audio_transcription=None  # 明確停用
)

# 僅啟用輸出逐字稿（停用輸入）：
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,  # 明確停用
    output_audio_transcription=types.AudioTranscriptionConfig()  # 明確啟用（與預設相同，屬多餘）
)
```

**事件結構**：

逐字稿以 `types.Transcription` 對象的形式在 `Event` 對象中傳遞：

```python
from dataclasses import dataclass
from typing import Optional
from google.genai import types

@dataclass
class Event:
    content: Optional[Content]  # 音訊/文字內容
    input_transcription: Optional[types.Transcription]  # 使用者語音 → 文字
    output_transcription: Optional[types.Transcription]  # 模型語音 → 文字
    # ... 其他欄位
```

> [!NOTE] 了解更多
有關完整的 Event 結構，請參閱 [第 3 部分：Event 類別](part3.md#event-類別)。

每個 `Transcription` 對象有兩個屬性：

- **`.text`**：轉錄的文字（字串）
- **`.finished`**：布林值，指示轉錄是否完成 (True) 或僅為部分內容 (False)

**逐字稿如何傳遞**：

逐字稿作為事件串流中的獨立欄位傳遞，而不是作為內容組件。存取逐字稿數據時，務必使用防禦性的空值檢查：

**處理逐字稿：**

```python
from google.adk.runners import Runner

# ... 執行器設定程式碼 ...

async for event in runner.run_live(...):
    # 使用者語音逐字稿（來自輸入音訊）
    if event.input_transcription:  # 第一層檢查：逐字稿對象是否存在
        # 存取逐字稿文字和狀態
        user_text = event.input_transcription.text
        is_finished = event.input_transcription.finished

        # 第二層檢查：文字不為 None 或空值
        # 這處理了逐字稿正在進行中或為空的情況
        if user_text and user_text.strip():
            print(f"使用者說了：{user_text} (完成：{is_finished})")

            # 您的字幕更新邏輯
            update_caption(user_text, is_user=True, is_final=is_finished)

    # 模型語音逐字稿（來自輸出音訊）
    if event.output_transcription:  # 第一層檢查：逐字稿對象是否存在
        model_text = event.output_transcription.text
        is_finished = event.output_transcription.finished

        # 第二層檢查：文字不為 None 或空值
        if model_text and model_text.strip():
            print(f"模型說了：{model_text} (完成：{is_finished})")

            # 您的字幕更新邏輯
            update_caption(model_text, is_user=False, is_final=is_finished)
```

> [!NOTE] 逐字稿空值檢查的最佳實踐
> 對於逐字稿，務必使用兩層空值檢查：
>
> 1. 檢查逐字稿對象是否存在 (`if event.input_transcription`)
> 2. 檢查文字是否非空 (`if user_text and user_text.strip()`)
>
> 這種模式可以防止來自 `None` 值的錯誤，並處理可能為空的部分轉錄內容。

### 在用戶端處理音訊逐字稿

在網頁應用程式中，逐字稿事件需要從伺服器轉發到瀏覽器並在 UI 中渲染。bidi-demo 展示了一種模式：伺服器將所有 ADK 事件（包括逐字稿事件）轉發給 WebSocket 用戶端，而用戶端則負責將逐字稿顯示為對話氣泡，並針對部分轉錄與完成轉錄提供視覺指標。

**架構：**

1. **伺服器端**：透過 WebSocket 轉發逐字稿事件（已在上一節展示）
2. **用戶端**：處理來自 WebSocket 的 `inputTranscription` 和 `outputTranscription` 事件
3. **UI 渲染**：顯示帶有輸入中指示器的部分逐字稿，當 `finished: true` 時完成氣泡

示範實作：[app.js:530-653](https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L532-L655)

```javascript
// 處理輸入逐字稿（使用者的說話內容）
if (adkEvent.inputTranscription && adkEvent.inputTranscription.text) {
    const transcriptionText = adkEvent.inputTranscription.text;
    const isFinished = adkEvent.inputTranscription.finished;

    if (transcriptionText) {
        if (currentInputTranscriptionId == null) {
            // 建立新的逐字稿氣泡
            currentInputTranscriptionId = Math.random().toString(36).substring(7);
            currentInputTranscriptionElement = createMessageBubble(
                transcriptionText,
                true,  // isUser
                !isFinished  // isPartial
            );
            currentInputTranscriptionElement.id = currentInputTranscriptionId;
            currentInputTranscriptionElement.classList.add("transcription");
            messagesDiv.appendChild(currentInputTranscriptionElement);
        } else {
            // 更新現有的逐字稿氣泡
            if (currentOutputTranscriptionId == null && currentMessageId == null) {
                // 累加輸入逐字稿文字（Live API 發送的是增量片段）
                const existingText = currentInputTranscriptionElement
                    .querySelector(".bubble-text").textContent;
                const cleanText = existingText.replace(/\.\.\.$/, '');
                const accumulatedText = cleanText + transcriptionText;
                updateMessageBubble(
                    currentInputTranscriptionElement,
                    accumulatedText,
                    !isFinished
                );
            }
        }

        // 如果逐字稿完成，重置狀態
        if (isFinished) {
            currentInputTranscriptionId = null;
            currentInputTranscriptionElement = null;
        }
    }
}

// 處理輸出逐字稿（模型的說話內容）
if (adkEvent.outputTranscription && adkEvent.outputTranscription.text) {
    const transcriptionText = adkEvent.outputTranscription.text;
    const isFinished = adkEvent.outputTranscription.finished;

    if (transcriptionText) {
        // 當模型開始回應時，完成任何當前活躍的輸入逐字稿
        if (currentInputTranscriptionId != null && currentOutputTranscriptionId == null) {
            const textElement = currentInputTranscriptionElement
                .querySelector(".bubble-text");
            const typingIndicator = textElement.querySelector(".typing-indicator");
            if (typingIndicator) {
                typingIndicator.remove();
            }
            currentInputTranscriptionId = null;
            currentInputTranscriptionElement = null;
        }

        if (currentOutputTranscriptionId == null) {
            // 為模型建立新的逐字稿氣泡
            currentOutputTranscriptionId = Math.random().toString(36).substring(7);
            currentOutputTranscriptionElement = createMessageBubble(
                transcriptionText,
                false,  // isUser
                !isFinished  // isPartial
            );
            currentOutputTranscriptionElement.id = currentOutputTranscriptionId;
            currentOutputTranscriptionElement.classList.add("transcription");
            messagesDiv.appendChild(currentOutputTranscriptionElement);
        } else {
            // 更新現有的逐字稿氣泡
            const existingText = currentOutputTranscriptionElement
                .querySelector(".bubble-text").textContent;
            const cleanText = existingText.replace(/\.\.\.$/, '');
            updateMessageBubble(
                currentOutputTranscriptionElement,
                cleanText + transcriptionText,
                !isFinished
            );
        }

        // 如果逐字稿完成，重置狀態
        if (isFinished) {
            currentOutputTranscriptionId = null;
            currentOutputTranscriptionElement = null;
        }
    }
}
```

**關鍵實作模式：**

1. **增量文字累加**：Live API 可能以多個分段發送逐字稿。將新片段附加到現有內容來累加文字：

   ```javascript
   const accumulatedText = cleanText + transcriptionText;
   ```

2. **部分 vs 完成狀態**：使用 `finished` 標記來決定是否顯示輸入中指示器：

3. `finished: false` → 顯示輸入中指示器（例如 "..."）

4. `finished: true` → 移除輸入中指示器，完成氣泡

5. **氣泡狀態管理**：使用 ID 分別追蹤當前輸入和輸出的逐字稿氣泡。僅在開始新的轉錄時建立氣泡：

   ```javascript
   if (currentInputTranscriptionId == null) {
       // 建立新氣泡
   } else {
       // 更新現有氣泡
   }
   ```

6. **回合協調**：當模型開始回應（收到第一個輸出逐字稿）時，完成所有活躍的輸入逐字稿，以防止更新重疊。

此模式可確保流暢的即時逐字稿顯示，並能正確處理串流更新、回合切換以及使用者的視覺回饋。

### 多代理程式逐字稿要求

對於多代理程式情境（具有 `sub_agents` 的代理程式），無論您的 `RunConfig` 設定如何，ADK 都會自動啟用音訊逐字稿。此自動行為對於代理程式轉移功能是必要的，因為文字逐字稿用於在代理程式之間傳遞對話背景。

**自動啟用行為：**

當代理程式定義了 `sub_agents` 時，即使您明確將其設置為 `None`，ADK 的 `run_live()` 方法也會自動啟用輸入和輸出音訊逐字稿。這確保了代理程式轉移能透過向下一位代理程式提供文字背景而正常運作。

**為什麼這很重要：**

1. **無法停用**：在多代理程式情境中，您無法關閉逐字稿功能
2. **功能必需**：沒有文字背景，代理程式轉移將會失敗
3. **對開發者透明**：逐字稿事件會自動可用
4. **數據處理計畫**：您的應用程式將會收到必須處理的逐字稿事件

**實作細節：**

當滿足以下兩個條件時，自動啟用發生在 `Runner.run_live()` 中：

- 代理程式定義了 `sub_agents`
- 提供了 `LiveRequestQueue`（雙向串流模式）

> [!NOTE] 資料來源
[`runners.py:1395-1404`](https://github.com/google/adk-python/blob/fd2c0f556b786417a9f6add744827b07e7a06b7d/src/google/adk/runners.py#L1395-L1404)

## 語音配置 (Speech Config)

Live API 提供的語音配置功能可讓您自定義模型在生成音訊回應時的聲音。ADK 支援兩個層級的語音配置：**代理程式級別 (agent-level)**（每個代理程式的語音設定）和 **工作階段級別 (session-level)**（透過 RunConfig 的全域語音設定）。這使得複雜的多代理程式情境（不同代理程式可以有不同聲音）以及具備一致語音特徵的單代理程式應用程式成為可能。

> [!NOTE] 資料來源
[Gemini Live API - 能力指南](https://ai.google.dev/gemini-api/docs/live-guide)

### 代理程式級別配置

您可以透過建立一個帶有語音設定的自定義 `Gemini` LLM 實例，然後將該實例傳遞給 `Agent`，在每個代理程式的基礎上配置 `speech_config`。這在多代理程式工作流中特別有用，其中不同代理程式代表不同角色或身分。

**配置：**

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

# 建立帶有自定義語音配置的 Gemini 實例
custom_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"
            )
        ),
        language_code="en-US"
    )
)

# 將 Gemini 實例傳遞給代理程式
agent = Agent(
    model=custom_llm,
    tools=[google_search],
    instruction="你是一個有用的助手。"
)
```

### RunConfig 級別配置

您也可以在 RunConfig 中設定 `speech_config`，為工作階段中的所有代理程式套用預設語音配置。這適用於單代理程式應用程式，或當您希望所有代理程式具備一致聲音時。

**配置：**

=== "Python"

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"
            )
        ),
        language_code="en-US"
    )
)
```

### 配置優先順序

當同時提供代理程式級別（透過 `Gemini` 實例）和工作階段級別（透過 `RunConfig`）的 `speech_config` 時，**代理程式級別的配置具有優先權**。這允許您在 RunConfig 中設定預設聲音，同時為特定代理程式進行覆寫。

**優先規則：**

1. **Gemini 實例具備 `speech_config`**：使用 Gemini 的語音配置（最高優先級）
1. **RunConfig 具備 `speech_config`**：使用 RunConfig 的語音配置
1. **兩者皆未指定**：使用 Live API 預設語音（最低優先級）

**範例：**

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig
from google.adk.tools import google_search

# 建立帶有自定義語音的 Gemini 實例
custom_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"  # 代理程式級別：最高優先級
            )
        )
    )
)

# 代理程式使用帶有自定義語音的 Gemini 實例
agent = Agent(
    model=custom_llm,
    tools=[google_search],
    instruction="你是一個有用的助手。"
)

# RunConfig 具備預設語音（將被上述代理程式的 Gemini 配置覆寫）
run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"  # 對於上述代理程式，此設定將被覆寫
            )
        )
    )
)
```

### 多代理程式語音配置

對於多代理程式工作流，您可以透過建立具有不同 `speech_config` 值的獨立 `Gemini` 實例，為不同的代理程式分配不同聲音。這可以創造更自然、更具辨識度的對話，讓每個代理程式都有自己的語音個性。

**多代理程式範例：**

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig

# 具有親切語音的客戶服務代理程式
customer_service_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Aoede"  # 親切、溫暖的聲音
            )
        )
    )
)

customer_service_agent = Agent(
    name="customer_service",
    model=customer_service_llm,
    instruction="你是一位親切的客戶服務代表。"
)

# 具有專業語音的技術支援代理程式
technical_support_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Charon"  # 專業、權威的聲音
            )
        )
    )
)

technical_support_agent = Agent(
    name="technical_support",
    model=technical_support_llm,
    instruction="你是一位技術支援專家。"
)

# 協調工作流的根代理程式
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    instruction="協調客戶服務與技術支援。",
    sub_agents=[customer_service_agent, technical_support_agent]
)

# 不帶 speech_config 的 RunConfig - 每個代理程式使用自己的語音
run_config = RunConfig(
    response_modalities=["AUDIO"]
)
```

在此範例中，當客戶服務代理程式說話時，使用者會聽到 "Aoede" 的聲音。當技術支援代理程式接手時，使用者會聽到 "Charon" 的聲音。這創造了更具參與感且自然的多代理程式體驗。

### 配置參數

**`voice_config`**：指定用於音訊生成的內建語音

- 透過巢狀的 `VoiceConfig` 和 `PrebuiltVoiceConfig` 對象配置
- `voice_name`：內建語音的字串識別碼（例如 "Kore", "Puck", "Charon"）

**`language_code`**：用於語音合成的 ISO 639 語言代碼（例如 "en-US", "ja-JP"）

- 決定合成語音的語言與地區口音
- **模型特定的行為：**
- **半串聯模型**：使用指定的 `language_code` 進行 TTS 輸出
- **原生音訊模型**：可能會忽略 `language_code` 並從對話背景自動判斷語言。請參考特定模型的文件以了解支援情況。

### 可用語音

可用語音隨模型架構而異。要驗證您的特定模型有哪些可用語音：

- 請查看 [Gemini Live API 文件](https://ai.google.dev/gemini-api/docs/live-guide) 中的完整清單
- 在部署到生產環境前，在開發過程中測試語音配置
- 如果不支援該語音，Live API 將返回錯誤

**半串聯模型**支援以下語音：

- Puck
- Charon
- Kore
- Fenrir
- Aoede
- Leda
- Orus
- Zephyr

**原生音訊模型**支援擴展語音清單，其中包括所有半串聯語音，以及來自文字轉語音 (TTS) 服務的額外語音。有關原生音訊模型支援的完整語音清單：

- 請參閱 [Gemini Live API 文件](https://ai.google.dev/gemini-api/docs/live-guide#available-voices)
- 或查看原生音訊模型也支援的 [文字轉語音語音清單](https://cloud.google.com/text-to-speech/docs/voices)

與半串聯模型相比，擴展語音清單提供了更多關於語音特徵、口音和語言的選項。

### 平台可用性

兩個平台都支援語音配置，但語音可用性可能有所不同：

**Gemini Live API：**

- ✅ 完全支援，具備已記載的語音選項
- ✅ 半串聯模型：8 種語音 (Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr)
- ✅ 原生音訊模型：擴展語音清單（參見 [說明文件](https://ai.google.dev/gemini-api/docs/live-guide)）

**Vertex AI Live API：**

- ✅ 支援語音配置
- ⚠️ **平台差異**：語音可用性可能與 Gemini Live API 不同
- ⚠️ **需要驗證**：請查看 [Vertex AI 文件](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api) 以獲取當前支援的語音清單

**最佳實踐**：在開發過程中，請務必在目標平台上測試您選擇的語音配置。如果您選擇的語音在該平台/模型組合上不受支援，Live API 將在連線時返回錯誤。

### 重要注意事項

- **模型相容性**：語音配置僅適用於具有音訊輸出能力的 Live API 模型
- **配置層級**：您可以在代理程式級別（透過 `Gemini(speech_config=...)`）或工作階段級別 (`RunConfig(speech_config=...)`) 設定 `speech_config`。代理程式級別配置具有優先權。
- **代理程式級別用法**：要為每個代理程式配置語音，請建立一個帶有 `speech_config` 的 `Gemini` 實例，並將其傳遞給 `Agent(model=gemini_instance)`
- **預設行為**：如果兩個層級都未指定 `speech_config`，Live API 將使用預設語音
- **原生音訊模型**：自動根據對話背景判斷語言；可能不支援明確的 `language_code`
- **語音可用性**：具體的語音名稱可能因模型而異；請參考當前 Live API 文件中您所選模型支援的語音

> [!NOTE] 了解更多
有關完整的 RunConfig 參考，請參閱 [第 4 部分：了解 RunConfig](https://google.github.io/adk-docs/streaming/dev-guide/part4/index.md)。

## 語音活動偵測 (VAD)

語音活動偵測 (VAD) 是 Live API 的一項功能，可自動偵測使用者何時開始和停止說話，實現自然的對話切換而無需手動控制。VAD 在所有 Live API 模型中**預設為啟用**，允許模型根據偵測到的語音活動自動管理對話回合。

> [!NOTE] 資料來源
[Gemini Live API - 語音活動偵測 (VAD)](https://ai.google.dev/gemini-api/docs/live-guide#voice-activity-detection-vad)

### VAD 如何運作

當 VAD 啟用時（預設），Live API 會自動：

1. **偵測說話開始**：辨識使用者何時開始說話
1. **偵測說話結束**：辨識使用者何時停止說話（自然停頓）
1. **管理回合切換**：在使用者說完話後允許模型做出回應
1. **處理中斷**：透過來回交流實現自然的對話流

這創造了一種免持、自然的對話體驗，使用者無需手動訊號告知他們正在說話或已說完。

### 何時停用 VAD

在以下情境中，您應該停用自動 VAD：

- **一鍵通 (Push-to-talk) 實作**：您的應用程式手動控制何時應發送音訊（例如，吵雜環境或多人交談房間中的音訊互動應用程式）
- **用戶端語音偵測**：您的應用程式使用用戶端 VAD，向伺服器發送活動訊號，以減少連續音訊串流帶來的 CPU 和網路開銷
- **特定 UX 模式**：您的設計要求使用者手動指示何時說完話

當您停用 VAD（預設為啟用）時，必須使用手動活動訊號 (`ActivityStart`/`ActivityEnd`) 來控制對話回合。有關手動回合控制的詳細資訊，請參閱 [第 2 部分：活動訊號](part2.md#活動訊號-activity-signals)。

### VAD 配置

**預設行為（啟用 VAD，無需配置）：**

```python
from google.adk.agents.run_config import RunConfig

# VAD 預設為啟用 - 無需明確配置
run_config = RunConfig(
    response_modalities=["AUDIO"]
)
```

**停用自動 VAD（啟用手動回合控制）：**

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True  # 停用自動 VAD
        )
    )
)
```

### 用戶端 VAD 範例

建構語音驅動的應用程式時，您可能希望實作用戶端語音活動偵測 (VAD) 以減少 CPU 和網路開銷。此模式將瀏覽器端 VAD 與手動活動訊號結合，控制何時將音訊發送到伺服器。

**架構：**

1. **用戶端**：瀏覽器使用 Web Audio API（帶有基於 RMS 的 VAD 的 AudioWorklet）偵測語音活動
1. **訊號協調**：偵測到語音時發送 `activity_start`，停止說話時發送 `activity_end`
1. **音訊串流**：僅在活躍語音期間發送音訊分段
1. **伺服器配置**：停用自動 VAD，因為用戶端已處理偵測

#### 伺服器端配置

**配置：**

```python
from fastapi import FastAPI, WebSocket
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

# 配置 RunConfig 以停用自動 VAD
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True  # 用戶端處理 VAD
        )
    )
)
```

#### WebSocket 上行任務

**實作：**

```python
async def upstream_task(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    """從用戶端接收音訊和活動訊號。"""
    try:
        while True:
            # 從 WebSocket 接收 JSON 訊息
            message = await websocket.receive_json()

            if message.get("type") == "activity_start":
                # 用戶端偵測到語音 - 向模型發送訊號
                live_request_queue.send_activity_start()

            elif message.get("type") == "activity_end":
                # 用戶端偵測到靜音 - 向模型發送訊號
                live_request_queue.send_activity_end()

            elif message.get("type") == "audio":
                # 向模型串流音訊分段
                import base64
                audio_data = base64.b64decode(message["data"])
                audio_blob = types.Blob(
                    mime_type="audio/pcm;rate=16000",
                    data=audio_data
                )
                live_request_queue.send_realtime(audio_blob)

    except WebSocketDisconnect:
        live_request_queue.close()
```

#### 用戶端 VAD 實作

**實作：**

```javascript
// vad-processor.js - 用於語音偵測的 AudioWorklet 處理器
class VADProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.threshold = 0.05;  // 根據環境調整
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const channelData = input[0];
            let sum = 0;

            // 計算 RMS (均方根 Root Mean Square)
            for (let i = 0; i < channelData.length; i++) {
                sum += channelData[i] ** 2;
            }
            const rms = Math.sqrt(sum / channelData.length);

            // 發送語音偵測狀態訊號
            this.port.postMessage({
                voice: rms > this.threshold,
                rms: rms
            });
        }
        return true;
    }
}
registerProcessor('vad-processor', VADProcessor);
```

#### 用戶端協調

**協調 VAD 訊號：**

```javascript
// 主要應用程式邏輯
let isSilence = true;
let lastVoiceTime = 0;
const SILENCE_TIMEOUT = 2000;  // 傳送 activity_end 前等待 2 秒靜音

// 設定 VAD 處理器
const vadNode = new AudioWorkletNode(audioContext, 'vad-processor');
vadNode.port.onmessage = (event) => {
    const { voice, rms } = event.data;

    if (voice) {
        // 偵測到語音
        if (isSilence) {
            // 從靜音過渡到說話 - 發送 activity_start
            websocket.send(JSON.stringify({ type: "activity_start" }));
            isSilence = false;
        }
        lastVoiceTime = Date.now();
    } else {
        // 未偵測到語音 - 檢查是否超過靜音超時時間
        if (!isSilence && Date.now() - lastVoiceTime > SILENCE_TIMEOUT) {
            // 持續靜音 - 發送 activity_end
            websocket.send(JSON.stringify({ type: "activity_end" }));
            isSilence = true;
        }
    }
};

// 設定錄音機以串流音訊分段
audioRecorderNode.port.onmessage = (event) => {
    const audioData = event.data;  // Float32Array

    // 僅在偵測到語音時發送音訊
    if (!isSilence) {
        // 轉換為 PCM16 並發送至伺服器
        const pcm16 = convertFloat32ToPCM(audioData);
        const base64Audio = arrayBufferToBase64(pcm16);

        websocket.send(JSON.stringify({
            type: "audio",
            mime_type: "audio/pcm;rate=16000",
            data: base64Audio
        }));
    }
};
```

**關鍵實作細節：**

1. **基於 RMS 的語音偵測**：AudioWorklet 處理器計算音訊採樣的均方根 (RMS) 來偵測語音活動。RMS 提供了一種簡單但有效的音訊能量測量，可以區分語音與靜音。
2. **可調整閾值**：範例中的 `threshold` 值 (0.05) 可以根據環境進行調整。較低的閾值更靈敏（可偵測更小聲的說話，但可能會被背景噪音觸發），較高的閾值則需要更大聲的語音。
3. **靜音超時**：在發送 `activity_end` 之前使用超時（例如 2000ms），以避免在語音的自然停頓期間過早結束回合。這創造了更自然的對話流。
4. **狀態管理**：追蹤 `isSilence` 狀態以偵測靜音與語音之間的轉換。僅在靜音→語音轉換時發送 `activity_start`，且僅在持續靜音後發送 `activity_end`。
5. **條件式音訊串流**：僅在 `!isSilence` 時發送音訊分段以減少頻寬。根據對話的語音靜音比，這可以節省約 50-90% 的網路流量。
6. **AudioWorklet 線程分離**：VAD 處理器在音訊渲染線程上執行，確保即時效能不受主線程 JavaScript 執行或網路延遲的影響。

#### 用戶端 VAD 的優點

此模式具備以下優勢：

- **減少 CPU 和網路開銷**：僅在說話期間發送音訊，而不是持續發送靜音
- **更快的回應**：即時本地偵測，無需伺服器往返
- **更好的控制**：根據用戶端環境微調 VAD 靈敏度

> [!NOTE] 活動訊號時序 (Activity Signal Timing)
> 使用帶有用戶端 VAD 的手動活動訊號時：
>
>- 務必在發送第一個音訊分段**之前**發送 `activity_start`
>- 務必在發送最後一個音訊分段**之後**發送 `activity_end`
>- 模型僅會處理 `activity_start` 和 `activity_end` 訊號之間的音訊
>- 時序錯誤可能會導致模型忽略音訊或產生非預期行為

## 主動性與情感對話 (Proactivity and Affective Dialog)

Live API 提供的進階對話功能可實現更自然、更具情境感知的互動。**主動音訊 (Proactive audio)** 允許模型智慧地決定何時回應、在沒有明確提示的情況下提供建議，或忽略無關輸入。**情感對話 (Affective dialog)** 使模型能夠偵測並適應語音語調與內容中的情緒線索，調整其回應風格以實現更具同理心的互動。這些功能目前僅原生音訊模型支援。

> [!NOTE] 資料來源
[Gemini Live API - 主動音訊](https://ai.google.dev/gemini-api/docs/live-guide#proactive-audio) | [情感對話](https://ai.google.dev/gemini-api/docs/live-guide#affective-dialog)

**配置：**

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    # 模型可以在沒有明確提示的情況下發起回應
    proactivity=types.ProactivityConfig(proactive_audio=True),

    # 模型適應使用者情緒
    enable_affective_dialog=True
)
```

**主動性：**

啟用後，模型可以：

- 在未被要求的情況下提供建議
- 主動提供後續資訊
- 忽略無關或離題的輸入
- 根據背景預測使用者需求

**情感對話：**

模型分析語音語調與內容中的情緒線索，以便：

- 偵測使用者情緒（沮喪、開心、困惑等）
- 相應地調整回應風格與語調
- 在客戶服務情境中提供具同理心的回應
- 根據偵測到的情緒調整正式程度

**實務範例 - 客服機器人：**

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# 配置具備同理心的客戶服務
run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI,

    # 模型可以主動提供幫助
    proactivity=types.ProactivityConfig(proactive_audio=True),

    # 模型適應客戶情緒
    enable_affective_dialog=True
)

# 互動範例（說明性質 - 實際模型行為可能有所不同）：
# 客戶：「我已經等我的訂單三個星期了...」
# [模型可能偵測到語氣中的沮喪並調整回應]
# 模型：「我很遺憾聽到這個延遲的消息。讓我立即為您檢查訂單狀態。
#        您可以提供您的訂單編號嗎？」
#
# [主動性展現]
# 模型：「我看到您之前詢問過物流更新。您希望我為您之後的訂單設定通知嗎？」
#
# 注意：主動與情感行為是機率性的。模型的的情緒感知和主動建議會根據背景、
# 對話歷史以及固有的模型變異性而有所不同。
```

### 平台相容性

這些功能是**模型特定**的，並具有平台影響：

**Gemini Live API：**

- ✅ 在 `gemini-2.5-flash-native-audio-preview-12-2025`（原生音訊模型）上支援
- ❌ 在 `gemini-live-2.5-flash-preview`（半串聯模型）上不支援

**Vertex AI Live API：**

- ❌ 目前在 `gemini-live-2.5-flash`（半串聯模型）上不支援
- ⚠️ **平台差異**：主動性與情感對話需要原生音訊模型，而這些模型目前僅在 Gemini Live API 上可用

**關鍵洞察**：如果您的應用程式需要主動音訊或情感對話功能，您必須使用具備原生音訊模型的 Gemini Live API。兩個平台上的半串聯模型都不支援這些功能。

**測試主動性**：

要驗證主動行為是否運作：

1. **建立開放式背景**：提供資訊但不提出問題
   - 使用者：「我下個月計畫去日本旅行。」
   - 預期：模型提供建議、詢問後續問題
1. **測試情緒反應**：
   - 使用者：[沮喪語氣] 「這根本沒用！」
   - 預期：模型確認情緒、調整回應風格
1. **監測未提示的回應**：
   - 模型應偶爾提供相關資訊
   - 應忽略真正無關的輸入
   - 應根據背景預測使用者需求

**何時停用**：

在以下情況考慮停用主動性/情感對話：

- **正式/專業背景**，其中情感調整不恰當
- **高精準度任務**，其中可預測性至關重要
- **無障礙應用**，其中預期一致的行為
- **測試/除錯**，其中需要確定性的行為

## 總結

在本部分中，您學習了如何在 ADK 雙向串流應用程式中實作多模態功能，重點關注音訊、圖片與影片能力。我們介紹了音訊規格與格式要求，探討了原生音訊與半串聯架構之間的差異，研究了如何透過 LiveRequestQueue 與 Event 發送及接收音訊串流，並學習了音訊逐字稿、語音活動偵測以及主動/情感對話等進階功能。您現在了解如何透過正確的音訊處理建構自然的語音 AI 體驗，實作用於視覺背景的影片串流，並根據平台能力配置特定模型的特殊功能。憑藉對 ADK 多模態串流功能的全面了解，您已具備建構能流暢處理文字、音訊、圖片與影片的生產級應用程式的能力，跨足多元用例創造豐富且具互動性的 AI 體驗。

**恭喜！** 您已完成 ADK 雙向串流開發者指南。您現在已全面了解如何使用 Google 的 Agent Development Kit 建構生產級的即時串流 AI 應用程式。

← [上一頁：第 4 部分：了解 RunConfig](part4.md)
