"""
專案結構驗證測試
"""

import os


class TestProjectStructure:
    """測試專案結構是否正確"""

    def test_chuck_norris_agent_directory_exists(self):
        """測試 chuck_norris_agent 目錄是否存在"""
        assert os.path.isdir("chuck_norris_agent")

    def test_init_py_exists(self):
        """測試 chuck_norris_agent/__init__.py 是否存在"""
        assert os.path.isfile("chuck_norris_agent/__init__.py")

    def test_agent_py_exists(self):
        """測試 chuck_norris_agent/agent.py 是否存在"""
        assert os.path.isfile("chuck_norris_agent/agent.py")

    def test_env_example_exists(self):
        """測試 chuck_norris_agent/.env.example 是否存在"""
        assert os.path.isfile("chuck_norris_agent/.env.example")

    def test_init_py_content(self):
        """測試 __init__.py 的內容是否正確"""
        with open("chuck_norris_agent/__init__.py", "r") as f:
            content = f.read().strip()
        assert "from .agent import root_agent" in content
        assert "__all__ = ['root_agent']" in content

    def test_agent_py_is_python_file(self):
        """測試 agent.py 是否為有效的 Python 檔案"""
        with open("chuck_norris_agent/agent.py", "r") as f:
            content = f.read()
        assert "from __future__ import annotations" in content
        assert "from google.adk.agents import Agent" in content
        assert "root_agent = Agent(" in content

    def test_env_example_content(self):
        """測試 .env.example 是否包含必要的變數"""
        with open("chuck_norris_agent/.env.example", "r") as f:
            content = f.read()
        assert "GOOGLE_GENAI_USE_VERTEXAI=FALSE" in content
        assert "GOOGLE_API_KEY=" in content


class TestTestStructure:
    """測試測試結構是否正確"""

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在"""
        assert os.path.isdir("tests")

    def test_tests_init_py_exists(self):
        """測試 tests/__init__.py 是否存在"""
        assert os.path.isfile("tests/__init__.py")

    def test_test_files_exist(self):
        """測試所有必要的測試檔案是否存在"""
        required_files = [
            "tests/test_agent.py",
            "tests/test_imports.py",
            "tests/test_structure.py",
        ]
        for file_path in required_files:
            assert os.path.isfile(file_path), f"遺失測試檔案：{file_path}"


class TestRootFiles:
    """測試根目錄級別的檔案是否存在且內容正確"""

    def test_readme_exists(self):
        """測試 README.md 是否存在"""
        assert os.path.isfile("README.md")

    def test_makefile_exists(self):
        """測試 Makefile 是否存在"""
        assert os.path.isfile("Makefile")

    def test_requirements_exists(self):
        """測試 requirements.txt 是否存在"""
        assert os.path.isfile("requirements.txt")

    def test_readme_content(self):
        """測試 README.md 是否有基本內容"""
        with open("README.md", "r") as f:
            content = f.read()
        assert "Chuck Norris" in content
        assert "OpenAPI" in content

    def test_makefile_content(self):
        """測試 Makefile 是否有基本的目標"""
        with open("Makefile", "r") as f:
            content = f.read()
        assert "setup:" in content
        assert "dev:" in content
        assert "test:" in content

    def test_requirements_content(self):
        """測試 requirements.txt 是否包含 google-adk"""
        with open("requirements.txt", "r") as f:
            content = f.read()
        assert "google-adk" in content
