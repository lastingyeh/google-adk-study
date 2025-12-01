"""測試客戶支援代理的結構和配置。"""

import pytest
import os
import sys

# 將父目錄加入路徑以進行匯入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestProjectStructure:
    """測試專案結構和檔案存在性。"""

    def test_agent_directory_exists(self):
        """測試 agent 目錄是否存在。"""
        agent_dir = os.path.join(os.path.dirname(__file__), "..", "agent")
        assert os.path.isdir(agent_dir), "agent directory should exist"

    def test_agent_file_exists(self):
        """測試 agent.py 是否存在。"""
        agent_file = os.path.join(
            os.path.dirname(__file__), "..", "agent", "agent.py"
        )
        assert os.path.isfile(agent_file), "agent/agent.py should exist"

    def test_init_file_exists(self):
        """測試 __init__.py 是否存在。"""
        init_file = os.path.join(
            os.path.dirname(__file__), "..", "agent", "__init__.py"
        )
        assert os.path.isfile(init_file), "agent/__init__.py should exist"

    def test_env_example_exists(self):
        """測試 .env.example 是否存在。"""
        env_example = os.path.join(
            os.path.dirname(__file__), "..", "agent", ".env.example"
        )
        assert os.path.isfile(env_example), "agent/.env.example should exist"

    def test_requirements_exists(self):
        """測試 requirements.txt 是否存在。"""
        req_file = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        assert os.path.isfile(req_file), "requirements.txt should exist"

    def test_pyproject_exists(self):
        """測試 pyproject.toml 是否存在。"""
        pyproject_file = os.path.join(
            os.path.dirname(__file__), "..", "pyproject.toml"
        )
        assert os.path.isfile(pyproject_file), "pyproject.toml should exist"

    def test_nextjs_frontend_exists(self):
        """測試 Next.js 前端目錄是否存在。"""
        frontend_dir = os.path.join(
            os.path.dirname(__file__), "..", "nextjs_frontend"
        )
        assert os.path.isdir(frontend_dir), "nextjs_frontend directory should exist"


class TestAgentImports:
    """測試 agent 模組匯入。"""

    def test_agent_module_imports(self):
        """測試 agent 模組是否可以匯入。"""
        try:
            from agent import agent as agent_module

            assert agent_module is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_root_agent_exported(self):
        """測試 root_agent 是否從 agent 模組匯出。"""
        try:
            from agent.agent import root_agent

            assert root_agent is not None
            assert hasattr(root_agent, "name")
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_fastapi_app_exported(self):
        """測試 FastAPI 應用程式是否匯出。"""
        try:
            from agent.agent import app

            assert app is not None
            assert hasattr(app, "title")
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


class TestAgentConfiguration:
    """測試 agent 配置和設定。"""

    def test_agent_has_correct_name(self):
        """測試 agent 是否有正確的名稱。"""
        try:
            from agent.agent import root_agent

            assert root_agent.name == "customer_support_agent"
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_agent_has_tools(self):
        """測試 agent 是否配置了工具。"""
        try:
            from agent.agent import root_agent

            assert hasattr(root_agent, "tools")
            assert len(root_agent.tools) > 0
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_agent_has_instruction(self):
        """測試 agent 是否配置了指令。"""
        try:
            from agent.agent import root_agent

            assert hasattr(root_agent, "instruction")
            assert root_agent.instruction is not None
            assert len(root_agent.instruction) > 0
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_agent_model_configured(self):
        """測試 agent 是否配置了模型。"""
        try:
            from agent.agent import root_agent

            assert hasattr(root_agent, "model")
            assert root_agent.model is not None
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


class TestToolDefinitions:
    """測試工具函式定義。"""

    def test_search_knowledge_base_exists(self):
        """測試 search_knowledge_base 函式是否存在。"""
        try:
            from agent.agent import search_knowledge_base

            assert callable(search_knowledge_base)
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_lookup_order_status_exists(self):
        """測試 lookup_order_status 函式是否存在。"""
        try:
            from agent.agent import lookup_order_status

            assert callable(lookup_order_status)
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_create_support_ticket_exists(self):
        """測試 create_support_ticket 函式是否存在。"""
        try:
            from agent.agent import create_support_ticket

            assert callable(create_support_ticket)
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_search_knowledge_base_returns_dict(self):
        """測試 search_knowledge_base 是否回傳字典。"""
        try:
            from agent.agent import search_knowledge_base

            result = search_knowledge_base("refund policy")
            assert isinstance(result, dict)
            assert "status" in result
            assert "report" in result
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_lookup_order_status_returns_dict(self):
        """測試 lookup_order_status 是否回傳字典。"""
        try:
            from agent.agent import lookup_order_status

            result = lookup_order_status("ORD-12345")
            assert isinstance(result, dict)
            assert "status" in result
            assert "report" in result
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_create_support_ticket_returns_dict(self):
        """測試 create_support_ticket 是否回傳字典。"""
        try:
            from agent.agent import create_support_ticket

            result = create_support_ticket("Test issue", "normal")
            assert isinstance(result, dict)
            assert "status" in result
            assert "report" in result
            assert "ticket" in result
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


class TestFastAPIConfiguration:
    """測試 FastAPI 應用程式配置。"""

    def test_app_has_title(self):
        """測試應用程式是否有標題。"""
        try:
            from agent.agent import app

            assert app.title == "Customer Support Agent API"
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_app_has_health_endpoint(self):
        """測試應用程式是否有健康檢查端點。"""
        try:
            from agent.agent import app

            routes = [route.path for route in app.routes]
            assert "/health" in routes
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")

    def test_app_has_copilotkit_endpoint(self):
        """測試應用程式是否有 copilotkit 端點。"""
        try:
            from agent.agent import app

            routes = [route.path for route in app.routes]
            # Check for copilotkit endpoint
            assert any("/api/copilotkit" in route for route in routes)
        except ImportError as e:
            pytest.skip(f"Import failed (dependencies not installed): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
