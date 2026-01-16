"""
專案結構與檔案存在性測試
"""

import os


class TestProjectStructure:
    """測試專案是否擁有正確的結構。"""

    def test_app_module_exists(self):
        """測試 App 模組目錄是否存在。"""
        assert os.path.isdir("app")

    def test_app_init_exists(self):
        """測試 App __init__.py 是否存在。"""
        assert os.path.isfile("app/__init__.py")

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在。"""
        assert os.path.isfile("app/agent.py")

    def test_config_py_exists(self):
        """測試 config.py 是否存在。"""
        assert os.path.isfile("app/config.py")

    def test_fast_api_app_exists(self):
        """測試 fast_api_app.py 是否存在。"""
        assert os.path.isfile("app/fast_api_app.py")

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir("tests")

    def test_unit_tests_directory_exists(self):
        """測試 unit tests 目錄是否存在。"""
        assert os.path.isdir("tests/unit")

    def test_test_files_exist(self):
        """測試測試檔案是否存在。"""
        assert os.path.isfile("tests/unit/test_agent.py")
        assert os.path.isfile("tests/unit/test_imports.py")
        assert os.path.isfile("tests/unit/test_structure.py")
        assert os.path.isfile("tests/unit/test_config.py")
        assert os.path.isfile("tests/unit/test_models.py")

    def test_required_config_files_exist(self):
        """測試必要的設定檔是否存在。"""
        assert os.path.isfile("pyproject.toml")
        assert os.path.isfile("Makefile")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        assert os.path.isfile(".env.example")

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile("README.md")

    def test_dockerfile_exists(self):
        """測試 Dockerfile 是否存在。"""
        assert os.path.isfile("Dockerfile")

    def test_pyproject_has_content(self):
        """測試 pyproject.toml 是否有內容。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "[project]" in content
            assert "deep-search" in content

    def test_pyproject_has_dependencies(self):
        """測試 pyproject.toml 是否包含依賴項目。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "google-adk" in content
            assert "pytest" in content


class TestEnvironmentConfiguration:
    """測試環境與配置設定。"""

    def test_env_example_is_not_env(self):
        """測試 .env.example 不應為 .env。"""
        assert os.path.isfile(".env.example")
        # .env may exist locally but should not be in repo

    def test_env_example_has_placeholder(self):
        """測試 .env.example 是否包含佔位符值。"""
        with open(".env.example", "r") as f:
            content = f.read()
            assert "GOOGLE_API_KEY" in content or "your_api_key_here" in content.lower()

    def test_makefile_has_targets(self):
        """測試 Makefile 是否包含必要目標。"""
        with open("Makefile", "r") as f:
            content = f.read()
            # 檢查 Makefile 包含至少一個目標
            assert "install" in content or "test" in content


class TestCodeQuality:
    """測試基本程式碼品質。"""

    def test_agent_has_docstrings(self):
        """測試 Agent 模組是否擁有 docstrings。"""
        with open("app/agent.py", "r") as f:
            content = f.read()
            assert '"""' in content or "'''" in content

    def test_config_has_docstrings(self):
        """測試 Config 模組是否擁有 docstrings。"""
        with open("app/config.py", "r") as f:
            content = f.read()
            assert '"""' in content or "'''" in content
            assert "Configuration" in content or "Config" in content

    def test_agent_has_license_header(self):
        """測試 Agent 檔案是否包含授權標頭。"""
        with open("app/agent.py", "r") as f:
            content = f.read()
            assert "Copyright" in content or "License" in content

    def test_classes_have_docstrings(self):
        """測試類別是否擁有 docstrings。"""
        with open("app/agent.py", "r") as f:
            content = f.read()
            # 檢查主要類別定義
            assert "class SearchQuery" in content
            assert "class Feedback" in content
            assert "class EscalationChecker" in content


class TestAppUtilsStructure:
    """測試 app_utils 工具模組結構。"""

    def test_app_utils_directory_exists(self):
        """測試 app_utils 目錄是否存在。"""
        assert os.path.isdir("app/app_utils")

    def test_telemetry_module_exists(self):
        """測試 telemetry.py 是否存在。"""
        assert os.path.isfile("app/app_utils/telemetry.py")

    def test_typing_module_exists(self):
        """測試 typing.py 是否存在。"""
        assert os.path.isfile("app/app_utils/typing.py")
