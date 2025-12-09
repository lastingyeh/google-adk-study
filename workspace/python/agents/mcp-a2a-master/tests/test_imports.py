"""
測試所有模組的匯入功能。
確保沒有循環相依或遺失的套件。
"""

import pytest


class TestAgentImports:
    """測試 Agent 模組匯入。"""

    def test_host_agent_import(self):
        """測試 HostAgent 能否匯入。

        重點說明：
        1. 嘗試匯入 HostAgent 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from agents.host_agent.agent import HostAgent
            assert HostAgent is not None
        except ImportError as e:
            pytest.fail(f"匯入 HostAgent 失敗：{e}")

    def test_host_agent_executor_import(self):
        """測試 HostAgentExecutor 能否匯入。

        重點說明：
        1. 嘗試匯入 HostAgentExecutor 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from agents.host_agent.agent_executor import HostAgentExecutor
            assert HostAgentExecutor is not None
        except ImportError as e:
            pytest.fail(f"匯入 HostAgentExecutor 失敗：{e}")

    def test_website_builder_agent_import(self):
        """測試 WebsiteBuilderSimple 能否匯入。

        重點說明：
        1. 嘗試匯入 WebsiteBuilderSimple 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from agents.website_builder_simple.agent import WebsiteBuilderSimple
            assert WebsiteBuilderSimple is not None
        except ImportError as e:
            pytest.fail(f"匯入 WebsiteBuilderSimple 失敗：{e}")

    def test_website_builder_executor_import(self):
        """測試 WebsiteBuilderSimpleAgentExecutor 能否匯入。

        重點說明：
        1. 嘗試匯入 WebsiteBuilderSimpleAgentExecutor 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from agents.website_builder_simple.agent_executor import (
                WebsiteBuilderSimpleAgentExecutor,
            )
            assert WebsiteBuilderSimpleAgentExecutor is not None
        except ImportError as e:
            pytest.fail(f"匯入 WebsiteBuilderSimpleAgentExecutor 失敗：{e}")


class TestUtilitiesImports:
    """測試 Utilities 模組匯入。"""

    def test_agent_connector_import(self):
        """測試 AgentConnector 能否匯入。

        重點說明：
        1. 嘗試匯入 AgentConnector 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from utilities.a2a.agent_connect import AgentConnector
            assert AgentConnector is not None
        except ImportError as e:
            pytest.fail(f"匯入 AgentConnector 失敗：{e}")

    def test_agent_discovery_import(self):
        """測試 AgentDiscovery 能否匯入。

        重點說明：
        1. 嘗試匯入 AgentDiscovery 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from utilities.a2a.agent_discovery import AgentDiscovery
            assert AgentDiscovery is not None
        except ImportError as e:
            pytest.fail(f"匯入 AgentDiscovery 失敗：{e}")

    def test_mcp_connector_import(self):
        """測試 MCPConnector 能否匯入。

        重點說明：
        1. 嘗試匯入 MCPConnector 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from utilities.mcp.mcp_connect import MCPConnector
            assert MCPConnector is not None
        except ImportError as e:
            pytest.fail(f"匯入 MCPConnector 失敗：{e}")

    def test_mcp_discovery_import(self):
        """測試 MCPDiscovery 能否匯入。

        重點說明：
        1. 嘗試匯入 MCPDiscovery 類別
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from utilities.mcp.mcp_discovery import MCPDiscovery
            assert MCPDiscovery is not None
        except ImportError as e:
            pytest.fail(f"匯入 MCPDiscovery 失敗：{e}")

    def test_file_loader_import(self):
        """測試 file_loader 能否匯入。

        重點說明：
        1. 嘗試匯入 load_instructions_file 函式
        2. 驗證匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from utilities.common.file_loader import load_instructions_file
            assert load_instructions_file is not None
        except ImportError as e:
            pytest.fail(f"匯入 load_instructions_file 失敗：{e}")


class TestDependenciesImports:
    """測試外部相依套件匯入。"""

    def test_adk_dependencies_import(self):
        """測試 Google ADK 相依套件能否匯入。

        重點說明：
        1. 嘗試匯入 Google ADK 相關模組 (LlmAgent, Runner, FunctionTool, types)
        2. 驗證所有模組匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from google.adk.agents import LlmAgent
            from google.adk import Runner
            from google.adk.tools.function_tool import FunctionTool
            from google.genai import types
            assert all([LlmAgent, Runner, FunctionTool, types])
        except ImportError as e:
            pytest.fail(f"匯入 Google ADK 相依套件失敗：{e}")

    def test_a2a_sdk_dependencies_import(self):
        """測試 A2A SDK 相依套件能否匯入。

        重點說明：
        1. 嘗試匯入 A2A SDK 相關模組 (AgentCard, Task, TaskState, A2AClient, AgentExecutor)
        2. 驗證所有模組匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from a2a.types import AgentCard, Task, TaskState
            from a2a.client import A2AClient
            from a2a.server.agent_execution import AgentExecutor
            assert all([AgentCard, Task, TaskState, A2AClient, AgentExecutor])
        except ImportError as e:
            pytest.fail(f"匯入 A2A SDK 相依套件失敗：{e}")

    def test_mcp_dependencies_import(self):
        """測試 MCP 相依套件能否匯入。

        重點說明：
        1. 嘗試匯入 MCP 相關模組 (MCPToolset, StdioConnectionParams, StdioServerParameters)
        2. 驗證所有模組匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
            from google.adk.tools.mcp_tool import StdioConnectionParams
            from mcp import StdioServerParameters
            assert all([MCPToolset, StdioConnectionParams, StdioServerParameters])
        except ImportError as e:
            pytest.fail(f"匯入 MCP 相依套件失敗：{e}")

    def test_other_dependencies_import(self):
        """測試其他相依套件能否匯入。

        重點說明：
        1. 嘗試匯入其他必要套件 (httpx, asyncio, pydantic, rich)
        2. 驗證所有套件匯入成功
        3. 若匯入失敗，使用 pytest.fail 報告錯誤
        """
        try:
            import httpx
            import asyncio
            from pydantic import BaseModel
            from rich import print as rprint
            assert all([httpx, asyncio, BaseModel, rprint])
        except ImportError as e:
            pytest.fail(f"匯入其他相依套件失敗：{e}")
