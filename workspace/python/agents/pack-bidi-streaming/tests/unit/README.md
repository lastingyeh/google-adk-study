# Pack-bidi-streaming 測試套件

本目錄包含 `pack-bidi-streaming` 專案的所有測試案例。

## 📁 目錄結構

```
tests/
├── conftest.py                # Pytest 配置與共用 fixtures
├── README.md                  # 本文件
├── unit/                      # 單元測試
│   ├── __init__.py
│   ├── test_imports.py        # 模組匯入測試
│   ├── test_structure.py      # 專案結構測試
│   ├── test_agent.py          # Agent 配置與工具測試
│   ├── test_models.py         # Pydantic 模型測試
│   └── test_telemetry.py      # 遙測設定測試
├── integration/               # 整合測試
│   ├── test_agent.py          # Agent 整合測試
│   └── test_server_e2e.py     # 伺服器端對端測試
└── load_test/                 # 負載測試
    ├── load_test.py
    └── README.md
```

## 🧪 測試類型

### 單元測試 (Unit Tests)

位於 `tests/unit/` 目錄，測試獨立的程式碼單元。

- **test_imports.py**: 驗證所有模組能正確匯入，無循環相依
- **test_structure.py**: 驗證專案結構完整性，必要檔案存在
- **test_agent.py**: 測試 Agent 配置、屬性與工具函式
- **test_models.py**: 測試 Pydantic 模型（Feedback、Request）
- **test_telemetry.py**: 測試遙測功能設定

### 整合測試 (Integration Tests)

位於 `tests/integration/` 目錄，測試多個元件的協同運作。

- **test_agent.py**: 測試 Agent 的完整運作流程
- **test_server_e2e.py**: 測試 FastAPI 伺服器的端對端功能

### 負載測試 (Load Tests)

位於 `tests/load_test/` 目錄，測試系統在高負載下的表現。

## 🚀 執行測試

### 執行所有測試

```bash
pytest
```

### 執行特定類型的測試

```bash
# 只執行單元測試
pytest tests/unit/

# 只執行整合測試
pytest tests/integration/

# 使用標記執行
pytest -m unit
pytest -m integration
```

### 執行特定測試檔案

```bash
# 執行匯入測試
pytest tests/unit/test_imports.py

# 執行 Agent 測試
pytest tests/unit/test_agent.py
```

### 執行特定測試函式

```bash
pytest tests/unit/test_agent.py::TestAgentConfiguration::test_root_agent_exists
```

### 詳細輸出

```bash
# 顯示詳細資訊
pytest -v

# 顯示 print 輸出
pytest -s

# 同時顯示詳細資訊與 print 輸出
pytest -vs
```

### 測試涵蓋率

```bash
# 執行測試並產生涵蓋率報告
pytest --cov=bidi_demo --cov-report=html --cov-report=term

# 查看涵蓋率報告
open htmlcov/index.html
```

## 📊 測試涵蓋範圍

### 已涵蓋的測試

✅ **模組匯入測試**
- Agent 模組
- FastAPI 應用
- 工具函式
- Pydantic 模型
- ADK 相依套件

✅ **專案結構測試**
- 必要目錄存在性
- 必要檔案存在性
- 配置檔案完整性

✅ **Agent 測試**
- Agent 配置與屬性
- 工具函式功能
- 環境變數設定

✅ **模型測試**
- Feedback 模型驗證
- Request 模型驗證
- 欄位型別檢查
- 預設值生成

✅ **遙測測試**
- 遙測功能設定
- 環境變數處理
- GCS 上傳配置

## 🔧 測試配置

### conftest.py

包含 pytest 配置與共用 fixtures：

- **pytest_configure**: 註冊測試標記
- **test_config**: 測試配置資料
- **mock_tool_context**: 模擬 ToolContext
- **reset_environment**: 自動重置環境變數
- **sample_feedback_data**: 測試用 Feedback 資料
- **sample_request_data**: 測試用 Request 資料

### 測試標記

- `@pytest.mark.unit`: 單元測試
- `@pytest.mark.integration`: 整合測試
- `@pytest.mark.e2e`: 端對端測試
- `@pytest.mark.slow`: 執行緩慢的測試

## 📝 撰寫新測試

### 測試檔案命名

- 檔案名稱以 `test_` 開頭
- 測試函式以 `test_` 開頭
- 測試類別以 `Test` 開頭

### 測試範例

```python
"""
測試模組說明
"""

class TestFeature:
    """測試功能類別。"""

    def test_feature_exists(self):
        """測試功能是否存在。"""
        from bidi_demo.module import feature

        assert feature is not None

    def test_feature_functionality(self):
        """測試功能運作正常。"""
        from bidi_demo.module import feature

        result = feature("input")
        assert result == "expected_output"
```

### 使用 Fixtures

```python
def test_with_fixture(sample_feedback_data):
    """使用 fixture 的測試。"""
    assert sample_feedback_data["score"] == 5
```

### Mock 外部相依

```python
from unittest.mock import patch

@patch('bidi_demo.module.external_function')
def test_with_mock(mock_external):
    """使用 mock 的測試。"""
    mock_external.return_value = "mocked_value"

    result = function_using_external()

    assert result is not None
    mock_external.assert_called_once()
```

## 🎯 測試最佳實踐

1. **獨立性**: 每個測試應該獨立運作，不依賴其他測試
2. **清晰命名**: 測試名稱應清楚描述測試內容
3. **AAA 模式**: 使用 Arrange-Act-Assert 組織測試
4. **最小化 Mock**: 只 mock 必要的外部相依
5. **完整涵蓋**: 測試正常路徑、錯誤處理與邊界條件

## 🐛 除錯測試

### 停在第一個失敗

```bash
pytest -x
```

### 進入 Python 除錯器

```bash
pytest --pdb
```

### 只執行上次失敗的測試

```bash
pytest --lf
```

### 執行特定測試並顯示詳細輸出

```bash
pytest tests/unit/test_agent.py::TestGetWeatherTool -vs
```

## 📈 持續改進

- 定期檢查測試涵蓋率
- 新功能必須包含對應測試
- 修正 bug 時新增回歸測試
- 保持測試程式碼的可維護性

## 🔗 相關資源

- [Pytest 官方文件](https://docs.pytest.org/)
- [Google ADK 文件](https://cloud.google.com/generative-ai-sdk)
- [專案 README](../README.md)

---

**最後更新**: 2026-02-03
**維護者**: pack-bidi-streaming 團隊
