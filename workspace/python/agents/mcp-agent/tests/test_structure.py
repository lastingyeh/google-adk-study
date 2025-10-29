"""
測試專案結構
"""

import os
import pytest


class TestProjectStructure:
    """測試專案是否具有必要的結構"""

    def test_mcp_agent_directory_exists(self):
        """測試 mcp_agent 目錄是否存在"""
        assert os.path.isdir("mcp_agent")

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在"""
        assert os.path.isdir("tests")

    def test_mcp_agent_init_exists(self):
        """測試 mcp_agent/__init__.py 是否存在"""
        assert os.path.isfile("mcp_agent/__init__.py")

    def test_mcp_agent_agent_exists(self):
        """測試 mcp_agent/agent.py 是否存在"""
        assert os.path.isfile("mcp_agent/agent.py")

    def test_mcp_agent_document_organizer_exists(self):
        """測試 mcp_agent/document_organizer.py 是否存在"""
        assert os.path.isfile("mcp_agent/document_organizer.py")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在"""
        assert os.path.isfile("mcp_agent/.env.example")

    def test_requirements_txt_exists(self):
        """測試 requirements.txt 是否存在"""
        assert os.path.isfile("requirements.txt")

    def test_pyproject_toml_exists(self):
        """測試 pyproject.toml 是否存在"""
        assert os.path.isfile("pyproject.toml")

    def test_makefile_exists(self):
        """測試 Makefile 是否存在"""
        assert os.path.isfile("Makefile")

    def test_readme_exists(self):
        """測試 README.md 是否存在"""
        assert os.path.isfile("README.md")

    def test_test_files_exist(self):
        """測試所有測試檔案是否存在"""
        assert os.path.isfile("tests/__init__.py")
        assert os.path.isfile("tests/test_agent.py")
        assert os.path.isfile("tests/test_imports.py")
        assert os.path.isfile("tests/test_structure.py")


class TestFileContent:
    """測試檔案是否包含必要的內容"""

    def test_mcp_agent_init_exports_root_agent(self):
        """測試 __init__.py 是否匯出 root_agent"""
        with open("mcp_agent/__init__.py", "r") as f:
            content = f.read()
            assert "root_agent" in content

    def test_agent_py_defines_root_agent(self):
        """測試 agent.py 是否定義 root_agent"""
        with open("mcp_agent/agent.py", "r") as f:
            content = f.read()
            assert "root_agent" in content
            assert "MCPToolset" in content

    def test_env_example_has_api_key(self):
        """測試 .env.example 是否有 API 金鑰的佔位符"""
        with open("mcp_agent/.env.example", "r") as f:
            content = f.read()
            assert "GOOGLE_API_KEY" in content

    def test_requirements_txt_has_google_genai(self):
        """測試 requirements.txt 是否包含 google-genai"""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "google-genai" in content

    def test_pyproject_toml_has_package_name(self):
        """測試 pyproject.toml 是否有套件名稱"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "name" in content
            assert "mcp_agent" in content or "mcp-agent" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
