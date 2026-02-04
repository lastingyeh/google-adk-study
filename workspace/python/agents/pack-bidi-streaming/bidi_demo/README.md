# ADK 雙向串流演示應用 - 技術文件

本文件詳細說明了 `bidi_demo` 應用的前後端架構與實作細節。該應用基於 Google ADK (Agent Development Kit)，展示了如何透過 WebSocket 實現與 AI 代理的多模態（文字、音訊、影像）即時雙向串流互動。

## 1. 系統架構概觀

本應用採前後端分離架構。前端利用 Web Audio API 進行低延遲音訊處理，後端基於 FastAPI 與 ADK Runner 實現非同步雙向串流通訊。

### 核心檔案說明

#### 前端 (Static)
- **`app.js`**: 應用主程式，負責 WebSocket 連線管理、UI 更新、事件處理及多媒體擷取。
- **`audio-player.js`**: 初始化音訊播放環境，載入播放 Worklet。
- **`audio-recorder.js`**: 初始化麥克風擷取環境，載入錄音 Worklet。
- **`pcm-player-processor.js`**: 運行於獨立線程的音訊播放處理器，使用環形緩衝區管理 PCM 串流。
- **`pcm-recorder-processor.js`**: 運行於獨立線程的音訊錄製處理器，擷取原始音訊樣本。

#### 後端 (Python)
- **`fast_api_app.py`**: 主進入點，提供 WebSocket 端點及會話管理邏輯。
- **`agent.py`**: 定義 AI 代理行為、模型配置與註冊工具（天氣、時間、搜尋）。
- **`app_utils/`**: 包含遙測 (Telemetry) 與類型定義等輔助工具。

## 2. 系統互動流程

```mermaid
sequenceDiagram
    participant U as 使用者 (User)
    participant UI as 前端介面 (App.js)
    participant WS as WebSocket 伺服器
    participant A as AI 代理 (Agent)

    U->>UI: 開啟網頁並點擊啟動音訊
    UI->>WS: 建立連線 (包含 RunConfig 選項)
    WS-->>UI: 確認連線成功

    rect rgb(240, 240, 240)
    Note over U, A: 文字互動流程
    U->>UI: 輸入文字並送出
    UI->>WS: 傳送 JSON 文字訊息
    WS->>A: 轉發至 AI 代理
    A-->>WS: 串流回傳文字/音訊
    WS-->>UI: 傳送 ADK 事件 (Content/Transcription)
    UI->>U: 更新對話泡泡與播放音訊
    end

    rect rgb(220, 240, 255)
    Note over U, A: 音訊互動流程
    U->>UI: 對麥克風說話
    UI->>WS: 傳送 PCM 二進位數據
    WS->>A: 進行即時轉錄與處理
    A-->>WS: 即時語音與轉錄
    WS-->>UI: 傳送轉錄事件 (Input/Output Transcription)
    UI->>U: 顯示即時轉錄內容
    end
```

## 3. 技術實作細節

### 3.1 WebSocket 通訊
使用標準 WebSocket 與後端通訊，URL 支援 `RunConfig` 選項：
- `proactivity`: 主動性開關。
- `affective_dialog`: 情感對話開關。

### 3.2 即時音訊處理
- **播放 (Output)**:
  - 取樣率：24000 Hz。
  - 機制：使用 **環形緩衝區 (Ring Buffer)** 緩存非同步抵達的 PCM 數據包，在 `AudioWorklet` 的 `process` 函數中穩定輸出。
- **錄製 (Input)**:
  - 取樣率：16000 Hz。
  - 格式轉換：在主線程將 Float32 樣本轉換為 **16-bit PCM (Int16)**，以減少網路頻寬消耗並符合後端 ASR 引擎需求。

### 3.3 圖像擷取
透過 `MediaDevices API` 存取相機，並在 `Canvas` 上擷取影格。擷取後的影格會轉換為 **JPEG (Base64)** 格式透過 WebSocket 傳送至代理進行影像理解。


## 4. 後端實作細節

### 4.1 代理定義與工具
後端使用 `google.adk.agents.Agent` 定義根代理，並註冊多個 Python 函式作為 LLM 的工具：
- **`get_weather(query)`**: 提供模擬的即時天氣數據。
- **`get_current_time(query)`**: 透過時區處理獲取精確的地區時間。
- **`google_search`**: 整合 Google 搜尋工具，增強代理的資訊獲取能力。

### 4.2 會話管理 (Session Management)
系統支援多種會話持久化方案：
- **Vertex AI Session Service**: 整合 Google Cloud 的 `reasoning-engines`，支援大規模生產環境。
- **In-Memory Session Service**: 提供本地快速測試與開發使用的記憶體內會話緩存。

### 4.3 雙向串流邏輯
在 `fast_api_app.py` 的 WebSocket 端點中，透過 `asyncio.gather` 同時執行兩個核心任務：
- **上游 (Upstream)**: 從 WebSocket 接收用戶輸入（音訊二進位、文字或圖像 JSON），並將其推送至 `LiveRequestQueue`。
- **下游 (Downstream)**: 呼叫 `runner.run_live()` 啟動 ADK 執行器。執行器會根據模型類型（原生音訊或半串聯）自動選擇最優的串流模態，並將產生的事件即時傳回前端。

### 4.4 自動模型適配
伺服器會分析所選模型的屬性：
- **原生音訊模型**: 配置為 `AUDIO` 回應模態，並啟用輸入/輸出轉錄。
- **半串聯模型**: 預設使用 `TEXT` 模態以獲得更短的延遲。

## 5. 情境實作流程圖

本章節提供詳細的情境流程時序圖，展示系統在不同使用場景下的運作機制，包含具體的函數呼叫與資料流向。

### 情境 1: 初始連線建立流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Browser as 瀏覽器 (index.html)
    participant AppJS as app.js
    participant FastAPI as fast_api_app.py
    participant Runner as ADK Runner
    participant Agent as agent.py::root_agent

    User->>Browser: 開啟網頁
    Browser->>AppJS: 載入頁面並執行
    AppJS->>AppJS: getWebSocketUrl()
    Note over AppJS: 組裝 WS URL 包含<br/>proactivity & affective_dialog
    AppJS->>AppJS: connectWebsocket()
    AppJS->>FastAPI: WebSocket 連線請求<br/>/ws/{user_id}/{session_id}
    FastAPI->>FastAPI: websocket_endpoint()
    FastAPI->>FastAPI: await websocket.accept()
    FastAPI->>FastAPI: 檢測模型類型<br/>is_native_audio = "native-audio" in model_name
    FastAPI->>FastAPI: 建立 RunConfig
    FastAPI->>FastAPI: session_service.get_session()
    alt 會話不存在
        FastAPI->>FastAPI: session_service.create_session()
    end
    FastAPI->>FastAPI: LiveRequestQueue()
    FastAPI->>FastAPI: asyncio.gather(<br/>upstream_task(),<br/>downstream_task())
    FastAPI-->>AppJS: WebSocket 連線成功
    AppJS->>AppJS: websocket.onopen()
    AppJS->>AppJS: updateConnectionStatus(true)
    AppJS->>AppJS: addSystemMessage("已連線至 ADK 串流伺服器")
    AppJS->>AppJS: addConsoleEntry('incoming', ...)
    AppJS-->>User: 顯示「已連線」狀態
```

### 情境 2: 文字訊息互動流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant AppJS as app.js
    participant FastAPI as fast_api_app.py
    participant Queue as LiveRequestQueue
    participant Runner as Runner.run_live()
    participant Agent as root_agent
    participant Tools as 工具函數

    User->>AppJS: 輸入文字並點擊「傳送」
    AppJS->>AppJS: messageForm.onsubmit()
    AppJS->>AppJS: createMessageBubble(message, true)
    AppJS->>AppJS: sendMessage(message)
    AppJS->>FastAPI: websocket.send(JSON.stringify({<br/>type: "text", text: message}))
    AppJS->>AppJS: addConsoleEntry('outgoing', ...)

    FastAPI->>FastAPI: upstream_task() 接收訊息
    FastAPI->>FastAPI: json.loads(text_data)
    FastAPI->>FastAPI: types.Content(parts=[<br/>types.Part(text=json_message['text'])])
    FastAPI->>Queue: live_request_queue.send_content(content)

    Queue->>Runner: 傳送內容至 run_live()
    Runner->>Agent: 處理使用者輸入

    opt 需要呼叫工具
        Agent->>Tools: get_weather(query) /<br/>get_current_time(query) /<br/>google_search()
        Tools-->>Agent: 返回工具結果
    end

    Agent->>Runner: 生成回應事件流
    Runner->>FastAPI: async for event in run_live()
    FastAPI->>FastAPI: downstream_task() 接收事件
    FastAPI->>FastAPI: event.model_dump_json()
    FastAPI->>AppJS: websocket.send_text(event_json)

    AppJS->>AppJS: websocket.onmessage()
    AppJS->>AppJS: JSON.parse(event.data)
    AppJS->>AppJS: addConsoleEntry('incoming', ...)

    alt 內容事件 (adkEvent.content)
        AppJS->>AppJS: createMessageBubble(part.text, false, true)
        Note over AppJS: currentMessageId 建立新泡泡
        AppJS->>AppJS: updateMessageBubble(element, text, true)
        Note over AppJS: 累積串流文字
    end

    alt 對話輪結束 (adkEvent.turnComplete)
        AppJS->>AppJS: 移除 typing-indicator
        AppJS->>AppJS: 重置 currentMessageId = null
    end

    AppJS->>AppJS: scrollToBottom()
    AppJS-->>User: 顯示 AI 回應訊息
```

### 情境 3: 音訊對話互動流程
```mermaid
sequenceDiagram
    participant User as 使用者
    participant AppJS as app.js
    participant Recorder as audio-recorder.js
    participant RecWorklet as pcm-recorder-processor.js
    participant FastAPI as fast_api_app.py
    participant Queue as LiveRequestQueue
    participant Runner as Runner.run_live()
    participant Agent as root_agent
    participant Player as audio-player.js
    participant PlayWorklet as pcm-player-processor.js

    User->>AppJS: 點擊「開始音訊」按鈕
    AppJS->>AppJS: startAudioButton.addEventListener('click')
    AppJS->>AppJS: startAudio()

    par 啟動音訊播放器
        AppJS->>Player: startAudioPlayerWorklet()
        Player->>Player: new AudioContext({sampleRate: 24000})
        Player->>Player: audioContext.audioWorklet.addModule()
        Player->>PlayWorklet: 載入 pcm-player-processor.js
        Player->>Player: new AudioWorkletNode()
        Player->>Player: node.connect(audioContext.destination)
        Player-->>AppJS: return [audioPlayerNode, audioPlayerContext]
    and 啟動音訊錄製器
        AppJS->>Recorder: startAudioRecorderWorklet(audioRecorderHandler)
        Recorder->>Recorder: new AudioContext({sampleRate: 16000})
        Recorder->>Recorder: navigator.mediaDevices.getUserMedia()
        Recorder->>Recorder: audioContext.audioWorklet.addModule()
        Recorder->>RecWorklet: 載入 pcm-recorder-processor.js
        Recorder->>Recorder: createMediaStreamSource(micStream)
        Recorder->>Recorder: new AudioWorkletNode()
        Recorder->>Recorder: source.connect(audioRecorderNode)
        Recorder-->>AppJS: return [audioRecorderNode, audioRecorderContext, micStream]
    end

    AppJS->>AppJS: addSystemMessage("音訊模式已啟用")
    AppJS->>AppJS: is_audio = true
    AppJS-->>User: 顯示「音訊模式已啟用」

    loop 使用者說話時
        User->>RecWorklet: 對麥克風說話
        RecWorklet->>RecWorklet: process(inputs, outputs)
        RecWorklet->>RecWorklet: 擷取 Float32 音訊樣本
        RecWorklet->>Recorder: port.postMessage(audioData)
        Recorder->>Recorder: convertFloat32ToPCM(event.data)
        Note over Recorder: 轉換為 16-bit PCM
        Recorder->>AppJS: audioRecorderHandler(pcmData)
        AppJS->>FastAPI: websocket.send(pcmData) [binary]

        FastAPI->>FastAPI: upstream_task() 接收 bytes
        FastAPI->>FastAPI: types.Blob("mime_type=audio/pcm,rate=16000")
        FastAPI->>Queue: live_request_queue.send_realtime(audio_blob)
        Queue->>Runner: 傳送音訊至 run_live()
        Runner->>Agent: 處理音訊輸入
    end

    loop AI 回應時
        Agent->>Runner: 生成回應 (音訊 + 轉錄)
        Runner->>FastAPI: async for event in run_live()

        alt 輸入轉錄事件
            FastAPI->>AppJS: send_text({inputTranscription: {...}})
            AppJS->>AppJS: adkEvent.inputTranscription
            AppJS->>AppJS: cleanCJKSpaces(transcriptionText)
            AppJS->>AppJS: createMessageBubble(text, true, !isFinished)
            AppJS->>AppJS: element.classList.add("transcription")
            Note over AppJS: 顯示使用者說話的轉錄
            AppJS-->>User: 顯示輸入轉錄泡泡
        end

        alt 輸出轉錄事件
            FastAPI->>AppJS: send_text({outputTranscription: {...}})
            AppJS->>AppJS: adkEvent.outputTranscription
            AppJS->>AppJS: createMessageBubble(text, false, !isFinished)
            AppJS->>AppJS: element.classList.add("transcription")
            Note over AppJS: 顯示 AI 說話的轉錄
            AppJS-->>User: 顯示輸出轉錄泡泡
        end

        alt 音訊內容事件
            FastAPI->>AppJS: send_text({content: {parts: [{inlineData: {...}}]}})
            AppJS->>AppJS: adkEvent.content.parts
            AppJS->>AppJS: part.inlineData (audio/pcm)
            AppJS->>AppJS: base64ToArray(data)
            AppJS->>PlayWorklet: audioPlayerNode.port.postMessage(arrayBuffer)
            PlayWorklet->>PlayWorklet: port.onmessage()
            PlayWorklet->>PlayWorklet: writeToRingBuffer(pcmData)
            PlayWorklet->>PlayWorklet: process(inputs, outputs)
            PlayWorklet->>PlayWorklet: readFromRingBuffer()
            PlayWorklet-->>User: 播放 AI 語音
        end

        alt 對話輪結束
            FastAPI->>AppJS: send_text({turnComplete: true})
            AppJS->>AppJS: 移除所有 typing-indicator
            AppJS->>AppJS: 重置狀態變數
        end
    end
```
### 情境 4: 相機圖像傳送流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant AppJS as app.js
    participant Modal as cameraModal (彈窗)
    participant Camera as MediaDevices API
    participant FastAPI as fast_api_app.py
    participant Queue as LiveRequestQueue
    participant Runner as Runner.run_live()
    participant Agent as root_agent

    User->>AppJS: 點擊「📷 相機」按鈕
    AppJS->>AppJS: cameraButton.addEventListener('click')
    AppJS->>AppJS: openCameraPreview()
    AppJS->>Camera: navigator.mediaDevices.getUserMedia({video: {...}})
    Camera-->>AppJS: return cameraStream
    AppJS->>Modal: cameraPreview.srcObject = cameraStream
    AppJS->>Modal: cameraModal.classList.add('show')
    AppJS-->>User: 顯示相機預覽彈窗

    User->>User: 查看預覽畫面

    alt 使用者取消
        User->>AppJS: 點擊「取消」或關閉按鈕
        AppJS->>AppJS: closeCameraPreview()
        AppJS->>Camera: cameraStream.getTracks().forEach(track.stop())
        AppJS->>Modal: cameraModal.classList.remove('show')
        AppJS-->>User: 關閉彈窗
    else 使用者擷取圖像
        User->>AppJS: 點擊「📷 傳送圖像」
        AppJS->>AppJS: captureImageFromPreview()
        AppJS->>AppJS: createElement('canvas')
        AppJS->>AppJS: context.drawImage(cameraPreview, 0, 0)
        AppJS->>AppJS: canvas.toDataURL('image/jpeg', 0.85)
        Note over AppJS: 轉換為 Base64
        AppJS->>AppJS: createImageBubble(imageDataUrl, true)
        AppJS-->>User: 顯示圖像泡泡

        AppJS->>AppJS: canvas.toBlob((blob) => {...})
        AppJS->>AppJS: FileReader().readAsDataURL(blob)
        AppJS->>AppJS: reader.result.split(',')[1]
        Note over AppJS: 提取 Base64 數據
        AppJS->>AppJS: sendImage(base64data)
        AppJS->>FastAPI: websocket.send(JSON.stringify({<br/>type: "image",<br/>data: base64Image,<br/>mimeType: "image/jpeg"}))
        AppJS->>AppJS: addConsoleEntry('outgoing', '圖像已擷取')
        AppJS->>AppJS: closeCameraPreview()

        FastAPI->>FastAPI: upstream_task() 接收文字訊息
        FastAPI->>FastAPI: json.loads(text_data)
        FastAPI->>FastAPI: base64.b64decode(json_message["data"])
        FastAPI->>FastAPI: types.Blob(mime_type=mime_type, data=image_data)
        FastAPI->>Queue: live_request_queue.send_realtime(image_blob)

        Queue->>Runner: 傳送圖像至 run_live()
        Runner->>Agent: 處理圖像輸入並生成回應
        Agent->>Runner: 返回圖像理解結果
        Runner->>FastAPI: async for event in run_live()
        FastAPI->>AppJS: websocket.send_text(event_json)
        AppJS->>AppJS: 處理並顯示 AI 回應
        AppJS-->>User: 顯示 AI 對圖像的理解
    end
```

### 情境 5: 對話中斷處理流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant AppJS as app.js
    participant FastAPI as fast_api_app.py
    participant Queue as LiveRequestQueue
    participant Runner as Runner.run_live()
    participant Agent as root_agent

    Note over Agent: AI 正在回應中...
    Runner->>FastAPI: 持續串流事件
    FastAPI->>AppJS: websocket.send_text(event_json)
    AppJS->>AppJS: 累積更新 currentBubbleElement
    AppJS-->>User: 顯示部分回應 (含 typing-indicator)

    User->>AppJS: 使用者打斷 (說話或輸入新訊息)
    AppJS->>FastAPI: websocket.send(新的音訊/文字數據)
    FastAPI->>Queue: live_request_queue.send_realtime() /<br/>send_content()
    Queue->>Runner: 傳送中斷信號
    Runner->>Agent: 中斷當前生成
    Agent->>Runner: 返回 interrupted 事件
    Runner->>FastAPI: event = {interrupted: true}
    FastAPI->>AppJS: websocket.send_text(event_json)

    AppJS->>AppJS: if (adkEvent.interrupted === true)

    alt 音訊正在播放
        AppJS->>AppJS: audioPlayerNode.port.postMessage({<br/>command: "endOfAudio"})
        Note over AppJS: 停止音訊播放
    end

    AppJS->>AppJS: currentBubbleElement.querySelector('.typing-indicator').remove()
    AppJS->>AppJS: currentBubbleElement.classList.add('interrupted')
    Note over AppJS: 標記訊息泡泡為「已中斷」

    alt 有輸出轉錄
        AppJS->>AppJS: currentOutputTranscriptionElement<br/>.classList.add('interrupted')
    end

    AppJS->>AppJS: 重置狀態變數:<br/>currentMessageId = null<br/>currentBubbleElement = null<br/>currentOutputTranscriptionId = null<br/>inputTranscriptionFinished = false

    AppJS-->>User: 顯示中斷狀態並準備接收新回應

    Note over Runner,Agent: 開始處理新的使用者輸入...
```

### 情境 6: RunConfig 變更與重新連線流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant AppJS as app.js
    participant FastAPI as fast_api_app.py
    participant Runner as Runner

    Note over AppJS,FastAPI: WebSocket 連線中...

    User->>AppJS: 切換「主動性」或「情感對話」核取方塊
    AppJS->>AppJS: enableProactivityCheckbox.addEventListener('change')
    AppJS->>AppJS: handleRunConfigChange()
    AppJS->>AppJS: if (websocket.readyState === WebSocket.OPEN)
    AppJS->>AppJS: addSystemMessage("正在使用更新後的設定重新連線...")
    AppJS->>AppJS: addConsoleEntry('outgoing', '由於設定變更正在重新連線', {<br/>proactivity: checked,<br/>affective_dialog: checked})
    AppJS->>FastAPI: websocket.close()
    Note over AppJS: 主動關閉連線

    FastAPI->>FastAPI: WebSocketDisconnect 異常
    FastAPI->>FastAPI: finally: live_request_queue.close()
    FastAPI->>FastAPI: logger.debug("客戶端正常斷開連線")

    AppJS->>AppJS: websocket.onclose()
    AppJS->>AppJS: updateConnectionStatus(false)
    AppJS->>AppJS: addSystemMessage("連線已斷開。將在 5 秒後重新連線...")
    AppJS->>AppJS: addConsoleEntry('error', 'WebSocket 已斷開連線')
    AppJS-->>User: 顯示「連線已斷開」

    AppJS->>AppJS: setTimeout(() => {connectWebsocket()}, 5000)
    Note over AppJS: 等待 5 秒

    AppJS->>AppJS: connectWebsocket()
    AppJS->>AppJS: getWebSocketUrl()
    Note over AppJS: 使用新的 RunConfig 參數
    AppJS->>FastAPI: WebSocket 連線請求<br/>/ws/{user_id}/{session_id}?<br/>proactivity=true&affective_dialog=true

    FastAPI->>FastAPI: websocket_endpoint(<br/>proactivity=True,<br/>affective_dialog=True)
    FastAPI->>FastAPI: 建立新的 RunConfig:<br/>types.ProactivityConfig(proactive_audio=True)<br/>enable_affective_dialog=True
    FastAPI->>FastAPI: session_service.get_session()
    Note over FastAPI: 恢復現有會話
    FastAPI->>FastAPI: 啟動新的 upstream_task() 和 downstream_task()

    FastAPI-->>AppJS: WebSocket 連線成功
    AppJS->>AppJS: websocket.onopen()
    AppJS->>AppJS: updateConnectionStatus(true)
    AppJS->>AppJS: addSystemMessage("已連線至 ADK 串流伺服器")
    AppJS-->>User: 顯示「已連線」(使用新設定)
```

### 情境 7: 工具呼叫處理流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant AppJS as app.js
    participant FastAPI as fast_api_app.py
    participant Runner as Runner.run_live()
    participant Agent as root_agent
    participant Weather as get_weather()
    participant Time as get_current_time()
    participant Search as google_search

    User->>AppJS: 輸入「舊金山的天氣如何?」
    AppJS->>FastAPI: websocket.send(JSON 文字訊息)
    FastAPI->>Queue: live_request_queue.send_content()
    Queue->>Runner: 傳送至 run_live()
    Runner->>Agent: 處理使用者查詢

    Agent->>Agent: 分析需要呼叫工具
    Note over Agent: LLM 決定使用 get_weather 工具
    Agent->>Weather: get_weather(query="舊金山")
    Note over Weather: if "sf" in query.lower()
    Weather-->>Agent: return "舊金山氣溫 60 度，有霧。"

    Agent->>Agent: 整合工具結果生成回應
    Agent->>Runner: 返回事件流

    Runner->>FastAPI: event = {content: {parts: [{<br/>executableCode: {...}<br/>}]}}
    FastAPI->>AppJS: 傳送可執行程式碼事件
    AppJS->>AppJS: adkEvent.content.parts (hasExecutableCode)
    AppJS->>AppJS: addConsoleEntry('incoming', <br/>'可執行程式碼 (PYTHON): ...')

    Runner->>FastAPI: event = {content: {parts: [{<br/>codeExecutionResult: {...}<br/>}]}}
    FastAPI->>AppJS: 傳送程式碼執行結果事件
    AppJS->>AppJS: adkEvent.content.parts (hasCodeExecutionResult)
    AppJS->>AppJS: addConsoleEntry('incoming', <br/>'程式碼執行結果 (OUTCOME_OK): ...')

    Runner->>FastAPI: event = {content: {parts: [{text: "..."}]}}
    FastAPI->>AppJS: 傳送最終文字回應
    AppJS->>AppJS: createMessageBubble(part.text, false)
    AppJS-->>User: 顯示「舊金山目前氣溫 60 度，有霧。」

    Runner->>FastAPI: event = {turnComplete: true}
    FastAPI->>AppJS: 傳送對話輪結束事件
    AppJS->>AppJS: 重置狀態變數

    alt 使用者詢問時間
        User->>AppJS: 輸入「舊金山現在幾點?」
        AppJS->>FastAPI: 同上流程
        Agent->>Time: get_current_time(query="舊金山")
        Time->>Time: tz = ZoneInfo("America/Los_Angeles")
        Time->>Time: datetime.datetime.now(tz)
        Time-->>Agent: return "查詢內容 舊金山 的目前時間為 ..."
        Agent->>Runner: 整合並返回
        Runner->>AppJS: 傳送回應事件
        AppJS-->>User: 顯示時間資訊
    else 使用者需要搜尋
        User->>AppJS: 輸入「搜尋最新的 AI 新聞」
        AppJS->>FastAPI: 同上流程
        Agent->>Search: google_search(query="最新的 AI 新聞")
        Search-->>Agent: return 搜尋結果
        Agent->>Runner: 整合並返回
        Runner->>AppJS: 傳送回應事件
        AppJS-->>User: 顯示搜尋結果摘要
    end
```

---

**情境說明總結**:

以上 7 個情境涵蓋了系統的完整運作流程：

1. **初始連線建立** - 展示從頁面載入到 WebSocket 連線建立的完整過程
2. **文字訊息互動** - 說明文字對話的雙向串流機制
3. **音訊對話互動** - 詳細描述音訊錄製、傳輸、處理與播放的完整流程
4. **相機圖像傳送** - 展示圖像擷取與多模態理解的實作
5. **對話中斷處理** - 說明系統如何優雅地處理使用者中斷
6. **RunConfig 變更** - 展示動態配置更新與會話恢復機制
7. **工具呼叫處理** - 說明 AI 代理如何呼叫外部工具並整合結果

每個時序圖都包含具體的函數名稱與參數,方便開發者追蹤程式碼執行路徑並進行除錯。
