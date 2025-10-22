# Software Bug Assistant - pyproject.toml 說明文件

## 專案概述
這是 Google ADK (AI Development Kit) 示例項目中的 Software Bug Assistant 的配置文件。該項目是一個使用 ADK 建構的軟體錯誤助手。

## 專案基本資訊
- **名稱**: software-bug-assistant
- **版本**: 0.1.0
- **描述**: Software bug assistant using ADK
- **作者**: Jack Wotherspoon (jackwoth@google.com)
- **授權**: Apache-2.0
- **Python 版本需求**: >=3.10,<3.13

## 主要依賴套件

### 核心依賴
- `google-adk>=1.8.0` - Google AI Development Kit 核心套件
- `langchain>=0.3.0,<0.4.0` - 語言鏈框架，用於構建 LLM 應用
- `google-cloud-aiplatform[agent-engines,evaluation]>=1.93.0` - Google Cloud AI Platform 套件
- `langchain-community>=0.3.25` - LangChain 社群套件
- `python-dotenv>=1.1.0` - 環境變數管理
- `stackapi>=0.3.1` - Stack Exchange API 客戶端
- `toolbox-core>=0.1.0` - 工具箱核心模組

### 開發依賴 (dev group)
- `pytest>=8.3.5` - 測試框架
- `pytest-asyncio>=0.26.0` - 異步測試支援
- `agent-starter-pack>=0.14.1` - 代理程式開發工具包

### 程式碼品質工具 (lint 可選依賴)
- `ruff>=0.4.6` - 現代 Python linter 和程式碼格式化工具
- `mypy>=1.15.0` - 靜態類型檢查
- `codespell>=2.2.0` - 拼字檢查
- `types-pyyaml>=6.0.12.20240917` - PyYAML 類型定義
- `types-requests>=2.32.0.20240914` - Requests 類型定義

## 工具配置

### Ruff 配置
- 行長度限制：88 字符
- 目標 Python 版本：3.10
- 啟用的規則包括：pycodestyle、pyflakes、isort、flake8-comprehensions 等
- 忽略規則：E501 (行過長)、C901 (過於複雜)

### MyPy 配置
- 嚴格的類型檢查設定
- 禁止未類型化的函數調用和定義
- 啟用各種警告和檢查
- 排除 `.venv` 目錄

### Codespell 配置
- 忽略單詞：rouge
- 跳過檢查的文件/目錄：locust_env、uv.lock、.venv、frontend、*.ipynb

### Pytest 配置
- Python 路徑設為當前目錄
- 異步測試的預設範圍為 function

## 建構系統
- 使用 `uv_build` 作為建構後端
- 模組根目錄為空字符串

## Agent Starter Pack 配置
這個項目使用 Google 的 agent-starter-pack 進行遠程模板化：
- 範例問題：「Can you help me debug a login page issue?」
- 代理程式目錄：software_bug_assistant

## 用途
這個配置文件定義了一個完整的 Python 專案結構，專門用於建構軟體錯誤診斷助手。它整合了 Google 的 AI 開發工具包，並包含了完整的開發工具鏈配置，適合用於開發和部署 AI 驅動的錯誤診斷系統。