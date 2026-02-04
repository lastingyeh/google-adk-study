"""
專案結構與檔案存在性測試

測試 pack-bidi-streaming 專案是否擁有正確的結構。
"""

import os


class TestProjectStructure:
    """測試專案是否擁有正確的結構。"""

    def test_bidi_demo_module_exists(self):
        """測試 bidi_demo 模組目錄是否存在。"""
        assert os.path.isdir("bidi_demo")

    def test_bidi_demo_init_exists(self):
        """測試 bidi_demo __init__.py 是否存在。"""
        assert os.path.isfile("bidi_demo/__init__.py")

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在。"""
        assert os.path.isfile("bidi_demo/agent.py")

    def test_fast_api_app_exists(self):
        """測試 fast_api_app.py 是否存在。"""
        assert os.path.isfile("bidi_demo/fast_api_app.py")

    def test_app_utils_directory_exists(self):
        """測試 app_utils 目錄是否存在。"""
        assert os.path.isdir("bidi_demo/app_utils")

    def test_telemetry_py_exists(self):
        """測試 telemetry.py 是否存在。"""
        assert os.path.isfile("bidi_demo/app_utils/telemetry.py")

    def test_typing_py_exists(self):
        """測試 typing.py 是否存在。"""
        assert os.path.isfile("bidi_demo/app_utils/typing.py")

    def test_static_directory_exists(self):
        """測試 static 目錄是否存在。"""
        assert os.path.isdir("bidi_demo/static")

    def test_static_index_html_exists(self):
        """測試 static/index.html 是否存在。"""
        assert os.path.isfile("bidi_demo/static/index.html")

    def test_static_css_directory_exists(self):
        """測試 static/css 目錄是否存在。"""
        assert os.path.isdir("bidi_demo/static/css")

    def test_static_js_directory_exists(self):
        """測試 static/js 目錄是否存在。"""
        assert os.path.isdir("bidi_demo/static/js")

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir("tests")

    def test_unit_tests_directory_exists(self):
        """測試 unit tests 目錄是否存在。"""
        assert os.path.isdir("tests/unit")

    def test_integration_tests_directory_exists(self):
        """測試 integration tests 目錄是否存在。"""
        assert os.path.isdir("tests/integration")

    def test_test_files_exist(self):
        """測試單元測試檔案是否存在。"""
        assert os.path.isfile("tests/unit/test_agent.py")
        assert os.path.isfile("tests/unit/test_imports.py")
        assert os.path.isfile("tests/unit/test_structure.py")
        assert os.path.isfile("tests/unit/test_models.py")

    def test_required_config_files_exist(self):
        """測試必要的設定檔是否存在。"""
        assert os.path.isfile("pyproject.toml")
        assert os.path.isfile("Makefile")
        assert os.path.isfile("README.md")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        assert os.path.isfile(".env.example")

    def test_dockerfile_exists(self):
        """測試 Dockerfile 是否存在。"""
        assert os.path.isfile("Dockerfile")

    def test_deployment_directory_exists(self):
        """測試 deployment 目錄是否存在。"""
        assert os.path.isdir("deployment")

    def test_notebooks_directory_exists(self):
        """測試 notebooks 目錄是否存在。"""
        assert os.path.isdir("notebooks")
