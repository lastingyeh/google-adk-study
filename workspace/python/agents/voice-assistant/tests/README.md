# 詳細測試案例：Voice Assistant

## 簡介

此文件提供了 `voice-assistant` 專案中 `tests` 目錄下所有測試的詳細案例說明。旨在為專案建立清晰、一致且全面的測試文件，確保所有關鍵功能、模組匯入與專案結構都得到充分的驗證。

## Agent 測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 組態、`VoiceAssistant` 類別、Live API 組態及整合的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 組態** | **TC-AGENT-001** | 測試 `root_agent` 是否已正確匯出 | `voice_assistant` 套件已安裝 | 1. 從 `voice_assistant` 匯入 `root_agent`<br>2. 檢查 `root_agent` 是否存在且為 `Agent` 實例 | `None` | `root_agent` 不為 `None` 且為 `Agent` 類別的實例。 |
| **Agent 組態** | **TC-AGENT-002** | 測試 `root_agent` 是否使用正確的 Live API 模型 | `voice_assistant` 套件已安裝 | 1. 從 `voice_assistant` 匯入 `root_agent`<br>2. 檢查 `root_agent.model` 是否包含 "live" 或 "gemini-2" | `None` | 模型名稱應符合 Live API 的要求。 |
| **Agent 組態** | **TC-AGENT-003** | 測試 `root_agent` 是否有正確的名稱 | `voice_assistant` 套件已安裝 | 1. 從 `voice_assistant` 匯入 `root_agent`<br>2. 檢查 `root_agent.name` 是否為 "voice_assistant" | `None` | `root_agent.name` 應為 "voice_assistant"。 |
| **Agent 組態** | **TC-AGENT-004** | 測試 `root_agent` 是否有描述 | `voice_assistant` 套件已安裝 | 1. 從 `voice_assistant` 匯入 `root_agent`<br>2. 檢查 `root_agent.description` 是否存在且長度大於 0 | `None` | `root_agent` 應有非空的描述。 |
| **Agent 組態** | **TC-AGENT-005** | 測試 `root_agent` 是否有說明 | `voice_assistant` 套件已安裝 | 1. 從 `voice_assistant` 匯入 `root_agent`<br>2. 檢查 `root_agent.instruction` 是否存在且長度大於 0 | `None` | `root_agent` 應有非空的說明。 |
| **Agent 組態** | **TC-AGENT-006** | 測試 `root_agent` 是否有正確的生成組態 | `voice_assistant` 套件已安裝 | 1. 從 `voice_assistant` 匯入 `root_agent`<br>2. 檢查 `generate_content_config` 的 `max_output_tokens` | `None` | `max_output_tokens` 應小於或等於 300，以確保語音回應簡潔。 |
| **VoiceAssistant 類別** | **TC-AGENT-007** | 測試 `VoiceAssistant` 是否可以被實例化 | `voice_assistant` 套件已安裝 | 1. 從 `voice_assistant` 匯入 `VoiceAssistant`<br>2. 建立 `VoiceAssistant` 的實例 | `None` | `VoiceAssistant` 實例應成功建立。 |
| **VoiceAssistant 類別** | **TC-AGENT-008** | 測試 `VoiceAssistant` 是否使用正確的預設模型 | `voice_assistant` 套件已安裝 | 1. 建立 `VoiceAssistant` 的實例<br>2. 檢查 `assistant.agent.model` | `None` | 預設模型應為 Live API 模型。 |
| **VoiceAssistant 類別** | **TC-AGENT-009** | 測試 `VoiceAssistant` 是否接受自訂語音 | `voice_assistant` 套件已安裝 | 1. 建立 `VoiceAssistant` 的實例並傳入不同的 `voice_name` | `voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]` | 系統應能成功為每個指定的語音名稱建立 `VoiceAssistant` 實例。 |
| **VoiceAssistant 類別** | **TC-AGENT-010** | 測試 `VoiceAssistant` 是否有正確的 `RunConfig` | `voice_assistant` 套件已安裝 | 1. 建立 `VoiceAssistant` 的實例<br>2. 檢查 `run_config` 的類型與 `streaming_mode` | `None` | `run_config` 應為 `RunConfig` 實例，且 `streaming_mode` 應為 `BIDI`。 |
| **VoiceAssistant 類別** | **TC-AGENT-011** | 測試 `VoiceAssistant` 是否有語音組態 | `voice_assistant` 套件已安裝 | 1. 建立 `VoiceAssistant` 的實例<br>2. 檢查 `run_config.speech_config` 是否存在 | `None` | `speech_config` 不應為 `None`。 |
| **VoiceAssistant 類別** | **TC-AGENT-012** | 測試 `VoiceAssistant` 是否有正確的回應模態 | `voice_assistant` 套件已安裝 | 1. 建立 `VoiceAssistant` 的實例<br>2. 檢查 `run_config.response_modalities` | `None` | 至少要有一種回應模態。 |
| **VoiceAssistant 類別** | **TC-AGENT-013** | 測試 `VoiceAssistant` 的 `cleanup` 功能是否不會引發錯誤 | `voice_assistant` 套件已安裝 | 1. 建立 `VoiceAssistant` 的實例<br>2. 呼叫 `assistant.cleanup()` | `None` | `cleanup` 方法應能順利執行，不引發任何例外。 |
| **Live API 組態** | **TC-AGENT-014** | 測試 `StreamingMode.BIDI` 是否可用 | `google.adk.agents.run_config` 模組可匯入 | 1. 檢查 `StreamingMode` 是否有 `BIDI` 屬性 | `None` | `StreamingMode` 應包含 `BIDI` 模式。 |
| **Live API 組態** | **TC-AGENT-015** | 測試 `SpeechConfig` 是否可以被建立 | `google.genai.types` 模組可匯入 | 1. 使用 `types.SpeechConfig` 建立組態物件 | `voice_name="Puck"` | `SpeechConfig` 物件應成功建立。 |
| **Live API 組態** | **TC-AGENT-016** | 測試有效的語音名稱不會引發錯誤 | `google.genai.types` 模組可匯入 | 1. 使用一系列有效的語音名稱建立 `PrebuiltVoiceConfig` | `valid_voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]` | 所有有效的語音名稱都應能成功建立組態物件。 |
| **整合測試** | **TC-AGENT-017** | 測試發送文字訊息（整合測試） | `GOOGLE_API_KEY` 或 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數已設定 | 1. 建立 `VoiceAssistant` 實例<br>2. 呼叫 `send_text("Hello!")`<br>3. 檢查回應 | `text="Hello!"` | 應收到非空的回應字串。 |
| **整合測試** | **TC-AGENT-018** | 測試 `LiveRequestQueue` 的使用（整合測試） | `GOOGLE_API_KEY` 或 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數已設定 | 1. 建立 `LiveRequestQueue` 實例<br>2. 呼叫 `send_content` 發送訊息<br>3. 呼叫 `close` | `text="Test message"` | `LiveRequestQueue` 的操作不應引發錯誤，且佇列應能成功關閉。 |

## 匯入測試 (`tests/test_imports.py`)

此部分驗證專案所有關鍵套件的匯入是否正常，確保環境設定正確無誤。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **套件匯入** | **TC-IMPORT-001** | 測試主套件 `voice_assistant` 的匯入 | Python 環境已設定 | 1. 執行 `import voice_assistant` | `None` | 套件應成功匯入，且 `__version__` 屬性存在。 |
| **套件匯入** | **TC-IMPORT-002** | 測試從 `voice_assistant` 匯入 `VoiceAssistant` 類別 | `voice_assistant` 套件已安裝 | 1. 執行 `from voice_assistant import VoiceAssistant` | `None` | `VoiceAssistant` 類別應成功匯入。 |
| **套件匯入** | **TC-IMPORT-003** | 測試從 `voice_assistant` 匯入 `root_agent` | `voice_assistant` 套件已安裝 | 1. 執行 `from voice_assistant import root_agent` | `None` | `root_agent` 物件應成功匯入。 |
| **套件匯入** | **TC-IMPORT-004** | 測試 `PyAudio` 可用性旗標 `PYAUDIO_AVAILABLE` | `voice_assistant` 套件已安裝 | 1. 匯入 `PYAUDIO_AVAILABLE` 旗標<br>2. 檢查其類型 | `None` | `PYAUDIO_AVAILABLE` 應為布林值。 |
| **套件匯入** | **TC-IMPORT-005** | 測試 Google ADK 相關模組的匯入 | `google-adk` 已安裝 | 1. 匯入所有必要的 ADK 模組 | `None` | 所有指定的 ADK 模組都應成功匯入。 |

## 專案結構測試 (`tests/test_structure.py`)

此部分驗證專案中必要的檔案與目錄是否存在，確保結構完整性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **檔案與目錄結構** | **TC-STRUCT-001** | 測試 `README.md` 是否存在 | 專案已複製 | 1. 檢查專案根目錄 | `None` | `README.md` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-002** | 測試 `requirements.txt` 是否存在 | 專案已複製 | 1. 檢查專案根目錄 | `None` | `requirements.txt` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-003** | 測試 `pyproject.toml` 是否存在 | 專案已複製 | 1. 檢查專案根目錄 | `None` | `pyproject.toml` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-004** | 測試 `Makefile` 是否存在 | 專案已複製 | 1. 檢查專案根目錄 | `None` | `Makefile` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-005** | 測試 `.env.example` 是否存在 | 專案已複製 | 1. 檢查專案根目錄 | `None` | `.env.example` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-006** | 測試 `voice_assistant` 套件目錄是否存在 | 專案已複製 | 1. 檢查專案根目錄 | `None` | `voice_assistant/` 目錄應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-007** | 測試 `voice_assistant/__init__.py` 是否存在 | 專案已複製 | 1. 檢查 `voice_assistant/` 目錄 | `None` | `__init__.py` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-008** | 測試 `voice_assistant/agent.py` 是否存在 | 專案已複製 | 1. 檢查 `voice_assistant/` 目錄 | `None` | `agent.py` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-009** | 測試 `tests/` 目錄是否存在 | 專案已複製 | 1. 檢查專案根目錄 | `None` | `tests/` 目錄應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-010** | 測試 `tests/test_imports.py` 是否存在 | 專案已複製 | 1. 檢查 `tests/` 目錄 | `None` | `test_imports.py` 檔案應存在。 |
| **檔案與目錄結構** | **TC-STRUCT-011** | 測試 `tests/test_agent.py` 是否存在 | 專案已複製 | 1. 檢查 `tests/` 目錄 | `None` | `test_agent.py` 檔案應存在。 |
| **檔案內容** | **TC-STRUCT-012** | 測試 `README.md` 是否有實質內容 | `README.md` 存在 | 1. 讀取檔案內容<br>2. 檢查內容長度與關鍵字 | `None` | 檔案內容應大於 100 字元並包含 "Tutorial 15" 與 "Live API"。 |
| **檔案內容** | **TC-STRUCT-013** | 測試 `requirements.txt` 是否包含必要的依賴 | `requirements.txt` 存在 | 1. 讀取檔案內容<br>2. 檢查是否包含必要套件 | `None` | 檔案應包含 "google-genai", "pyaudio", "pytest"。 |
| **檔案內容** | **TC-STRUCT-014** | 測試 `pyproject.toml` 是否包含必要的元數據 | `pyproject.toml` 存在 | 1. 讀取檔案內容<br>2. 檢查是否包含元數據 | `None` | 檔案應包含套件名稱與 "google-genai" 依賴。 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
