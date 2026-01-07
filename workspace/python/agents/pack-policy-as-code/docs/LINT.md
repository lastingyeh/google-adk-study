# Lint 配置說明

## 設計目的

本專案採用多層次的程式碼品質檢查工具，確保程式碼的可讀性、可維護性與型別安全。主要目的包括：

### 1. **程式碼品質保證**

- 在開發早期發現潛在問題，降低 bug 率
- 統一程式碼風格，提升團隊協作效率
- 確保型別安全，減少執行時期錯誤

### 2. **持續整合友善**

- 可整合至 CI/CD pipeline，作為程式碼合併的門檻
- 自動化檢查，減少人工 code review 負擔
- 提供明確的錯誤訊息，加速問題定位

### 3. **開發體驗優化**

- 提供即時回饋，協助開發者遵循最佳實踐
- 支援自動修復，加速開發流程
- 與 VS Code 等編輯器整合，提供即時提示

## Lint 工具組成

專案使用三種互補的工具來確保程式碼品質：

### 1. **codespell** - 拼字檢查

**用途**：偵測程式碼、註解、文件中的拼字錯誤

**配置檔案**：`.codespellrc`

**特點**：

- 快速掃描所有文字內容
- 支援自訂忽略清單（如專有名詞）
- 輕量級，執行速度快

**範例配置**：

```ini
[codespell]
# ROUGE 是 Recall-Oriented Understudy for Gisting Evaluation 的縮寫
# 這是文本評估中的標準指標名稱
ignore-words-list = ROUGE
```

### 2. **ruff** - Python Linter & Formatter

**用途**：程式碼風格檢查與自動格式化

**特點**：

- 極快速度（使用 Rust 實作）
- 整合超過 700 種 lint 規則（涵蓋 flake8、isort、pylint 等）
- 支援自動修復
- 零配置即可使用

**主要檢查項目**：

- 程式碼風格一致性
- 未使用的 import/變數
- 複雜度檢查
- 安全性問題（如 SQL injection）

**使用方式**：

```bash
# 檢查但不修改
ruff check . --diff

# 自動修復（安全修復）
ruff check . --fix

# 自動修復（包含不安全修復）
ruff check . --fix --unsafe-fixes

# 格式化檢查
ruff format . --check --diff

# 自動格式化
ruff format .
```

### 3. **mypy** - 靜態型別檢查

**用途**：驗證 Python 型別注釋的正確性

**配置位置**：`pyproject.toml` 中的 `[tool.mypy]` 區段

**特點**：

- 在執行前發現型別錯誤
- 改善程式碼自動補全
- 提升程式碼可讀性與可維護性

**主要檢查項目**：

- 函式參數與回傳值型別
- 變數型別注釋
- 第三方套件型別存根（type stubs）

**配置說明**：

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = false          # 不警告回傳 Any 型別
warn_unused_configs = true       # 警告未使用的配置
disallow_untyped_defs = false    # 允許未標註型別的函式
allow_untyped_globals = true     # 允許全域變數無型別
allow_untyped_defs = true        # 允許函式定義無型別
allow_redefinition = true        # 允許變數重新定義

# 忽略缺少型別標記的第三方套件
[[tool.mypy.overrides]]
module = ["google.cloud", "google.cloud.*"]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = ["locust", "locust.*"]
ignore_missing_imports = true

# 測試檔案使用較寬鬆的規則
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
check_untyped_defs = false
```

## 安裝與執行

### 安裝依賴

Lint 工具已定義在 `pyproject.toml` 的可選依賴中：

```toml
[project.optional-dependencies]
lint = [
    "codespell",      # 拼字檢查工具
    "ruff",           # Python linter 和格式化工具
    "mypy",           # 靜態類型檢查工具
    "types-requests", # requests 的類型 stub
]
```

安裝方式：

```bash
# 使用 uv 安裝
uv sync --dev --extra lint

# 或使用 make 指令（會自動安裝）
make lint
```

### 執行 Lint

```bash
# 執行所有 lint 檢查
make lint

# 這會依序執行：
# 1. uv sync --dev --extra lint  (安裝依賴)
# 2. uv run codespell             (拼字檢查)
# 3. uv run ruff check . --diff   (程式碼檢查)
# 4. uv run ruff format . --check --diff  (格式檢查)
# 5. uv run mypy .                (型別檢查)
```

## 常見問題處理

### 1. 處理第三方套件型別問題

**問題**：某些 Google Cloud 套件缺少型別標記

**解決方案**：

- 安裝 type stubs（如 `types-requests`）
- 使用 `# type: ignore` 註釋
- 在 mypy 配置中忽略特定模組

**範例**：

```python
from google.cloud import storage  # type: ignore
```

### 2. 處理複雜的型別推斷

**問題**：mypy 無法正確推斷某些動態程式碼的型別

**解決方案**：

```python
# 方法 1：添加明確的型別注釋
sample_values: dict[str, Any] = {}

# 方法 2：使用 type: ignore 註釋
violations = check_policy_func(metadata)  # type: ignore[operator]

# 方法 3：使用 cast
from typing import cast
result = cast(dict[str, str], some_function())
```

### 3. 處理測試程式碼的型別錯誤

測試程式碼通常使用 mock 和動態特性，可能導致型別錯誤。建議：

```python
# 在特定行添加 type: ignore
new_tools.append(mock)  # type: ignore[arg-type]

# 或在函式層級添加
def test_something():  # type: ignore
    ...
```

## 開發建議

### 1. **開發流程整合**

建議在以下時機執行 lint：

- **提交前**：在 git commit 前執行 `make lint`
- **推送前**：確保 CI 不會因 lint 失敗而中斷
- **Pull Request**：作為 code review 的第一道防線

### 2. **漸進式採用**

對於現有專案：

1. 先修復 codespell 錯誤（最簡單）
2. 執行 ruff 自動格式化
3. 逐步添加型別注釋，提升 mypy 覆蓋率

### 3. **編輯器整合**

**VS Code 建議擴充套件**：

- `charliermarsh.ruff` - Ruff 官方擴充
- `ms-python.mypy-type-checker` - Mypy 型別檢查
- `streetsidesoftware.code-spell-checker` - 拼字檢查

**配置範例**（`.vscode/settings.json`）：

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  },
  "mypy-type-checker.args": ["--config-file=pyproject.toml"],
  "ruff.lint.args": ["--config=pyproject.toml"]
}
```

### 4. **CI/CD 整合**

在 GitHub Actions 或其他 CI 系統中：

```yaml
- name: Run linting
  run: |
    make lint
  # 或分別執行以獲得更詳細的錯誤報告
  # run: |
  #   uv run codespell
  #   uv run ruff check .
  #   uv run ruff format . --check
  #   uv run mypy .
```

### 5. **型別注釋最佳實踐**

```python
# ✅ 好的實踐
def process_data(items: list[dict[str, Any]]) -> dict[str, int]:
    """處理資料並回傳統計結果。"""
    result: dict[str, int] = {}
    for item in items:
        # 處理邏輯
        pass
    return result

# ❌ 避免
def process_data(items):  # 缺少型別注釋
    result = {}  # mypy 無法推斷型別
    return result
```

## 效益評估

實施 lint 工具後的預期效益：

### 短期效益

- ✅ 減少 30-50% 的低階錯誤（拼字、格式、簡單型別錯誤）
- ✅ 統一程式碼風格，減少 code review 時間
- ✅ 提早發現潛在 bug

### 長期效益

- ✅ 降低維護成本（程式碼更易讀、易理解）
- ✅ 加速新成員上手（一致的程式碼風格）
- ✅ 提升程式碼品質文化

## 參考資源

- **ruff**：https://docs.astral.sh/ruff/
- **mypy**：https://mypy.readthedocs.io/
- **codespell**：https://github.com/codespell-project/codespell
- **Python Type Hints**：https://docs.python.org/3/library/typing.html
- **PEP 484**：https://peps.python.org/pep-0484/ (Type Hints)
- **PEP 8**：https://peps.python.org/pep-0008/ (Style Guide)

## 總結

本專案的 lint 配置採用業界標準工具，在程式碼品質、開發體驗與執行效能間取得平衡：

- **codespell** 確保文件與註解的正確性
- **ruff** 提供極速的程式碼檢查與格式化
- **mypy** 保證型別安全，減少執行時期錯誤

透過 `make lint` 指令，開發者可以一鍵執行所有檢查，確保程式碼符合專案標準。建議將 lint 檢查整合至開發流程與 CI/CD pipeline，以維持高品質的程式碼基底。
