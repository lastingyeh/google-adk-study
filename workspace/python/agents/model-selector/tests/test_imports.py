# 教學 22：模型選擇與優化 - 匯入測試
# 驗證所有必要的匯入是否能正常運作

import pytest


class TestImports:
    """測試所有 ADK 匯入是否能正常運作。"""

    def test_google_adk_agents_import(self):
        """測試我們是否可以從 google.adk.agents 匯入 Agent。"""
        try:
            from google.adk.agents import Agent
            assert Agent is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Agent from google.adk.agents: {e}")

    def test_google_adk_runner_import(self):
        """測試我們是否可以從 google.adk.runners 匯入 Runner。"""
        try:
            from google.adk.runners import Runner
            assert Runner is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Runner from google.adk.runners: {e}")

    def test_google_genai_types_import(self):
        """測試我們是否可以從 google.genai 匯入 types。"""
        try:
            from google.genai import types
            assert types is not None
        except ImportError as e:
            pytest.fail(f"Failed to import types from google.genai: {e}")

    def test_tool_context_import(self):
        """測試我們是否可以匯入 ToolContext。"""
        try:
            from google.adk.tools.tool_context import ToolContext
            assert ToolContext is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ToolContext: {e}")

    def test_model_selector_import(self):
        """測試我們是否可以匯入 model_selector 模組。"""
        try:
            import model_selector
            assert model_selector is not None
        except ImportError as e:
            pytest.fail(f"Failed to import model_selector module: {e}")

    def test_model_selector_agent_import(self):
        """測試我們是否可以從 model_selector 匯入 agent 模組。"""
        try:
            from model_selector import agent
            assert agent is not None
        except ImportError as e:
            pytest.fail(f"Failed to import agent from model_selector: {e}")

    def test_root_agent_exists(self):
        """測試 root_agent 是否在 agent 模組中被定義。"""
        try:
            from model_selector.agent import root_agent
            assert root_agent is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Failed to import root_agent: {e}")

    def test_model_selector_class_import(self):
        """測試 ModelSelector 類別是否可以被匯入。"""
        try:
            from model_selector.agent import ModelSelector
            assert ModelSelector is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Failed to import ModelSelector: {e}")

    def test_model_benchmark_import(self):
        """測試 ModelBenchmark 資料類別是否可以被匯入。"""
        try:
            from model_selector.agent import ModelBenchmark
            assert ModelBenchmark is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Failed to import ModelBenchmark: {e}")

    def test_tool_functions_import(self):
        """測試工具函式是否可以被匯入。"""
        try:
            from model_selector.agent import (
                recommend_model_for_use_case,
                get_model_info
            )
            assert recommend_model_for_use_case is not None
            assert get_model_info is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Failed to import tool functions: {e}")
