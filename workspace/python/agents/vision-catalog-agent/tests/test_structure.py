"""
測試 vision_catalog_agent 的專案結構。

此檔案確保專案具備所有必要的目錄和設定檔，
例如原始碼目錄、測試目錄、requirements.txt、pyproject.toml 等。
"""

import os
from pathlib import Path


class TestProjectStructure:
    """測試專案結構與必要檔案。"""

    @property
    def project_root(self):
        """取得專案根目錄。"""
        return Path(__file__).parent.parent

    def test_project_root_exists(self):
        """測試專案根目錄是否存在。"""
        assert self.project_root.exists()
        assert self.project_root.is_dir()

    def test_agent_directory_exists(self):
        """測試 Agent 的原始碼目錄是否存在。"""
        agent_dir = self.project_root / 'vision_catalog_agent'
        assert agent_dir.exists()
        assert agent_dir.is_dir()

    def test_tests_directory_exists(self):
        """測試測試目錄是否存在。"""
        tests_dir = self.project_root / 'tests'
        assert tests_dir.exists()
        assert tests_dir.is_dir()

    def test_requirements_file_exists(self):
        """測試 requirements.txt 檔案是否存在。"""
        requirements = self.project_root / 'requirements.txt'
        assert requirements.exists()
        assert requirements.is_file()

    def test_pyproject_file_exists(self):
        """測試 pyproject.toml 檔案是否存在。"""
        pyproject = self.project_root / 'pyproject.toml'
        assert pyproject.exists()
        assert pyproject.is_file()

    def test_makefile_exists(self):
        """測試 Makefile 檔案是否存在。"""
        makefile = self.project_root / 'Makefile'
        assert makefile.exists()
        assert makefile.is_file()

    def test_env_example_exists(self):
        """測試 .env.example 檔案是否存在。"""
        env_example = self.project_root / '.env.example'
        assert env_example.exists()
        assert env_example.is_file()

    def test_adkignore_exists(self):
        """測試 .adkignore 檔案是否存在。"""
        adkignore = self.project_root / '.adkignore'
        assert adkignore.exists()
        assert adkignore.is_file()

    def test_agent_init_exists(self):
        """測試 Agent 的 __init__.py 檔案是否存在。"""
        init_file = self.project_root / 'vision_catalog_agent' / '__init__.py'
        assert init_file.exists()
        assert init_file.is_file()

    def test_agent_py_exists(self):
        """測試 agent.py 檔案是否存在。"""
        agent_file = self.project_root / 'vision_catalog_agent' / 'agent.py'
        assert agent_file.exists()
        assert agent_file.is_file()


class TestRequiredDependencies:
    """測試必要的相依性套件。"""

    @property
    def requirements_path(self):
        """取得 requirements.txt 的路徑。"""
        return Path(__file__).parent.parent / 'requirements.txt'

    def test_requirements_content(self):
        """測試 requirements.txt 是否包含必要的套件。"""
        with open(self.requirements_path) as f:
            content = f.read().lower()

        required = [
            'google-genai',
            'pillow',
            'pytest'
        ]

        for package in required:
            assert package in content, f"遺失必要的套件: {package}"


class TestPyprojectConfiguration:
    """測試 pyproject.toml 的設定。"""

    @property
    def pyproject_path(self):
        """取得 pyproject.toml 的路徑。"""
        return Path(__file__).parent.parent / 'pyproject.toml'

    def test_pyproject_content(self):
        """測試 pyproject.toml 是否包含必要的區段。"""
        with open(self.pyproject_path) as f:
            content = f.read()

        required_sections = [
            '[build-system]',
            '[project]',
            '[tool.pytest.ini_options]'
        ]

        for section in required_sections:
            assert section in content, f"遺失區段: {section}"

    def test_project_name(self):
        """測試專案名稱是否已正確設定。"""
        with open(self.pyproject_path) as f:
            content = f.read()

        assert 'name = "vision_catalog_agent"' in content


class TestMakefileTargets:
    """測試 Makefile 的目標。"""

    @property
    def makefile_path(self):
        """取得 Makefile 的路徑。"""
        return Path(__file__).parent.parent / 'Makefile'

    def test_makefile_targets(self):
        """測試 Makefile 是否包含標準的目標。"""
        with open(self.makefile_path) as f:
            content = f.read()

        required_targets = [
            'setup:',
            'dev:',
            'test:',
            'demo:',
            'clean:'
        ]

        for target in required_targets:
            assert target in content, f"遺失 Makefile 目標: {target}"


class TestSampleImagesDirectory:
    """測試範例圖片目錄的結構。"""

    @property
    def sample_dir(self):
        """取得 _sample_images 目錄。"""
        return Path(__file__).parent.parent / '_sample_images'

    def test_sample_dir_exists(self):
        """測試 _sample_images 目錄是否存在。"""
        assert self.sample_dir.exists()
        assert self.sample_dir.is_dir()
