# Poetry 完整使用指南

## 目錄
- [什麼是 Poetry](#什麼是-poetry)
- [安裝 Poetry](#安裝-poetry)
- [建立新專案](#建立新專案)
- [依賴管理](#依賴管理)
- [虛擬環境](#虛擬環境)
- [執行指令](#執行指令)
- [配置設定](#配置設定)
- [發佈套件](#發佈套件)
- [常見問題](#常見問題)

## 什麼是 Poetry

Poetry 是一個現代化的 Python 依賴管理和打包工具，提供以下功能：

- **依賴解析**：自動解決套件之間的依賴衝突
- **虛擬環境管理**：自動建立和管理虛擬環境
- **套件發佈**：簡化 PyPI 發佈流程
- **確定性建構**：透過 `poetry.lock` 確保可重現的建構

## 安裝 Poetry

### macOS / Linux / WSL
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows (PowerShell)
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 使用 Homebrew (macOS)
```bash
brew install poetry
```

### 驗證安裝
```bash
poetry --version
```

### 更新 Poetry
```bash
poetry self update
```

## 建立新專案

### 建立全新專案
```bash
poetry new my-project
```

這會建立以下結構：
```
my-project/
├── pyproject.toml
├── README.md
├── my_project/
│   └── __init__.py
└── tests/
    └── __init__.py
```

### 在現有專案中初始化
```bash
cd existing-project
poetry init
```

這會互動式地引導你建立 `pyproject.toml`。

## 依賴管理

### 安裝所有依賴
```bash
# 安裝 pyproject.toml 中定義的所有依賴
poetry install

# 不安裝開發依賴
poetry install --only main

# 只安裝開發依賴
poetry install --only dev
```

### 新增套件
```bash
# 新增正式依賴
poetry add requests
poetry add "django>=4.0,<5.0"

# 新增開發依賴
poetry add --group dev pytest
poetry add --group dev black flake8

# 新增可選依賴
poetry add --optional redis
```

### 移除套件
```bash
poetry remove requests
poetry remove --group dev pytest
```

### 更新套件
```bash
# 更新所有套件
poetry update

# 更新特定套件
poetry update requests

# 顯示可更新的套件
poetry show --outdated
```

### 查看已安裝的套件
```bash
# 列出所有套件
poetry show

# 顯示套件樹狀結構
poetry show --tree

# 查看特定套件資訊
poetry show requests
```

## 虛擬環境

### 啟動虛擬環境
```bash
poetry shell
```

### 退出虛擬環境
```bash
exit
```

### 查看虛擬環境資訊
```bash
# 顯示虛擬環境路徑
poetry env info

# 列出所有虛擬環境
poetry env list
```

### 移除虛擬環境
```bash
poetry env remove python3.11
```

### 使用特定 Python 版本
```bash
poetry env use python3.11
poetry env use /usr/local/bin/python3.9
```

## 執行指令

### 在虛擬環境中執行指令
```bash
# 執行 Python 腳本
poetry run python script.py

# 執行測試
poetry run pytest

# 執行格式化工具
poetry run black .

# 執行任何指令
poetry run <command>
```

### 定義腳本快捷方式

在 `pyproject.toml` 中定義：
```toml
[tool.poetry.scripts]
start = "my_project.main:main"
test = "pytest"
```

執行：
```bash
poetry run start
poetry run test
```

## 配置設定

### pyproject.toml 結構

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "專案描述"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
license = "MIT"

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.28.0"
django = ">=4.0,<5.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
flake8 = "^6.0.0"

[tool.poetry.group.test.dependencies]
pytest-cov = "^4.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 版本約束符號

- `^`：兼容版本更新
  - `^1.2.3` → `>=1.2.3 <2.0.0`
  - `^0.2.3` → `>=0.2.3 <0.3.0`

- `~`：小版本更新
  - `~1.2.3` → `>=1.2.3 <1.3.0`

- `*`：任何版本
  - `1.*` → `>=1.0.0 <2.0.0`

- 精確版本：`==1.2.3`
- 範圍：`>=1.2,<2.0`

### Poetry 配置

```bash
# 列出所有配置
poetry config --list

# 在專案目錄建立虛擬環境
poetry config virtualenvs.in-project true

# 設定 PyPI 認證
poetry config pypi-token.pypi <token>

# 新增私有倉庫
poetry config repositories.private https://private.repo.com
```

## 發佈套件

### 建構套件
```bash
# 建構 wheel 和 sdist
poetry build
```

### 發佈到 PyPI
```bash
# 發佈到 PyPI（需先設定認證）
poetry publish

# 建構並發佈
poetry publish --build

# 發佈到測試 PyPI
poetry publish -r testpypi
```

### 設定 PyPI Token
```bash
poetry config pypi-token.pypi <your-token>
```

## 常見問題

### 匯出 requirements.txt
```bash
# 匯出所有依賴
poetry export -f requirements.txt --output requirements.txt

# 不包含雜湊值
poetry export -f requirements.txt --output requirements.txt --without-hashes

# 只匯出開發依賴
poetry export -f requirements.txt --output requirements-dev.txt --only dev
```

### 鎖定依賴版本
```bash
# 更新 poetry.lock 但不安裝
poetry lock

# 不更新已鎖定的依賴
poetry lock --no-update
```

### 檢查依賴
```bash
# 檢查 pyproject.toml 的有效性
poetry check

# 檢查過期的依賴
poetry show --outdated

# 檢查依賴樹
poetry show --tree
```

### 清除快取
```bash
poetry cache clear pypi --all
```

### 從 requirements.txt 遷移

如果你有現有的 `requirements.txt`：

```bash
# 初始化 Poetry
poetry init

# 逐一新增套件（需手動處理）
cat requirements.txt | grep -v "^#" | xargs -n 1 poetry add
```

或使用工具：
```bash
# 使用 poetry add 配合檔案內容
poetry add $(<requirements.txt)
```

### 多環境管理

```toml
[tool.poetry.group.dev]
optional = false

[tool.poetry.group.test]
optional = true

[tool.poetry.group.docs]
optional = true
```

安裝特定群組：
```bash
poetry install --with test,docs
poetry install --without dev
```

### 使用 Poetry 與 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝 Poetry
RUN pip install poetry

# 複製依賴定義
COPY pyproject.toml poetry.lock ./

# 配置 Poetry 不建立虛擬環境（Docker 已隔離）
RUN poetry config virtualenvs.create false

# 安裝依賴
RUN poetry install --no-dev --no-interaction --no-ansi

# 複製應用程式碼
COPY . .

CMD ["poetry", "run", "python", "main.py"]
```

### 疑難排解

#### 依賴衝突
```bash
# 顯示詳細錯誤訊息
poetry add package-name -vvv

# 清除快取重試
poetry cache clear pypi --all
poetry install
```

#### 虛擬環境問題
```bash
# 移除並重建虛擬環境
poetry env remove python
poetry install
```

#### 鎖定檔案過期
```bash
# 重新生成鎖定檔案
poetry lock --no-update
```

## 最佳實踐

1. **提交 poetry.lock**：確保團隊使用相同的依賴版本
2. **使用依賴群組**：區分開發、測試、文件等不同用途的依賴
3. **定期更新依賴**：定期執行 `poetry update` 並測試
4. **使用版本約束**：合理使用 `^` 和 `~` 符號
5. **CI/CD 整合**：使用 `poetry install --no-root` 加速 CI 建構

## 參考資源

- [Poetry 官方文件](https://python-poetry.org/docs/)
- [pyproject.toml 規範](https://peps.python.org/pep-0518/)
- [語義化版本](https://semver.org/lang/zh-TW/)

---

最後更新：2026年1月1日
