# Multi-LLM Agent 測試案例

## 簡介

此文件提供了 `multi-llm-agent` 專案的詳細測試案例，旨在確保所有關鍵功能都得到充分的驗證。

## Agent 模組測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 設定、替代 Agent、工具函式及整合的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 root_agent 是否可以被匯入。 | None | 1. 匯入 `root_agent` | None | 成功匯入 `root_agent` 物件 |
| **Agent 設定** | **TC-AGENT-002** | 測試 root_agent 是否為 Agent 的一個實例。 | None | 1. 檢查 `root_agent` 的類型 | None | `root_agent` 是 `Agent` 的實例 |
| **Agent 設定** | **TC-AGENT-003** | 測試 root_agent 是否有正確的名稱。 | None | 1. 檢查 `root_agent.name` 屬性 | None | 名稱為 `multi_llm_agent` |
| **Agent 設定** | **TC-AGENT-004** | 測試 root_agent 是否有正確的模型。 | None | 1. 檢查 `root_agent.model` 屬性 | None | 模型是 `LiteLlm` 的實例 |
| **Agent 設定** | **TC-AGENT-005** | 測試 root_agent 是否有描述。 | None | 1. 檢查 `root_agent.description` | None | 描述包含 `Multi-LLM agent` 和 `LiteLLM` |
| **Agent 設定** | **TC-AGENT-006** | 測試 root_agent 是否有指令。 | None | 1. 檢查 `root_agent.instruction` | None | 指令長度超過 100 個字元 |
| **Agent 設定** | **TC-AGENT-007** | 測試 root_agent 是否擁有工具。 | None | 1. 檢查 `root_agent.tools` | None | 擁有 3 個工具 |
| **替代 Agent** | **TC-AGENT-008** | 測試 gpt4o_agent 是否可以被匯入。 | None | 1. 匯入 `gpt4o_agent` | None | 成功匯入 |
| **替代 Agent** | **TC-AGENT-009** | 測試 gpt4o_agent 是否使用正確的模型。 | None | 1. 檢查 `gpt4o_agent.model` | None | 模型是 `LiteLlm` 的實例 |
| **替代 Agent** | **TC-AGENT-010** | 測試 claude_agent 是否可以被匯入。 | None | 1. 匯入 `claude_agent` | None | 成功匯入 |
| **替代 Agent** | **TC-AGENT-011** | 測試 claude_agent 是否有正確的名稱。 | None | 1. 檢查 `claude_agent.name` | None | 名稱為 `claude_agent` |
| **替代 Agent** | **TC-AGENT-012** | 測試 ollama_agent 是否可以被匯入。 | None | 1. 匯入 `ollama_agent` | None | 成功匯入 |
| **替代 Agent** | **TC-AGENT-013** | 測試 ollama_agent 的描述中是否提及隱私。 | None | 1. 檢查 `ollama_agent.description` | None | 描述包含 `privacy` 和 `local` |
| **替代 Agent** | **TC-AGENT-014** | 測試所有 Agent 是否擁有相同的工具集。 | None | 1. 比較各 Agent 的工具數量 | None | 所有 Agent 的工具數量相同 |
| **工具函式** | **TC-TOOL-001** | 測試 calculate_square 函式搭配基本輸入。 | None | 1. 使用正整數和零呼叫函式 | `5`, `10`, `0` | 回傳 `25`, `100`, `0` |
| **工具函式** | **TC-TOOL-002** | 測試 calculate_square 函式搭配負數輸入。 | None | 1. 使用負整數呼叫函式 | `-5` | 回傳 `25` |
| **工具函式** | **TC-TOOL-003** | 測試 get_weather 是否回傳一個字典。 | None | 1. 呼叫 `get_weather` | `"San Francisco"` | 回傳 `dict` 類型 |
| **工具函式** | **TC-TOOL-004** | 測試 get_weather 的回傳值是否包含必要欄位。 | None | 1. 檢查回傳的 `dict` 鍵 | `"New York"` | 包含 `city`, `temperature`, `condition`, `humidity` |
| **工具函式** | **TC-TOOL-005** | 測試 get_weather 是否保留城市名稱。 | None | 1. 檢查回傳 `dict` 中的 `city` 欄位 | `"London"` | `city` 欄位為 `London` |
| **工具函式** | **TC-TOOL-006** | 測試 analyze_sentiment 是否回傳一個字典。 | None | 1. 呼叫 `analyze_sentiment` | `"This is great!"` | 回傳 `dict` 類型 |
| **工具函式** | **TC-TOOL-007** | 測試 analyze_sentiment 的回傳值是否包含必要欄位。 | None | 1. 檢查回傳的 `dict` 鍵 | `"Amazing product!"` | 包含 `sentiment`, `confidence`, `key_phrases` |
| **工具函式** | **TC-TOOL-008** | 測試信賴度是否為浮點數。 | None | 1. 檢查 `confidence` 欄位的類型和範圍 | `"Wonderful experience"` | `confidence` 是 0 到 1 之間的 `float` |
| **工具函式** | **TC-TOOL-009** | 測試 key_phrases 是否為一個列表。 | None | 1. 檢查 `key_phrases` 欄位的類型 | `"Excellent service"` | `key_phrases` 是 `list` |
| **模型類型** | **TC-MODEL-001** | 測試 root_agent 是否使用 LiteLlm 模型。 | None | 1. 檢查 `root_agent.model` 類型 | None | `root_agent.model` 是 `LiteLlm` 的實例 |
| **模型類型** | **TC-MODEL-002** | 測試所有替代 Agent 是否都使用 LiteLlm 模型。 | None | 1. 檢查各替代 Agent 的模型類型 | None | 所有模型都是 `LiteLlm` 的實例 |
| **整合測試** | **TC-INT-001** | 測試 Agent 是否可以在不引發例外的情況下被建立。 | ADK 環境已設定 | 1. 嘗試建立 `root_agent` | None | 無例外拋出 |
| **整合測試** | **TC-INT-002** | 測試所有 Agent 變體是否都可以被建立。 | ADK 環境已設定 | 1. 嘗試建立所有 Agent | None | 無例外拋出 |
| **整合測試** | **TC-INT-003** | 測試工具是否被正確包裝為 FunctionTools。 | ADK 環境已設定 | 1. 檢查 `root_agent` 中各工具的類型 | None | 所有工具都是 `FunctionTool` 的實例 |
| **整合測試** | **TC-INT-004** | 測試所有工具函式是否都可呼叫。 | None | 1. 檢查各工具函式的可呼叫性 | None | 所有工具函式都是可呼叫的 |

## 匯入模組測試 (`tests/test_imports.py`)

此部分涵蓋對所有必要模組匯入的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPRT-001** | 測試 ADK 核心匯入是否能正常運作。 | None | 1. 匯入 ADK 核心元件 | None | 成功匯入 |
| **匯入測試** | **TC-IMPRT-002** | 測試 LiteLLM 匯入是否能正常運作。 | None | 1. 匯入 `litellm` | None | 成功匯入 |
| **匯入測試** | **TC-IMPRT-003** | 測試 OpenAI 匯入是否能正常運作。 | None | 1. 匯入 `openai` | None | 成功匯入 |
| **匯入測試** | **TC-IMPRT-004** | 測試 Anthropic 匯入是否能正常運作。 | None | 1. 匯入 `anthropic` | None | 成功匯入 |
| **匯入測試** | **TC-IMPRT-005** | 測試 agent 套件是否可以被匯入。 | None | 1. 從 `multi_llm_agent` 匯入 `agent` | None | 成功匯入 |
| **匯入測試** | **TC-IMPRT-006** | 測試 root_agent 是否可以被匯入。 | None | 1. 匯入 `root_agent` | None | 成功匯入 |
| **匯入測試** | **TC-IMPRT-007** | 測試替代 agents 是否可以被匯入。 | None | 1. 匯入 `gpt4o_agent`, `claude_agent`, `ollama_agent` | None | 成功匯入 |
| **匯入測試** | **TC-IMPRT-008** | 測試工具函式是否可以被匯入。 | None | 1. 匯入 `calculate_square`, `get_weather`, `analyze_sentiment` | None | 成功匯入 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案檔案結構與設定的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRC-001** | 測試專案根目錄是否存在。 | None | 1. 檢查專案根目錄路徑 | None | 目錄存在且為資料夾 |
| **專案結構** | **TC-STRC-002** | 測試 agent 套件是否存在。 | None | 1. 檢查 `multi_llm_agent` 套件路徑 | None | 目錄存在且為資料夾 |
| **專案結構** | **TC-STRC-003** | 測試 agent __init__.py 檔案是否存在。 | None | 1. 檢查 `__init__.py` 檔案路徑 | None | 檔案存在 |
| **專案結構** | **TC-STRC-004** | 測試 agent.py 檔案是否存在。 | None | 1. 檢查 `agent.py` 檔案路徑 | None | 檔案存在 |
| **專案結構** | **TC-STRC-005** | 測試 .env.example 檔案是否存在。 | None | 1. 檢查 `.env.example` 檔案路徑 | None | 檔案存在 |
| **專案結構** | **TC-STRC-006** | 測試 requirements.txt 檔案是否存在。 | None | 1. 檢查 `requirements.txt` 檔案路徑 | None | 檔案存在 |
| **專案結構** | **TC-STRC-007** | 測試 pyproject.toml 檔案是否存在。 | None | 1. 檢查 `pyproject.toml` 檔案路徑 | None | 檔案存在 |
| **專案結構** | **TC-STRC-008** | 測試 Makefile 檔案是否存在。 | None | 1. 檢查 `Makefile` 檔案路徑 | None | 檔案存在 |
| **專案結構** | **TC-STRC-009** | 測試 tests 目錄是否存在。 | None | 1. 檢查 `tests` 目錄路徑 | None | 目錄存在且為資料夾 |
| **專案結構** | **TC-STRC-010** | 測試 README.md 檔案是否存在。 | None | 1. 檢查 `README.md` 檔案路徑 | None | 檔案存在 |
| **設定檔** | **TC-CONF-001** | 測試 requirements.txt 檔案是否包含 google-adk。 | None | 1. 讀取 `requirements.txt` 內容 | None | 內容包含 `google-adk` |
| **設定檔** | **TC-CONF-002** | 測試 requirements.txt 檔案是否包含 litellm。 | None | 1. 讀取 `requirements.txt` 內容 | None | 內容包含 `litellm` |
| **設定檔** | **TC-CONF-003** | 測試 requirements.txt 檔案是否包含 openai。 | None | 1. 讀取 `requirements.txt` 內容 | None | 內容包含 `openai` |
| **設定檔** | **TC-CONF-004** | 測試 requirements.txt 檔案是否包含 anthropic。 | None | 1. 讀取 `requirements.txt` 內容 | None | 內容包含 `anthropic` |
| **設定檔** | **TC-CONF-005** | 測試 pyproject.toml 檔案是否擁有正確的套件名稱。 | None | 1. 讀取 `pyproject.toml` 內容 | None | 內容包含 `name = "tutorial28"` |
| **設定檔** | **TC-CONF-006** | 測試 .env.example 檔案是否擁有所有必要的金鑰範本。 | None | 1. 讀取 `.env.example` 內容 | None | 內容包含所有必要的 API 金鑰 |
