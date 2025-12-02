"""測試數據分析代理的專案結構。"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """獲取專案根目錄。"""
    return Path(__file__).parent.parent


def test_agent_directory_exists(project_root):
    """測試 agent 目錄是否存在。"""
    agent_dir = project_root / "agent"
    assert agent_dir.exists()
    assert agent_dir.is_dir()


def test_agent_init_exists(project_root):
    """測試 agent/__init__.py 是否存在。"""
    init_file = project_root / "agent" / "__init__.py"
    assert init_file.exists()
    assert init_file.is_file()


def test_agent_py_exists(project_root):
    """測試 agent/agent.py 是否存在。"""
    agent_file = project_root / "agent" / "agent.py"
    assert agent_file.exists()
    assert agent_file.is_file()


def test_requirements_exists(project_root):
    """測試 requirements.txt 是否存在。"""
    req_file = project_root / "requirements.txt"
    assert req_file.exists()
    assert req_file.is_file()


def test_agent_requirements_exists(project_root):
    """測試 agent/requirements.txt 是否存在。"""
    req_file = project_root / "agent" / "requirements.txt"
    assert req_file.exists()
    assert req_file.is_file()


def test_pyproject_exists(project_root):
    """測試 pyproject.toml 是否存在。"""
    pyproject = project_root / "pyproject.toml"
    assert pyproject.exists()
    assert pyproject.is_file()


def test_env_example_exists(project_root):
    """測試 agent/.env.example 是否存在。"""
    env_example = project_root / "agent" / ".env.example"
    assert env_example.exists()
    assert env_example.is_file()


def test_tests_directory_exists(project_root):
    """測試 tests 目錄是否存在。"""
    tests_dir = project_root / "tests"
    assert tests_dir.exists()
    assert tests_dir.is_dir()


def test_frontend_directory_exists(project_root):
    """測試 frontend 目錄是否存在。"""
    frontend_dir = project_root / "frontend"
    assert frontend_dir.exists()
    assert frontend_dir.is_dir()


def test_frontend_package_json_exists(project_root):
    """測試 frontend/package.json 是否存在。"""
    package_json = project_root / "frontend" / "package.json"
    assert package_json.exists()
    assert package_json.is_file()


def test_frontend_vite_config_exists(project_root):
    """測試 frontend/vite.config.ts 是否存在。"""
    vite_config = project_root / "frontend" / "vite.config.ts"
    assert vite_config.exists()
    assert vite_config.is_file()


def test_frontend_src_exists(project_root):
    """測試 frontend/src 目錄是否存在。"""
    src_dir = project_root / "frontend" / "src"
    assert src_dir.exists()
    assert src_dir.is_dir()


def test_frontend_app_tsx_exists(project_root):
    """測試 frontend/src/App.tsx 是否存在。"""
    app_tsx = project_root / "frontend" / "src" / "App.tsx"
    assert app_tsx.exists()
    assert app_tsx.is_file()


def test_frontend_components_exists(project_root):
    """測試 frontend/src/components 目錄是否存在。"""
    components_dir = project_root / "frontend" / "src" / "components"
    assert components_dir.exists()
    assert components_dir.is_dir()


def test_chart_renderer_exists(project_root):
    """測試 ChartRenderer 組件是否存在。"""
    chart_renderer = project_root / "frontend" / "src" / "components" / "ChartRenderer.tsx"
    assert chart_renderer.exists()
    assert chart_renderer.is_file()


def test_data_table_exists(project_root):
    """測試 DataTable 組件是否存在。"""
    data_table = project_root / "frontend" / "src" / "components" / "DataTable.tsx"
    assert data_table.exists()
    assert data_table.is_file()
