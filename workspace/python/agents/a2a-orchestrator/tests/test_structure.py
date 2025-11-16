"""
測試專案結構

**重點說明：**
- 測試專案結構及必要檔案是否存在。
- 確保 `pyproject.toml`、`requirements.txt` 等設定檔存在且內容正確。
- 驗證 Agent 目錄結構及 `__init__.py` 的匯入設定。
"""

import os


class TestProjectStructure:
    """測試專案是否具有必要的結構與檔案。"""

    def test_pyproject_toml_exists(self):
        """測試 `pyproject.toml` 是否存在。"""
        assert os.path.exists("pyproject.toml"), "pyproject.toml not found"

    def test_requirements_txt_exists(self):
        """測試 `requirements.txt` 是否存在。"""
        assert os.path.exists("requirements.txt"), "requirements.txt not found"

    def test_agent_directory_exists(self):
        """測試 Agent 目錄是否存在。"""
        assert os.path.exists(
            "a2a_orchestrator"
        ), "a2a_orchestrator directory not found"

    def test_agent_init_exists(self):
        """測試 `__init__.py` 是否存在於 Agent 目錄中。"""
        init_file = os.path.join("a2a_orchestrator", "__init__.py")
        assert os.path.exists(init_file), "__init__.py not found in a2a_orchestrator"

    def test_agent_py_exists(self):
        """測試 `agent.py` 是否存在。"""
        agent_file = os.path.join("a2a_orchestrator", "agent.py")
        assert os.path.exists(agent_file), "agent.py not found"

    def test_env_example_exists(self):
        """測試 `.env.example` 是否存在。"""
        env_file = os.path.join("a2a_orchestrator", ".env.example")
        assert os.path.exists(env_file), ".env.example not found"

    def test_tests_directory_exists(self):
        """測試 `tests` 目錄是否存在。"""
        assert os.path.exists("tests"), "tests directory not found"

    def test_test_files_exist(self):
        """測試測試檔案是否存在。"""
        test_files = ["test_agent.py", "test_imports.py", "test_structure.py"]
        for test_file in test_files:
            test_path = os.path.join("tests", test_file)
            assert os.path.exists(test_path), f"{test_file} not found"

    def test_init_imports_root_agent(self):
        """測試 `__init__.py` 是否正確匯入 `root_agent`。"""
        init_file = os.path.join("a2a_orchestrator", "__init__.py")
        with open(init_file, "r") as f:
            content = f.read()

        assert (
            "from .agent import root_agent" in content
        ), "__init__.py doesn't import root_agent"
        assert (
            "__all__ = ['root_agent']" in content
        ), "__init__.py doesn't export root_agent"

    def test_pyproject_has_correct_name(self):
        """測試 `pyproject.toml` 是否有正確的專案名稱。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()

        assert (
            'name = "tutorial17"' in content
        ), "pyproject.toml doesn't have correct name"

    def test_requirements_has_adk(self):
        """測試 `requirements.txt` 是否包含 `google-adk`。"""
        with open("requirements.txt", "r") as f:
            content = f.read()

        assert "google-adk" in content, "requirements.txt doesn't include google-adk"

    def test_env_example_has_required_vars(self):
        """測試 `.env.example` 是否包含必要的環境變數。"""
        env_file = os.path.join("a2a_orchestrator", ".env.example")
        with open(env_file, "r") as f:
            content = f.read()

        required_vars = [
            "GOOGLE_GENAI_USE_VERTEXAI",
            "GOOGLE_API_KEY",
            "RESEARCH_AGENT_TOKEN",
            "ANALYSIS_AGENT_TOKEN",
            "CONTENT_AGENT_TOKEN",
        ]

        for var in required_vars:
            assert var in content, f".env.example missing {var}"
