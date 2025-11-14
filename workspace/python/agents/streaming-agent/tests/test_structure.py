"""
測試專案結構與設定。

重點：確保專案包含所有必要的目錄和檔案，且設定檔（如 .env.example、pyproject.toml）符合預期格式。
"""

from pathlib import Path


def test_project_structure():
    """測試：專案是否具有預期的目錄結構。"""
    base_path = Path(__file__).parent.parent

    # 檢查：必要目錄是否存在
    assert (base_path / "streaming_agent").exists()
    assert (base_path / "streaming_agent").is_dir()

    assert (base_path / "tests").exists()
    assert (base_path / "tests").is_dir()

    # 檢查：必要檔案是否存在
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "Makefile",
        "streaming_agent/__init__.py",
        "streaming_agent/agent.py",
        "streaming_agent/.env.example",
        "tests/__init__.py",
        "tests/test_agent.py",
        "tests/test_imports.py",
        "tests/test_structure.py"
    ]

    for file_path in required_files:
        assert (base_path / file_path).exists(), f"Missing required file: {file_path}"
        assert (base_path / file_path).is_file(), f"Expected file, got directory: {file_path}"


def test_env_example_structure():
    """測試：.env.example 是否具有必要的結構。"""
    base_path = Path(__file__).parent.parent
    env_example = base_path / "streaming_agent" / ".env.example"

    assert env_example.exists()

    content = env_example.read_text()

    # 檢查：必要的環境變數是否存在
    required_vars = [
        "GOOGLE_API_KEY",
        "GOOGLE_GENAI_USE_VERTEXAI"
    ]

    for var in required_vars:
        assert var in content, f"Missing required environment variable in .env.example: {var}"


def test_pyproject_toml_structure():
    """測試：pyproject.toml 是否具有必要的結構。"""
    base_path = Path(__file__).parent.parent
    pyproject = base_path / "pyproject.toml"

    assert pyproject.exists()

    content = pyproject.read_text()

    # 檢查：必要的區段是否存在
    required_sections = [
        "[build-system]",
        "[project]",
        "[tool.setuptools.packages.find]"
    ]

    for section in required_sections:
        assert section in content, f"Missing required section in pyproject.toml: {section}"

    # 檢查：專案名稱是否存在
    assert 'name = "streaming_agent"' in content


def test_requirements_txt_structure():
    """測試：requirements.txt 是否包含必要的依賴項。"""
    base_path = Path(__file__).parent.parent
    requirements = base_path / "requirements.txt"

    assert requirements.exists()

    content = requirements.read_text()

    # 檢查：必要的依賴項是否存在
    required_deps = [
        "google-genai",
        "pytest"
    ]

    for dep in required_deps:
        assert dep in content, f"Missing required dependency in requirements.txt: {dep}"


def test_makefile_structure():
    """測試：Makefile 是否包含必要的目標。"""
    base_path = Path(__file__).parent.parent
    makefile = base_path / "Makefile"

    assert makefile.exists()

    content = makefile.read_text()

    # 檢查：必要的目標是否存在
    required_targets = [
        ".PHONY: setup dev test demo clean help",
        "setup:",
        "dev:",
        "test:",
        "demo:",
        "clean:"
    ]

    for target in required_targets:
        assert target in content, f"Missing required target in Makefile: {target}"


def test_agent_file_structure():
    """測試：agent.py 是否具有必要的結構。"""
    base_path = Path(__file__).parent.parent
    agent_file = base_path / "streaming_agent" / "agent.py"

    assert agent_file.exists()

    content = agent_file.read_text()

    # 檢查：必要的匯出/函式是否存在
    required_elements = [
        "root_agent",
        "create_streaming_agent",
        "stream_agent_response",
        "get_complete_response",
        "create_demo_session"
    ]

    for element in required_elements:
        assert element in content, f"Missing required element in agent.py: {element}"


def test_init_file_structure():
    """測試：__init__.py 是否包含必要的匯出。"""
    base_path = Path(__file__).parent.parent
    init_file = base_path / "streaming_agent" / "__init__.py"

    assert init_file.exists()

    content = init_file.read_text()

    # 檢查：必要的匯出是否存在
    required_exports = [
        "root_agent",
        "stream_agent_response",
        "get_complete_response",
        "create_demo_session"
    ]

    for export in required_exports:
        assert export in content, f"Missing required export in __init__.py: {export}"


def test_no_env_file():
    """測試：.env 檔案不存在（安全性檢查）。"""
    base_path = Path(__file__).parent.parent
    env_file = base_path / "streaming_agent" / ".env"

    # 檢查：.env 不應存在 - 只應存在 .env.example
    assert not env_file.exists(), ".env file should not exist - only .env.example should be present"


def test_readme_exists():
    """測試：README.md 是否存在。"""
    base_path = Path(__file__).parent.parent
    readme = base_path / "README.md"

    # 檢查：README 是可選的，但建議存在
    if readme.exists():
        assert readme.is_file()
        content = readme.read_text()
        assert len(content.strip()) > 0, "README.md should not be empty"


def test_test_files_executable():
    """測試：測試檔案是否結構正確。"""
    base_path = Path(__file__).parent

    test_files = [
        "test_agent.py",
        "test_imports.py",
        "test_structure.py"
    ]

    for test_file in test_files:
        file_path = base_path / test_file
        assert file_path.exists()

    content = file_path.read_text()

    # 檢查：測試檔案是否包含基本的測試結構
    assert "def test_" in content or "class Test" in content, f"Test file {test_file} lacks test structure"
