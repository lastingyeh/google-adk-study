---
applyTo: '**/tests/**'
---

# 測試規範與案例建立指南

本文件提供完整的測試規範與範例，用於分析目標專案並建立符合最佳實踐的測試案例。

## 📋 核心流程

```
目標專案 → 分析階段 → 參考測試規範 → 建立測試案例 → 執行驗證
```

---

## 🎯 第一階段：專案分析

### 1.1 專案結構分析

**分析清單：**

- [ ] 識別專案類型 (Agent/Tool/Service/Library)
- [ ] 檢查現有檔案結構
- [ ] 確認相依套件與框架
- [ ] 識別核心功能模組
- [ ] 檢查是否有現有測試

**執行指令：**

```bash
# 查看專案結構
tree -L 3 -I '__pycache__|*.pyc|.pytest_cache'

# 檢查相依套件
cat requirements.txt
cat pyproject.toml

# 搜尋現有測試
find . -name "test_*.py" -o -name "*_test.py"
```

### 1.2 功能模組識別

**需要識別的元件：**

1. **Agent 相關**

   - Agent 定義檔案 (通常在 `agent.py` 或 `root_agent.yaml`)
   - Sub-agents (子 Agent)
   - Agent 配置 (模型、指令、描述)

2. **工具函式**

   - Tools 目錄下的所有函式
   - 自訂工具 (custom tools)
   - 外部 API 整合

3. **資料模型**

   - Pydantic models
   - 資料類別 (dataclasses)
   - 類型定義

4. **整合點**
   - A2A 連接
   - MCP 整合
   - 資料庫連接
   - 外部服務

---

## 📚 第二階段：參考測試規範

### 2.1 標準測試檔案架構

每個 Agent 專案應包含以下四個核心測試檔案：

#### A. `test_imports.py` - 匯入測試

**目的：** 確保所有模組能正確匯入，避免循環相依或遺失套件

**範例模板：**

```python
"""
測試所有模組的匯入功能。
確保沒有循環相依或遺失的套件。
"""

import pytest


class TestImports:
    """測試模組匯入功能。"""

    def test_main_package_import(self):
        """測試主套件能否匯入。"""
        try:
            import {package_name}
            assert {package_name} is not None
        except ImportError as e:
            pytest.fail(f"匯入主套件失敗：{e}")

    def test_agent_module_import(self):
        """測試 agent 模組能否匯入。"""
        try:
            from {package_name} import agent
            assert agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 agent 模組失敗：{e}")

    def test_tools_import(self):
        """測試 tools 套件能否匯入。"""
        try:
            from {package_name} import tools
            assert tools is not None
        except ImportError as e:
            pytest.fail(f"匯入 tools 套件失敗：{e}")

    def test_all_tool_functions_importable(self):
        """測試所有工具函式能否匯入。"""
        try:
            from {package_name}.tools import (
                {tool_function_1},
                {tool_function_2},
                # ... 列出所有工具函式
            )
            assert True
        except ImportError as e:
            pytest.fail(f"匯入工具函式失敗：{e}")

    def test_adk_dependencies_import(self):
        """測試 ADK 相依套件能否匯入。"""
        try:
            from google.adk.agents import Agent
            from google.genai import types
            assert True
        except ImportError as e:
            pytest.fail(f"匯入 ADK 相依套件失敗：{e}")
```

#### B. `test_structure.py` - 結構測試

**目的：** 驗證專案結構完整性、必要檔案存在

**範例模板：**

```python
"""
測試專案結構與檔案組織。
確保所有必要的檔案與目錄都存在。
"""

import os
import pytest


class TestProjectStructure:
    """測試專案結構完整性。"""

    def test_package_directory_exists(self):
        """測試主套件目錄是否存在。"""
        assert os.path.exists('{package_name}'), "{package_name} 目錄應該存在"
        assert os.path.isdir('{package_name}'), "{package_name} 應該是一個目錄"

    def test_agent_file_exists(self):
        """測試 agent.py 是否存在。"""
        assert os.path.exists('{package_name}/agent.py'), "agent.py 應該存在"

    def test_yaml_config_exists(self):
        """測試 YAML 配置檔案是否存在（如適用）。"""
        yaml_path = '{package_name}/root_agent.yaml'
        if os.path.exists(yaml_path):
            assert os.path.isfile(yaml_path), "root_agent.yaml 應該是一個檔案"

    def test_tools_directory_exists(self):
        """測試 tools 目錄是否存在。"""
        tools_path = '{package_name}/tools'
        if os.path.exists(tools_path):
            assert os.path.isdir(tools_path), "tools 應該是一個目錄"
            assert os.path.exists(f'{tools_path}/__init__.py'), "tools/__init__.py 應該存在"

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.exists('tests'), "tests 目錄應該存在"
        assert os.path.isdir('tests'), "tests 應該是一個目錄"

    def test_required_test_files_exist(self):
        """測試必要的測試檔案是否存在。"""
        required_files = [
            'tests/__init__.py',
            'tests/test_imports.py',
            'tests/test_structure.py',
            'tests/test_agent.py',
        ]

        for file_path in required_files:
            assert os.path.exists(file_path), f"{file_path} 應該存在"

    def test_project_config_files_exist(self):
        """測試專案配置檔案是否存在。"""
        config_files = ['README.md', 'requirements.txt', 'pyproject.toml']

        for config_file in config_files:
            if os.path.exists(config_file):
                assert os.path.isfile(config_file), f"{config_file} 應該是一個檔案"

    def test_makefile_exists(self):
        """測試 Makefile 是否存在。"""
        if os.path.exists('Makefile'):
            assert os.path.isfile('Makefile'), "Makefile 應該是一個檔案"
```

#### C. `test_agent.py` - Agent 測試

**目的：** 測試 Agent 的核心功能、配置、屬性

**範例模板：**

```python
"""
測試 Agent 的核心功能與配置。
"""

import pytest
from unittest.mock import Mock, patch
from {package_name}.agent import root_agent  # 或其他 agent 名稱


class TestAgentConfiguration:
    """測試 Agent 配置。"""

    def test_agent_exists(self):
        """測試 Agent 物件是否存在。"""
        assert root_agent is not None

    def test_agent_basic_properties(self):
        """測試 Agent 的基本屬性。"""
        # 驗證名稱
        assert hasattr(root_agent, 'name')
        assert isinstance(root_agent.name, str)
        assert len(root_agent.name) > 0

        # 驗證模型
        assert hasattr(root_agent, 'model')
        assert root_agent.model in [
            'gemini-2.0-flash',
            'gemini-2.0-flash-exp',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
        ]

        # 驗證描述
        assert hasattr(root_agent, 'description')
        assert isinstance(root_agent.description, str)

    def test_agent_instruction(self):
        """測試 Agent 的指令設定。"""
        assert hasattr(root_agent, 'instruction')
        assert isinstance(root_agent.instruction, str)
        assert len(root_agent.instruction) > 0

    def test_agent_tools(self):
        """測試 Agent 的工具配置。"""
        assert hasattr(root_agent, 'tools')
        assert isinstance(root_agent.tools, list)
        # 根據實際情況調整工具數量
        assert len(root_agent.tools) >= 0

    def test_agent_has_expected_tools(self):
        """測試 Agent 是否包含預期的工具。"""
        tool_names = [tool.name for tool in root_agent.tools]

        # 列出預期的工具名稱
        expected_tools = [
            '{tool_name_1}',
            '{tool_name_2}',
            # ... 其他工具
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"應包含工具：{expected_tool}"


class TestAgentFunctionality:
    """測試 Agent 的功能性。"""

    @pytest.mark.asyncio
    async def test_agent_can_be_instantiated(self):
        """測試 Agent 能否被實例化。"""
        from google.adk.agents import Agent
        assert isinstance(root_agent, Agent)

    def test_agent_sub_agents(self):
        """測試 Agent 的子 Agent 配置（如適用）。"""
        if hasattr(root_agent, 'sub_agents'):
            assert isinstance(root_agent.sub_agents, list)
            for sub_agent in root_agent.sub_agents:
                assert hasattr(sub_agent, 'name')

    def test_agent_planner_configuration(self):
        """測試 Agent 的 Planner 配置（如適用）。"""
        if hasattr(root_agent, 'planner'):
            assert root_agent.planner is not None


class TestYAMLConfiguration:
    """測試 YAML 配置載入（如適用）。"""

    def test_yaml_config_loading(self):
        """測試從 YAML 載入 Agent。"""
        yaml_path = '{package_name}/root_agent.yaml'

        if not os.path.exists(yaml_path):
            pytest.skip("沒有 YAML 配置檔案")

        try:
            from google.adk.agents import config_agent_utils
            agent = config_agent_utils.from_config(yaml_path)
            assert agent is not None
        except Exception as e:
            pytest.fail(f"從 YAML 載入失敗：{e}")
```

#### D. `test_tools.py` - 工具測試

**目的：** 測試所有工具函式的功能正確性

**範例模板：**

```python
"""
測試工具函式的功能。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from {package_name}.tools import (
    {tool_function_1},
    {tool_function_2},
    # ... 其他工具函式
)


class Test{ToolName1}:
    """測試 {tool_function_1} 工具。"""

    def setup_method(self):
        """每個測試前的設定。"""
        self.tool_context = Mock()

    def test_tool_basic_functionality(self):
        """測試工具的基本功能。"""
        # 準備測試資料
        test_input = "test_value"

        # 執行工具
        result = {tool_function_1}(test_input, self.tool_context)

        # 驗證結果
        assert result is not None
        assert 'status' in result
        assert result['status'] == 'success'

    def test_tool_with_valid_input(self):
        """測試使用有效輸入。"""
        result = {tool_function_1}("valid_input", self.tool_context)

        assert result['status'] == 'success'
        assert 'data' in result
        assert 'report' in result

    def test_tool_with_invalid_input(self):
        """測試使用無效輸入。"""
        result = {tool_function_1}("", self.tool_context)

        # 根據實際行為調整斷言
        assert result['status'] in ['error', 'failure']

    def test_tool_error_handling(self):
        """測試錯誤處理機制。"""
        with pytest.raises(Exception):
            {tool_function_1}(None, self.tool_context)

    @patch('{external_dependency}')
    def test_tool_with_mocked_dependency(self, mock_dependency):
        """測試使用 mock 外部相依。"""
        mock_dependency.return_value = "mocked_result"

        result = {tool_function_1}("test", self.tool_context)

        assert result is not None
        mock_dependency.assert_called_once()


class Test{ToolName2}:
    """測試 {tool_function_2} 工具。"""

    # 重複上述測試模式
    pass
```

---

### 2.2 進階測試類型

#### E. `test_integration.py` - 整合測試

**適用場景：** 多個元件互動、完整工作流程

**範例模板：**

```python
"""
整合測試 - 測試多個元件的協同工作。
"""

import pytest
from unittest.mock import Mock, AsyncMock


@pytest.mark.integration
class TestAgentToolIntegration:
    """測試 Agent 與工具的整合。"""

    @pytest.mark.asyncio
    async def test_agent_uses_tool_correctly(self):
        """測試 Agent 能否正確使用工具。"""
        from {package_name}.agent import root_agent

        # 模擬執行
        # 根據實際情況調整
        assert root_agent is not None


@pytest.mark.integration
class TestWorkflowIntegration:
    """測試完整工作流程。"""

    def setup_method(self):
        """每個測試前的初始化。"""
        # 初始化資料庫、連接等
        pass

    def teardown_method(self):
        """每個測試後的清理。"""
        # 清理資料
        pass

    def test_complete_workflow(self):
        """測試完整的使用者工作流程。"""
        # 步驟 1
        # 步驟 2
        # 步驟 3
        # 驗證結果
        pass
```

#### F. `test_e2e.py` - 端對端測試

**適用場景：** 完整使用者情境、多步驟流程

**範例模板：**

```python
"""
端對端測試 - 測試完整的使用者情境。
"""

import pytest


@pytest.mark.e2e
class TestUserScenarios:
    """測試完整的使用者情境。"""

    def setup_method(self):
        """每個測試前的設定。"""
        # 初始化測試環境
        pass

    def test_scenario_new_user(self):
        """測試新使用者的完整流程。"""
        # 步驟 1：使用者註冊
        # 步驟 2：設定偏好
        # 步驟 3：執行操作
        # 步驟 4：驗證結果
        pass

    def test_scenario_returning_user(self):
        """測試回訪使用者的流程。"""
        pass
```

#### G. 領域特定測試

根據專案類型建立特化測試：

**G1. `test_multimodal.py` - 多模態測試**

```python
"""測試圖片、音訊、視訊處理功能。"""

class TestImageProcessing:
    """測試圖片處理工具。"""

    @pytest.fixture
    def sample_image(self, tmp_path):
        """建立測試用圖片。"""
        pass

    def test_load_image(self, sample_image):
        """測試圖片載入。"""
        pass

    def test_analyze_image(self, sample_image):
        """測試圖片分析。"""
        pass
```

**G2. `test_hitl.py` - Human-in-the-Loop 測試**

```python
"""測試人機互動功能。"""

class TestToolApprovalWorkflow:
    """測試工具審批工作流程。"""

    def test_destructive_operation_detection(self):
        """測試破壞性操作偵測。"""
        pass

    def test_approval_workflow(self):
        """測試審批流程。"""
        pass
```

**G3. `test_observability.py` - 可觀察性測試**

```python
"""測試監控與日誌功能。"""

class TestEventLogger:
    """測試事件記錄器。"""
    pass

class TestMetricsCollector:
    """測試指標收集器。"""
    pass
```

**G4. `test_plugins.py` - 外掛系統測試**

```python
"""測試外掛程式系統。"""

class TestPluginLoading:
    """測試外掛載入。"""
    pass

class TestPluginExecution:
    """測試外掛執行。"""
    pass
```

---

### 2.3 測試配置檔案

#### `conftest.py` - Pytest 配置

**範例模板：**

```python
"""
Pytest 配置與共用 fixtures。
"""

import pytest


def pytest_configure(config):
    """配置 pytest。"""
    # 註冊自訂標記
    config.addinivalue_line("markers", "unit: 單元測試")
    config.addinivalue_line("markers", "integration: 整合測試")
    config.addinivalue_line("markers", "e2e: 端對端測試")
    config.addinivalue_line("markers", "slow: 執行緩慢的測試")


@pytest.fixture(scope="session")
def test_config():
    """測試配置 fixture。"""
    return {
        "test_mode": True,
        "mock_external_services": True,
    }


@pytest.fixture
def mock_tool_context():
    """模擬 ToolContext。"""
    from unittest.mock import Mock
    context = Mock()
    context.state = {}
    return context


@pytest.fixture(autouse=True)
def reset_environment():
    """每個測試後重置環境。"""
    yield
    # 清理邏輯
```

---

## 🛠️ 第三階段：建立測試案例

### 3.1 測試案例建立步驟

#### 步驟 1：分析目標功能

**問題清單：**

- 這個功能的輸入是什麼？
- 預期的輸出是什麼？
- 有哪些邊界條件？
- 可能的錯誤情況有哪些？
- 需要 mock 哪些外部相依？

#### 步驟 2：設計測試案例

**測試案例設計模板：**

| 測試案例 ID | 測試描述     | 輸入           | 預期輸出 | 測試類型 |
| ----------- | ------------ | -------------- | -------- | -------- |
| TC-001      | 測試正常情況 | valid_input    | success  | 單元測試 |
| TC-002      | 測試空輸入   | ""             | error    | 單元測試 |
| TC-003      | 測試無效格式 | invalid_format | error    | 單元測試 |
| TC-004      | 測試邊界值   | boundary_value | success  | 單元測試 |
| TC-005      | 測試整合流程 | workflow_data  | success  | 整合測試 |

#### 步驟 3：實作測試程式碼

**測試函式命名規範：**

```python
# ✅ 良好的命名
def test_user_can_login_with_valid_credentials():
    pass

def test_order_creation_fails_with_invalid_product_id():
    pass

def test_search_returns_empty_list_when_no_results():
    pass

# ❌ 不好的命名
def test_1():
    pass

def test_function():
    pass
```

**AAA 模式（Arrange-Act-Assert）：**

```python
def test_calculate_total_price():
    # Arrange - 準備測試資料
    items = [
        {"price": 100, "quantity": 2},
        {"price": 50, "quantity": 1},
    ]

    # Act - 執行測試目標
    result = calculate_total(items)

    # Assert - 驗證結果
    assert result == 250
```

#### 步驟 4：涵蓋率檢查

**執行涵蓋率測試：**

```bash
# 執行測試並產生涵蓋率報告
pytest --cov={package_name} --cov-report=html --cov-report=term

# 查看涵蓋率報告
open htmlcov/index.html
```

**涵蓋率目標：**

- 核心功能：≥ 90%
- 工具函式：≥ 80%
- 整體專案：≥ 70%

---

## ✅ 第四階段：執行驗證

### 4.1 測試執行指令

```bash
# 執行所有測試
pytest

# 執行特定檔案
pytest tests/test_agent.py

# 執行特定測試類別
pytest tests/test_tools.py::TestToolName

# 執行特定測試函式
pytest tests/test_tools.py::TestToolName::test_basic_functionality

# 使用標記執行
pytest -m unit           # 只執行單元測試
pytest -m integration    # 只執行整合測試
pytest -m "not slow"     # 排除緩慢的測試

# 詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s

# 停在第一個失敗
pytest -x

# 並行執行（需要 pytest-xdist）
pytest -n auto
```

### 4.2 持續整合配置

**GitHub Actions 範例：**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 📝 完整範例：建立新專案的測試

### 範例情境：建立 `weather-agent` 的測試

#### 1. 專案分析

```
weather-agent/
├── weather_agent/
│   ├── __init__.py
│   ├── agent.py           # 包含 root_agent
│   └── tools/
│       ├── __init__.py
│       └── weather_tools.py  # get_weather, get_forecast
├── requirements.txt
├── pyproject.toml
└── README.md
```

#### 2. 建立測試目錄

```bash
mkdir -p tests
touch tests/__init__.py
touch tests/test_imports.py
touch tests/test_structure.py
touch tests/test_agent.py
touch tests/test_tools.py
touch tests/conftest.py
```

#### 3. 實作 `test_imports.py`

```python
"""測試 weather-agent 的匯入功能。"""

import pytest


class TestImports:
    """測試模組匯入。"""

    def test_main_package_import(self):
        """測試主套件能否匯入。"""
        try:
            import weather_agent
            assert weather_agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 weather_agent 失敗：{e}")

    def test_agent_module_import(self):
        """測試 agent 模組能否匯入。"""
        try:
            from weather_agent import agent
            assert agent is not None
        except ImportError as e:
            pytest.fail(f"匯入 agent 模組失敗：{e}")

    def test_tools_import(self):
        """測試 tools 套件能否匯入。"""
        try:
            from weather_agent import tools
            assert tools is not None
        except ImportError as e:
            pytest.fail(f"匯入 tools 套件失敗：{e}")

    def test_weather_tools_functions_import(self):
        """測試天氣工具函式能否匯入。"""
        try:
            from weather_agent.tools.weather_tools import (
                get_weather,
                get_forecast,
            )
            assert True
        except ImportError as e:
            pytest.fail(f"匯入天氣工具失敗：{e}")
```

#### 4. 實作 `test_structure.py`

```python
"""測試 weather-agent 的專案結構。"""

import os


class TestProjectStructure:
    """測試專案結構。"""

    def test_package_exists(self):
        """測試套件目錄是否存在。"""
        assert os.path.exists('weather_agent')
        assert os.path.isdir('weather_agent')

    def test_agent_file_exists(self):
        """測試 agent.py 是否存在。"""
        assert os.path.exists('weather_agent/agent.py')

    def test_tools_directory_exists(self):
        """測試 tools 目錄是否存在。"""
        assert os.path.exists('weather_agent/tools')
        assert os.path.isdir('weather_agent/tools')
        assert os.path.exists('weather_agent/tools/__init__.py')
        assert os.path.exists('weather_agent/tools/weather_tools.py')

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.exists('tests')
        assert os.path.isdir('tests')

    def test_config_files_exist(self):
        """測試配置檔案是否存在。"""
        assert os.path.exists('README.md')
        assert os.path.exists('requirements.txt')
```

#### 5. 實作 `test_agent.py`

```python
"""測試 weather-agent 的 Agent 功能。"""

import pytest
from weather_agent.agent import root_agent


class TestWeatherAgent:
    """測試天氣 Agent。"""

    def test_agent_exists(self):
        """測試 Agent 是否存在。"""
        assert root_agent is not None

    def test_agent_properties(self):
        """測試 Agent 屬性。"""
        assert root_agent.name == "weather_agent"
        assert root_agent.model in ['gemini-2.0-flash', 'gemini-1.5-pro']
        assert len(root_agent.description) > 0

    def test_agent_has_tools(self):
        """測試 Agent 是否有工具。"""
        assert hasattr(root_agent, 'tools')
        assert len(root_agent.tools) >= 2

    def test_agent_has_weather_tools(self):
        """測試 Agent 是否包含天氣工具。"""
        tool_names = [tool.name for tool in root_agent.tools]
        assert 'get_weather' in tool_names
        assert 'get_forecast' in tool_names
```

#### 6. 實作 `test_tools.py`

```python
"""測試 weather-agent 的工具函式。"""

import pytest
from unittest.mock import Mock, patch
from weather_agent.tools.weather_tools import get_weather, get_forecast


class TestGetWeather:
    """測試 get_weather 工具。"""

    def setup_method(self):
        """測試前設定。"""
        self.tool_context = Mock()

    @patch('weather_agent.tools.weather_tools.requests.get')
    def test_get_weather_success(self, mock_get):
        """測試成功取得天氣。"""
        # Mock API 回應
        mock_get.return_value.json.return_value = {
            'temperature': 25,
            'condition': 'sunny',
        }
        mock_get.return_value.status_code = 200

        result = get_weather('Taipei', self.tool_context)

        assert result['status'] == 'success'
        assert 'temperature' in result['data']
        assert result['data']['temperature'] == 25

    def test_get_weather_invalid_city(self):
        """測試無效城市名稱。"""
        result = get_weather('', self.tool_context)

        assert result['status'] == 'error'
        assert 'Invalid city' in result['message']


class TestGetForecast:
    """測試 get_forecast 工具。"""

    def setup_method(self):
        """測試前設定。"""
        self.tool_context = Mock()

    def test_get_forecast_3_days(self):
        """測試取得 3 天預報。"""
        result = get_forecast('Taipei', 3, self.tool_context)

        assert result['status'] == 'success'
        assert len(result['data']['forecast']) == 3

    def test_get_forecast_invalid_days(self):
        """測試無效天數。"""
        result = get_forecast('Taipei', -1, self.tool_context)

        assert result['status'] == 'error'
```

#### 7. 實作 `conftest.py`

```python
"""Pytest 配置。"""

import pytest


def pytest_configure(config):
    """配置 pytest 標記。"""
    config.addinivalue_line("markers", "unit: 單元測試")
    config.addinivalue_line("markers", "integration: 整合測試")


@pytest.fixture
def mock_tool_context():
    """模擬 ToolContext。"""
    from unittest.mock import Mock
    context = Mock()
    context.state = {}
    return context
```

#### 8. 執行測試

```bash
# 執行所有測試
pytest -v

# 執行涵蓋率測試
pytest --cov=weather_agent --cov-report=html

# 只執行單元測試
pytest -m unit
```

---

## 🎓 最佳實踐建議

### 1. 測試命名

- ✅ 使用描述性名稱：`test_user_login_with_valid_credentials`
- ❌ 避免模糊名稱：`test_1`, `test_function`

### 2. 測試獨立性

- ✅ 每個測試應獨立運作
- ✅ 使用 fixtures 進行設定與清理
- ❌ 不要依賴其他測試的執行順序

### 3. 使用 Mock

- ✅ Mock 外部服務（API、資料庫）
- ✅ 使用 `patch` 隔離相依
- ❌ 不要過度 mock，失去真實性

### 4. 測試涵蓋率

- ✅ 測試正常路徑
- ✅ 測試錯誤處理
- ✅ 測試邊界條件
- ✅ 測試整合點

### 5. 持續維護

- ✅ 程式碼變更時同步更新測試
- ✅ 定期檢查測試涵蓋率
- ✅ 移除過時的測試

---

## 📊 測試檢查清單

### 新專案測試檢查清單

- [ ] 建立 `tests/` 目錄
- [ ] 實作 `test_imports.py`
- [ ] 實作 `test_structure.py`
- [ ] 實作 `test_agent.py`
- [ ] 實作 `test_tools.py` (如有工具)
- [ ] 建立 `conftest.py`
- [ ] 設定 pytest 標記
- [ ] 所有測試通過
- [ ] 測試涵蓋率 ≥ 70%
- [ ] 在 Makefile 加入測試指令
- [ ] 在 README 加入測試說明
- [ ] 設定 CI/CD 自動測試

### 程式碼審查檢查清單

- [ ] 測試命名清晰描述性
- [ ] 使用 AAA 模式組織測試
- [ ] 適當使用 fixtures
- [ ] Mock 外部相依
- [ ] 測試涵蓋錯誤情況
- [ ] 測試涵蓋邊界條件
- [ ] 無重複的測試邏輯
- [ ] 測試執行快速
- [ ] 測試可重複執行
- [ ] 有適當的註解說明

---

## 🔗 參考資源

### 官方文件

- [Pytest 官方文件](https://docs.pytest.org/)
- [Google ADK 測試指南](https://cloud.google.com/generative-ai-sdk)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### 測試工具

- `pytest` - 測試框架
- `pytest-cov` - 涵蓋率測試
- `pytest-asyncio` - 非同步測試
- `pytest-xdist` - 並行測試
- `pytest-mock` - Mock 工具

### 程式碼品質

- `black` - 程式碼格式化
- `flake8` - 程式碼檢查
- `mypy` - 型別檢查
- `coverage` - 涵蓋率工具

---

## 📞 支援

如有測試相關問題，請參考：

1. 查看現有 Agent 的測試範例
2. 閱讀 pytest 官方文件
3. 查看專案的 `tests/` 目錄範例

---

**最後更新：** 2025 年 12 月 9 日
**版本：** 1.0.0
