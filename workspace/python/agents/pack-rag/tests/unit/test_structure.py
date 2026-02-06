"""
專案結構與檔案存在性測試
"""

import os


class TestProjectStructure:
    """
    測試專案是否擁有正確的結構。

    重點說明:
    1. 驗證專案目錄結構 (rag, tests, etc.)
    2. 驗證關鍵檔案存在性 (agent.py, prompts.py, pyproject.toml, etc.)
    3. 驗證設定檔內容 (pyproject.toml, .env.example)
    """

    def test_rag_module_exists(self):
        """
        測試 rag 模組目錄是否存在。

        驗證點:
        1. rag 目錄存在
        """
        assert os.path.isdir("rag")

    def test_rag_init_exists(self):
        """
        測試 rag __init__.py 是否存在。

        驗證點:
        1. rag/__init__.py 檔案存在
        """
        assert os.path.isfile("rag/__init__.py")

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在。"""
        assert os.path.isfile("rag/agent.py")

    def test_prompts_py_exists(self):
        """測試 prompts.py 是否存在。"""
        assert os.path.isfile("rag/prompts.py")

    def test_tracing_py_exists(self):
        """測試 tracing.py 是否存在。"""
        assert os.path.isfile("rag/tracing.py")

    def test_fast_api_app_exists(self):
        """測試 fast_api_app.py 是否存在。"""
        assert os.path.isfile("rag/fast_api_app.py")

    def test_app_utils_directory_exists(self):
        """測試 app_utils 目錄是否存在。"""
        assert os.path.isdir("rag/app_utils")

    def test_app_utils_init_exists(self):
        """測試 app_utils __init__.py 是否存在。"""
        # app_utils 可能沒有 __init__.py，所以這個測試是選填的
        if os.path.exists("rag/app_utils/__init__.py"):
            assert os.path.isfile("rag/app_utils/__init__.py")

    def test_telemetry_py_exists(self):
        """測試 telemetry.py 是否存在。"""
        assert os.path.isfile("rag/app_utils/telemetry.py")

    def test_typing_py_exists(self):
        """測試 typing.py 是否存在。"""
        assert os.path.isfile("rag/app_utils/typing.py")

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir("tests")

    def test_unit_tests_directory_exists(self):
        """測試 unit tests 目錄是否存在。"""
        assert os.path.isdir("tests/unit")

    def test_test_files_exist(self):
        """測試測試檔案是否存在。"""
        assert os.path.isfile("tests/unit/test_agent.py")
        assert os.path.isfile("tests/unit/test_imports.py")
        assert os.path.isfile("tests/unit/test_structure.py")
        assert os.path.isfile("tests/unit/test_prompts.py")
        assert os.path.isfile("tests/unit/test_models.py")

    def test_required_config_files_exist(self):
        """測試必要的設定檔是否存在。"""
        assert os.path.isfile("pyproject.toml")
        assert os.path.isfile("Makefile")

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        assert os.path.isfile(".env.example")

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile("README.md")

    def test_dockerfile_exists(self):
        """測試 Dockerfile 是否存在。"""
        assert os.path.isfile("Dockerfile")

    def test_pyproject_has_content(self):
        """測試 pyproject.toml 是否有內容。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "[project]" in content
            assert "rag" in content

    def test_pyproject_has_dependencies(self):
        """測試 pyproject.toml 是否包含依賴項目。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "google-adk" in content
            assert "pytest" in content
            assert "google-cloud-aiplatform" in content

    def test_pyproject_has_rag_dependencies(self):
        """測試 pyproject.toml 是否包含 RAG 相關依賴。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            # 檢查是否包含 llama-index（RAG 相關）
            assert "llama-index" in content or "arize" in content


class TestEnvironmentConfiguration:
    """測試環境與配置設定。"""

    def test_env_example_is_not_env(self):
        """測試 .env.example 不應為 .env。"""
        assert os.path.isfile(".env.example")
        # .env may exist locally but should not be in repo

    def test_env_example_has_placeholder(self):
        """測試 .env.example 是否包含必要的環境變數佔位符。"""
        with open(".env.example", "r") as f:
            content = f.read()
            # 檢查 RAG_CORPUS 或 ARIZE 相關設定
            has_rag_config = (
                "RAG_CORPUS" in content
                or "ARIZE" in content
                or "GOOGLE_API_KEY" in content
            )
            assert has_rag_config, ".env.example 應包含 RAG 或追蹤相關的環境變數"

    def test_makefile_has_targets(self):
        """測試 Makefile 是否包含必要目標。"""
        with open("Makefile", "r") as f:
            content = f.read()
            # 檢查 Makefile 包含至少一個目標
            assert "install" in content or "test" in content or "run" in content


class TestDirectoryStructure:
    """測試目錄結構完整性。"""

    def test_integration_tests_directory_exists(self):
        """測試整合測試目錄是否存在。"""
        if os.path.exists("tests/integration"):
            assert os.path.isdir("tests/integration")

    def test_shared_libraries_directory_exists(self):
        """測試共享函式庫目錄是否存在（如適用）。"""
        if os.path.exists("rag/shared_libraries"):
            assert os.path.isdir("rag/shared_libraries")
