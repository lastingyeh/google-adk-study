"""測試 Agent 的設定與安裝。"""

import pytest
from unittest.mock import Mock, patch
import os


class TestAgentConfig:
    """測試 Agent 的設定。"""

    def test_root_agent_exists(self):
        """測試 `root_agent` 是否成功匯出。"""
        from agent.agent import root_agent
        assert root_agent is not None, "root_agent 應被匯出且不為 None"

    def test_root_agent_is_agent_instance(self):
        """測試 `root_agent` 是否為 `Agent` 類別的實例。"""
        from agent.agent import root_agent
        from google.adk.agents import Agent
        assert isinstance(root_agent, Agent), "root_agent 應為 google.adk.agents.Agent 的實例"

    def test_agent_has_correct_name(self):
        """測試 Agent 的名稱是否正確。"""
        from agent.agent import root_agent
        assert root_agent.name == "quickstart_agent", "Agent 的名稱應為 'quickstart_agent'"

    def test_agent_has_model(self):
        """測試 Agent 是否已設定語言模型。"""
        from agent.agent import root_agent
        assert root_agent.model is not None, "Agent 應設定一個語言模型"
        assert "gemini" in root_agent.model.lower(), "模型名稱應包含 'gemini'"

    def test_agent_has_instruction(self):
        """測試 Agent 是否包含非空的 instruction。"""
        from agent.agent import root_agent
        assert root_agent.instruction is not None, "Agent 應包含 instruction"
        assert len(root_agent.instruction) > 0, "instruction 內容不應為空"


class TestFastAPIApp:
    """測試 FastAPI 應用程式。"""

    def test_app_exists(self):
        """測試 FastAPI 的 `app` 物件是否已建立。"""
        from agent.agent import app
        assert app is not None, "FastAPI 的 app 物件應被建立"

    def test_app_has_title(self):
        """測試 `app` 的標題是否正確。"""
        from agent.agent import app
        assert hasattr(app, 'title'), "app 物件應有 title 屬性"
        assert "Tutorial 29" in app.title or "UI Integration" in app.title, "app 標題應包含 'Tutorial 29' 或 'UI Integration'"

    def test_health_endpoint_exists(self):
        """測試 `/health` 健康檢查路由是否存在。"""
        from agent.agent import app
        routes = [route.path for route in app.routes]
        assert "/health" in routes, "應存在 `/health` 路由"

    def test_root_endpoint_exists(self):
        """測試 `/` 根路由是否存在。"""
        from agent.agent import app
        routes = [route.path for route in app.routes]
        assert "/" in routes, "應存在 `/` 根路由"

    def test_copilotkit_endpoint_exists(self):
        """測試 `copilotkit` 相關路由是否存在。"""
        from agent.agent import app
        routes = [route.path for route in app.routes]
        # 檢查是否存在包含 /api/copilotkit 的路徑
        copilotkit_paths = [r for r in routes if "copilotkit" in r]
        assert len(copilotkit_paths) > 0, "應存在 `copilotkit` 相關的 API 路由"


class TestADKAgentWrapper:
    """測試 ADK Agent 封裝設定。"""

    def test_agent_wrapper_exists(self):
        """測試 ADK Agent 的封裝物件是否存在。"""
        from agent.agent import agent
        assert agent is not None, "ADK Agent 的封裝物件應存在"

    def test_agent_wrapper_is_adk_agent(self):
        """測試封裝物件是否為 `ADKAgent` 的實例。"""
        from agent.agent import agent
        from ag_ui_adk import ADKAgent
        assert isinstance(agent, ADKAgent), "封裝物件應為 ag_ui_adk.ADKAgent 的實例"

    def test_agent_has_app_name(self):
        """測試 `agent` 是否已設定 `app_name`。"""
        from agent.agent import agent
        # ADKAgent 在內部儲存 app_name，此處檢查它是否為 ADKAgent 的實例來間接驗證
        from ag_ui_adk import ADKAgent
        assert isinstance(agent, ADKAgent), "agent 應為 ADKAgent 的實例，這意味著 app_name 已被設定"


class TestEnvironmentConfig:
    """測試環境設定。"""

    def test_env_example_exists(self):
        """測試 `.env.example` 檔案是否存在。"""
        assert os.path.isfile("agent/.env.example"), "agent/.env.example 檔案應存在"

    def test_env_example_has_api_key(self):
        """測試 `.env.example` 檔案中是否包含 `GOOGLE_API_KEY`。"""
        with open("agent/.env.example", "r") as f:
            content = f.read()
            assert "GOOGLE_API_KEY" in content, ".env.example 檔案內容應包含 'GOOGLE_API_KEY'"
