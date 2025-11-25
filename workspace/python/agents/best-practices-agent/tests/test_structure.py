"""測試專案結構和配置。"""

import os
import pytest
from pathlib import Path


def test_project_structure():
    """測試必需的檔案和目錄是否存在。"""
    base_dir = Path(__file__).parent.parent

    # 必需的檔案
    assert (base_dir / "README.md").exists(), "README.md 缺失"
    assert (base_dir / "requirements.txt").exists(), "requirements.txt 缺失"
    assert (base_dir / "pyproject.toml").exists(), "pyproject.toml 缺失"
    assert (base_dir / "Makefile").exists(), "Makefile 缺失"
    assert (base_dir / ".env.example").exists(), ".env.example 缺失"

    # 必需的目錄
    assert (base_dir / "best_practices_agent").is_dir(), "best_practices_agent 目錄缺失"
    assert (base_dir / "tests").is_dir(), "tests 目錄缺失"

    # 代理模組檔案
    assert (base_dir / "best_practices_agent" / "__init__.py").exists()
    assert (base_dir / "best_practices_agent" / "agent.py").exists()


def test_requirements_txt():
    """測試 requirements.txt 是否包含必要的依賴。"""
    base_dir = Path(__file__).parent.parent
    requirements_file = base_dir / "requirements.txt"

    content = requirements_file.read_text()

    assert "google-genai" in content, "google-genai 未在 requirements.txt 中"
    assert "google-adk" in content, "google-adk 未在 requirements.txt 中"
    assert "pydantic" in content, "pydantic 未在 requirements.txt 中"


def test_pyproject_toml():
    """測試 pyproject.toml 是否正確配置。"""
    base_dir = Path(__file__).parent.parent
    pyproject_file = base_dir / "pyproject.toml"

    content = pyproject_file.read_text()

    assert "best_practices_agent" in content
    assert "google-genai" in content
    assert "google-adk" in content
    assert "pydantic" in content


def test_env_example():
    """測試 .env.example 是否存在且包含必需的變數。"""
    base_dir = Path(__file__).parent.parent
    env_example = base_dir / ".env.example"

    content = env_example.read_text()

    assert "GOOGLE_API_KEY" in content


def test_makefile_targets():
    """測試 Makefile 是否包含必需的目標。"""
    base_dir = Path(__file__).parent.parent
    makefile = base_dir / "Makefile"

    content = makefile.read_text()

    # 檢查基本目標
    assert "setup:" in content
    assert "dev:" in content
    assert "test:" in content
    assert "clean:" in content
    assert "demo:" in content
