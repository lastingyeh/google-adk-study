"""
用於教學課程 06：多代理系統 - 內容發布系統的專案結構測試。
"""

import os


class TestProjectStructure:
    """測試專案檔案與目錄結構"""

    def test_content_publisher_directory_exists(self):
        """測試 `content_publisher` 目錄是否存在"""
        assert os.path.isdir("content_publisher")

    def test_init_py_exists(self):
        """測試 `__init__.py` 是否存在"""
        assert os.path.isfile("content_publisher/__init__.py")

    def test_agent_py_exists(self):
        """測試 `agent.py` 是否存在"""
        assert os.path.isfile("content_publisher/agent.py")

    def test_env_example_exists(self):
        """測試 `.env.example` 是否存在"""
        assert os.path.isfile("content_publisher/.env.example")

    def test_init_py_content(self):
        """測試 `__init__.py` 是否包含正確的匯入"""
        with open("content_publisher/__init__.py", "r") as f:
            content = f.read().strip()
            assert "from . import agent" in content

    def test_agent_py_is_python_file(self):
        """測試 `agent.py` 是否為有效的 Python 檔案"""
        with open("content_publisher/agent.py", "r") as f:
            content = f.read()
            assert "from __future__ import annotations" in content
            assert "root_agent = content_publishing_system" in content

    def test_env_example_content(self):
        """測試 `.env.example` 是否包含必要的變數"""
        with open("content_publisher/.env.example", "r") as f:
            content = f.read()
            assert "GOOGLE_GENAI_USE_VERTEXAI=FALSE" in content
            assert "GOOGLE_API_KEY=" in content


class TestTestStructure:
    """測試測試目錄與檔案結構"""

    def test_tests_directory_exists(self):
        """測試 `tests` 目錄是否存在"""
        assert os.path.isdir("tests")

    def test_tests_init_py_exists(self):
        """測試 `tests/__init__.py` 是否存在"""
        assert os.path.isfile("tests/__init__.py")

    def test_test_files_exist(self):
        """測試測試檔案是否存在"""
        assert os.path.isfile("tests/test_agent.py")
        assert os.path.isfile("tests/test_imports.py")
        assert os.path.isfile("tests/test_structure.py")
