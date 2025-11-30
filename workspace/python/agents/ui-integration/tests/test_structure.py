"""測試教學專案的目錄結構。"""

import os
import pytest


def test_agent_directory_exists():
    """測試 `agent` 目錄是否存在。"""
    assert os.path.isdir("agent"), "應存在 `agent/` 目錄"


def test_agent_files_exist():
    """測試 `agent` 目錄中必要的檔案是否存在。"""
    assert os.path.isfile("agent/__init__.py"), "應存在 `agent/__init__.py` 檔案"
    assert os.path.isfile("agent/agent.py"), "應存在 `agent/agent.py` 檔案"
    assert os.path.isfile("agent/.env.example"), "應存在 `agent/.env.example` 檔案"


def test_frontend_directory_exists():
    """測試 `frontend` 目錄是否存在。"""
    assert os.path.isdir("frontend"), "應存在 `frontend/` 目錄"


def test_tests_directory_exists():
    """測試 `tests` 目錄是否存在。"""
    assert os.path.isdir("tests"), "應存在 `tests/` 目錄"


def test_root_files_exist():
    """測試根目錄中必要的檔案是否存在。"""
    assert os.path.isfile("requirements.txt"), "應存在 `requirements.txt` 檔案"
    assert os.path.isfile("pyproject.toml"), "應存在 `pyproject.toml` 檔案"
    assert os.path.isfile("Makefile"), "應存在 `Makefile` 檔案"
    assert os.path.isfile("README.md"), "應存在 `README.md` 檔案"


def test_env_example_content():
    """測試 `.env.example` 檔案是否包含必要的變數。"""
    with open("agent/.env.example", "r") as f:
        content = f.read()
        assert "GOOGLE_API_KEY" in content, "`.env.example` 檔案應包含 `GOOGLE_API_KEY`"


def test_requirements_content():
    """測試 `requirements.txt` 檔案是否包含所有必要的套件。"""
    with open("requirements.txt", "r") as f:
        content = f.read()
        required_packages = [
            "google-adk",
            "fastapi",
            "uvicorn",
            "ag-ui-adk",
            "python-dotenv",
            "pytest"
        ]
        for package in required_packages:
            assert package in content, f"`requirements.txt` 應包含 `{package}`"
