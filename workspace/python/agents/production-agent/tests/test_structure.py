"""測試專案結構和必要檔案。"""

import os
from pathlib import Path


def test_project_structure():
    """測試所有必要檔案和目錄是否存在。"""
    project_root = Path(__file__).parent.parent

    # 必要檔案
    required_files = [
        "production_agent/__init__.py",
        "production_agent/agent.py",
        "production_agent/server.py",
        "requirements.txt",
        "pyproject.toml",
        "Makefile",
        "README.md",
        ".env.example",
    ]

    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"缺少必要檔案: {file_path}"


def test_required_directories():
    """測試必要目錄是否存在。"""
    project_root = Path(__file__).parent.parent

    required_dirs = [
        "production_agent",
        "tests",
    ]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        assert full_path.is_dir(), f"缺少必要目錄: {dir_path}"


def test_env_example_format():
    """測試 .env.example 格式是否正確。"""
    project_root = Path(__file__).parent.parent
    env_example = project_root / ".env.example"

    content = env_example.read_text()

    # 檢查重要的環境變數
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_API_KEY",
        "MODEL",
    ]

    for var in required_vars:
        assert var in content, f".env.example 中缺少環境變數: {var}"


def test_requirements_file():
    """測試 requirements.txt 是否包含必要的套件。"""
    project_root = Path(__file__).parent.parent
    requirements = project_root / "requirements.txt"

    content = requirements.read_text()

    # 檢查關鍵套件
    required_packages = [
        "google-genai",
        "fastapi",
        "uvicorn",
        "pytest",
    ]

    for package in required_packages:
        assert package in content, f"requirements.txt 中缺少套件: {package}"


def test_pyproject_toml():
    """測試 pyproject.toml 是否正確設定。"""
    project_root = Path(__file__).parent.parent
    pyproject = project_root / "pyproject.toml"

    content = pyproject.read_text()

    # 檢查重要區段
    assert "[project]" in content
    assert 'name = "production_agent"' in content
    assert "google-genai" in content


def test_makefile_targets():
    """測試 Makefile 是否有必要的目標。"""
    project_root = Path(__file__).parent.parent
    makefile = project_root / "Makefile"

    content = makefile.read_text()

    # 檢查必要目標
    required_targets = [
        "setup:",
        "dev:",
        "test:",
        "demo:",
        "clean:",
    ]

    for target in required_targets:
        assert target in content, f"Makefile 缺少目標: {target}"
