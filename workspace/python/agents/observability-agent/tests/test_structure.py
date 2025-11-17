"""
針對專案結構與必要檔案進行測試。
"""

import os


def test_required_files_exist():
    """測試所有必要的專案檔案是否存在。
    重點：
    - 驗證 `pyproject.toml`、`requirements.txt`、`Makefile` 等核心檔案都存在於專案根目錄中。
    - 確保 `observability_agent` 套件與測試檔案都在預期的位置。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    required_files = [
        'pyproject.toml',
        'requirements.txt',
        'Makefile',
        'README.md',
        '.env.example',
        'observability_agent/__init__.py',
        'observability_agent/agent.py',
        'tests/test_agent.py',
        'tests/test_events.py',
        'tests/test_observability.py',
        'tests/test_imports.py',
        'tests/test_structure.py'
    ]

    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        assert os.path.exists(full_path), f"缺少必要檔案：{file_path}"


def test_observability_agent_is_package():
    """測試 observability_agent 目錄是否為一個合法的 Python 套件。
    重點：
    - 檢查 `observability_agent` 目錄下是否存在 `__init__.py` 檔案，以確認其為可匯入的套件。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    init_file = os.path.join(base_dir, 'observability_agent', '__init__.py')

    assert os.path.exists(init_file)
    assert os.path.isfile(init_file)


def test_tests_directory_exists():
    """測試 tests 目錄是否存在。
    重點：
    - 確認專案中包含 `tests` 目錄，用於存放所有測試程式碼。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_dir = os.path.join(base_dir, 'tests')

    assert os.path.exists(tests_dir)
    assert os.path.isdir(tests_dir)


def test_pyproject_toml_valid():
    """測試 pyproject.toml 是否包含必要欄位。
    重點：
    - 檢查 `pyproject.toml` 檔案中是否包含 `[project]`區塊、專案名稱及 `google-genai` 依賴項。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pyproject_path = os.path.join(base_dir, 'pyproject.toml')

    with open(pyproject_path, 'r') as f:
        content = f.read()

    assert '[project]' in content
    assert 'name = "observability_agent"' in content
    assert 'google-genai' in content


def test_makefile_has_required_targets():
    """測試 Makefile 是否包含必要指令。
    重點：
    - 驗證 `Makefile` 中是否存在 `setup`、`dev`、`test` 等常用開發指令。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    makefile_path = os.path.join(base_dir, 'Makefile')

    with open(makefile_path, 'r') as f:
        content = f.read()

    required_targets = ['setup', 'dev', 'test', 'demo', 'clean', 'coverage']

    for target in required_targets:
        assert f'{target}:' in content, f"Makefile 缺少指令：{target}"
