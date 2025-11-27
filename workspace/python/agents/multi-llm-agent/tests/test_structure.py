# 教學 28：使用其他 LLM - 結構測試
# 驗證專案結構與設定

import pytest
import os
from pathlib import Path


class TestProjectStructure:
    """測試專案是否擁有正確的結構。"""

    def test_project_root_exists(self):
        """測試專案根目錄是否存在。"""
        project_root = Path(__file__).parent.parent
        assert project_root.exists()
        assert project_root.is_dir()

    def test_agent_package_exists(self):
        """測試 agent 套件是否存在。"""
        project_root = Path(__file__).parent.parent
        agent_dir = project_root / "multi_llm_agent"
        assert agent_dir.exists()
        assert agent_dir.is_dir()

    def test_agent_init_exists(self):
        """測試 agent __init__.py 檔案是否存在。"""
        project_root = Path(__file__).parent.parent
        init_file = project_root / "multi_llm_agent" / "__init__.py"
        assert init_file.exists()
        assert init_file.is_file()

    def test_agent_file_exists(self):
        """測試 agent.py 檔案是否存在。"""
        project_root = Path(__file__).parent.parent
        agent_file = project_root / "multi_llm_agent" / "agent.py"
        assert agent_file.exists()
        assert agent_file.is_file()

    def test_env_example_exists(self):
        """測試 .env.example 檔案是否存在。"""
        project_root = Path(__file__).parent.parent
        env_example = project_root / "multi_llm_agent" / ".env.example"
        assert env_example.exists()
        assert env_example.is_file()

    def test_requirements_exists(self):
        """測試 requirements.txt 檔案是否存在。"""
        project_root = Path(__file__).parent.parent
        requirements = project_root / "requirements.txt"
        assert requirements.exists()
        assert requirements.is_file()

    def test_pyproject_exists(self):
        """測試 pyproject.toml 檔案是否存在。"""
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        assert pyproject.exists()
        assert pyproject.is_file()

    def test_makefile_exists(self):
        """測試 Makefile 檔案是否存在。"""
        project_root = Path(__file__).parent.parent
        makefile = project_root / "Makefile"
        assert makefile.exists()
        assert makefile.is_file()

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        project_root = Path(__file__).parent.parent
        tests_dir = project_root / "tests"
        assert tests_dir.exists()
        assert tests_dir.is_dir()

    def test_readme_exists(self):
        """測試 README.md 檔案是否存在。"""
        project_root = Path(__file__).parent.parent
        readme = project_root / "README.md"
        assert readme.exists()
        assert readme.is_file()


class TestConfiguration:
    """測試設定檔。"""

    def test_requirements_has_adk(self):
        """測試 requirements.txt 檔案是否包含 google-adk。"""
        project_root = Path(__file__).parent.parent
        requirements = project_root / "requirements.txt"
        content = requirements.read_text()
        assert "google-adk" in content

    def test_requirements_has_litellm(self):
        """測試 requirements.txt 檔案是否包含 litellm。"""
        project_root = Path(__file__).parent.parent
        requirements = project_root / "requirements.txt"
        content = requirements.read_text()
        assert "litellm" in content

    def test_requirements_has_openai(self):
        """測試 requirements.txt 檔案是否包含 openai。"""
        project_root = Path(__file__).parent.parent
        requirements = project_root / "requirements.txt"
        content = requirements.read_text()
        assert "openai" in content

    def test_requirements_has_anthropic(self):
        """測試 requirements.txt 檔案是否包含 anthropic。"""
        project_root = Path(__file__).parent.parent
        requirements = project_root / "requirements.txt"
        content = requirements.read_text()
        assert "anthropic" in content

    def test_pyproject_has_correct_name(self):
        """測試 pyproject.toml 檔案是否擁有正確的套件名稱。"""
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text()
        assert 'name = "tutorial28"' in content

    def test_env_example_has_all_keys(self):
        """測試 .env.example 檔案是否擁有所有必要的金鑰範本。"""
        project_root = Path(__file__).parent.parent
        env_example = project_root / "multi_llm_agent" / ".env.example"
        content = env_example.read_text()

        assert "GOOGLE_API_KEY" in content
        assert "OPENAI_API_KEY" in content
        assert "ANTHROPIC_API_KEY" in content
        assert "OLLAMA_API_BASE" in content
