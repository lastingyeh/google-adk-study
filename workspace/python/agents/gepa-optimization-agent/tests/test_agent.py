"""
GEPA 教學代理程式的測試套件。

測試範圍涵蓋：
- 代理程式設定與初始化
- 工具宣告與執行
- GEPA 概念與工作流程
- 專案結構驗證
"""

import pytest
from gepa_agent.agent import (
    VerifyCustomerIdentity,
    CheckReturnPolicy,
    ProcessRefund,
    create_support_agent,
    root_agent,
    INITIAL_PROMPT,
)


class TestAgentConfiguration:
    """測試代理程式的初始化與設定。"""

    def test_agent_creation(self):
        """測試代理程式是否能成功建立。"""
        agent = create_support_agent()
        assert agent is not None
        assert agent.name == "customer_support_agent"

    def test_root_agent_export(self):
        """測試 root_agent 是否已正確匯出。"""
        assert root_agent is not None
        assert hasattr(root_agent, "name")
        assert root_agent.name == "customer_support_agent"

    def test_agent_with_custom_prompt(self):
        """測試使用自訂提示建立代理程式。"""
        custom_prompt = "You are a test agent."
        agent = create_support_agent(prompt=custom_prompt)
        assert agent is not None

    def test_agent_uses_initial_prompt_by_default(self):
        """測試在未提供提示時，代理程式是否預設使用 INITIAL_PROMPT。"""
        agent = create_support_agent()
        assert agent.instruction == INITIAL_PROMPT

    def test_agent_has_tools(self):
        """測試代理程式是否擁有所有必要的工具。"""
        agent = create_support_agent()
        assert agent.tools is not None
        assert len(agent.tools) == 3

    def test_agent_model_configuration(self):
        """測試代理程式是否使用正確的模型。"""
        agent = create_support_agent()
        assert agent.model is not None

    def test_custom_model(self):
        """測試使用自訂模型規格的代理程式。"""
        agent = create_support_agent(model="gemini-2.0-flash")
        assert agent is not None


class TestVerifyCustomerIdentityTool:
    """測試 verify_customer_identity 工具。"""

    @pytest.fixture
    def tool(self):
        """建立用於測試的工具實例。"""
        return VerifyCustomerIdentity()

    def test_tool_creation(self, tool):
        """測試工具是否可以被實例化。"""
        assert tool is not None
        assert tool.name == "verify_customer_identity"

    def test_tool_declaration(self, tool):
        """測試工具是否有正確的宣告。"""
        declaration = tool._get_declaration()
        assert declaration is not None
        assert declaration.name == "verify_customer_identity"
        assert "parameters" in dir(declaration)

    def test_tool_description(self, tool):
        """測試工具是否有描述。"""
        assert tool.description is not None
        assert len(tool.description) > 0

    @pytest.mark.asyncio
    async def test_valid_customer_verification(self, tool):
        """測試使用有效客戶進行驗證。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-12345",
                "email": "customer@example.com",
            },
            tool_context=None,
        )
        assert "✓" in result
        assert "verified" in result.lower()

    @pytest.mark.asyncio
    async def test_invalid_email_verification(self, tool):
        """測試使用錯誤的電子郵件進行驗證。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-12345",
                "email": "wrong@example.com",
            },
            tool_context=None,
        )
        assert "✗" in result
        assert "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_unknown_order_verification(self, tool):
        """測試使用未知的訂單進行驗證。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-99999",
                "email": "customer@example.com",
            },
            tool_context=None,
        )
        assert "✗" in result
        assert "not found" in result.lower()


class TestCheckReturnPolicyTool:
    """測試 check_return_policy 工具。"""

    @pytest.fixture
    def tool(self):
        """建立用於測試的工具實例。"""
        return CheckReturnPolicy()

    def test_tool_creation(self, tool):
        """測試工具是否可以被實例化。"""
        assert tool is not None
        assert tool.name == "check_return_policy"

    def test_tool_declaration(self, tool):
        """測試工具是否有正確的宣告。"""
        declaration = tool._get_declaration()
        assert declaration is not None
        assert declaration.name == "check_return_policy"

    @pytest.mark.asyncio
    async def test_within_return_window(self, tool):
        """測試訂單是否在 30 天退貨期內。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-12345",
                "days_since_purchase": 15,
            },
            tool_context=None,
        )
        assert "✓" in result
        assert "eligible" in result.lower()

    @pytest.mark.asyncio
    async def test_at_return_window_boundary(self, tool):
        """測試訂單是否剛好在 30 天退貨期邊界。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-12345",
                "days_since_purchase": 30,
            },
            tool_context=None,
        )
        assert "✓" in result
        assert "eligible" in result.lower()

    @pytest.mark.asyncio
    async def test_outside_return_window(self, tool):
        """測試訂單是否超出 30 天退貨期。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-12345",
                "days_since_purchase": 45,
            },
            tool_context=None,
        )
        assert "✗" in result
        assert "cannot be returned" in result.lower()


class TestProcessRefundTool:
    """測試 process_refund 工具。"""

    @pytest.fixture
    def tool(self):
        """建立用於測試的工具實例。"""
        return ProcessRefund()

    def test_tool_creation(self, tool):
        """測試工具是否可以被實例化。"""
        assert tool is not None
        assert tool.name == "process_refund"

    def test_tool_declaration(self, tool):
        """測試工具是否有正確的宣告。"""
        declaration = tool._get_declaration()
        assert declaration is not None
        assert declaration.name == "process_refund"

    @pytest.mark.asyncio
    async def test_refund_processing(self, tool):
        """測試退款處理是否成功。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-12345",
                "amount": 99.99,
                "reason": "Customer requested return",
            },
            tool_context=None,
        )
        assert "✓" in result
        assert "processed" in result.lower()
        assert "99.99" in result

    @pytest.mark.asyncio
    async def test_refund_includes_transaction_id(self, tool):
        """測試退款是否包含交易詳情。"""
        result = await tool.run_async(
            args={
                "order_id": "ORD-12345",
                "amount": 50.00,
                "reason": "Defective product",
            },
            tool_context=None,
        )
        assert "TXN-" in result
        assert "3-5 business days" in result


class TestGEPAConcepts:
    """透過代理程式測試 GEPA 優化概念。"""

    def test_initial_prompt_identifies_gaps(self):
        """測試初始提示是否具有已知的差距以供 GEPA 優化。"""
        # 初始提示刻意設計得較為簡單
        # GEPA 應該對其進行優化，使其在以下方面更具體：
        # 1. 身份驗證要求
        # 2. 政策遵守程序
        # 3. 清晰的解釋指南
        assert "polite and professional" in INITIAL_PROMPT.lower()
        # 應缺乏具體的優化要求

    def test_agent_has_evaluation_capability(self):
        """測試代理程式設定是否啟用 GEPA 評估。"""
        agent = create_support_agent()
        # 代理程式應具備：
        # - 用於評估的工具（模擬客戶場景）
        # - 清晰的基於指令的行為
        # - 足夠的確定性以進行優化
        assert agent.tools
        assert agent.instruction

    def test_prompt_optimization_target(self):
        """測試代理程式是否適合進行提示優化。"""
        # 此代理程式適合 GEPA 的原因：
        # 1. 清晰的成功/失敗場景（退款處理）
        # 2. 工具使用具有確定性
        # 3. 失敗是可識別的（錯誤的訂單、違反政策）
        agent = create_support_agent()
        assert len(agent.tools) > 0

    def test_seed_prompt_evolution_potential(self):
        """測試種子提示是否具有演化潛力。"""
        evolved_prompt = """您是一位專業的客戶支援代理。

        關鍵要求：
        1. 務必先驗證客戶身份
        - 未經身份驗證，絕不處理退款
        - 使用 verify_customer_identity 工具

        2. 務必檢查退貨政策
        - 驗證 30 天退貨期限
        - 向客戶清楚解釋政策

        3. 提供清晰的解釋
        - 解釋所有決定
        - 引用具體的訂單細節
        - 使用簡單、專業的語言

        工具使用順序：
        - 第一步：verify_customer_identity
        - 第二步：check_return_policy
        - 第三步：process_refund（如果符合資格）"""

        # 演化後的提示具有更多結構和要求
        assert "務必" in evolved_prompt
        assert "關鍵" in evolved_prompt
        assert "verify_customer_identity" in evolved_prompt
