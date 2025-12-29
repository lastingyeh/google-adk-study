# 教學 15：Live API 與音訊 - 即時語音互動

此實作展示了如何使用 Gemini 的 Live API 進行即時雙向串流，包括語音對話、音訊處理以及主動性和情感對話等進階功能。

## 功能

- ✅ 使用 `StreamingMode.BIDI` 進行雙向串流
- ✅ 使用 `LiveRequestQueue` 進行即時通訊
- ✅ 具備語音辨識的音訊輸入/輸出
- ✅ 多種語音設定 (Puck, Charon, Kore 等)
- ✅ 純文字示範模式 (無需麥克風)
- ✅ 互動式語音模式 (需要麥克風)
- ✅ 進階功能：主動性、情感對話、視訊串流
- ✅ 多代理人語音會話

## 先決條件

- Python 3.10+
- 已啟用 Vertex AI API 的 Google Cloud 專案
- (可選) 用於互動式語音模式的麥克風

## 設定

```bash
make setup
```

設定環境：
```bash
cp .env.example .env
# 編輯 .env 檔案，填入您的 Google Cloud 憑證
```

## 使用方式

### 純文字示範 (無需麥克風)

```bash
make demo
```

### ADK 網頁介面

```bash
make dev
```

開啟 http://localhost:8000 並從下拉選單中選擇 "voice_assistant"。

### Live API 示範

**文字輸入 + 音訊輸出** (建議 - 可與 ADK Runner 搭配使用)：
```bash
make basic_demo_text    # 文字回應
make basic_demo_audio   # 音訊回應 (透過喇叭播放)
```

**純音訊輸入** (直接使用 Live API - 繞過 ADK)：
```bash
make direct_audio_demo  # 麥克風 → 代理人 → 喇叭
```

⚠️ **重要音訊限制**：ADK `Runner.run_live()` API 目前僅支援**文字輸入與音訊輸出**。對於真正的雙向音訊 (麥克風輸入)，您必須使用：
- `make direct_audio_demo` - 直接使用 `genai.Client` API (繞過 ADK 代理人/工具)
- `make dev` - 帶有音訊按鈕的 ADK Web UI (WebSocket 連線)

詳情請參閱下方的[音訊輸入限制](#音訊輸入限制)。

## 音訊輸入限制

**可行的 ✅**：
- 文字輸入 → 音訊輸出 (透過 ADK Runner)
- 文字輸入 → 文字輸出 (透過 ADK Runner)
- ADK Web UI 音訊串流 (WebSocket)

**不可行的 ❌**：
- 透過 `LiveRequestQueue.send_realtime()` + `Runner.run_live()` 進行音訊輸入
- 透過 ADK 框架進行程式化的麥克風輸入

**為何這很重要**：
ADK Runner 不支援透過 `send_realtime()` 傳送音訊輸入的二進位大型物件 (blob)。對於真正的語音對語音互動，您有兩個選擇：

1. **直接使用 Live API** (`make direct_audio_demo`)：
   - 直接使用 `google.genai.Client`
   - 真正支援雙向音訊
   - ❌ 無法使用 ADK 代理人功能 (工具、狀態管理)
   - ✅ 官方 Google API，經證實可運作

2. **ADK Web UI** (`make dev`)：
   - 透過瀏覽器提供完整的音訊支援
   - ✅ 可使用 ADK 代理人功能 (工具、狀態)
   - ❌ 非程式化，需要手動互動

詳細分析請參閱 `log/20251012_152300_tutorial15_audio_input_critical_discovery.md`。

## 測試

執行所有測試：
```bash
make test
```

## 專案結構

```
voice-assistant/
├── voice_assistant/
│   ├── __init__.py              # 套件初始化
│   ├── agent.py                 # VoiceAssistant 類別 (匯出 root_agent)
│   ├── audio_utils.py           # 音訊錄製/播放工具
│   ├── basic_demo.py            # ✅ 文字→音訊示範 (可運作)
│   ├── direct_live_audio.py     # ✅ 音訊→音訊示範 (直接使用 API)
│   ├── demo.py                  # 純文字示範
│   ├── advanced.py              # 進階功能範例
│   └── multi_agent.py           # 多代理人語音會話
├── tests/
│   ├── test_agent.py         # 代理人設定測試
│   ├── test_imports.py       # 匯入驗證
│   └── test_structure.py     # 專案結構測試
├── Makefile
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## 可用聲音

- **Puck**：友善、健談
- **Charon**：低沉、權威
- **Kore**：溫暖、專業
- **Fenrir**：充滿活力、動感
- **Aoede**：平靜、舒緩

## Live API 模型

**原生音訊 (預設)**：`gemini-live-2.5-flash-preview-native-audio`
**半級聯音訊 (文字+音訊混合)**：`gemini-live-2.5-flash-preview`
**其他原生音訊 SKU**：`gemini-2.5-flash-native-audio-preview-09-2025`

## 重要注意事項

- 每個會話只能有一種回應模式 (文字或音訊，不能兩者皆有)
- 使用 `send_content()` 傳送文字，`send_realtime()` 傳送音訊/視訊
- 完成後務必使用 `close()` 關閉佇列
- 保持語音回應簡潔 (max_output_tokens=150-200)

## 資源

- [教學文件](../../docs/tutorial/15_live_api_audio.md)
- [Live API 文件](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini-live)
- [官方範例](https://github.com/google/adk-python/tree/main/contributing/samples/live_bidi_streaming_single_agent/)
