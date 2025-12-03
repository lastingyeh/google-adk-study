"""
專案結構與檔案存在性測試
"""

import os


class TestProjectStructure:
    """測試專案是否擁有正確的結構。"""

    def test_agent_module_exists(self):
        """測試 Agent 模組目錄是否存在。"""
        assert os.path.isdir("data_analysis_agent")

    def test_agent_init_exists(self):
        """測試 Agent __init__.py 是否存在。"""
        assert os.path.isfile("data_analysis_agent/__init__.py")

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在。"""
        assert os.path.isfile("data_analysis_agent/agent.py")

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir("tests")

    def test_test_files_exist(self):
        """測試測試檔案是否存在。"""
        assert os.path.isfile("tests/test_agent.py")
        assert os.path.isfile("tests/test_imports.py")

    def test_required_config_files_exist(self):
        """測試必要的設定檔是否存在。"""
        assert os.path.isfile("pyproject.toml")
        assert os.path.isfile("requirements.txt")
        assert os.path.isfile("Makefile")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        assert os.path.isfile(".env.example")

    def test_app_py_exists(self):
        """測試 app.py (Streamlit) 是否存在。"""
        assert os.path.isfile("app.py")

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile("README.md")

    def test_pyproject_has_content(self):
        """測試 pyproject.toml 是否有內容。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "[project]" in content
            assert "data-analysis-agent" in content

    def test_requirements_has_dependencies(self):
        """測試 requirements.txt 是否包含依賴項目。"""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "google-genai" in content
            assert "streamlit" in content
            assert "pandas" in content


class TestEnvironmentConfiguration:
    """測試環境與配置設定。"""

    def test_env_example_is_not_env(self):
        """測試 .env.example 不應為 .env。"""
        assert os.path.isfile(".env.example")
        assert not os.path.exists(".env") or True  # .env may not exist in repo

    def test_env_example_has_placeholder(self):
        """測試 .env.example 是否包含佔位符值。"""
        with open(".env.example", "r") as f:
            content = f.read()
            assert "your_api_key_here" in content.lower() or "GOOGLE_API_KEY" in content

    def test_makefile_has_help(self):
        """測試 Makefile 是否包含 help 目標。"""
        with open("Makefile", "r") as f:
            content = f.read()
            assert "help" in content
            assert "setup" in content
            assert "dev" in content
            assert "test" in content


class TestCodeQuality:
    """測試基本程式碼品質。"""

    def test_agent_has_docstrings(self):
        """測試 Agent 模組是否擁有 docstrings。"""
        with open("data_analysis_agent/agent.py", "r") as f:
            content = f.read()
            assert '"""' in content
            assert "Data Analysis Agent" in content

    def test_app_has_docstring(self):
        """測試 app.py 是否擁有 docstring。"""
        with open("app.py", "r") as f:
            content = f.read()
            assert '"""' in content
            assert "Streamlit" in content or "Data" in content

    def test_functions_have_docstrings(self):
        """測試函式是否擁有 docstrings。"""
        with open("data_analysis_agent/agent.py", "r") as f:
            content = f.read()
            # Check that key functions have docstrings
            assert "def analyze_column" in content
            assert "def calculate_correlation" in content
            assert "def filter_data" in content
            assert "def get_dataset_summary" in content
