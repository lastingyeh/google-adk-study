# 測試快速參考指南

## 🚀 快速開始

### 安裝測試相依套件

```bash
# 從專案根目錄執行
pip install pytest pytest-asyncio pytest-cov
```

### 執行所有測試

```bash
# 基本執行
pytest

# 詳細輸出
pytest -v

# 顯示 print 輸出
pytest -vs
```

---

## 📋 常用測試指令

### 按類型執行

```bash
# 單元測試
pytest tests/unit/

# 整合測試
pytest tests/integration/

# 排除整合測試
pytest tests/unit/ -v
```

### 按檔案執行

```bash
# 匯入測試
pytest tests/unit/test_imports.py -v

# Agent 測試
pytest tests/unit/test_agent.py -v

# 工具測試
pytest tests/unit/test_tools.py -v

# 伺服器測試
pytest tests/integration/test_server_e2e.py -v
```

### 按測試類別執行

```bash
# Story Agent 測試
pytest tests/unit/test_agent.py::TestStoryAgent -v

# Request 模型測試
pytest tests/unit/test_models.py::TestRequestModel -v

# Storyboard 工具測試
pytest tests/unit/test_tools.py::TestStoryboardGenerateTool -v
```

---

## 📊 涵蓋率測試

### 產生涵蓋率報告

```bash
# HTML 報告
pytest --cov=app --cov-report=html

# 終端報告
pytest --cov=app --cov-report=term

# 同時產生兩種報告
pytest --cov=app --cov-report=html --cov-report=term
```

### 查看報告

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

---

## 🔍 測試篩選

### 使用標記

```bash
# 只執行單元測試
pytest -m unit

# 只執行整合測試
pytest -m integration

# 排除緩慢測試
pytest -m "not slow"
```

### 使用關鍵字

```bash
# 執行名稱包含 "agent" 的測試
pytest -k agent

# 執行名稱包含 "import" 的測試
pytest -k import

# 執行名稱包含 "story" 的測試
pytest -k story
```

---

## 🐛 除錯測試

### 顯示詳細資訊

```bash
# 顯示本地變數
pytest -l

# 停在第一個失敗
pytest -x

# 顯示最慢的 10 個測試
pytest --durations=10
```

### 重新執行失敗測試

```bash
# 只執行上次失敗的測試
pytest --lf

# 先執行失敗的測試
pytest --ff
```

### 進入除錯器

```bash
# 失敗時進入 pdb
pytest --pdb

# 從開始就進入 pdb
pytest --trace
```

---

## 📝 測試檢查清單

### 執行測試前

- [ ] 確保已安裝所有相依套件
- [ ] 確認專案結構完整
- [ ] 檢查環境變數設定（如需要）

### 新增測試時

- [ ] 測試命名清晰描述性
- [ ] 使用 AAA 模式（Arrange-Act-Assert）
- [ ] 適當使用 mock
- [ ] 測試正常和異常情況
- [ ] 測試通過且涵蓋率符合目標

### 提交前

- [ ] 所有測試通過
- [ ] 涵蓋率報告正常
- [ ] 無測試警告
- [ ] 更新相關文件

---

## 🎯 測試目標

### 涵蓋率目標

- **核心功能：** ≥ 90%
- **工具函式：** ≥ 80%
- **整體專案：** ≥ 70%

### 測試數量

當前測試統計：
- 單元測試：101 個
- 整合測試：9 個
- 總計：110 個

---

## 💡 提示與技巧

### 提升測試速度

```bash
# 並行執行（需要 pytest-xdist）
pip install pytest-xdist
pytest -n auto
```

### 測試特定功能

```bash
# 測試所有 Agent
pytest -k "agent" -v

# 測試所有模型
pytest -k "model" -v

# 測試所有工具
pytest -k "tool" -v
```

### 產生測試報告

```bash
# JUnit XML 報告
pytest --junitxml=report.xml

# HTML 報告（需要 pytest-html）
pip install pytest-html
pytest --html=report.html
```

---

## 📞 問題排查

### 常見問題

1. **ModuleNotFoundError**
   ```bash
   # 確保在專案根目錄執行
   cd /path/to/short-movie-agents
   pytest
   ```

2. **Import 錯誤**
   ```bash
   # 檢查 PYTHONPATH
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   pytest
   ```

3. **測試掛起**
   ```bash
   # 使用 timeout
   pytest --timeout=30
   ```

---

## 📚 參考連結

- [Pytest 文件](https://docs.pytest.org/)
- [測試完整文件](./README.md)
- [測試摘要](./TEST_SUMMARY.md)

---

**最後更新：** 2026 年 1 月 28 日
