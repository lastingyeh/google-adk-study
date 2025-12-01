"""測試專案結構。"""

import os
import pytest


class TestProjectStructure:
    """測試專案結構和必要檔案。"""

    def test_agent_directory_exists(self):
        """測試 agent 目錄是否存在。"""
        assert os.path.isdir("agent"), "agent directory should exist"

    def test_tests_directory_exists(self):
        """測試 tests 目錄是否存在。"""
        assert os.path.isdir("tests"), "tests directory should exist"

    def test_nextjs_frontend_directory_exists(self):
        """測試 nextjs_frontend 目錄是否存在。"""
        assert os.path.isdir("nextjs_frontend"), "nextjs_frontend directory should exist"

    def test_agent_init_exists(self):
        """測試 agent/__init__.py 是否存在。"""
        assert os.path.isfile(
            "agent/__init__.py"
        ), "agent/__init__.py should exist"

    def test_agent_py_exists(self):
        """測試 agent/agent.py 是否存在。"""
        assert os.path.isfile("agent/agent.py"), "agent/agent.py should exist"

    def test_env_example_exists(self):
        """測試 agent/.env.example 是否存在。"""
        assert os.path.isfile(
            "agent/.env.example"
        ), "agent/.env.example should exist"

    def test_requirements_txt_exists(self):
        """測試 requirements.txt 是否存在。"""
        assert os.path.isfile("requirements.txt"), "requirements.txt should exist"

    def test_pyproject_toml_exists(self):
        """測試 pyproject.toml 是否存在。"""
        assert os.path.isfile("pyproject.toml"), "pyproject.toml should exist"

    def test_makefile_exists(self):
        """測試 Makefile 是否存在。"""
        assert os.path.isfile("Makefile"), "Makefile should exist"

    def test_readme_exists(self):
        """測試 README.md 是否存在。"""
        assert os.path.isfile("README.md"), "README.md should exist"

    def test_nextjs_package_json_exists(self):
        """測試 nextjs_frontend/package.json 是否存在。"""
        assert os.path.isfile(
            "nextjs_frontend/package.json"
        ), "nextjs_frontend/package.json should exist"

    def test_nextjs_app_directory_exists(self):
        """測試 nextjs_frontend/app 目錄是否存在。"""
        assert os.path.isdir(
            "nextjs_frontend/app"
        ), "nextjs_frontend/app directory should exist"

    def test_nextjs_page_exists(self):
        """測試 nextjs_frontend/app/page.tsx 是否存在。"""
        assert os.path.isfile(
            "nextjs_frontend/app/page.tsx"
        ), "nextjs_frontend/app/page.tsx should exist"

    def test_nextjs_layout_exists(self):
        """測試 nextjs_frontend/app/layout.tsx 是否存在。"""
        assert os.path.isfile(
            "nextjs_frontend/app/layout.tsx"
        ), "nextjs_frontend/app/layout.tsx should exist"


class TestRequirementsContent:
    """測試 requirements.txt 的內容。"""

    def test_requirements_has_google_adk(self):
        """測試 requirements.txt 是否包含 google-adk。"""
        with open("requirements.txt", "r") as f:
            content = f.read()
        assert "google-adk" in content.lower(), "requirements.txt should include google-adk"

    def test_requirements_has_fastapi(self):
        """測試 requirements.txt 是否包含 fastapi。"""
        with open("requirements.txt", "r") as f:
            content = f.read()
        assert "fastapi" in content.lower(), "requirements.txt should include fastapi"

    def test_requirements_has_uvicorn(self):
        """測試 requirements.txt 是否包含 uvicorn。"""
        with open("requirements.txt", "r") as f:
            content = f.read()
        assert "uvicorn" in content.lower(), "requirements.txt should include uvicorn"

    def test_requirements_has_ag_ui_adk(self):
        """測試 requirements.txt 是否包含 ag-ui-adk。"""
        with open("requirements.txt", "r") as f:
            content = f.read()
        assert "ag-ui-adk" in content.lower() or "ag_ui_adk" in content.lower(), \
            "requirements.txt should include ag-ui-adk"


class TestEnvExample:
    """測試 .env.example 檔案。"""

    def test_env_example_has_google_api_key(self):
        """測試 .env.example 是否提及 GOOGLE_API_KEY。"""
        with open("agent/.env.example", "r") as f:
            content = f.read()
        assert "GOOGLE_API_KEY" in content, ".env.example should mention GOOGLE_API_KEY"

    def test_env_example_no_real_key(self):
        """測試 .env.example 是否不包含真實的 API 金鑰。"""
        with open("agent/.env.example", "r") as f:
            content = f.read()
        # 檢查值是否為佔位符
        lines = [line for line in content.split("\n") if "GOOGLE_API_KEY" in line and not line.strip().startswith("#")]
        if lines:
            assert "your" in lines[0].lower() or "placeholder" in lines[0].lower() or "example" in lines[0].lower(), \
                ".env.example should not contain real API keys"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
