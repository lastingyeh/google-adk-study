# 教學 22：模型選擇與優化 - 結構測試
# 驗證專案結構是否遵循 ADK 慣例

import os


class TestProjectStructure:
    """測試專案是否遵循必要的 ADK 結構。"""

    def test_model_selector_directory_exists(self):
        """測試 model_selector 目錄是否存在。"""
        assert os.path.isdir('model_selector'), "model_selector directory not found"

    def test_init_py_exists(self):
        """測試 __init__.py 是否存在於 model_selector 中。"""
        init_file = os.path.join('model_selector', '__init__.py')
        assert os.path.isfile(init_file), "__init__.py not found in model_selector"

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在於 model_selector 中。"""
        agent_file = os.path.join('model_selector', 'agent.py')
        assert os.path.isfile(agent_file), "agent.py not found in model_selector"

    def test_env_example_exists(self):
        """測試 .env.example 是否存在於 model_selector 中。"""
        env_file = os.path.join('model_selector', '.env.example')
        assert os.path.isfile(env_file), ".env.example not found in model_selector"

    def test_init_py_content(self):
        """測試 __init__.py 是否有正確的內容。"""
        init_file = os.path.join('model_selector', '__init__.py')
        with open(init_file, 'r') as f:
            content = f.read().strip()

        assert content == "from . import agent", f"__init__.py content incorrect: {content}"

    def test_agent_py_is_python_file(self):
        """測試 agent.py 是否為一個有效的 Python 檔案。"""
        agent_file = os.path.join('model_selector', 'agent.py')

        # Should be readable
        with open(agent_file, 'r') as f:
            content = f.read()

        assert len(content) > 0, "agent.py is empty"

        # Should contain Python code
        assert "from google.adk.agents import Agent" in content
        assert "root_agent = Agent(" in content
        assert "ModelSelector" in content

    def test_env_example_content(self):
        """測試 .env.example 是否有必要的設定。"""
        env_file = os.path.join('model_selector', '.env.example')
        with open(env_file, 'r') as f:
            content = f.read()

        # Should contain required environment variables
        assert "GOOGLE_API_KEY=" in content


class TestTestStructure:
    """測試測試目錄結構是否正確。"""

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir('tests'), "tests directory not found"

    def test_tests_init_py_exists(self):
        """測試 tests/__init__.py 是否存在。"""
        init_file = os.path.join('tests', '__init__.py')
        assert os.path.isfile(init_file), "tests/__init__.py not found"

    def test_test_files_exist(self):
        """測試所有測試檔案是否存在。"""
        test_files = [
            'test_agent.py',
            'test_imports.py',
            'test_structure.py'
        ]

        for test_file in test_files:
            file_path = os.path.join('tests', test_file)
            assert os.path.isfile(file_path), f"{test_file} not found in tests/"


class TestRootFiles:
    """測試根目錄級別的檔案是否存在。"""

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile('README.md'), "README.md not found"

    def test_makefile_exists(self):
        """測試 Makefile 是否存在。"""
        assert os.path.isfile('Makefile'), "Makefile not found"

    def test_requirements_exists(self):
        """測試 requirements.txt 是否存在。"""
        assert os.path.isfile('requirements.txt'), "requirements.txt not found"

    def test_pyproject_exists(self):
        """測試 pyproject.toml 是否存在。"""
        assert os.path.isfile('pyproject.toml'), "pyproject.toml not found"

    def test_readme_content(self):
        """測試 README.md 是否有基本內容。"""
        with open('README.md', 'r') as f:
            content = f.read()

        assert len(content) > 100, "README.md seems too short"
        assert "Tutorial 22" in content
        assert "Model Selection" in content

    def test_makefile_content(self):
        """測試 Makefile 是否有基本的目標。"""
        with open('Makefile', 'r') as f:
            content = f.read()

        assert "help:" in content
        assert "setup:" in content
        assert "test:" in content
        assert "dev:" in content

    def test_requirements_content(self):
        """測試 requirements.txt 是否包含 ADK。"""
        with open('requirements.txt', 'r') as f:
            content = f.read()

        assert "google-adk" in content, "google-adk not found in requirements.txt"

    def test_pyproject_content(self):
        """測試 pyproject.toml 是否有正確的專案名稱。"""
        with open('pyproject.toml', 'r') as f:
            content = f.read()

        assert "tutorial22" in content, "tutorial22 not found in pyproject.toml"
        assert "Model Selection" in content
