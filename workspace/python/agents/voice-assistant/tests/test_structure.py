"""
測試專案結構
驗證專案中必要的檔案與目錄是否存在，確保結構完整性。
"""

import os
import pytest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_readme_exists():
    """測試 README.md 是否存在。"""
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    assert os.path.exists(readme_path), "找不到 README.md"


def test_requirements_exists():
    """測試 requirements.txt 是否存在。"""
    requirements_path = os.path.join(PROJECT_ROOT, "requirements.txt")
    assert os.path.exists(requirements_path), "找不到 requirements.txt"


def test_pyproject_exists():
    """測試 pyproject.toml 是否存在。"""
    pyproject_path = os.path.join(PROJECT_ROOT, "pyproject.toml")
    assert os.path.exists(pyproject_path), "找不到 pyproject.toml"


def test_makefile_exists():
    """測試 Makefile 是否存在。"""
    makefile_path = os.path.join(PROJECT_ROOT, "Makefile")
    assert os.path.exists(makefile_path), "找不到 Makefile"


def test_env_example_exists():
    """測試 .env.example 是否存在。"""
    env_example_path = os.path.join(PROJECT_ROOT, ".env.example")
    assert os.path.exists(env_example_path), "找不到 .env.example"


def test_voice_assistant_package_exists():
    """測試 voice_assistant 套件目錄是否存在。"""
    package_dir = os.path.join(PROJECT_ROOT, "voice_assistant")
    assert os.path.isdir(package_dir), "找不到 voice_assistant 套件目錄"


def test_voice_assistant_init_exists():
    """測試 voice_assistant/__init__.py 是否存在。"""
    init_path = os.path.join(PROJECT_ROOT, "voice_assistant", "__init__.py")
    assert os.path.exists(init_path), "找不到 voice_assistant/__init__.py"


def test_voice_assistant_agent_exists():
    """測試 voice_assistant/agent.py 是否存在。"""
    agent_path = os.path.join(PROJECT_ROOT, "voice_assistant", "agent.py")
    assert os.path.exists(agent_path), "找不到 voice_assistant/agent.py"


# Removed demo scripts: demo.py, basic_demo.py, basic_live.py, advanced.py,
# multi_agent.py, direct_live_audio.py, interactive.py
# Use 'adk web' for Live API interaction instead


def test_tests_directory_exists():
    """測試 tests/ 目錄是否存在。"""
    tests_dir = os.path.join(PROJECT_ROOT, "tests")
    assert os.path.isdir(tests_dir), "找不到 tests 目錄"


def test_test_imports_exists():
    """測試 tests/test_imports.py 是否存在。"""
    test_imports_path = os.path.join(PROJECT_ROOT, "tests", "test_imports.py")
    assert os.path.exists(test_imports_path), "找不到 tests/test_imports.py"


def test_test_agent_exists():
    """測試 tests/test_agent.py 是否存在。"""
    test_agent_path = os.path.join(PROJECT_ROOT, "tests", "test_agent.py")
    assert os.path.exists(test_agent_path), "找不到 tests/test_agent.py"


def test_readme_has_content():
    """測試 README.md 是否有實質內容。"""
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    with open(readme_path, "r") as f:
        content = f.read()

    assert len(content) > 100, "README.md 內容過短"
    assert "Tutorial 15" in content, "README.md 缺少教學參考"
    assert "Live API" in content, "README.md 缺少 Live API 參考"


def test_requirements_has_dependencies():
    """測試 requirements.txt 是否包含必要的依賴。"""
    requirements_path = os.path.join(PROJECT_ROOT, "requirements.txt")
    with open(requirements_path, "r") as f:
        content = f.read()

    assert "google-genai" in content, "requirements.txt 缺少 google-genai"
    assert "pyaudio" in content, "requirements.txt 缺少 pyaudio"
    assert "pytest" in content, "requirements.txt 缺少 pytest"


def test_pyproject_has_metadata():
    """測試 pyproject.toml 是否包含必要的元數據。"""
    pyproject_path = os.path.join(PROJECT_ROOT, "pyproject.toml")
    with open(pyproject_path, "r") as f:
        content = f.read()

    assert 'name = "voice_assistant"' in content, "pyproject.toml 缺少套件名稱"
    assert "google-genai" in content, "pyproject.toml 缺少 google-genai 依賴"
