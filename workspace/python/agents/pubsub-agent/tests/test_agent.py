# 教學範例 34：文件處理代理 - 代理測試
# 驗證多重代理設定與 JSON 輸出強制執行
#
# 重點說明：
# 此測試模組涵蓋了文件處理代理系統的核心配置驗證。
# 主要測試範圍包括：
# 1. Root Agent (協調者) 的屬性、模型與指令設定。
# 2. 四個子代理 (財務、技術、銷售、行銷) 的獨立設定與輸出 Schema。
# 3. 驗證子代理是否正確包裝為工具 (AgentTool)。
# 4. 驗證 Pydantic 輸出模型 (Schema) 的欄位定義。
# 5. 整合測試以確保代理之間的路由邏輯與結構正確。

import pytest
from typing import Dict, Any


class TestAgentConfiguration:
    """測試協調代理是否已正確設定。"""

    def test_root_agent_import(self):
        """測試 root_agent 是否可以被匯入。"""
        from pubsub_agent.agent import root_agent
        assert root_agent is not None

    def test_agent_is_llm_agent_instance(self):
        """測試 root_agent 是否為 LlmAgent 的實例。"""
        from pubsub_agent.agent import root_agent
        from google.adk.agents import LlmAgent

        assert isinstance(root_agent, LlmAgent)

    def test_agent_name(self):
        """測試代理是否具有正確的名稱。"""
        from pubsub_agent.agent import root_agent

        assert hasattr(root_agent, 'name')
        assert root_agent.name == "pubsub_processor"

    def test_agent_model_is_gemini_25_flash(self):
        """測試代理是否使用 gemini-2.5-flash 模型。"""
        from pubsub_agent.agent import root_agent

        assert hasattr(root_agent, 'model')
        assert root_agent.model == "gemini-2.5-flash"

    def test_agent_description(self):
        """測試代理是否具有描述。"""
        from pubsub_agent.agent import root_agent

        assert hasattr(root_agent, 'description')
        assert "event-driven" in root_agent.description.lower()
        assert "document processing" in root_agent.description.lower()
        assert "coordinator" in root_agent.description.lower()

    def test_agent_instruction(self):
        """測試代理是否具有指令。"""
        from pubsub_agent.agent import root_agent

        assert hasattr(root_agent, 'instruction')
        # Check for key routing responsibilities
        # 檢查關鍵路由職責
        assert "financial" in root_agent.instruction.lower()
        assert "technical" in root_agent.instruction.lower()
        assert "sales" in root_agent.instruction.lower()
        assert "marketing" in root_agent.instruction.lower()

    def test_agent_has_tools(self):
        """測試協調代理是否擁有子代理工具。"""
        from pubsub_agent.agent import root_agent

        assert hasattr(root_agent, 'tools')
        assert root_agent.tools is not None
        # Should have 4 sub-agent tools (financial, technical, sales, marketing)
        # 應具有 4 個子代理工具（財務、技術、銷售、行銷）
        assert len(root_agent.tools) == 4


class TestSubAgentConfiguration:
    """測試每個子代理是否已正確設定。"""

    def test_financial_agent_import(self):
        """測試 financial_agent 是否可以被匯入。"""
        from pubsub_agent.agent import financial_agent
        assert financial_agent is not None

    def test_financial_agent_is_llm_agent(self):
        """測試 financial_agent 是否為 LlmAgent 的實例。"""
        from pubsub_agent.agent import financial_agent
        from google.adk.agents import LlmAgent

        assert isinstance(financial_agent, LlmAgent)

    def test_financial_agent_configuration(self):
        """測試 financial_agent 是否具有正確的設定。"""
        from pubsub_agent.agent import financial_agent

        assert financial_agent.name == "financial_analyzer"
        assert financial_agent.model == "gemini-2.5-flash"
        assert "financial" in financial_agent.description.lower()

    def test_financial_agent_output_schema(self):
        """測試 financial_agent 是否設定了 FinancialAnalysisOutput 架構。"""
        from pubsub_agent.agent import financial_agent, FinancialAnalysisOutput

        # Sub-agents enforce JSON output using Pydantic schemas
        # 子代理使用 Pydantic 架構強制執行 JSON 輸出
        assert hasattr(financial_agent, 'output_schema')
        assert financial_agent.output_schema == FinancialAnalysisOutput

    def test_technical_agent_import(self):
        """測試 technical_agent 是否可以被匯入。"""
        from pubsub_agent.agent import technical_agent
        assert technical_agent is not None

    def test_technical_agent_configuration(self):
        """測試 technical_agent 是否具有正確的設定。"""
        from pubsub_agent.agent import technical_agent

        assert technical_agent.name == "technical_analyzer"
        assert technical_agent.model == "gemini-2.5-flash"
        assert "technical" in technical_agent.description.lower()

    def test_technical_agent_output_schema(self):
        """測試 technical_agent 是否設定了 TechnicalAnalysisOutput 架構。"""
        from pubsub_agent.agent import technical_agent, TechnicalAnalysisOutput

        # Sub-agents enforce JSON output using Pydantic schemas
        # 子代理使用 Pydantic 架構強制執行 JSON 輸出
        assert hasattr(technical_agent, 'output_schema')
        assert technical_agent.output_schema == TechnicalAnalysisOutput

    def test_sales_agent_import(self):
        """測試 sales_agent 是否可以被匯入。"""
        from pubsub_agent.agent import sales_agent
        assert sales_agent is not None

    def test_sales_agent_configuration(self):
        """測試 sales_agent 是否具有正確的設定。"""
        from pubsub_agent.agent import sales_agent

        assert sales_agent.name == "sales_analyzer"
        assert sales_agent.model == "gemini-2.5-flash"
        assert "sales" in sales_agent.description.lower()

    def test_sales_agent_output_schema(self):
        """測試 sales_agent 是否設定了 SalesAnalysisOutput 架構。"""
        from pubsub_agent.agent import sales_agent, SalesAnalysisOutput

        # Sub-agents enforce JSON output using Pydantic schemas
        # 子代理使用 Pydantic 架構強制執行 JSON 輸出
        assert hasattr(sales_agent, 'output_schema')
        assert sales_agent.output_schema == SalesAnalysisOutput

    def test_marketing_agent_import(self):
        """測試 marketing_agent 是否可以被匯入。"""
        from pubsub_agent.agent import marketing_agent
        assert marketing_agent is not None

    def test_marketing_agent_configuration(self):
        """測試 marketing_agent 是否具有正確的設定。"""
        from pubsub_agent.agent import marketing_agent

        assert marketing_agent.name == "marketing_analyzer"
        assert marketing_agent.model == "gemini-2.5-flash"
        assert "marketing" in marketing_agent.description.lower()

    def test_marketing_agent_output_schema(self):
        """測試 marketing_agent 是否設定了 MarketingAnalysisOutput 架構。"""
        from pubsub_agent.agent import marketing_agent, MarketingAnalysisOutput

        # Sub-agents enforce JSON output using Pydantic schemas
        # 子代理使用 Pydantic 架構強制執行 JSON 輸出
        assert hasattr(marketing_agent, 'output_schema')
        assert marketing_agent.output_schema == MarketingAnalysisOutput


class TestAgentToolsAsSubAgents:
    """測試子代理是否正確包裝為工具。"""

    def test_financial_tool_import(self):
        """測試 financial_tool 是否可以被匯入。"""
        from pubsub_agent.agent import financial_tool
        assert financial_tool is not None

    def test_financial_tool_is_agent_tool(self):
        """測試 financial_tool 是否為 AgentTool 的實例。"""
        from pubsub_agent.agent import financial_tool
        from google.adk.tools import AgentTool

        assert isinstance(financial_tool, AgentTool)

    def test_technical_tool_is_agent_tool(self):
        """測試 technical_tool 是否為 AgentTool 的實例。"""
        from pubsub_agent.agent import technical_tool
        from google.adk.tools import AgentTool

        assert isinstance(technical_tool, AgentTool)

    def test_sales_tool_is_agent_tool(self):
        """測試 sales_tool 是否為 AgentTool 的實例。"""
        from pubsub_agent.agent import sales_tool
        from google.adk.tools import AgentTool

        assert isinstance(sales_tool, AgentTool)

    def test_marketing_tool_is_agent_tool(self):
        """測試 marketing_tool 是否為 AgentTool 的實例。"""
        from pubsub_agent.agent import marketing_tool
        from google.adk.tools import AgentTool

        assert isinstance(marketing_tool, AgentTool)


class TestOutputSchemas:
    """測試 Pydantic 輸出架構是否正確定義。"""

    def test_entity_extraction_schema_imports(self):
        """測試 EntityExtraction 架構是否可以被匯入。"""
        from pubsub_agent.agent import EntityExtraction
        assert EntityExtraction is not None

    def test_document_summary_schema_imports(self):
        """測試 DocumentSummary 架構是否可以被匯入。"""
        from pubsub_agent.agent import DocumentSummary
        assert DocumentSummary is not None

    def test_financial_analysis_output_schema(self):
        """測試 FinancialAnalysisOutput 是否具有正確的欄位。"""
        from pubsub_agent.agent import FinancialAnalysisOutput
        from pubsub_agent.agent import DocumentSummary, EntityExtraction

        # Test that it has required fields
        # 測試它是否具有必要的欄位
        assert hasattr(FinancialAnalysisOutput, 'model_fields')
        fields = FinancialAnalysisOutput.model_fields
        assert 'summary' in fields
        assert 'entities' in fields
        assert 'financial_metrics' in fields
        assert 'fiscal_periods' in fields
        assert 'recommendations' in fields

    def test_technical_analysis_output_schema(self):
        """測試 TechnicalAnalysisOutput 是否具有正確的欄位。"""
        from pubsub_agent.agent import TechnicalAnalysisOutput

        fields = TechnicalAnalysisOutput.model_fields
        assert 'summary' in fields
        assert 'entities' in fields
        assert 'technologies' in fields
        assert 'components' in fields
        assert 'recommendations' in fields

    def test_sales_analysis_output_schema(self):
        """測試 SalesAnalysisOutput 是否具有正確的欄位。"""
        from pubsub_agent.agent import SalesAnalysisOutput

        fields = SalesAnalysisOutput.model_fields
        assert 'summary' in fields
        assert 'entities' in fields
        assert 'deals' in fields
        assert 'pipeline_value' in fields
        assert 'recommendations' in fields

    def test_marketing_analysis_output_schema(self):
        """測試 MarketingAnalysisOutput 是否具有正確的欄位。"""
        from pubsub_agent.agent import MarketingAnalysisOutput

        fields = MarketingAnalysisOutput.model_fields
        assert 'summary' in fields
        assert 'entities' in fields
        assert 'campaigns' in fields
        assert 'metrics' in fields
        assert 'recommendations' in fields

    def test_entity_extraction_instantiation(self):
        """測試 EntityExtraction 是否可以被實例化。"""
        from pubsub_agent.agent import EntityExtraction

        entity = EntityExtraction(
            dates=["2024-10-08"],
            currency_amounts=["$1,200.50"],
            percentages=["35%"],
            numbers=["100"]
        )

        assert entity.dates == ["2024-10-08"]
        assert entity.currency_amounts == ["$1,200.50"]
        assert entity.percentages == ["35%"]
        assert entity.numbers == ["100"]

    def test_document_summary_instantiation(self):
        """測試 DocumentSummary 是否可以被實例化。"""
        from pubsub_agent.agent import DocumentSummary

        summary = DocumentSummary(
            main_points=["Point 1", "Point 2"],
            key_insight="Main insight",
            summary="Brief summary"
        )

        assert summary.main_points == ["Point 1", "Point 2"]
        assert summary.key_insight == "Main insight"
        assert summary.summary == "Brief summary"


class TestAgentFunctionality:
    """測試基本的代理功能。"""

    def test_root_agent_creation(self):
        """測試 root_agent 是否可以被建立且無錯誤。"""
        try:
            from pubsub_agent.agent import root_agent
            assert root_agent is not None
            assert hasattr(root_agent, 'name')
        except Exception as e:
            pytest.fail(f"Root agent creation failed: {e}")

    def test_all_sub_agents_created(self):
        """測試所有子代理是否都已建立且無錯誤。"""
        try:
            from pubsub_agent.agent import (
                financial_agent,
                technical_agent,
                sales_agent,
                marketing_agent
            )
            assert financial_agent is not None
            assert technical_agent is not None
            assert sales_agent is not None
            assert marketing_agent is not None
        except Exception as e:
            pytest.fail(f"Sub-agent creation failed: {e}")

    def test_all_tools_created(self):
        """測試所有 AgentTools 是否都已建立且無錯誤。"""
        try:
            from pubsub_agent.agent import (
                financial_tool,
                technical_tool,
                sales_tool,
                marketing_tool
            )
            assert financial_tool is not None
            assert technical_tool is not None
            assert sales_tool is not None
            assert marketing_tool is not None
        except Exception as e:
            pytest.fail(f"Tool creation failed: {e}")

    def test_coordinator_agent_has_all_tools(self):
        """測試協調代理是否包含所有子代理工具。"""
        from pubsub_agent.agent import root_agent

        assert len(root_agent.tools) == 4

    def test_coordinator_instructions_include_routing(self):
        """測試協調者指令是否提及路由邏輯。"""
        from pubsub_agent.agent import root_agent

        instruction = root_agent.instruction.lower()
        assert "route" in instruction
        assert "financial" in instruction
        assert "technical" in instruction
        assert "sales" in instruction
        assert "marketing" in instruction


@pytest.mark.integration
class TestAgentIntegration:
    """多重代理架構的整合測試。"""

    def test_root_agent_can_be_instantiated(self):
        """測試 root_agent 是否可以被實例化且無錯誤。"""
        try:
            from pubsub_agent.agent import root_agent
            assert root_agent is not None
        except Exception as e:
            pytest.fail(f"Agent instantiation failed: {e}")

    def test_sub_agents_have_output_schemas(self):
        """測試子代理是否設定了 JSON 輸出架構。"""
        from pubsub_agent.agent import (
            financial_agent,
            technical_agent,
            sales_agent,
            marketing_agent,
            FinancialAnalysisOutput,
            TechnicalAnalysisOutput,
            SalesAnalysisOutput,
            MarketingAnalysisOutput
        )

        # Verify each sub-agent has its corresponding output schema
        # 驗證每個子代理是否具有對應的輸出架構
        assert financial_agent.output_schema == FinancialAnalysisOutput
        assert technical_agent.output_schema == TechnicalAnalysisOutput
        assert sales_agent.output_schema == SalesAnalysisOutput
        assert marketing_agent.output_schema == MarketingAnalysisOutput

    def test_coordinator_routing_strategy(self):
        """測試協調者是否具有適當的路由指令。"""
        from pubsub_agent.agent import root_agent

        instruction = root_agent.instruction
        # Should have all routing keywords
        # 應包含所有路由關鍵字
        assert "financial" in instruction.lower()
        assert "technical" in instruction.lower()
        assert "sales" in instruction.lower()
        assert "marketing" in instruction.lower()
        # Should mention decision framework
        # 應提及決策框架
        assert "keywords" in instruction.lower() or "framework" in instruction.lower()
