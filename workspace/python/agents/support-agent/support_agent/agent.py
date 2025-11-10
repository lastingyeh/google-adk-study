"""
客戶支援代理 (Customer Support Agent) - 評估測試示範

此代理展示了可測試的模式 (Testable Patterns):
- 清晰的工具使用 (易於驗證軌跡)
- 結構化的回應 (易於比較)
- 確定性行為 (盡可能)
"""

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any
import uuid
from datetime import datetime

# ============================================================================
# 工具函數 (TOOLS)
# ============================================================================

def search_knowledge_base(
    query: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    在知識庫中搜尋常見客戶問題的資訊。

    程式流程:
    1. 定義內建知識庫字典 (包含常見問題與解答)
    2. 將查詢轉換為小寫進行不區分大小寫的關鍵字比對
    3. 遍歷知識庫,找出所有匹配的主題
    4. 返回搜尋結果或無結果訊息

    Args:
        query: 在知識庫中查詢的搜尋關鍵字
        tool_context: ADK 工具上下文

    Returns:
        包含狀態、報告和搜尋結果的字典
    """
    # 記憶體內知識庫 (為測試提供確定性結果)
    knowledge_base = {
        "password reset": "要重設密碼,請前往 設定 > 安全性 > 重設密碼。您將在 5 分鐘內收到包含重設說明的電子郵件。",
        "refund policy": "我們對所有購買提供 30 天退款保證。請將您的訂單編號寄至 support@example.com 以啟動退款。",
        "shipping": "標準運送需要 3-5 個工作天。快速運送 (1-2 天) 需額外支付 $10。在 example.com/track 追蹤您的訂單",
        "account": "在 example.com/account 管理您的帳戶設定。您可以更新個人資料、付款方式和通知偏好設定。",
        "billing": "在 example.com/billing 查看您的帳單歷史記錄和發票。有關付款相關問題,請聯絡 billing@example.com。",
        "technical support": "對於技術問題,請提供您的系統詳細資訊和錯誤訊息。我們的支援團隊將在 24 小時內回覆。"
    }

    # 簡單的關鍵字匹配 (不區分大小寫)
    query_lower = query.lower()
    results = []

    # 遍歷知識庫,找出匹配的主題
    for key, content in knowledge_base.items():
        # 檢查主題關鍵字是否出現在查詢中,或查詢中的任何單字是否匹配主題
        if key in query_lower or any(word in query_lower for word in key.split()):
            results.append({
                "topic": key,
                "content": content
            })

    # 根據搜尋結果返回適當的回應
    if results:
        return {
            'status': 'success',
            'report': f'找到 {len(results)} 篇與 "{query}" 相關的文章',
            'results': results
        }
    else:
        return {
            'status': 'success',
            'report': f'未找到與 "{query}" 相關的文章。請嘗試重新描述您的問題或聯絡支援團隊。',
            'results': []
        }


def create_ticket(
    issue: str,
    tool_context: ToolContext,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    為客戶問題建立新的支援工單。

    程式流程:
    1. 驗證優先級別是否有效
    2. 產生唯一的工單 ID (使用 UUID)
    3. 根據優先級設定預估回應時間
    4. 建立工單記錄並儲存到上下文狀態
    5. 返回工單建立成功的確認訊息

    Args:
        issue: 客戶問題的描述
        priority: 優先級別 (low, normal, high, urgent)
        tool_context: ADK 工具上下文

    Returns:
        包含狀態、報告和工單詳細資訊的字典
    """
    # 驗證優先級別是否有效
    valid_priorities = ["low", "normal", "high", "urgent"]
    if priority not in valid_priorities:
        return {
            'status': 'error',
            'error': f'無效的優先級別 "{priority}"。必須是以下之一: {", ".join(valid_priorities)}',
            'report': f'建立工單失敗: 無效的優先級別 "{priority}"'
        }

    # 產生工單 ID (格式: TICK-XXXXXXXX)
    ticket_id = f"TICK-{uuid.uuid4().hex[:8].upper()}"

    # 建立工單記錄
    ticket = {
        'ticket_id': ticket_id,
        'issue': issue,
        'priority': priority,
        'status': 'open',
        'created_at': datetime.now().isoformat(),
        # 根據優先級別設定預估回應時間
        'estimated_response': {
            'low': '5 個工作天',
            'normal': '2 個工作天',
            'high': '24 小時',
            'urgent': '4 小時'
        }.get(priority, '2 個工作天')
    }

    # 儲存到工具上下文狀態 (實際應用中應儲存到資料庫)
    if not hasattr(tool_context, 'tickets'):
        tool_context.tickets = {}
    tool_context.tickets[ticket_id] = ticket

    return {
        'status': 'success',
        'report': f'工單 {ticket_id} 已成功建立,優先級別為 {priority}。預計回應時間: {ticket["estimated_response"]}',
        'ticket': ticket
    }


def check_ticket_status(
    ticket_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    查詢現有支援工單的狀態。

    程式流程:
    1. 檢查工具上下文中是否存在工單記錄
    2. 驗證指定的工單 ID 是否存在
    3. 如果找到,返回工單的詳細狀態資訊
    4. 如果未找到,返回錯誤訊息

    Args:
        ticket_id: 要查詢的工單 ID
        tool_context: ADK 工具上下文

    Returns:
        包含狀態、報告和工單資訊的字典
    """
    # 檢查上下文中是否存在工單記錄
    if not hasattr(tool_context, 'tickets') or ticket_id not in tool_context.tickets:
        return {
            'status': 'error',
            'error': f'未找到工單 {ticket_id}',
            'report': f'找不到工單 {ticket_id}。請確認工單 ID 是否正確。'
        }

    # 取得工單資訊
    ticket = tool_context.tickets[ticket_id]

    return {
        'status': 'success',
        'report': f'工單 {ticket_id} 目前狀態為 {ticket["status"]} (優先級別: {ticket["priority"]})',
        'ticket': ticket
    }


# ============================================================================
# 代理定義 (AGENT DEFINITION)
# ============================================================================

# 建立客戶支援代理
# 整合流程:
# 1. 客戶提出問題 → 首先使用 search_knowledge_base 搜尋知識庫
# 2. 若知識庫無法解答 → 使用 create_ticket 建立支援工單
# 3. 客戶詢問工單狀態 → 使用 check_ticket_status 查詢進度
root_agent = Agent(
    name="support_agent",
    model="gemini-2.0-flash-exp",
    description="可搜尋知識庫、建立工單及查詢工單狀態的客戶支援代理",
    instruction="""你是一位樂於助人的客戶支援代理。請按照以下方式協助客戶:

1. 首先,嘗試使用知識庫搜尋工具回答他們的問題
2. 如果找不到相關資訊,則建立支援工單
3. 如果他們提到工單 ID,請查詢其狀態

永遠保持禮貌、清晰,並提供具體的後續步驟。根據客戶的需求適當使用工具。""",
    tools=[search_knowledge_base, create_ticket, check_ticket_status],
    output_key="support_response"
)