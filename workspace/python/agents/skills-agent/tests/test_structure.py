# 技能代理人測試：專案結構測試
# 驗證專案是否具有必要的檔案與結構
#
# 重點說明：
# 此測試模組驗證整個專案的檔案組織、配置檔案內容以及基本程式碼品質。
# 主要測試範圍包括：
# 1. 確認必要的目錄 (skills_agent, tests) 與檔案 (pyproject.toml, README) 是否存在。
# 2. 檢查配置檔案 (pyproject.toml) 是否包含正確的依賴項目與設定。
# 3. 驗證程式碼檔案 (agent.py, 測試檔) 是否符合 Python 語法。
# 4. 確保 .env.example 格式正確且不包含真實機密資訊。
# 5. 確認 README.md 存在且內容充實。
# 6. 驗證技能目錄結構的完整性 (skills/)。

import os
import pytest


class TestProjectStructure:
    """測試專案是否具有正確的結構。"""

    def test_skills_agent_directory_exists(self):
        """測試 skills_agent 目錄是否存在。"""
        assert os.path.isdir('skills_agent')

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir('tests')

    def test_skills_agent_init_exists(self):
        """測試 skills_agent/__init__.py 是否存在。"""
        assert os.path.isfile('skills_agent/__init__.py')

    def test_skills_agent_agent_module_exists(self):
        """測試 skills_agent/agent.py 是否存在。"""
        assert os.path.isfile('skills_agent/agent.py')

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        assert os.path.isfile('.env.example')

    def test_tests_init_exists(self):
        """測試 tests/__init__.py 是否存在。"""
        assert os.path.isfile('tests/__init__.py')

    def test_test_agent_module_exists(self):
        """測試 tests/test_agent.py 是否存在。"""
        assert os.path.isfile('tests/test_agent.py')

    def test_test_imports_module_exists(self):
        """測試 tests/test_imports.py 是否存在。"""
        assert os.path.isfile('tests/test_imports.py')

    def test_pyproject_toml_exists(self):
        """測試 pyproject.toml 是否存在。"""
        assert os.path.isfile('pyproject.toml')

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile('README.md')

    def test_skills_directory_exists(self):
        """測試 skills 目錄是否存在。"""
        assert os.path.isdir('skills_agent/skills')


class TestSkillsStructure:
    """測試技能 (Skills) 目錄結構。"""

    def test_weather_skill_directory_exists(self):
        """測試 weather-skill 目錄是否存在。"""
        assert os.path.isdir('skills_agent/skills/weather-skill')

    def test_weather_skill_md_exists(self):
        """測試 weather-skill/SKILL.md 是否存在。"""
        assert os.path.isfile('skills_agent/skills/weather-skill/SKILL.md')

    def test_weather_skill_references_directory_exists(self):
        """測試 weather-skill/references 目錄是否存在。"""
        assert os.path.isdir('skills_agent/skills/weather-skill/references')

    def test_weather_skill_references_md_exists(self):
        """測試 weather-skill/references/weather_info.md 是否存在。"""
        assert os.path.isfile('skills_agent/skills/weather-skill/references/weather_info.md')


class TestConfigurationFiles:
    """測試設定檔案是否具有必要的內容。"""

    def test_pyproject_toml_valid_name(self):
        """測試 pyproject.toml 是否具有有效的套件名稱。"""
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            assert 'name = "skills-agent"' in content

    def test_pyproject_toml_has_dependencies(self):
        """測試 pyproject.toml 是否包含 google-adk 依賴項目。"""
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            assert 'google-adk' in content

    def test_env_example_has_api_key(self):
        """測試 .env.example 是否具有 API 金鑰預留位置。"""
        with open('.env.example', 'r') as f:
            content = f.read()
            assert 'GOOGLE_API_KEY' in content

    def test_env_example_no_real_credentials(self):
        """測試 .env.example 沒有包含真實的憑證。"""
        with open('.env.example', 'r') as f:
            content = f.read()
            # 確保沒有真實的 API 金鑰格式
            assert 'your_api_key_here' in content.lower() or 'xxx' in content.lower()


class TestCodeFiles:
    """測試程式碼檔案的基本品質。"""

    def test_agent_py_is_valid_python(self):
        """測試 agent.py 是否為有效的 Python 檔案。"""
        try:
            with open('skills_agent/agent.py', 'r') as f:
                code = f.read()
                compile(code, 'skills_agent/agent.py', 'exec')
        except SyntaxError as e:
            pytest.fail(f"agent.py 包含語法錯誤：{e}")

    def test_agent_py_has_docstring(self):
        """測試 agent.py 是否包含 docstring。"""
        with open('skills_agent/agent.py', 'r') as f:
            content = f.read()
            assert '"""' in content or "'''" in content

    def test_agent_py_imports_adk(self):
        """測試 agent.py 是否匯入 ADK 模組。"""
        with open('skills_agent/agent.py', 'r') as f:
            content = f.read()
            assert 'from google.adk import Agent' in content or 'import google.adk' in content


class TestReadmeContent:
    """測試 README.md 內容完整性。"""

    def test_readme_not_empty(self):
        """測試 README.md 不為空。"""
        with open('README.md', 'r') as f:
            content = f.read()
            assert len(content) > 100

    def test_readme_has_title(self):
        """測試 README.md 包含標題。"""
        with open('README.md', 'r') as f:
            content = f.read()
            assert '# ' in content

    def test_readme_mentions_skills(self):
        """測試 README.md 提到技能相關內容。"""
        with open('README.md', 'r') as f:
            content = f.read().lower()
            assert 'skill' in content
