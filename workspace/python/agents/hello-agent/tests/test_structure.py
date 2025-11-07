# 教學 01: Hello World Agent - 結構測試
# 驗證專案結構是否符合 ADK 的慣例

import os


class TestProjectStructure:
    """測試專案是否遵循必要的 ADK 結構。"""

    def test_hello_agent_directory_exists(self):
        """測試 hello_agent 目錄是否存在。"""
        assert os.path.isdir('hello_agent'), "找不到 hello_agent 目錄"

    def test_init_py_exists(self):
        """測試 hello_agent 中是否存在 __init__.py。"""
        init_file = os.path.join('hello_agent', '__init__.py')
        assert os.path.isfile(init_file), "在 hello_agent 中找不到 __init__.py"

    def test_agent_py_exists(self):
        """測試 hello_agent 中是否存在 agent.py。"""
        agent_file = os.path.join('hello_agent', 'agent.py')
        assert os.path.isfile(agent_file), "在 hello_agent 中找不到 agent.py"

    def test_env_example_exists(self):
        """測試 hello_agent 中是否存在 .env.example。"""
        env_file = os.path.join('hello_agent', '.env.example')
        assert os.path.isfile(env_file), "在 hello_agent 中找不到 .env.example"

    def test_init_py_content(self):
        """測試 __init__.py 的內容是否正確。"""
        init_file = os.path.join('hello_agent', '__init__.py')
        with open(init_file, 'r') as f:
            content = f.read().strip()

        assert content == "from . import agent", f"__init__.py 內容不正確: {content}"

    def test_agent_py_is_python_file(self):
        """測試 agent.py 是否為有效的 Python 檔案。"""
        agent_file = os.path.join('hello_agent', 'agent.py')

        # 應該是可讀的
        with open(agent_file, 'r') as f:
            content = f.read()

        assert len(content) > 0, "agent.py 是空的"

        # 應該包含 Python 程式碼
        assert "from __future__ import annotations" in content, "agent.py 應包含 __future__ 匯入"
        assert "from google.adk.agents import Agent" in content, "agent.py 應匯入 Agent"
        assert "root_agent = Agent(" in content, "agent.py 應定義 root_agent"

    def test_env_example_content(self):
        """測試 .env.example 是否包含必要的設定。"""
        env_file = os.path.join('hello_agent', '.env.example')
        with open(env_file, 'r') as f:
            content = f.read()

        # 應該包含必要的環境變數
        assert "GOOGLE_GENAI_USE_VERTEXAI=FALSE" in content, ".env.example 應包含 GOOGLE_GENAI_USE_VERTEXAI"
        assert "GOOGLE_API_KEY=" in content, ".env.example 應包含 GOOGLE_API_KEY"
        assert "# Get your free API key" in content, ".env.example 應包含 API 金鑰的說明"


class TestTestStructure:
    """測試測試目錄結構是否正確。"""

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir('tests'), "找不到 tests 目錄"

    def test_tests_init_py_exists(self):
        """測試 tests/__init__.py 是否存在。"""
        init_file = os.path.join('tests', '__init__.py')
        assert os.path.isfile(init_file), "找不到 tests/__init__.py"

    def test_test_files_exist(self):
        """測試所有測試檔案是否存在。"""
        test_files = [
            'test_agent.py',
            'test_imports.py',
            'test_structure.py'
        ]

        for test_file in test_files:
            file_path = os.path.join('tests', test_file)
            assert os.path.isfile(file_path), f"在 tests/ 中找不到 {test_file}"


class TestRootFiles:
    """測試根層級檔案是否存在。"""

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile('README.md'), "找不到 README.md"

    def test_makefile_exists(self):
        """測試 Makefile 是否存在。"""
        assert os.path.isfile('Makefile'), "找不到 Makefile"

    def test_requirements_exists(self):
        """測試 requirements.txt 是否存在。"""
        assert os.path.isfile('requirements.txt'), "找不到 requirements.txt"

    def test_readme_content(self):
        """測試 README.md 是否有基本內容。"""
        with open('README.md', 'r') as f:
            content = f.read()

        assert len(content) > 100, "README.md 內容似乎太短"
        assert "Tutorial 01" in content, "README.md 應包含 'Tutorial 01'"
        assert "Hello World Agent" in content, "README.md 應包含 'Hello World Agent'"

    def test_makefile_content(self):
        """測試 Makefile 是否有基本的目標。"""
        with open('Makefile', 'r') as f:
            content = f.read()

        assert "help:" in content, "Makefile 應包含 help 目標"
        assert "setup:" in content, "Makefile 應包含 setup 目標"
        assert "test:" in content, "Makefile 應包含 test 目標"
        assert "dev:" in content, "Makefile 應包含 dev 目標"

    def test_requirements_content(self):
        """測試 requirements.txt 是否包含 ADK。"""
        with open('requirements.txt', 'r') as f:
            content = f.read()

        assert "google-adk" in content, "在 requirements.txt 中找不到 google-adk"
