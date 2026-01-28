"""
專案結構與檔案存在性測試

測試專案是否擁有正確的結構，確保所有必要的檔案與目錄都存在。
"""

import os


class TestProjectStructure:
    """測試專案是否擁有正確的結構。"""

    def test_app_module_exists(self):
        """測試 App 模組目錄是否存在。"""
        assert os.path.isdir("app")

    def test_app_init_exists(self):
        """測試 App __init__.py 是否存在。"""
        assert os.path.isfile("app/__init__.py")

    def test_agent_py_exists(self):
        """測試 agent.py 是否存在。"""
        assert os.path.isfile("app/agent.py")

    def test_sub_agent_files_exist(self):
        """測試所有子 Agent 檔案是否存在。"""
        assert os.path.isfile("app/story_agent.py")
        assert os.path.isfile("app/screenplay_agent.py")
        assert os.path.isfile("app/storyboard_agent.py")
        assert os.path.isfile("app/video_agent.py")

    def test_server_py_exists(self):
        """測試 server.py 是否存在。"""
        assert os.path.isfile("app/server.py")

    def test_utils_directory_exists(self):
        """測試 utils 目錄是否存在。"""
        assert os.path.isdir("app/utils")

    def test_utils_files_exist(self):
        """測試 utils 檔案是否存在。"""
        assert os.path.isfile("app/utils/__init__.py")
        assert os.path.isfile("app/utils/utils.py")
        assert os.path.isfile("app/utils/typing.py")
        assert os.path.isfile("app/utils/gcs.py")
        assert os.path.isfile("app/utils/tracing.py")

    def test_prompts_directory_exists(self):
        """測試 prompts 目錄是否存在。"""
        assert os.path.isdir("app/prompts")

    def test_prompts_files_exist(self):
        """測試所有提示詞檔案是否存在。"""
        assert os.path.isfile("app/prompts/director_agent.txt")
        assert os.path.isfile("app/prompts/story_agent.txt")
        assert os.path.isfile("app/prompts/story_agent_desc.txt")
        assert os.path.isfile("app/prompts/screenplay_agent.txt")
        assert os.path.isfile("app/prompts/storyboard_agent.txt")
        assert os.path.isfile("app/prompts/video_agent.txt")

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
        """測試測試檔案是否存在。"""
        assert os.path.isfile("tests/__init__.py")
        assert os.path.isfile("tests/unit/__init__.py")
        assert os.path.isfile("tests/unit/test_imports.py")
        assert os.path.isfile("tests/unit/test_structure.py")

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

    def test_pyproject_has_content(self):
        """測試 pyproject.toml 是否有內容。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "[project]" in content
            assert "short-movie-agents" in content

    def test_pyproject_has_dependencies(self):
        """測試 pyproject.toml 是否包含依賴項目。"""
        with open("pyproject.toml", "r") as f:
            content = f.read()
            assert "google-adk" in content
            assert "pytest" in content
            assert "fastapi" in content
            assert "vertexai" in content or "google-cloud-aiplatform" in content

    def test_readme_has_content(self):
        """測試 README.md 是否有內容。"""
        with open("README.md", "r") as f:
            content = f.read()
            assert len(content) > 0


class TestEnvironmentConfiguration:
    """測試環境與配置設定。"""

    def test_env_example_is_not_env(self):
        """測試 .env.example 不應為 .env。"""
        assert os.path.isfile(".env.example")
        # .env may exist locally but should not be in repo

    def test_env_example_has_placeholder(self):
        """測試 .env.example 是否包含佔位符值。"""
        with open(".env.example", "r") as f:
            content = f.read()
            assert (
                "GOOGLE_CLOUD_PROJECT" in content
                or "GOOGLE_API_KEY" in content
                or "your_project_id" in content.lower()
            )

    def test_makefile_has_targets(self):
        """測試 Makefile 是否包含必要目標。"""
        with open("Makefile", "r") as f:
            content = f.read()
            # 檢查 Makefile 包含至少一個目標
            assert "install" in content or "test" in content or "run" in content

    def test_dockerfile_has_content(self):
        """測試 Dockerfile 是否有內容。"""
        with open("Dockerfile", "r") as f:
            content = f.read()
            assert "FROM" in content
            assert len(content) > 0
