# Software Bug Assistant - UV 初始化專案指南

這個指南將逐步引導您使用 `uv` 建立和配置 Software Bug Assistant 專案。

## 前置需求

1. **安裝 uv**

   ```bash
   # macOS 使用 Homebrew
   brew install uv

   # 或使用 curl
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **驗證安裝**
   ```bash
   uv --version
   ```

## 步驟 1: 專案初始化

### 1.1 創建新專案

```bash
# 進入工作目錄
cd /Users/cfh00543956/Desktop/Labs/google-adk-study/workspace/python/agents/software-bug-assistant

# 使用 uv 初始化專案
uv init --name software-bug-assistant
```

**說明**: 這會創建基本的專案結構，包括 `pyproject.toml`、`src/` 目錄和初始的 Python 文件。

### 1.2 設定 Python 版本

```bash
# 設定 Python 版本為 3.11（符合 >=3.10,<3.13 要求）
uv python pin 3.11
```

**說明**: 這會在專案中固定 Python 版本，確保團隊成員使用相同版本。

## 步驟 2: 配置專案元數據

### 2.1 編輯 pyproject.toml

更新專案的基本信息：

```toml
[project]
name = "software-bug-assistant"
version = "0.1.0"
description = "Software bug assistant using ADK"
authors = [{ name = "Your Name", email = "your.email@gmail.com" }]
license = "Apache-2.0"
readme = "README.md"
requires-python = ">=3.10,<3.13"
```

**說明**: 定義專案的基本元數據，包括名稱、版本、描述和 Python 版本需求。

## 步驟 3: 核心依賴安裝

### 3.1 安裝主要依賴

```bash
# Google ADK 核心套件
uv add "google-adk>=1.8.0"

# LangChain 生態系統
uv add "langchain>=0.3.0,<0.4.0"
uv add "langchain-community>=0.3.25"

# Google Cloud AI Platform
uv add "google-cloud-aiplatform[agent-engines,evaluation]>=1.93.0"
```

**說明**:

- `google-adk`: Google Agent Development Kit 核心功能
- `langchain`: 大語言模型應用開發框架
- `google-cloud-aiplatform`: Google Cloud AI 平台整合

### 3.2 安裝工具類依賴

```bash
# 環境變數管理
uv add "python-dotenv>=1.1.0"

# Stack Overflow API
uv add "stackapi>=0.3.1"

# 工具箱核心
uv add "toolbox-core>=0.1.0"
```

**說明**:

- `python-dotenv`: 管理環境變數檔案
- `stackapi`: 與 Stack Overflow API 互動
- `toolbox-core`: 提供核心工具功能

## 步驟 4: 開發依賴安裝

### 4.1 測試框架

```bash
# 創建開發依賴群組
uv add --group dev "pytest>=8.3.5"
uv add --group dev "pytest-asyncio>=0.26.0"
uv add --group dev "agent-starter-pack>=0.14.1"
```

**說明**:

- `pytest`: Python 測試框架
- `pytest-asyncio`: 異步測試支援
- `agent-starter-pack`: Agent 開發入門工具包

### 4.2 代碼品質工具

```bash
# 代碼格式化和檢查
uv add --optional lint "ruff>=0.4.6"
uv add --optional lint "mypy>=1.15.0"
uv add --optional lint "codespell>=2.2.0"
uv add --optional lint "types-pyyaml>=6.0.12.20240917"
uv add --optional lint "types-requests>=2.32.0.20240914"
```

**說明**:

- `ruff`: 快速的 Python linter 和格式化工具
- `mypy`: 靜態類型檢查
- `codespell`: 拼寫檢查工具

## 步驟 5: 專案結構設置

### 5.1 創建基本目錄結構

```bash
# 創建主要模組目錄
mkdir -p software_bug_assistant
mkdir -p tests
mkdir -p deployment
mkdir -p eval

# 創建初始 Python 文件
touch software_bug_assistant/__init__.py
touch software_bug_assistant/main.py
touch tests/__init__.py
touch tests/test_main.py
```

### 5.2 創建配置文件

```bash
# 創建環境變數範例檔案
touch .env.example

# 創建 README 檔案
touch README.md
```

## 步驟 6: 工具配置

### 6.1 配置 Ruff（代碼格式化）

在 `pyproject.toml` 中添加：

```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "I",   # isort
    "C",   # flake8-comprehensions
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
    "RUF", # ruff specific rules
]
ignore = ["E501", "C901"]

[tool.ruff.lint.isort]
known-first-party = ["software_bug_assistant"]
```

### 6.2 配置 MyPy（類型檢查）

```toml
[tool.mypy]
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
check_untyped_defs = true
disallow_subclassing_any = true
warn_incomplete_stub = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_unreachable = true
follow_imports = "silent"
ignore_missing_imports = true
explicit_package_bases = true
disable_error_code = ["misc", "no-untyped-call", "no-any-return"]

exclude = [".venv"]
```

### 6.3 配置 Pytest

```toml
[tool.pytest.ini_options]
pythonpath = "."
asyncio_default_fixture_loop_scope = "function"
```

## 步驟 7: 建構系統配置

### 7.1 設定 UV 建構後端

```toml
[build-system]
requires = ["uv_build>=0.8.14,<0.9.0"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-root = ""
```

### 7.2 Agent Starter Pack 配置

```toml
[tool.agent-starter-pack]
example_question = "Can you help me debug a login page issue?"

[tool.agent-starter-pack.settings]
agent_directory = "software_bug_assistant"
```

## 步驟 8: 驗證安裝

### 8.1 檢查依賴

```bash
# 查看已安裝的套件
uv tree

# 檢查專案狀態
uv sync --check
```

### 8.2 運行測試

```bash
# 安裝開發依賴並運行測試
uv run --group dev pytest

# 運行代碼檢查
uv run --extra lint ruff check .
uv run --extra lint mypy .
```

## 步驟 9: 開發環境準備

### 9.1 啟動虛擬環境

```bash
# UV 會自動管理虛擬環境，直接運行腳本
uv run python software_bug_assistant/main.py
```

### 9.2 添加 Git 忽略文件

創建 `.gitignore`：

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# UV
uv.lock
```

## 常用命令總結

```bash
# 安裝依賴
uv add <package-name>

# 安裝開發依賴
uv add --group dev <package-name>

# 運行腳本
uv run python <script.py>

# 運行測試
uv run --group dev pytest

# 更新依賴
uv lock --upgrade

# 同步依賴
uv sync

# 建構專案
uv build
```

## 下一步

1. 開始開發您的 Agent 邏輯
2. 編寫測試案例
3. 配置部署環境
4. 設定 CI/CD 流程

這個指南提供了完整的專案初始化流程，您可以根據具體需求調整配置。
