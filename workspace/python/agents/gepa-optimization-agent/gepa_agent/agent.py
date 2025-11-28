"""
GEPA 教學代理：模擬客服代理

此代理透過實作一個處理各種客戶請求的客服代理，
來展示 GEPA (遺傳演算法-帕雷托提示最佳化) 的概念。
此提示可使用 GEPA 進行最佳化，以改善在身份驗證、
政策遵守及解釋清晰度方面的處理能力。

此代理使用三種工具：
1. verify_customer_identity - 驗證客戶資訊
2. check_return_policy - 驗證退貨資格
3. process_refund - 處理退款操作
"""

from typing import Any, Dict

from google.adk.agents import llm_agent
from google.adk.models import google_llm
from google.adk.tools import base_tool
from google.genai import types


class VerifyCustomerIdentity(base_tool.BaseTool):
    """在執行敏感操作前，驗證客戶身份。"""

    def __init__(self):
        super().__init__(
            name="verify_customer_identity",
            description="透過檢查訂單號碼和電子郵件來驗證客戶身份",
        )

    def _get_declaration(self) -> types.FunctionDeclaration:
        """定義工具的結構與參數"""
        return types.FunctionDeclaration(
            name="verify_customer_identity",
            description="為安全敏感操作驗證客戶身份",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "order_id": types.Schema(
                        type=types.Type.STRING,
                        description="客戶訂單 ID",
                    ),
                    "email": types.Schema(
                        type=types.Type.STRING,
                        description="客戶電子郵件地址",
                    ),
                },
                required=["order_id", "email"],
            ),
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: Any
    ) -> str:
        """
        驗證客戶身份。

        根據簡單的驗證邏輯回傳成功或失敗。
        """
        order_id = args.get("order_id", "")
        email = args.get("email", "")

        # 模擬客戶資料庫查詢
        valid_customers = {
            "ORD-12345": "customer@example.com",
            "ORD-67890": "john@example.com",
            "ORD-11111": "jane@example.com",
        }

        if order_id in valid_customers:
            if valid_customers[order_id] == email:
                return (
                    f"✓ 客戶身份驗證成功。訂單：{order_id}, "
                    f"電子郵件：{email}"
                )
            else:
                return (
                    f"✗ 訂單 {order_id} 的電子郵件不符。"
                    f"驗證失敗。"
                )
        else:
            return f"✗ 系統中找不到訂單 {order_id}。"


class CheckReturnPolicy(base_tool.BaseTool):
    """根據退貨政策檢查訂單是否符合退貨資格。"""

    def __init__(self):
        super().__init__(
            name="check_return_policy",
            description="檢查訂單是否在 30 天的退貨期限內",
        )

    def _get_declaration(self) -> types.FunctionDeclaration:
        """定義工具的結構與參數"""
        return types.FunctionDeclaration(
            name="check_return_policy",
            description="驗證退貨政策 - 30 天退貨期限",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "order_id": types.Schema(
                        type=types.Type.STRING,
                        description="要檢查的訂單 ID",
                    ),
                    "days_since_purchase": types.Schema(
                        type=types.Type.INTEGER,
                        description="自下單以來的天數",
                    ),
                },
                required=["order_id", "days_since_purchase"],
            ),
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: Any
    ) -> str:
        """
        檢查是否符合退貨政策。

        回傳訂單是否在 30 天退貨期限內。
        """
        order_id = args.get("order_id", "")
        days = args.get("days_since_purchase", 0)

        if days <= 30:
            return (
                f"✓ 訂單 {order_id} 符合退貨資格。"
                f"({days} 天前購買 - 在 30 天期限內)"
            )
        else:
            return (
                f"✗ 訂單 {order_id} 無法退貨。"
                f"({days} 天前購買 - 超出 30 天期限)。"
                f"我們的退貨政策允許在購買後 30 天內退貨。"
            )


class ProcessRefund(base_tool.BaseTool):
    """為符合資格的訂單處理退款。"""

    def __init__(self):
        super().__init__(
            name="process_refund",
            description="為符合資格的客戶訂單處理退款",
        )

    def _get_declaration(self) -> types.FunctionDeclaration:
        """定義工具的結構與參數"""
        return types.FunctionDeclaration(
            name="process_refund",
            description="在驗證和政策檢查後處理退款",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "order_id": types.Schema(
                        type=types.Type.STRING,
                        description="要退款的訂單 ID",
                    ),
                    "amount": types.Schema(
                        type=types.Type.NUMBER,
                        description="退款金額 (美元)",
                    ),
                    "reason": types.Schema(
                        type=types.Type.STRING,
                        description="退款原因",
                    ),
                },
                required=["order_id", "amount", "reason"],
            ),
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: Any
    ) -> str:
        """
        處理退款操作。

        回傳包含交易詳情的確認訊息。
        """
        order_id = args.get("order_id", "")
        amount = args.get("amount", 0)
        reason = args.get("reason", "")

        # 產生交易 ID
        transaction_id = f"TXN-{order_id}-001"

        return (
            f"✓ 退款處理成功！\n"
            f"  交易 ID：{transaction_id}\n"
            f"  訂單：{order_id}\n"
            f"  金額：${amount:.2f}\n"
            f"  原因：{reason}\n"
            f"  預計退回至帳戶時間：3-5 個工作天"
        )


# 客服代理的初始提示
# 這是將由 GEPA 進行最佳化的種子提示
INITIAL_PROMPT = """
    您是一位線上零售商的樂於助人的客服代理。

    您的職責是協助客戶處理訂單、退貨與退款事宜。

    重要指南：
    - 保持禮貌與專業
    - 徹底了解客戶問題
    - 使用可用的工具協助客戶
    - 遵守公司政策

    處理退款時：
    - 詢問必要資訊 (訂單 ID、電子郵件)
    - 驗證客戶身份
    - 檢查退貨政策
    - 清楚解釋您的決定
"""


def create_support_agent(
    prompt: str | None = None,
    model: str = "gemini-2.5-flash",
) -> llm_agent.LlmAgent:
    """
    建立一個客服代理。

    Args:
        prompt: 代理的自訂系統提示。若為 None，則使用 INITIAL_PROMPT。
        model: 要使用的 LLM 模型。

    Returns:
        設定好的 ADK LLM 代理。
    """
    if prompt is None:
        prompt = INITIAL_PROMPT

    return llm_agent.LlmAgent(
        name="customer_support_agent",
        model=google_llm.Gemini(model=model),
        instruction=prompt,
        tools=[
            VerifyCustomerIdentity(),
            CheckReturnPolicy(),
            ProcessRefund(),
        ],
        description="處理訂單與退款的客服代理",
    )


# 根代理匯出 (ADK 要求)
root_agent = create_support_agent()
