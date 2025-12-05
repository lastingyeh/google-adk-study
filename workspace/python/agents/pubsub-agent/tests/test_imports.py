# 教學範例 34：匯入與模組測試
# 驗證所有匯入和模組結構是否正確
#
# 重點說明：
# 此測試模組確保專案的模組結構符合預期，且所有關鍵組件皆可正確匯入。
# 主要測試範圍包括：
# 1. 驗證 pubsub_agent 模組及其子模組的存在性。
# 2. 確保 Google ADK 與專案內的 Pydantic Schema 可被正確匯入。
# 3. 檢查模組匯出的物件類型是否正確 (如 LlmAgent, Pydantic Models)。
# 4. 驗證 __init__.py 是否正確暴露了 agent 模組。

import pytest
import sys


class TestModuleStructure:
    """測試模組結構是否正確。"""

    def test_pubsub_agent_module_exists(self):
        """測試 pubsub_agent 模組是否存在。"""
        import pubsub_agent
        assert pubsub_agent is not None

    def test_pubsub_agent_agent_module_exists(self):
        """測試 pubsub_agent.agent 模組是否存在。"""
        import pubsub_agent.agent
        assert pubsub_agent.agent is not None

    def test_agent_module_has_root_agent(self):
        """測試 agent 模組是否匯出 root_agent。"""
        from pubsub_agent import agent
        assert hasattr(agent, 'root_agent')

    def test_root_agent_is_exported(self):
        """測試 root_agent 是否可以直接匯入。"""
        from pubsub_agent.agent import root_agent
        assert root_agent is not None


class TestImports:
    """測試所有必要的匯入是否正常運作。"""

    def test_google_adk_agents_import(self):
        """測試 google.adk.agents 是否可以被匯入。"""
        from google.adk.agents import Agent
        assert Agent is not None

    def test_structured_output_schemas_import(self):
        """測試 Pydantic 輸出架構是否可以被匯入。"""
        from pubsub_agent.agent import (
            DocumentSummary,
            EntityExtraction,
            FinancialAnalysisOutput,
            TechnicalAnalysisOutput,
            SalesAnalysisOutput,
            MarketingAnalysisOutput
        )
        assert DocumentSummary is not None
        assert EntityExtraction is not None
        assert FinancialAnalysisOutput is not None
        assert TechnicalAnalysisOutput is not None
        assert SalesAnalysisOutput is not None
        assert MarketingAnalysisOutput is not None

    def test_agent_import(self):
        """測試 agent 是否可以被匯入。"""
        from pubsub_agent.agent import root_agent
        assert root_agent is not None


class TestModuleExports:
    """測試模組是否匯出所需的項目。"""

    def test_agent_module_exports_agent_instance(self):
        """測試 agent 模組是否匯出 Agent 實例。"""
        from pubsub_agent.agent import root_agent
        from google.adk.agents import LlmAgent
        assert isinstance(root_agent, LlmAgent)

    def test_structured_schemas_are_pydantic_models(self):
        """測試輸出架構是否為 Pydantic 模型。"""
        from pubsub_agent.agent import (
            DocumentSummary,
            EntityExtraction,
            FinancialAnalysisOutput,
            TechnicalAnalysisOutput,
            SalesAnalysisOutput,
            MarketingAnalysisOutput
        )
        from pydantic import BaseModel

        assert issubclass(DocumentSummary, BaseModel)
        assert issubclass(EntityExtraction, BaseModel)
        assert issubclass(FinancialAnalysisOutput, BaseModel)
        assert issubclass(TechnicalAnalysisOutput, BaseModel)
        assert issubclass(SalesAnalysisOutput, BaseModel)
        assert issubclass(MarketingAnalysisOutput, BaseModel)

    def test_agent_uses_gemini_2_5_flash(self):
        """測試代理是否設定使用 gemini-2.5-flash 模型。"""
        from pubsub_agent.agent import root_agent
        assert root_agent.model == "gemini-2.5-flash"

    def test_agent_has_descriptive_instruction(self):
        """測試代理是否具有完整的指令。"""
        from pubsub_agent.agent import root_agent
        assert root_agent.instruction is not None
        assert "extract" in root_agent.instruction.lower()
        assert "structured" in root_agent.instruction.lower()


class TestPackageInit:
    """測試 __init__.py 結構。"""

    def test_package_init_exists(self):
        """測試 __init__.py 是否存在且可以被匯入。"""
        import pubsub_agent
        # If we got here, __init__.py was successfully imported
        # 如果執行到這裡，表示 __init__.py 已成功匯入
        assert True

    def test_agent_module_imported_in_init(self):
        """測試 agent 模組是否在 __init__.py 中被匯入。"""
        import pubsub_agent
        assert hasattr(pubsub_agent, 'agent')
