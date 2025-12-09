# MCP-A2A-Master 測試文件

本目錄包含 MCP-A2A-Master 專案的所有測試程式碼。

## 📋 測試結構

```
tests/
├── __init__.py                    # 測試套件初始化
├── conftest.py                    # Pytest 配置與共用 fixtures
├── test_imports.py                # 匯入測試
├── test_structure.py              # 專案結構測試
├── test_utilities.py              # Utilities 模組測試
├── test_host_agent.py             # HostAgent 測試
├── test_website_builder_agent.py  # WebsiteBuilderSimple 測試
└── test_integration.py            # 整合測試
```

## 🚀 快速開始

### 安裝測試相依套件

```bash
# 安裝所有相依套件（包含測試套件）
make setup

# 或使用 uv 直接安裝
uv sync --extra dev
```

### 執行測試

```bash
# 執行所有測試
make test

# 執行單元測試
make test-unit

# 執行整合測試
make test-integration

# 執行測試涵蓋率分析
make test-coverage
```

## 📝 測試類型

### 1. 匯入測試 (`test_imports.py`)

驗證所有模組能正確匯入，避免循環相依或遺失套件。

**測試範圍：**

- Agent 模組匯入
- Utilities 模組匯入
- 外部相依套件匯入

**執行：**

```bash
pytest tests/test_imports.py -v
```

### 2. 結構測試 (`test_structure.py`)

驗證專案結構完整性，確保所有必要的檔案與目錄都存在。

**測試範圍：**

- 主要目錄存在性
- Agent 檔案完整性
- Utilities 檔案完整性
- 配置檔案存在性

**執行：**

```bash
pytest tests/test_structure.py -v
```

### 3. Utilities 測試 (`test_utilities.py`)

測試工具類別的功能正確性。

**測試範圍：**

- `FileLoader` - 檔案載入工具
- `AgentConnector` - A2A Agent 連接器
- `AgentDiscovery` - A2A Agent 發現服務
- `MCPConnector` - MCP Server 連接器
- `MCPDiscovery` - MCP Server 發現服務

**執行：**

```bash
pytest tests/test_utilities.py -v
```

### 4. HostAgent 測試 (`test_host_agent.py`)

測試 HostAgent 的核心功能與配置。

**測試範圍：**

- Agent 初始化與配置
- Agent 建立流程
- 工具函式（`_list_agents`, `_delegate_task`）
- Invoke 功能
- HostAgentExecutor

**執行：**

```bash
pytest tests/test_host_agent.py -v
```

### 5. WebsiteBuilder 測試 (`test_website_builder_agent.py`)

測試 WebsiteBuilderSimple Agent 的功能。

**測試範圍：**

- Agent 初始化與配置
- Agent 建立流程
- Invoke 功能
- AgentResponse 模型驗證
- WebsiteBuilderSimpleAgentExecutor

**執行：**

```bash
pytest tests/test_website_builder_agent.py -v
```

### 6. 整合測試 (`test_integration.py`)

測試多個元件的協同工作。

**測試範圍：**

- HostAgent 與 MCP 整合
- HostAgent 與 A2A 整合
- AgentExecutor 整合
- Utilities 整合
- 端對端工作流程

**執行：**

```bash
pytest tests/test_integration.py -v
```

## 🏷️ 測試標記 (Markers)

本專案使用以下 pytest 標記來組織測試：

- `@pytest.mark.unit` - 單元測試
- `@pytest.mark.integration` - 整合測試
- `@pytest.mark.e2e` - 端對端測試
- `@pytest.mark.slow` - 執行緩慢的測試

### 使用範例

```bash
# 只執行單元測試
pytest -m unit

# 只執行整合測試
pytest -m integration

# 排除緩慢的測試
pytest -m "not slow"

# 執行特定標記組合
pytest -m "unit and not slow"
```

## 🧪 測試涵蓋率

### 查看涵蓋率報告

```bash
# 產生 HTML 涵蓋率報告
make test-coverage

# 開啟報告
open htmlcov/index.html
```

### 涵蓋率目標

| 模組                             | 目標覆蓋率 |
| -------------------------------- | ---------- |
| `agents/host_agent/`             | ≥ 90%      |
| `agents/website_builder_simple/` | ≥ 85%      |
| `utilities/a2a/`                 | ≥ 90%      |
| `utilities/mcp/`                 | ≥ 90%      |
| `utilities/common/`              | ≥ 80%      |
| **整體專案**                     | **≥ 80%**  |

## 🔧 共用 Fixtures

`conftest.py` 提供以下共用 fixtures：

### `test_config`

測試配置字典。

```python
def test_example(test_config):
    assert test_config["test_mode"] is True
```

### `mock_agent_card`

模擬的 AgentCard 物件。

```python
def test_example(mock_agent_card):
    assert mock_agent_card.name == "test_website_builder"
```

### `mock_mcp_server_config`

模擬的 MCP Server 配置。

```python
def test_example(mock_mcp_server_config):
    assert "test_server" in mock_mcp_server_config
```

### `mock_a2a_registry`

模擬的 A2A Agent Registry。

```python
def test_example(mock_a2a_registry):
    assert len(mock_a2a_registry) >= 2
```

### `sample_queries`

測試用查詢範例。

```python
def test_example(sample_queries):
    query = sample_queries[0]
    assert len(query) > 0
```

## 📊 測試指令完整列表

```bash
# 基本測試指令
pytest                              # 執行所有測試
pytest -v                           # 詳細輸出
pytest -s                           # 顯示 print 輸出
pytest -x                           # 停在第一個失敗
pytest --lf                         # 只執行上次失敗的測試
pytest --ff                         # 先執行上次失敗的測試

# 執行特定測試
pytest tests/test_imports.py        # 執行特定檔案
pytest tests/test_imports.py::TestAgentImports  # 執行特定類別
pytest tests/test_imports.py::TestAgentImports::test_host_agent_import  # 執行特定測試

# 使用標記
pytest -m unit                      # 只執行單元測試
pytest -m integration               # 只執行整合測試
pytest -m "not slow"                # 排除緩慢測試

# 涵蓋率測試
pytest --cov=agents --cov=utilities  # 基本涵蓋率
pytest --cov=agents --cov-report=html  # HTML 報告
pytest --cov=agents --cov-report=term-missing  # 顯示遺失的行號

# 並行執行（需要 pytest-xdist）
pytest -n auto                      # 自動判斷 CPU 核心數
pytest -n 4                         # 使用 4 個 worker

# 其他實用選項
pytest --durations=10               # 顯示最慢的 10 個測試
pytest --tb=short                   # 簡短的 traceback
pytest --tb=no                      # 不顯示 traceback
pytest -k "test_agent"              # 只執行名稱包含 "test_agent" 的測試
```

## 🛠️ 撰寫新測試

### 基本測試範例

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestMyFeature:
    """測試我的功能。"""

    def test_basic_functionality(self):
        """測試基本功能。"""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == "expected"
```

### 非同步測試範例

```python
@pytest.mark.asyncio
async def test_async_function(self):
    """測試非同步函式。"""
    result = await my_async_function()
    assert result is not None
```

### 使用 Mock 範例

```python
@pytest.mark.asyncio
async def test_with_mock(self):
    """測試使用 mock。"""
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = await my_function()
        assert result == "mocked"
        mock_func.assert_called_once()
```

## 📚 最佳實踐

### 1. 測試命名

- ✅ 使用描述性名稱：`test_user_can_login_with_valid_credentials`
- ❌ 避免模糊名稱：`test_1`, `test_function`

### 2. AAA 模式

所有測試應遵循 Arrange-Act-Assert 模式：

```python
def test_example(self):
    # Arrange - 準備測試資料
    input_data = "test"

    # Act - 執行測試目標
    result = my_function(input_data)

    # Assert - 驗證結果
    assert result == "expected"
```

### 3. 測試獨立性

- ✅ 每個測試應獨立運作
- ✅ 使用 fixtures 進行設定與清理
- ❌ 不要依賴其他測試的執行順序

### 4. Mock 外部相依

- ✅ Mock HTTP 請求
- ✅ Mock 資料庫操作
- ✅ Mock LLM 呼叫
- ❌ 不要在測試中進行真實的外部呼叫

## 🐛 疑難排解

### 問題：測試失敗 "ModuleNotFoundError"

**解決方法：**

```bash
# 確保已安裝所有相依套件
uv sync --extra dev

# 或重新安裝
make setup
```

### 問題：非同步測試失敗

**解決方法：**
確保使用 `@pytest.mark.asyncio` 裝飾器：

```python
@pytest.mark.asyncio
async def test_my_async_function(self):
    result = await my_function()
    assert result is not None
```

### 問題：Import 錯誤

**解決方法：**
確保從專案根目錄執行測試：

```bash
# 正確 ✅
cd /path/to/mcp-a2a-master
pytest tests/

# 錯誤 ❌
cd tests
pytest .
```

## 📞 需要協助？

- 查看測試規範：`.github/instructions/test-specification.instructions.md`
- 查看現有測試範例
- 參考 pytest 官方文件：https://docs.pytest.org/

---

**最後更新：** 2025 年 12 月 9 日
**維護者：** MCP-A2A-Master Team
