"""
Support Agent 的全方位 Pytest 測試套件。

執行方式：pytest tests/test_agent.py -v
"""

import pytest
from unittest.mock import Mock
from google.adk.evaluation.agent_evaluator import AgentEvaluator
from support_agent.agent import (
    root_agent,
    search_knowledge_base,
    create_ticket,
    check_ticket_status
)


class TestToolFunctions:
    """獨立測試工具函式"""

    def setup_method(self):
        """每個測試前的設定"""
        # 建立一個用於測試的模擬 ToolContext
        self.tool_context = Mock()
        self.tool_context.tickets = {}

    def test_search_knowledge_base_password_reset(self):
        """測試知識庫搜尋密碼重設"""
        result = search_knowledge_base("password reset", self.tool_context)

        assert result["status"] == "success"
        assert "password" in result["report"].lower()
        assert len(result["results"]) > 0
        assert "reset your password" in result["results"][0]["content"]

    def test_search_knowledge_base_refund_policy(self):
        """測試知識庫搜尋退款政策"""
        result = search_knowledge_base("refund", self.tool_context)

        assert result["status"] == "success"
        assert "refund" in result["report"].lower()
        assert len(result["results"]) > 0
        assert "30-day" in result["results"][0]["content"]

    def test_search_knowledge_base_shipping(self):
        """測試知識庫搜尋運送資訊"""
        result = search_knowledge_base("shipping", self.tool_context)

        assert result["status"] == "success"
        assert "shipping" in result["report"].lower()
        assert len(result["results"]) > 0
        assert "3-5 business days" in result["results"][0]["content"]

    def test_search_knowledge_base_not_found(self):
        """測試知識庫搜尋不存在的主題"""
        result = search_knowledge_base("nonexistent topic", self.tool_context)

        assert result["status"] == "success"
        assert "no articles found" in result["report"].lower()
        assert len(result["results"]) == 0

    def test_create_ticket_normal_priority(self):
        """測試建立一般優先級工單"""
        result = create_ticket("My account is locked", self.tool_context, "normal")

        assert result["status"] == "success"
        assert "created successfully" in result["report"]
        assert "normal" in result["report"]
        assert result["ticket"]["priority"] == "normal"
        assert result["ticket"]["status"] == "open"
        assert "ticket_id" in result["ticket"]

    def test_create_ticket_high_priority(self):
        """測試建立高優先級工單"""
        result = create_ticket("Website is down", self.tool_context, "high")

        assert result["status"] == "success"
        assert "high priority" in result["report"]
        assert result["ticket"]["priority"] == "high"
        assert "24 hours" in result["ticket"]["estimated_response"]

    def test_create_ticket_invalid_priority(self):
        """測試使用無效優先級建立工單"""
        result = create_ticket("Test issue", self.tool_context, "invalid")

        assert result["status"] == "error"
        assert "Invalid priority" in result["error"]
        assert "ticket" not in result

    def test_create_ticket_unique_ids(self):
        """測試工單 ID 的唯一性"""
        result1 = create_ticket("Issue 1", self.tool_context)
        result2 = create_ticket("Issue 2", self.tool_context)

        assert result1["ticket"]["ticket_id"] != result2["ticket"]["ticket_id"]

    def test_check_ticket_status_existing(self):
        """測試檢查現有工單的狀態"""
        # 先建立一張工單
        create_result = create_ticket("Test issue", self.tool_context)
        ticket_id = create_result["ticket"]["ticket_id"]

        # 檢查其狀態
        status_result = check_ticket_status(ticket_id, self.tool_context)

        assert status_result["status"] == "success"
        assert ticket_id in status_result["report"]
        assert status_result["ticket"]["status"] == "open"

    def test_check_ticket_status_not_found(self):
        """測試檢查不存在的工單狀態"""
        result = check_ticket_status("TICK-NONEXISTENT", self.tool_context)

        assert result["status"] == "error"
        assert "not found" in result["error"]
        assert "ticket" not in result


class TestAgentConfiguration:
    """測試 Agent 的設定與組態"""

    def test_agent_exists(self):
        """測試 Agent 是否已正確定義"""
        assert root_agent is not None
        assert hasattr(root_agent, 'name')

    def test_agent_name(self):
        """測試 Agent 名稱是否正確"""
        assert root_agent.name == "support_agent"

    def test_agent_has_tools(self):
        """測試 Agent 是否具備必要工具"""
        tool_names = [tool.__name__ for tool in root_agent.tools]
        assert "search_knowledge_base" in tool_names
        assert "create_ticket" in tool_names
        assert "check_ticket_status" in tool_names

    def test_agent_model(self):
        """測試 Agent 使用的模型是否正確"""
        assert root_agent.model == "gemini-2.0-flash-exp"

    def test_agent_has_description(self):
        """測試 Agent 是否有描述"""
        assert root_agent.description is not None
        assert "support" in root_agent.description.lower()

    def test_agent_has_instruction(self):
        """測試 Agent 是否有指令"""
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_agent_output_key(self):
        """測試 Agent 的輸出金鑰是否正確"""
        assert root_agent.output_key == "support_response"


class TestIntegration:
    """多步驟工作流程的整合測試"""

    def setup_method(self):
        """每個測試前的設定"""
        self.tool_context = Mock()
        self.tool_context.tickets = {}

    def test_knowledge_base_completeness(self):
        """測試知識庫是否涵蓋預期主題"""
        topics = ["password", "refund", "shipping", "account", "billing", "technical"]

        for topic in topics:
            result = search_knowledge_base(topic, self.tool_context)
            assert result["status"] == "success"
            assert len(result["results"]) > 0, f"No results found for topic: {topic}"

    def test_ticket_creation_workflow(self):
        """測試完整的工單建立與狀態檢查流程"""
        # 建立工單
        create_result = create_ticket("Website loading slowly", self.tool_context, "high")
        assert create_result["status"] == "success"

        ticket_id = create_result["ticket"]["ticket_id"]

        # 檢查狀態
        status_result = check_ticket_status(ticket_id, self.tool_context)
        assert status_result["status"] == "success"
        assert status_result["ticket"]["ticket_id"] == ticket_id
        assert status_result["ticket"]["status"] == "open"


class TestAgentEvaluation:
    """使用 AgentEvaluator 進行 Agent 評估測試"""

    @pytest.mark.asyncio
    async def test_simple_kb_search(self):
        """測試簡單知識庫搜尋評估"""
        await AgentEvaluator.evaluate(
            agent_module="support_agent",
            eval_dataset_file_path_or_dir="tests/simple.test.json",
            num_runs=1
        )

    @pytest.mark.asyncio
    async def test_ticket_creation(self):
        """測試工單建立流程評估"""
        await AgentEvaluator.evaluate(
            agent_module="support_agent",
            eval_dataset_file_path_or_dir="tests/ticket_creation.test.json",
            num_runs=1
        )

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self):
        """測試複雜的多輪對話"""
        await AgentEvaluator.evaluate(
            agent_module="support_agent",
            eval_dataset_file_path_or_dir="tests/complex.evalset.json",
            num_runs=1
        )
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
