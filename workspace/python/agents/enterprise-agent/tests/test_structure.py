"""
Tutorial 26 的測試套件：專案結構驗證。
"""

import os
import pytest


class TestProjectStructure:
    """測試專案是否包含必要的檔案和目錄。"""

    def test_enterprise_agent_directory_exists(self):
        """測試 enterprise_agent 目錄是否存在。"""
        assert os.path.isdir("enterprise_agent")

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir("tests")

    def test_enterprise_agent_init_exists(self):
        """測試 enterprise_agent/__init__.py 是否存在。"""
        assert os.path.isfile("enterprise_agent/__init__.py")

    def test_enterprise_agent_agent_exists(self):
        """測試 enterprise_agent/agent.py 是否存在。"""
        assert os.path.isfile("enterprise_agent/agent.py")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        assert os.path.isfile("enterprise_agent/.env.example")

    def test_pyproject_toml_exists(self):
        """測試 pyproject.toml 是否存在。"""
        assert os.path.isfile("pyproject.toml")

    def test_requirements_txt_exists(self):
        """測試 requirements.txt 是否存在。"""
        assert os.path.isfile("requirements.txt")

    def test_makefile_exists(self):
        """測試 Makefile 是否存在。"""
        assert os.path.isfile("Makefile")

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile("README.md")


class TestTestFiles:
    """測試所有必要的測試檔案是否存在。"""

    def test_tests_init_exists(self):
        """測試 tests/__init__.py 是否存在。"""
        assert os.path.isfile("tests/__init__.py")

    def test_test_agent_exists(self):
        """測試 test_agent.py 是否存在。"""
        assert os.path.isfile("tests/test_agent.py")

    def test_test_tools_exists(self):
        """測試 test_tools.py 是否存在。"""
        assert os.path.isfile("tests/test_tools.py")

    def test_test_imports_exists(self):
        """測試 test_imports.py 是否存在。"""
        assert os.path.isfile("tests/test_imports.py")

    def test_test_structure_exists(self):
        """測試 test_structure.py 是否存在。"""
        assert os.path.isfile("tests/test_structure.py")


class TestFileContent:
    """測試關鍵檔案是否包含預期內容。"""

    def test_pyproject_toml_has_name(self):
        """測試 pyproject.toml 是否定義了專案名稱。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
        assert "name" in content
        assert "tutorial26" in content.lower()

    def test_requirements_has_adk(self):
        """測試 requirements.txt 是否包含 google-adk。"""
        with open("requirements.txt", "r") as f:
            content = f.read()
        assert "google-adk" in content.lower()

    def test_makefile_has_targets(self):
        """測試 Makefile 是否包含標準目標。"""
        with open("Makefile", "r") as f:
            content = f.read()
        assert "setup:" in content
        assert "test:" in content
        assert "dev:" in content
        assert "clean:" in content

    def test_readme_has_tutorial_info(self):
        """測試 README.md 是否包含教學資訊。"""
        with open("README.md", "r") as f:
            content = f.read()
        assert "Tutorial 26" in content or "tutorial 26" in content.lower()

    def test_env_example_has_api_key(self):
        """測試 .env.example 是否有 API 金鑰佔位符。"""
        with open("enterprise_agent/.env.example", "r") as f:
            content = f.read()
        assert "GOOGLE_API_KEY" in content
        assert "GOOGLE_GENAI_USE_VERTEXAI" in content
