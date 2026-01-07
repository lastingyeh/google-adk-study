# PyProject.toml 初學者完整教學指南

## 📚 目錄

- [什麼是 pyproject.toml？](#什麼是-pyprojecttoml)
- [為什麼需要 pyproject.toml？](#為什麼需要-pyprojecttoml)
- [檔案結構總覽](#檔案結構總覽)
- [逐節詳細說明](#逐節詳細說明)
  - [1. 建置系統設定](#1-建置系統設定-build-system)
  - [2. 專案設定](#2-專案設定-project)
  - [3. 依賴套件管理](#3-依賴套件管理)
  - [4. Setuptools 設定](#4-setuptools-設定)
  - [5. 測試設定](#5-測試設定-pytest)
  - [6. 型別檢查設定](#6-型別檢查設定-toolmypy)
  - [7. 程式碼格式設定](#7-程式碼格式設定-pyink)
  - [8. 自訂工具設定](#8-自訂工具設定)
- [實用指令](#實用指令)
- [常見問題](#常見問題)
- [最佳實踐](#最佳實踐)

---

## 什麼是 pyproject.toml？

`pyproject.toml` 是 Python 專案的現代化配置檔案，使用 TOML（Tom's Obvious, Minimal Language）格式撰寫。它是 Python 專案的「身分證」和「說明書」，定義了專案的所有重要資訊。

### TOML 格式基礎

TOML 是一種易讀的配置格式：

```toml
# 這是註解
key = "value"                    # 字串
number = 42                      # 數字
flag = true                      # 布林值
list = ["item1", "item2"]        # 陣列
[section]                        # 區段
nested_key = "nested_value"
```

---

## 為什麼需要 pyproject.toml？

### 傳統做法的問題

過去 Python 專案需要多個配置檔案：

- `setup.py` - 套件安裝
- `requirements.txt` - 依賴管理
- `MANIFEST.in` - 打包規則
- `setup.cfg` - 額外設定
- `.pytest.ini` - 測試設定
- 各種工具的配置檔案

### 現代做法的優勢

使用 `pyproject.toml` 可以：
✅ **統一配置** - 所有設定集中在一個檔案
✅ **標準化** - 遵循 PEP 518、PEP 621 等 Python 標準
✅ **易讀易維護** - TOML 格式清晰明瞭
✅ **工具整合** - 大多數現代工具都支援

---

## 檔案結構總覽

```
pyproject.toml
├── [build-system]                 建置系統
├── [project]                      專案基本資訊
├── [project.optional-dependencies] 可選依賴
├── [dependency-groups]            依賴分組
├── [tool.setuptools]              打包工具設定
├── [tool.pytest.ini_options]      測試設定
├── [tool.mypy]                    型別檢查設定
├── [tool.pyink]                   程式碼格式設定
└── [tool.agent-starter-pack]      自訂工具設定
```

---

## 逐節詳細說明

### 1. 建置系統設定 [build-system]

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
```

#### 📖 說明

這個區段告訴 Python 如何建置（build）你的專案。

#### 🔑 關鍵概念

**`requires`** - 建置依賴

- 指定建置專案所需的工具和版本
- `setuptools>=45`: 使用 setuptools 版本 45 或更高
- `wheel`: 用於創建 wheel 格式的套件（.whl 檔案）

**`build-backend`** - 建置後端

- 指定使用哪個工具來執行建置
- `setuptools.build_meta`: 使用 setuptools 的現代建置 API

#### 💡 為什麼重要？

沒有這個設定，當你執行：

```bash
pip install -e .        # 可編輯模式安裝
pip install .           # 正常安裝
python -m build         # 建置套件
```

Python 將不知道該使用什麼工具來安裝你的專案。

#### 🎯 其他選擇

```toml
# 使用 Poetry
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# 使用 Hatchling
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

### 2. 專案設定 [project]

```toml
[project]
name = "pack-policy-as-code"
version = "0.0.1"
description = "[agent-starter-pack] - 實作 (更新) Policy as Code Agent 範例"
authors = [{ name = "Lastingyeh", email = "lastingyeh@gmail.com" }]
readme = "README.md"
requires-python = ">=3.11"
```

#### 📖 說明

定義專案的基本元資料（metadata）。

#### 🔑 各欄位解釋

**`name`** - 專案名稱

- 套件在 PyPI 上的唯一識別名稱
- 使用小寫字母和連字號
- 範例：`pack-policy-as-code`

**`version`** - 版本號

- 遵循語義化版本（Semantic Versioning）
- 格式：`主版本.次版本.修訂號`
  - `0.0.1` - 初始開發版本
  - `1.0.0` - 第一個穩定版本
  - `1.1.0` - 新增功能但向後相容
  - `2.0.0` - 有重大變更，不向後相容

**`description`** - 簡短描述

- 一行簡短說明專案用途
- 會顯示在 PyPI 套件列表中

**`authors`** - 作者資訊

- 陣列格式，可以有多個作者
- 每個作者包含 `name` 和 `email`

```toml
authors = [
    { name = "張三", email = "zhang@example.com" },
    { name = "李四", email = "li@example.com" }
]
```

**`readme`** - 說明文件

- 指向專案的 README 檔案
- 內容會顯示在 PyPI 專案頁面

**`requires-python`** - Python 版本需求

- `>=3.11` 表示需要 Python 3.11 或更高版本
- 其他寫法：
  - `>=3.8,<4.0` - Python 3.8 到 4.0 之間
  - `==3.11.*` - 只能用 Python 3.11 系列

#### 🎯 更多可選欄位

```toml
[project]
# ... 基本欄位 ...
license = {text = "MIT"}
keywords = ["ai", "agent", "policy"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
]

[project.urls]
Homepage = "https://github.com/username/project"
Documentation = "https://docs.example.com"
Repository = "https://github.com/username/project.git"
Issues = "https://github.com/username/project/issues"
```

---

### 3. 依賴套件管理

#### 3.1 核心依賴 dependencies

```toml
dependencies = [
    "PyYAML==6.0.3",
    "google-adk[eval]==1.21.0",
    "google-cloud-storage==2.19.0",
    # ... 更多套件
]
```

#### 📖 說明

列出專案**執行時必需**的套件。

#### 🔑 版本指定語法

**固定版本** `==`

```toml
"PyYAML==6.0.3"           # 只能用 6.0.3
```

✅ 優點：完全可重現的環境
❌ 缺點：無法獲得安全性更新

**最低版本** `>=`

```toml
"PyYAML>=6.0.3"           # 6.0.3 或更高
```

✅ 優點：可獲得更新
❌ 缺點：可能遇到不相容變更

**範圍限制** `>=,<`

```toml
"PyYAML>=6.0,<7.0"        # 6.x 系列
```

✅ 優點：平衡穩定性和更新

**相容版本** `~=`

```toml
"PyYAML~=6.0.3"           # 等同於 >=6.0.3,<6.1.0
```

**額外功能** `[extra]`

```toml
"google-adk[eval]==1.21.0"  # 安裝 google-adk 和 eval 額外功能
```

#### 💡 各套件用途說明

| 套件                       | 用途                           |
| -------------------------- | ------------------------------ |
| `PyYAML`                   | 讀寫 YAML 格式檔案             |
| `google-adk[eval]`         | Google ADK 框架（含評估功能）  |
| `google-cloud-storage`     | Google Cloud Storage 操作      |
| `vertexai`                 | Google Vertex AI 服務          |
| `google-cloud-dataplex`    | Google Cloud Dataplex 資料治理 |
| `google-cloud-aiplatform`  | Google Cloud AI Platform       |
| `google-api-python-client` | Google API 通用客戶端          |
| `google-cloud-firestore`   | Google Cloud Firestore 資料庫  |

#### 3.2 開發依賴 [dependency-groups]

```toml
[dependency-groups]
dev = [
    "pytest==8.4.2",
    "pytest-xdist==3.8.0",
    "pytest-asyncio==1.3.0",
]
```

#### 📖 說明

只在**開發過程**需要的套件，發佈後的使用者不需要安裝。

#### 🔑 依賴分組概念

**為什麼要分組？**

- 使用者只需要核心功能
- 開發者需要測試、格式化等工具
- 分組可以選擇性安裝

**安裝方式：**

```bash
# 安裝核心依賴
pip install .

# 安裝核心 + 開發依賴
pip install -e .[dev]

# 使用 uv（現代套件管理工具）
uv sync              # 只安裝核心依賴
uv sync --dev        # 安裝核心 + 開發依賴
```

#### 💡 測試套件說明

| 套件             | 用途                         |
| ---------------- | ---------------------------- |
| `pytest`         | Python 測試框架              |
| `pytest-xdist`   | 平行執行測試（加快測試速度） |
| `pytest-asyncio` | 支援非同步測試               |

#### 🎯 其他常見開發依賴分組

```toml
[dependency-groups]
dev = ["pytest", "black", "ruff"]
docs = ["sphinx", "sphinx-rtd-theme"]
test = ["pytest", "pytest-cov", "pytest-mock"]
lint = ["ruff", "mypy", "black"]
```

---

### 4. Setuptools 設定

#### 4.1 基本設定 [tool.setuptools]

```toml
[tool.setuptools]
include-package-data = true
```

#### 📖 說明

**`include-package-data`** - 是否包含非 Python 檔案

- `true`: 包含 MANIFEST.in 指定的檔案
- 常見用途：包含資料檔、模板、配置檔等

#### 4.2 套件發現 [tool.setuptools.packages.find]

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["policy_as_code_agent*"]
exclude = ["tests*", "docs*", "deployment*", "notebooks*"]
```

#### 📖 說明

告訴 setuptools 哪些目錄要打包成套件。

#### 🔑 各參數說明

**`where`** - 搜尋起點

- `["."]`: 從專案根目錄開始尋找
- 可以指定多個目錄：`["src", "lib"]`

**`include`** - 包含規則

- `["policy_as_code_agent*"]`: 包含所有以 `policy_as_code_agent` 開頭的套件
- 萬用字元 `*` 表示匹配任意字元

**`exclude`** - 排除規則

- 不想打包的目錄
- `tests*`: 測試檔案（使用者不需要）
- `docs*`: 文件原始碼（使用者看發佈的文件）
- `deployment*`: 部署腳本
- `notebooks*`: Jupyter 筆記本

#### 💡 實際效果

專案結構：

```
project/
├── policy_as_code_agent/     ✅ 會被包含
│   ├── __init__.py
│   ├── agent.py
│   └── utils/                ✅ 會被包含（符合 policy_as_code_agent*）
├── tests/                    ❌ 被排除
├── docs/                     ❌ 被排除
├── deployment/               ❌ 被排除
└── notebooks/                ❌ 被排除
```

#### 🎯 其他配置範例

**方案一：使用 src 佈局**

```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["mypackage*"]
```

**方案二：明確列出套件**

```toml
[tool.setuptools]
packages = ["mypackage", "mypackage.submodule"]
```

---

### 5. 測試設定 [pytest]

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "asyncio: mark a test as asyncio.",
]
```

#### 📖 說明

配置 pytest 測試框架的行為。

#### 🔑 各參數說明

**`testpaths`** - 測試目錄

- 告訴 pytest 在哪裡尋找測試
- `["tests"]`: 在 `tests/` 目錄下尋找
- 執行 `pytest` 時會自動搜尋這些目錄

**`markers`** - 自訂標記

- 用來分類和選擇性執行測試
- `asyncio`: 標記非同步測試

#### 💡 使用範例

在測試檔案中：

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

執行測試：

```bash
pytest                          # 執行所有測試
pytest tests/unit               # 只執行 unit 測試
pytest -m asyncio               # 只執行有 asyncio 標記的測試
pytest -k "test_agent"          # 只執行名稱包含 "test_agent" 的測試
pytest -v                       # 詳細輸出
pytest --maxfail=1              # 遇到第一個失敗就停止
```

#### 🎯 更多常用設定

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]      # 測試檔案命名模式
python_classes = ["Test*"]                      # 測試類別命名
python_functions = ["test_*"]                   # 測試函式命名
addopts = [
    "-v",                                       # 詳細輸出
    "--strict-markers",                         # 嚴格標記檢查
    "--cov=policy_as_code_agent",              # 程式碼覆蓋率
    "--cov-report=html",                        # 產生 HTML 報告
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

---

### 6. 型別檢查設定 [tool.mypy]

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = false
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = false
allow_untyped_globals = true
allow_redefinition = true
show_error_codes = true

[[tool.mypy.overrides]]
module = ["google.cloud", "google.cloud.*"]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = ["locust", "locust.*"]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
warn_return_any = false
check_untyped_defs = false
```

#### 📖 說明

mypy 是 Python 的靜態型別檢查工具，可以在執行前發現型別相關的錯誤。

#### 🔑 基本設定說明

**`python_version`** - 目標 Python 版本

- `"3.11"`: 針對 Python 3.11 進行型別檢查
- 確保型別檢查符合特定 Python 版本的語法

**`warn_return_any`** - 回傳 Any 型別警告

- `false`: 不對回傳 `Any` 型別發出警告
- 適用於與動態型別程式碼整合的情況

**`warn_unused_configs`** - 未使用設定警告

- `true`: 當 mypy 設定未被使用時發出警告
- 幫助保持設定檔的乾淨

**`disallow_untyped_defs`** - 禁止未標註型別的函式

- `false`: 允許沒有型別註解的函式定義
- 適合逐步引入型別檢查的專案

**`ignore_missing_imports`** - 忽略缺少型別的匯入

- `false`: 不自動忽略缺少型別的匯入
- 需要明確處理第三方套件的型別問題

**`allow_untyped_globals`** - 允許未標註型別的全域變數

- `true`: 允許全域變數沒有型別註解
- 減少遷移到型別檢查的負擔

**`allow_redefinition`** - 允許變數重新定義

- `true`: 允許在不同分支中重新定義變數
- 提高程式碼彈性

**`show_error_codes`** - 顯示錯誤代碼

- `true`: 在錯誤訊息中顯示錯誤代碼（如 `[arg-type]`）
- 方便查詢錯誤文件和設定忽略規則

#### 🔑 模組覆寫設定 [[tool.mypy.overrides]]

**為什麼需要覆寫設定？**
某些第三方套件可能：

- 沒有提供型別 stub（型別定義檔）
- 型別定義不完整或不正確
- 測試程式碼需要更寬鬆的規則

**覆寫一：Google Cloud 相關模組**

```toml
[[tool.mypy.overrides]]
module = ["google.cloud", "google.cloud.*"]
ignore_missing_imports = true
```

- `google.cloud.*`: 匹配所有 google.cloud 子模組
- `ignore_missing_imports = true`: 忽略這些模組的型別匯入錯誤
- 原因：某些 Google Cloud 套件可能沒有完整的型別定義

**覆寫二：Locust 負載測試框架**

```toml
[[tool.mypy.overrides]]
module = ["locust", "locust.*"]
ignore_missing_imports = true
```

- 處理 locust 負載測試工具的型別問題

**覆寫三：測試程式碼**

```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
warn_return_any = false
check_untyped_defs = false
```

- 對測試程式碼採用更寬鬆的規則
- 允許測試中使用未標註型別的函式
- 提高測試撰寫的靈活性

#### 💡 使用方式

```bash
# 安裝 mypy
pip install mypy
# 或從可選依賴安裝
pip install -e .[lint]

# 檢查整個專案
mypy .

# 檢查特定目錄
mypy policy_as_code_agent/

# 檢查特定檔案
mypy policy_as_code_agent/agent.py

# 顯示更詳細的資訊
mypy --verbose .

# 只顯示錯誤，不顯示警告
mypy --no-warn-return-any .
```

#### 🎯 型別註解範例

**基本型別註解：**

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

from typing import List, Dict, Optional

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

def find_user(user_id: int) -> Optional[str]:
    # 可能回傳 str 或 None
    return users.get(user_id)
```

**進階型別註解：**

```python
from typing import Union, Callable, TypeVar

# 聯合型別
def process(value: Union[int, str]) -> str:
    return str(value)

# 函式型別
def apply_func(func: Callable[[int], int], value: int) -> int:
    return func(value)

# 泛型
T = TypeVar('T')
def first_item(items: List[T]) -> Optional[T]:
    return items[0] if items else None
```

#### 🎯 常見錯誤與解決方法

**錯誤 1：找不到型別 stub**

```
error: Cannot find implementation or library stub for module named "requests"
```

解決方法：

```bash
pip install types-requests
```

或在 pyproject.toml 中忽略：

```toml
[[tool.mypy.overrides]]
module = "requests"
ignore_missing_imports = true
```

**錯誤 2：函式缺少回傳型別**

```
error: Function is missing a return type annotation
```

解決方法：

```python
# 之前
def my_function():
    return 42

# 之後
def my_function() -> int:
    return 42
```

**錯誤 3：參數缺少型別**

```
error: Function is missing a type annotation for one or more arguments
```

解決方法：

```python
# 之前
def greet(name):
    return f"Hello, {name}"

# 之後
def greet(name: str) -> str:
    return f"Hello, {name}"
```

#### 🎯 更嚴格的設定範例

如果想要更嚴格的型別檢查：

```toml
[tool.mypy]
python_version = "3.11"
# 嚴格模式
strict = true
# 或手動設定各項嚴格規則
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
no_implicit_optional = true
strict_equality = true
warn_redundant_casts = true
warn_unused_ignores = true
```

#### 💡 最佳實踐

1. **逐步引入型別檢查**

   - 從重要模組開始
   - 新程式碼要求型別註解
   - 舊程式碼逐步加入

2. **為第三方套件安裝型別 stub**

   ```bash
   pip install types-requests types-PyYAML
   ```

3. **使用 `# type: ignore` 註解臨時忽略錯誤**

   ```python
   result = complex_function()  # type: ignore[return-value]
   ```

4. **在 CI 中執行 mypy**
   ```yaml
   # .github/workflows/ci.yml
   - name: Type check with mypy
     run: mypy .
   ```

---

### 7. 程式碼格式設定 [pyink]

```toml
[tool.pyink]
line-length = 80
pyink-indentation = 4
pyink-use-majority-quotes = true
```

#### 📖 說明

pyink 是 Google 風格的 Python 程式碼格式化工具（基於 Black）。

#### 🔑 各參數說明

**`line-length`** - 每行最大長度

- `80`: 每行最多 80 個字元
- 傳統標準，易於在小螢幕閱讀
- 現代標準常用 88、100 或 120

**`pyink-indentation`** - 縮排空格數

- `4`: 使用 4 個空格縮排
- Python 官方 PEP 8 建議

**`pyink-use-majority-quotes`** - 引號風格

- `true`: 自動統一使用專案中最常見的引號風格
- 讓程式碼風格一致

#### 💡 使用方式

安裝：

```bash
pip install pyink
```

格式化程式碼：

```bash
pyink .                         # 格式化所有檔案
pyink path/to/file.py           # 格式化特定檔案
pyink --check .                 # 檢查但不修改
pyink --diff .                  # 顯示會做的修改
```

#### 🎯 其他格式化工具

**Black（最流行）**

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

**Ruff（最快速）**

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]        # 選擇規則
ignore = ["E501"]               # 忽略規則
```

---

### 8. 自訂工具設定

```toml
[tool.agent-starter-pack]
example_question = "所有表格必須有一個 DATA_OWNER 標籤。"

[tool.agent-starter-pack.settings]
agent_directory = "policy_as_code_agent"
```

#### 📖 說明

可以在 `pyproject.toml` 中為自己的工具或應用程式添加配置。

#### 🔑 使用情境

1. **應用程式設定**

   - 儲存應用程式特定的配置
   - 避免創建額外的配置檔案

2. **工具整合**
   - 自訂工具可以讀取這些設定
   - 保持所有配置集中管理

#### 💡 如何在程式中讀取

```python
import tomli  # Python < 3.11
# import tomllib  # Python >= 3.11

def load_config():
    with open("pyproject.toml", "rb") as f:
        data = tomli.load(f)

    agent_config = data["tool"]["agent-starter-pack"]
    example = agent_config["example_question"]
    agent_dir = agent_config["settings"]["agent_directory"]

    return example, agent_dir
```

#### 🎯 常見自訂設定範例

```toml
# 應用程式配置
[tool.myapp]
debug = true
database_url = "postgresql://localhost/mydb"

# CI/CD 設定
[tool.ci]
test_environments = ["py311", "py312"]
coverage_threshold = 80

# 文件生成
[tool.sphinx]
source_dir = "docs/source"
build_dir = "docs/build"
```

---

## 實用指令

### 專案安裝與管理

```bash
# 安裝專案（可編輯模式）
pip install -e .
# 或使用 uv（更快）
uv pip install -e .

# 安裝包含開發依賴
pip install -e .[dev]
uv sync --dev

# 只安裝依賴（不安裝專案本身）
pip install -r <(grep -v "^#" pyproject.toml)
```

### 測試相關

```bash
# 執行所有測試
pytest

# 執行單元測試
pytest tests/unit

# 執行整合測試
pytest tests/integration

# 產生覆蓋率報告
pytest --cov=policy_as_code_agent --cov-report=html

# 平行執行測試（需要 pytest-xdist）
pytest -n auto
```

### 程式碼品質

```bash
# 格式化程式碼
pyink .
# 或使用 black
black .

# 檢查程式碼風格
ruff check .

# 拼字檢查
codespell .

# 型別檢查
mypy .
mypy policy_as_code_agent/  # 只檢查特定目錄
mypy --strict .             # 使用嚴格模式
```

### 套件建置與發佈

```bash
# 建置套件
python -m build

# 檢查建置的套件
twine check dist/*

# 上傳到 PyPI（需要先註冊帳號）
twine upload dist/*

# 上傳到 TestPyPI（測試用）
twine upload --repository testpypi dist/*
```

### 依賴管理

```bash
# 查看已安裝的套件
pip list
uv pip list

# 查看過時的套件
pip list --outdated
uv pip list --outdated

# 產生 requirements.txt
pip freeze > requirements.txt

# 更新特定套件
pip install --upgrade package-name
uv pip install --upgrade package-name
```

---

## 常見問題

### Q1: pyproject.toml vs requirements.txt 哪個比較好？

**A:**

- `pyproject.toml` 用於**定義專案**（包含依賴）
- `requirements.txt` 用於**鎖定環境**（固定版本）

最佳實踐：

```toml
# pyproject.toml - 宣告性，指定範圍
dependencies = [
    "requests>=2.28.0,<3.0.0",
]
```

```txt
# requirements.txt - 命令式，鎖定版本
requests==2.31.0
certifi==2023.7.22
charset-normalizer==3.3.0
```

### Q2: 如何處理版本衝突？

**A:** 使用虛擬環境和依賴解析工具：

```bash
# 創建虛擬環境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 使用 pip-tools
pip install pip-tools
pip-compile pyproject.toml
pip-sync

# 或使用 uv（更快）
uv pip compile pyproject.toml -o requirements.txt
uv pip sync requirements.txt
```

### Q3: 如何指定 Python 版本？

**A:**

```toml
[project]
requires-python = ">=3.11"  # 最低版本
# 或
requires-python = ">=3.11,<4.0"  # 範圍
# 或
requires-python = "==3.11.*"  # 固定主次版本
```

### Q4: 開發依賴要放在哪裡？

**A:**

```toml
# 推薦：使用 dependency-groups（PEP 735，最新標準）
[dependency-groups]
dev = ["pytest", "black"]

# 或：使用 optional-dependencies（舊標準但廣泛支援）
[project.optional-dependencies]
dev = ["pytest", "black"]
```

安裝方式：

```bash
pip install -e .[dev]      # optional-dependencies
uv sync --dev              # dependency-groups
```

### Q5: 如何組織大型專案的依賴？

**A:** 使用多個依賴組：

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=2.0",
]
lint = [
    "ruff>=0.1.0",
    "mypy>=1.7",
]
all = [
    {include-group = "dev"},
    {include-group = "docs"},
    {include-group = "lint"},
]
```

安裝：

```bash
uv sync --group dev        # 只安裝開發工具
uv sync --group docs       # 只安裝文件工具
uv sync --all-groups       # 安裝所有組
```

### Q6: 如何處理私有套件？

**A:**

```toml
dependencies = [
    "my-private-package @ git+https://github.com/user/repo.git@main",
    # 或
    "my-private-package @ https://example.com/packages/my-package-1.0.0.tar.gz",
]
```

### Q7: 建置失敗怎麼辦？

**A:** 檢查清單：

1. **確認 build-system 正確**

   ```toml
   [build-system]
   requires = ["setuptools>=45", "wheel"]
   build-backend = "setuptools.build_meta"
   ```

2. **確認套件可以被找到**

   ```toml
   [tool.setuptools.packages.find]
   where = ["."]
   include = ["your_package*"]
   ```

3. **確認有 **init**.py**

   ```
   your_package/
   ├── __init__.py  ← 必須存在
   └── module.py
   ```

4. **清理舊的建置產物**
   ```bash
   rm -rf build/ dist/ *.egg-info/
   pip install -e . --force-reinstall
   ```

---

## 最佳實踐

### 1. 版本管理策略

```toml
# ❌ 避免：完全固定版本（除非有特殊原因）
dependencies = [
    "requests==2.31.0",
]

# ✅ 推薦：指定相容範圍
dependencies = [
    "requests>=2.28.0,<3.0.0",  # 允許 2.x 更新
]

# ✅ 推薦：使用相容版本運算符
dependencies = [
    "requests~=2.31.0",  # 等同於 >=2.31.0,<2.32.0
]
```

### 2. 專案結構

```
my-project/
├── pyproject.toml          ← 專案配置
├── README.md               ← 專案說明
├── LICENSE                 ← 授權條款
├── .gitignore              ← Git 忽略檔案
├── src/                    ← 或直接放套件目錄
│   └── my_package/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/                  ← 測試目錄
│   ├── __init__.py
│   ├── test_module1.py
│   └── test_module2.py
└── docs/                   ← 文件目錄
    └── index.md
```

### 3. 配置檔案組織

```toml
# 推薦順序
[build-system]                  # 1. 建置系統
[project]                       # 2. 專案資訊
[project.optional-dependencies] # 3. 可選依賴
[dependency-groups]             # 4. 依賴分組
[tool.setuptools]               # 5. 打包設定
[tool.pytest.ini_options]       # 6. 測試設定
[tool.mypy]                     # 7. 型別檢查
[tool.black]                    # 8. 格式化設定
[tool.ruff]                     # 9. Linter 設定
[tool.coverage]                 # 10. 覆蓋率設定
```

### 4. 語義化版本規範

```toml
# 版本格式：主版本.次版本.修訂號
version = "1.2.3"

# 主版本（Major）：不向後相容的變更
# 次版本（Minor）：向後相容的新功能
# 修訂號（Patch）：向後相容的錯誤修復
```

版本更新時機：

- `0.0.1` → `0.0.2` : 修復 bug
- `0.0.2` → `0.1.0` : 新增功能
- `0.1.0` → `1.0.0` : 第一個穩定版本
- `1.0.0` → `2.0.0` : 重大變更（破壞性更新）

### 5. 文件化最佳實踐

在 `pyproject.toml` 中添加詳細註解：

```toml
[project]
name = "my-package"
version = "1.0.0"  # 更新於 2026-01-07：新增 XYZ 功能

dependencies = [
    # 核心功能依賴
    "requests>=2.28.0",      # HTTP 請求
    "pydantic>=2.0.0",       # 資料驗證

    # Google Cloud 相關
    "google-cloud-storage>=2.10.0",  # GCS 操作
]
```

### 6. 持續整合（CI）配置

```toml
# 建議在 CI 中使用的命令
[tool.pytest.ini_options]
addopts = [
    "-v",                    # 詳細輸出
    "--strict-markers",      # 嚴格標記
    "--tb=short",            # 簡短回溯
    "--cov=src",             # 覆蓋率
    "--cov-report=xml",      # XML 報告（給 CI 用）
    "--cov-report=term",     # 終端報告
]
```

### 7. 安全性考量

```toml
# ✅ 好：指定最低安全版本
dependencies = [
    "requests>=2.31.0",  # 2.31.0 修復了重要安全問題
]

# ❌ 避免：使用有已知漏洞的舊版本
dependencies = [
    "requests==2.20.0",  # 已知有安全漏洞
]
```

定期檢查安全性：

```bash
# 使用 pip-audit 檢查漏洞
pip install pip-audit
pip-audit

# 或使用 safety
pip install safety
safety check
```

### 8. 效能優化

使用現代工具加速安裝：

```bash
# 傳統方式（較慢）
pip install -e .

# 使用 uv（快 10-100 倍）
uv pip install -e .

# 使用 uv sync（推薦）
uv sync --dev
```

### 9. 開發工作流程

```bash
# 1. 創建專案
mkdir my-project && cd my-project
git init

# 2. 創建 pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]
EOF

# 3. 創建套件結構
mkdir -p src/my_project tests
touch src/my_project/__init__.py
touch tests/test_example.py

# 4. 安裝開發環境
uv sync --dev

# 5. 開發循環
# - 撰寫程式碼
# - 執行測試：pytest
# - 格式化：ruff format .
# - 提交：git commit
```

---

## 參考資源

### 官方文件

- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [PEP 621 - project metadata](https://peps.python.org/pep-0621/)
- [PEP 735 - dependency groups](https://peps.python.org/pep-0735/)
- [Python Packaging User Guide](https://packaging.python.org/)

### 工具文件

- [Setuptools](https://setuptools.pypa.io/)
- [Pytest](https://docs.pytest.org/)
- [Black](https://black.readthedocs.io/)
- [Ruff](https://docs.astral.sh/ruff/)
- [uv](https://docs.astral.sh/uv/)

### 範例專案

- [Python Package Template](https://github.com/rochacbruno/python-project-template)
- [PyPA Sample Project](https://github.com/pypa/sampleproject)

---

## 總結

`pyproject.toml` 是現代 Python 專案的核心配置檔案。透過本指南，你應該已經了解：

✅ 為什麼需要 pyproject.toml
✅ 各個區段的作用和配置方式
✅ 如何管理依賴和版本
✅ 如何整合各種開發工具
✅ 最佳實踐和常見陷阱

記住：

1. **從簡單開始** - 只添加必要的配置
2. **持續改進** - 隨著專案成長調整配置
3. **保持一致** - 遵循社群標準和最佳實踐
4. **善用工具** - 使用 uv、ruff 等現代工具提升效率

祝你的 Python 專案開發順利！🚀
