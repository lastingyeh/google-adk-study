# Skills Agent 測試文件

本目錄包含 **Skills Agent** 專案的測試套件，驗證技能系統 (Skill System) 和代理人配置的正確性。

## 📋 測試結構

```
tests/
├── __init__.py           # 測試套件初始化
├── conftest.py           # Pytest 配置與共用 fixtures
├── test_imports.py       # 匯入與模組測試
├── test_structure.py     # 專案結構測試
├── test_agent.py         # 代理人與技能測試
└── README.md             # 本文件
```

## 🎯 測試涵蓋範圍

### 1. `test_imports.py` - 匯入測試

驗證所有模組和依賴項目能夠正確匯入：

- ✅ `skills_agent` 模組結構
- ✅ Google ADK 依賴項目
- ✅ Skill 和 SkillToolset 類別
- ✅ Agent 實例匯出
- ✅ 模型版本驗證 (gemini-2.5-flash)

**測試類別：**
- `TestModuleStructure` - 模組結構測試
- `TestImports` - 匯入功能測試
- `TestModuleExports` - 匯出物件測試

### 2. `test_structure.py` - 結構測試

驗證專案檔案結構的完整性：

- ✅ 必要目錄 (`skills_agent/`, `tests/`)
- ✅ 必要檔案 (`agent.py`, `pyproject.toml`, `README.md`)
- ✅ 技能目錄結構 (`skills/weather-skill/`)
- ✅ 技能定義檔案 (`SKILL.md`)
- ✅ 技能參考資料 (`references/weather_info.md`)
- ✅ 配置檔案內容 (`pyproject.toml`, `.env.example`)
- ✅ 程式碼品質 (語法正確性、docstring)
- ✅ README 內容完整性

**測試類別：**
- `TestProjectStructure` - 專案結構測試
- `TestSkillsStructure` - 技能目錄結構測試
- `TestConfigurationFiles` - 配置檔案測試
- `TestCodeFiles` - 程式碼品質測試
- `TestReadmeContent` - README 內容測試

### 3. `test_agent.py` - 代理人與技能測試

驗證代理人配置和技能系統的正確性：

#### Agent 配置測試
- ✅ Agent 實例化
- ✅ 模型設定 (gemini-2.5-flash)
- ✅ 名稱與描述
- ✅ 工具配置 (SkillToolset)

#### Greeting Skill 測試
- ✅ Skill 實例化
- ✅ Frontmatter 配置
- ✅ 指令 (Instructions)
- ✅ 資源 (Resources)
- ✅ 參考資料 (References)

#### Weather Skill 測試
- ✅ Skill 實例化
- ✅ 從目錄載入
- ✅ Frontmatter 配置
- ✅ SKILL.md 存在性

#### SkillToolset 測試
- ✅ SkillToolset 實例化
- ✅ 包含兩個技能
- ✅ 技能名稱驗證
- ✅ Agent 整合

**測試類別：**
- `TestAgentConfiguration` - Agent 配置測試
- `TestGreetingSkillConfiguration` - Greeting Skill 測試
- `TestWeatherSkillConfiguration` - Weather Skill 測試
- `TestSkillToolsetConfiguration` - SkillToolset 測試
- `TestAgentToolIntegration` - Agent 與工具整合測試

## 🚀 執行測試

### 環境準備

```bash
# 1. 進入專案目錄
cd /path/to/skills-agent

# 2. 啟動虛擬環境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 3. 安裝測試依賴（如需要）
uv add --dev pytest pytest-cov
```

### 執行方式

```bash
# 執行所有測試
pytest

# 執行特定測試檔案
pytest tests/test_imports.py
pytest tests/test_structure.py
pytest tests/test_agent.py

# 詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s

# 執行特定測試類別
pytest tests/test_agent.py::TestAgentConfiguration

# 執行特定測試函式
pytest tests/test_agent.py::TestAgentConfiguration::test_agent_name

# 使用標記執行
pytest -m unit              # 只執行單元測試
pytest -m skill             # 只執行技能相關測試
pytest -m "not slow"        # 排除緩慢的測試

# 停在第一個失敗
pytest -x

# 顯示測試涵蓋率
pytest --cov=skills_agent --cov-report=html
pytest --cov=skills_agent --cov-report=term

# 查看涵蓋率報告
open htmlcov/index.html    # macOS
# 或
xdg-open htmlcov/index.html  # Linux
```

## 📊 測試統計

### 測試數量概覽

- **test_imports.py**: ~12 測試
- **test_structure.py**: ~20 測試
- **test_agent.py**: ~30 測試
- **總計**: ~62 測試

### 涵蓋率目標

- 核心功能：≥ 90%
- 技能系統：≥ 85%
- 整體專案：≥ 80%

## 🔧 測試配置

### Pytest 標記

以下標記可用於有選擇地執行測試：

- `@pytest.mark.unit` - 單元測試
- `@pytest.mark.integration` - 整合測試
- `@pytest.mark.skill` - 技能相關測試
- `@pytest.mark.slow` - 執行緩慢的測試

### Fixtures

在 `conftest.py` 中定義的共用 fixtures：

- `test_config` - 測試配置物件
- `project_root` - 專案根目錄路徑
- `skills_dir` - 技能目錄路徑
- `weather_skill_dir` - 天氣技能目錄路徑
- `mock_skill` - 模擬的技能物件
- `reset_environment` - 測試後環境重置

## 📝 測試案例說明

### 匯入測試範例

```python
def test_skills_agent_module_exists(self):
    """測試 skills_agent 模組是否存在。"""
    import skills_agent
    assert skills_agent is not None
```

### 結構測試範例

```python
def test_weather_skill_directory_exists(self):
    """測試 weather-skill 目錄是否存在。"""
    assert os.path.isdir('skills_agent/skills/weather-skill')
```

### Agent 測試範例

```python
def test_agent_model_is_gemini_25_flash(self):
    """測試代理是否使用 gemini-2.5-flash 模型。"""
    from skills_agent.agent import root_agent
    assert root_agent.model == "gemini-2.5-flash"
```

### 技能測試範例

```python
def test_greeting_skill_has_references(self):
    """測試 greeting_skill 是否具有參考資料。"""
    from skills_agent.agent import greeting_skill
    assert 'hello_world.txt' in greeting_skill.resources.references
```

## 🐛 常見問題

### Q1: 測試執行時出現 ModuleNotFoundError

**解決方案：**
```bash
# 確保虛擬環境已啟動
source .venv/bin/activate

# 確保 skills_agent 在 Python 路徑中
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Q2: 無法匯入 google.adk 模組

**解決方案：**
```bash
# 確認 ADK 安裝
uv add git+https://github.com/google/adk-python.git@main

# 或使用 pip
pip install git+https://github.com/google/adk-python.git@main
```

### Q3: 技能載入失敗

**解決方案：**
- 檢查 `skills_agent/skills/weather-skill/SKILL.md` 是否存在
- 檢查 SKILL.md 的 frontmatter 格式是否正確
- 確認 references 目錄和檔案存在

## 🧪 詳細測試案例說明

### 1. 代理人與技能測試 (`tests/test_agent.py`)

此部分驗證代理人配置與技能系統的正確性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 配置** | **TC-AGENT-001** | 驗證 root_agent 匯入 | None | 匯入 skills_agent.agent.root_agent | None | root_agent 不為 None |
| **Agent 配置** | **TC-AGENT-002** | 驗證 Agent 實例 | root_agent 已匯入 | 檢查 root_agent 是否為 Agent 類別的實例 | None | 是 Agent 實例 |
| **Agent 配置** | **TC-AGENT-003** | 驗證代理人名稱 | root_agent 已匯入 | 檢查 root_agent.name 屬性 | None | 名稱為 "skill_user_agent" |
| **Agent 配置** | **TC-AGENT-004** | 驗證模型版本 | root_agent 已匯入 | 檢查 root_agent.model 屬性 | None | 模型為 "gemini-2.5-flash" |
| **Greeting Skill** | **TC-GSKILL-001** | 驗證問候技能名稱 | greeting_skill 已匯入 | 檢查 greeting_skill.frontmatter.name | None | 名稱為 "greeting-skill" |
| **Weather Skill** | **TC-WSKILL-001** | 驗證天氣技能載入 | 技能目錄存在 | 檢查 SKILL.md 是否存在且可讀取 | None | 技能成功從目錄載入 |
| **Toolset** | **TC-TOOLSET-001** | 驗證技能工具集數量 | my_skill_toolset 已匯入 | 檢查 toolset 中的技能數量 | None | 包含 2 個技能 |

### 2. 匯入與模組測試 (`tests/test_imports.py`)

此部分確保專案所有模組與依賴項目能正確匯入。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組結構** | **TC-IMP-001** | 驗證核心模組存在 | None | 匯入 skills_agent 模組 | None | 模組匯入成功 |
| **依賴項目** | **TC-IMP-002** | 驗證 Google ADK 匯入 | None | 從 google.adk 匯入 Agent | None | 匯入成功 |
| **模型驗證** | **TC-IMP-003** | 驗證 Gemini 模型配置 | root_agent 已匯入 | 檢查 root_agent.model | None | 為 "gemini-2.5-flash" |

### 3. 專案結構測試 (`tests/test_structure.py`)

此部分驗證專案檔案與目錄結構的完整性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **基礎結構** | **TC-STR-001** | 驗證必要目錄存在 | None | 檢查 skills_agent 與 tests 目錄 | None | 目錄皆存在 |
| **技能結構** | **TC-STR-002** | 驗證技能目錄結構 | None | 檢查 weather-skill 及其 references 目錄 | None | 目錄與必要檔案皆存在 |
| **配置檔案** | **TC-STR-003** | 驗證 pyproject.toml 內容 | 檔案存在 | 讀取檔案並檢查套件名稱與依賴 | None | 名稱為 "skills-agent" 且包含 google-adk |

---

## 📚 參考資源

- [Google ADK 文件](https://google.github.io/adk-docs/)
- [Skills for ADK agents](https://google.github.io/adk-docs/skills/)
- [Pytest 官方文件](https://docs.pytest.org/)
- [測試規範指南](../../../.github/instructions/test-specification.instructions.md)

## ✅ 測試檢查清單

執行測試前的檢查清單：

- [ ] 虛擬環境已啟動
- [ ] 依賴項目已安裝
- [ ] `GOOGLE_API_KEY` 環境變數已設定（某些測試可能需要）
- [ ] 專案結構完整
- [ ] 技能目錄存在
- [ ] SKILL.md 檔案格式正確

## 🔄 持續整合

建議在 CI/CD 流程中加入以下測試階段：

```yaml
# .github/workflows/test.yml 範例
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
      - run: pip install uv
      - run: uv sync
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

**最後更新：** 2026 年 2 月 25 日
**測試版本：** 1.0.0
**維護者：** lastingyeh
