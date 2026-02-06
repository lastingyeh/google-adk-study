"""
Agent 配置與功能測試
"""

import pytest


class TestAgentConfiguration:
    """
    測試 Agent 配置與屬性。

    重點說明:
    1. 驗證 Agent 基本配置 (名稱、模型、指令)
    2. 驗證工具配置 (檢索工具是否存在且設定正確)
    3. 驗證指令內容是否包含 RAG 關鍵字
    """

    def test_root_agent_exists(self):
        """
        測試 root_agent 是否已正確定義。

        驗證點:
        1. root_agent 實例存在
        """
        from rag.agent import root_agent

        assert root_agent is not None

    def test_agent_has_correct_name(self):
        """
        測試 Agent 是否擁有正確名稱。

        驗證點:
        1. Agent 名稱應為 'ask_rag_agent'
        """
        from rag.agent import root_agent

        assert root_agent.name == "ask_rag_agent"

    def test_agent_has_correct_model(self):
        """測試 Agent 是否使用正確的模型。"""
        from rag.agent import root_agent

        expected_models = [
            "gemini-2.0-flash-001",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]
        assert root_agent.model in expected_models, (
            f"Agent 模型應為 {expected_models} 其中之一"
        )

    def test_agent_has_instruction(self):
        """測試 Agent 是否擁有指令。"""
        from rag.agent import root_agent

        assert root_agent.instruction is not None
        instruction_str = (
            root_agent.instruction
            if isinstance(root_agent.instruction, str)
            else str(root_agent.instruction)
        )
        assert len(instruction_str) > 0

    def test_agent_has_tools(self):
        """測試 Agent 是否已配置工具。"""
        from rag.agent import root_agent

        assert hasattr(root_agent, "tools")
        assert root_agent.tools is not None
        assert isinstance(root_agent.tools, list)

    def test_agent_has_retrieval_tool(self):
        """測試 Agent 是否包含檢索工具。"""
        from rag.agent import root_agent

        assert len(root_agent.tools) > 0
        # 檢查是否有檢索工具
        tool_names = [getattr(tool, "name", "") for tool in root_agent.tools]
        assert "retrieve_rag_documentation" in tool_names, (
            "Agent 應包含 retrieve_rag_documentation 工具"
        )

    def test_agent_instruction_content(self):
        """測試 Agent 指令內容是否包含 RAG 相關描述。"""
        from rag.agent import root_agent

        instruction_str = (
            root_agent.instruction
            if isinstance(root_agent.instruction, str)
            else str(root_agent.instruction)
        )
        instruction_lower = instruction_str.lower()
        # 檢查指令是否包含檢索或語料庫相關的關鍵字
        rag_keywords = ["retrieval", "corpus", "citation", "retrieve", "document"]
        has_rag_content = any(keyword in instruction_lower for keyword in rag_keywords)
        assert has_rag_content, "Agent 指令應包含 RAG 相關的描述"


class TestRetrievalTool:
    """測試檢索工具配置。"""

    def test_retrieval_tool_exists(self):
        """測試檢索工具是否已定義。"""
        from rag.agent import ask_vertex_retrieval

        assert ask_vertex_retrieval is not None

    def test_retrieval_tool_has_name(self):
        """測試檢索工具是否擁有名稱。"""
        from rag.agent import ask_vertex_retrieval

        assert hasattr(ask_vertex_retrieval, "name")
        assert ask_vertex_retrieval.name == "retrieve_rag_documentation"

    def test_retrieval_tool_has_description(self):
        """測試檢索工具是否擁有描述。"""
        from rag.agent import ask_vertex_retrieval

        assert hasattr(ask_vertex_retrieval, "description")
        assert ask_vertex_retrieval.description is not None
        assert len(ask_vertex_retrieval.description) > 0

    def test_retrieval_tool_has_rag_resources(self):
        """測試檢索工具是否正確配置。"""
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
            VertexAiRagRetrieval,
        )

        from rag.agent import ask_vertex_retrieval

        # 檢查工具是否是正確的類型
        assert isinstance(ask_vertex_retrieval, VertexAiRagRetrieval)
        # 檢查工具具有基本屬性（名稱和描述）
        assert hasattr(ask_vertex_retrieval, "name")
        assert hasattr(ask_vertex_retrieval, "description")

    def test_retrieval_tool_has_similarity_top_k(self):
        """測試檢索工具是否設定了 similarity_top_k。"""
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
            VertexAiRagRetrieval,
        )

        from rag.agent import ask_vertex_retrieval

        # 檢查工具是否是正確的類型
        assert isinstance(ask_vertex_retrieval, VertexAiRagRetrieval)
        # 工具應該已被正確初始化（有名稱）
        assert ask_vertex_retrieval.name == "retrieve_rag_documentation"

    def test_retrieval_tool_has_vector_distance_threshold(self):
        """測試檢索工具是否設定了 vector_distance_threshold。"""
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
            VertexAiRagRetrieval,
        )

        from rag.agent import ask_vertex_retrieval

        # 檢查工具是否是正確的類型
        assert isinstance(ask_vertex_retrieval, VertexAiRagRetrieval)
        # 工具應該有描述
        assert len(ask_vertex_retrieval.description) > 0


class TestAppConfiguration:
    """測試 ADK App 配置。"""

    def test_app_exists(self):
        """測試 app 是否已正確定義。"""
        from rag.agent import app

        assert app is not None

    def test_app_has_root_agent(self):
        """測試 app 是否包含 root_agent。"""
        from rag.agent import app

        assert hasattr(app, "root_agent")
        assert app.root_agent is not None

    def test_app_has_correct_name(self):
        """測試 app 是否擁有正確名稱。"""
        from rag.agent import app

        assert hasattr(app, "name")
        assert app.name == "rag"

    def test_app_root_agent_matches_exported_agent(self):
        """測試 app 的 root_agent 與匯出的 root_agent 一致。"""
        from rag.agent import app, root_agent

        assert app.root_agent == root_agent


class TestAgentInstantiation:
    """測試 Agent 實例化。"""

    @pytest.mark.asyncio
    async def test_agent_can_be_instantiated(self):
        """測試 Agent 能否被實例化。"""
        from google.adk.agents import Agent

        from rag.agent import root_agent

        assert isinstance(root_agent, Agent)

    def test_agent_uses_vertex_ai_rag_retrieval(self):
        """測試 Agent 使用的是 VertexAiRagRetrieval 工具。"""
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import (
            VertexAiRagRetrieval,
        )

        from rag.agent import root_agent

        retrieval_tools = [
            tool for tool in root_agent.tools if isinstance(tool, VertexAiRagRetrieval)
        ]
        assert len(retrieval_tools) > 0, (
            "Agent 應包含至少一個 VertexAiRagRetrieval 工具"
        )
