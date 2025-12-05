# 教學範例 34：專案結構測試
# 驗證專案是否具有必要的檔案與結構
#
# 重點說明：
# 此測試模組驗證整個專案的檔案組織、配置檔案內容以及基本程式碼品質。
# 主要測試範圍包括：
# 1. 確認必要的目錄 (pubsub_agent, tests) 與檔案 (Makefile, pyproject.toml, README) 是否存在。
# 2. 檢查配置檔案 (requirements.txt, pyproject.toml) 是否包含正確的依賴項目與設定。
# 3. 驗證程式碼檔案 (agent.py, 測試檔) 是否符合 Python 語法且包含 Docstrings。
# 4. 確保 .env.example 格式正確且不包含真實機密資訊。
# 5. 確認 README.md 存在且內容充實。

import os
import pytest


class TestProjectStructure:
    """測試專案是否具有正確的結構。"""

    def test_pubsub_agent_directory_exists(self):
        """測試 pubsub_agent 目錄是否存在。"""
        assert os.path.isdir('pubsub_agent')

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir('tests')

    def test_pubsub_agent_init_exists(self):
        """測試 pubsub_agent/__init__.py 是否存在。"""
        assert os.path.isfile('pubsub_agent/__init__.py')

    def test_pubsub_agent_agent_module_exists(self):
        """測試 pubsub_agent/agent.py 是否存在。"""
        assert os.path.isfile('pubsub_agent/agent.py')

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        assert os.path.isfile('pubsub_agent/.env.example')

    def test_tests_init_exists(self):
        """測試 tests/__init__.py 是否存在。"""
        assert os.path.isfile('tests/__init__.py')

    def test_test_agent_module_exists(self):
        """測試 tests/test_agent.py 是否存在。"""
        assert os.path.isfile('tests/test_agent.py')

    def test_test_imports_module_exists(self):
        """測試 tests/test_imports.py 是否存在。"""
        assert os.path.isfile('tests/test_imports.py')

    def test_requirements_txt_exists(self):
        """測試 requirements.txt 是否存在。"""
        assert os.path.isfile('requirements.txt')

    def test_pyproject_toml_exists(self):
        """測試 pyproject.toml 是否存在。"""
        assert os.path.isfile('pyproject.toml')

    def test_makefile_exists(self):
        """測試 Makefile 是否存在。"""
        assert os.path.isfile('Makefile')

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile('README.md')


class TestConfigurationFiles:
    """測試設定檔案是否具有必要的內容。"""

    def test_requirements_includes_adk(self):
        """測試 requirements.txt 是否包含 google-adk。"""
        with open('requirements.txt', 'r') as f:
            content = f.read()
            assert 'google-adk' in content

    def test_requirements_includes_pubsub(self):
        """測試 requirements.txt 是否包含 google-cloud-pubsub。"""
        with open('requirements.txt', 'r') as f:
            content = f.read()
            assert 'google-cloud-pubsub' in content

    def test_pyproject_toml_valid_name(self):
        """測試 pyproject.toml 是否具有有效的套件名稱。"""
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            assert 'name = "tutorial34"' in content

    def test_pyproject_toml_has_dependencies(self):
        """測試 pyproject.toml 是否包含依賴項目。"""
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            assert 'google-adk' in content

    def test_env_example_has_api_key(self):
        """測試 .env.example 是否具有 API 金鑰預留位置。"""
        with open('pubsub_agent/.env.example', 'r') as f:
            content = f.read()
            assert 'GOOGLE_API_KEY' in content

    def test_env_example_has_gcp_project(self):
        """測試 .env.example 是否具有 GCP_PROJECT。"""
        with open('pubsub_agent/.env.example', 'r') as f:
            content = f.read()
            assert 'GCP_PROJECT' in content


class TestCodeQuality:
    """測試基本的程式碼品質標準。"""

    def test_agent_py_is_valid_python(self):
        """測試 agent.py 是否為有效的 Python 程式碼。"""
        with open('pubsub_agent/agent.py', 'r') as f:
            code = f.read()
            try:
                compile(code, 'pubsub_agent/agent.py', 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in agent.py: {e}")

    def test_agent_py_has_docstrings(self):
        """測試 agent.py 是否具有模組文件字串。"""
        with open('pubsub_agent/agent.py', 'r') as f:
            code = f.read()
            assert '"""' in code or "'''" in code

    def test_test_files_are_valid_python(self):
        """測試所有測試檔案是否為有效的 Python 程式碼。"""
        test_files = [
            'tests/test_agent.py',
            'tests/test_imports.py',
            'tests/test_structure.py'
        ]

        for test_file in test_files:
            if os.path.isfile(test_file):
                with open(test_file, 'r') as f:
                    code = f.read()
                    try:
                        compile(code, test_file, 'exec')
                    except SyntaxError as e:
                        pytest.fail(f"Syntax error in {test_file}: {e}")


class TestEnvExample:
    """測試 .env.example 檔案格式是否正確。"""

    def test_env_example_has_comments(self):
        """測試 .env.example 是否具有描述性註解。"""
        with open('pubsub_agent/.env.example', 'r') as f:
            content = f.read()
            assert '#' in content

    def test_env_example_has_no_real_secrets(self):
        """測試 .env.example 是否沒有真實的 API 金鑰。"""
        with open('pubsub_agent/.env.example', 'r') as f:
            content = f.read()
            # Should only have placeholder values like "your-api-key-here"
            # Real keys start with specific patterns
            # 應僅包含如 "your-api-key-here" 的預留位置值
            # 真實金鑰以特定模式開頭
            assert 'your-api-key-here' in content
            assert 'your-gcp-project-id' in content

    def test_env_example_not_in_env_pattern(self):
        """測試檔案名稱是否為 .env.example 而非 .env。"""
        # This prevents accidental secrets in version control
        # 這可防止意外將機密資訊納入版本控制
        assert os.path.isfile('pubsub_agent/.env.example')
        assert not os.path.isfile('pubsub_agent/.env')


class TestDocumentation:
    """測試文件檔案是否存在且具有內容。"""

    def test_readme_exists_and_has_content(self):
        """測試 README.md 是否存在且非空白。"""
        assert os.path.isfile('README.md')
        with open('README.md', 'r') as f:
            content = f.read()
            assert len(content) > 100  # Should have substantial content

    def test_readme_has_title(self):
        """測試 README 是否具有標題。"""
        with open('README.md', 'r') as f:
            content = f.read()
            assert '#' in content  # Should have at least one heading
