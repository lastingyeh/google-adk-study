"""
測試專案結構與設定。
"""

import os
import pytest
from pathlib import Path


class TestProjectStructure:
    """測試專案結構是否正確。"""

    def test_project_root_exists(self):
        """測試專案根目錄是否存在。"""
        root_dir = Path(__file__).parent.parent
        assert root_dir.exists()
        assert root_dir.is_dir()

    def test_observability_plugins_agent_package_exists(self):
        """測試 observability_plugins_agent 套件是否存在。"""
        root_dir = Path(__file__).parent.parent
        agent_dir = root_dir / "observability_plugins_agent"
        assert agent_dir.exists()
        assert agent_dir.is_dir()

    def test_init_files_exist(self):
        """測試 __init__.py 檔案是否存在。"""
        root_dir = Path(__file__).parent.parent
        assert (root_dir / "observability_plugins_agent" / "__init__.py").exists()
        assert (root_dir / "tests" / "__init__.py").exists()

    def test_agent_file_exists(self):
        """測試 agent.py 檔案是否存在。"""
        root_dir = Path(__file__).parent.parent
        agent_file = root_dir / "observability_plugins_agent" / "agent.py"
        assert agent_file.exists()
        assert agent_file.is_file()

    def test_config_files_exist(self):
        """測試設定檔是否存在。"""
        root_dir = Path(__file__).parent.parent
        required_files = [
            "pyproject.toml",
            "requirements.txt",
            "Makefile",
            ".env.example"
        ]
        for filename in required_files:
            file_path = root_dir / filename
            assert file_path.exists(), f"必要檔案 {filename} 不存在"
            assert file_path.is_file(), f"{filename} 不是一個檔案"

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        root_dir = Path(__file__).parent.parent
        readme = root_dir / "README.md"
        assert readme.exists()
        assert readme.is_file()

    def test_env_example_not_committed(self):
        """測試 .env 檔案未被提交 (僅 .env.example 應該存在)。"""
        root_dir = Path(__file__).parent.parent
        env_file = root_dir / ".env"
        env_example = root_dir / ".env.example"

        assert env_example.exists(), ".env.example 應該存在"
        # .env 不應該存在於儲存庫 (僅 .env.example)
        # 注意：在本地開發環境中 .env 可能存在，此測試主要用於 CI/CD 環境檢查，
        # 或者確保我們不會意外地在測試環境中依賴 .env
        # 這裡的邏輯是檢查 .env 是否存在，但在這個環境下我們可能需要調整邏輯，
        # 因為使用者可能已經建立了 .env。
        # 為了符合原始測試意圖，我們保留此斷言，但在實際開發中可能需要忽略此錯誤。
        assert not env_file.exists(), ".env 不應該被提交 - 請使用 .env.example 作為範本"

    def test_makefile_is_executable_conceptually(self):
        """測試 Makefile 在概念上是否可執行 (可讀)。"""
        root_dir = Path(__file__).parent.parent
        makefile = root_dir / "Makefile"
        assert makefile.exists()
        # 在 Unix 類系統上，檢查是否可讀
        assert os.access(makefile, os.R_OK), "Makefile 應該是可讀的"

    def test_requirements_format(self):
        """測試 requirements.txt 格式是否有效。"""
        root_dir = Path(__file__).parent.parent
        req_file = root_dir / "requirements.txt"

        with open(req_file, 'r') as f:
            content = f.read().strip()

        assert content, "requirements.txt 不應為空"

        # 檢查是否包含預期的套件
        lines = content.split('\n')
        package_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

        # 應該包含 google-genai 和 google-adk
        package_names = [line.split('>=')[0].split('==')[0].strip() for line in package_lines]
        assert "google-genai" in package_names, "requirements.txt 應該包含 google-genai"
        assert "google-adk" in package_names, "requirements.txt 應該包含 google-adk"

    def test_pyproject_toml_format(self):
        """測試 pyproject.toml 格式是否有效。"""
        root_dir = Path(__file__).parent.parent
        toml_file = root_dir / "pyproject.toml"

        with open(toml_file, 'r') as f:
            content = f.read()

        assert "[build-system]" in content, "pyproject.toml 應該有 build-system 區段"
        assert "[project]" in content, "pyproject.toml 應該有 project 區段"
        assert "name = \"observability_plugins_agent\"" in content, "pyproject.toml 應該定義 observability_plugins_agent 套件"
        assert "google-genai" in content, "pyproject.toml 應該包含 google-genai 依賴"
        assert "google-adk" in content, "pyproject.toml 應該包含 google-adk 依賴"
