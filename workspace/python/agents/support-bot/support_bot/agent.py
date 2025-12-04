"""
團隊支援機器人 Agent (Support Bot Agent)

此 Agent 提供團隊支援功能，並包含以下工具：
- 知識庫搜尋
- 支援工單建立
"""

from typing import Dict, Any
from google.adk.agents import Agent
import uuid
from datetime import datetime


# Agent 的模擬知識庫
KNOWLEDGE_BASE = {
    "password_reset": {
        "title": "如何重設您的密碼 (How to Reset Your Password)",
        "content": """重設密碼步驟：
        1. 造訪 https://account.company.com
        2. 點擊「忘記密碼」(Forgot Password)
        3. 輸入您的公司電子郵件
        4. 檢查您的信箱以獲取重設連結
        5. 建立一個新的強密碼 (8 個字元以上，包含字母/數字/符號的組合)

        如果您在 5 分鐘內未收到郵件，請檢查垃圾郵件資料夾或聯絡 IT 部門：it-help@company.com。""",
                "tags": ["password", "reset", "account", "login", "密碼", "重設", "帳戶", "登入"]
            },
            "expense_report": {
                "title": "提交費用報告 (Filing Expense Reports)",
                "content": """提交費用報告步驟：
        1. 登入 Expensify：https://expensify.company.com
        2. 點擊「新報告」(New Report)
        3. 新增費用並附上收據
        4. 提交給經理批准
        5. 在 7 個工作天內獲得核銷

        可報銷費用：差旅費、餐費 (每天最高 50 美元)、軟體訂閱費 (需預先批准)。

        有問題嗎？請寄信至 finance@company.com""",
                "tags": ["expense", "reimbursement", "finance", "expensify", "費用", "報銷", "財務"]
            },
            "vacation_policy": {
                "title": "休假與特休政策 (Vacation and PTO Policy)",
                "content": """我們的特休 (PTO) 政策：
        • 每年 15 天特休 (第一年按比例計算)
        • 每年 5 天病假
        • 10 天公司國定假日
        • 無限制無薪假 (需經經理批准)

        申請休假：
        1. 在 BambooHR 提交申請：https://bamboo.company.com
        2. 獲得經理批准
        3. 更新您的 Slack 狀態
        4. 新增至團隊行事曆

        請為繁忙時期 (Q4、產品發布) 提前規劃。""",
                "tags": ["vacation", "pto", "time off", "leave", "holiday", "休假", "特休", "請假", "假日"]
            },
            "remote_work": {
                "title": "遠端工作政策 (Remote Work Policy)",
                "content": """遠端工作選項：
        • 混合模式：3 天進辦公室，2 天遠端 (標準)
        • 全遠端：適用於經批准的職位
        • 臨時遠端：用於差旅、緊急情況 (需通知經理)

        要求：
        • 可靠的網路連線 (50+ Mbps)
        • 安靜的工作空間
        • 核心時段 (當地時間上午 10 點至下午 3 點) 可聯繫
        • 定期透過視訊參與會議

        設備津貼：每年 500 美元用於居家辦公設定。""",
                "tags": ["remote", "work from home", "hybrid", "wfh", "遠端", "在家工作", "混合辦公"]
            },
            "it_support": {
                "title": "IT 支援聯絡資訊 (IT Support Contacts)",
                "content": """IT 支援管道：
        • Slack: #it-support (最快，美東時間上午 9 點至下午 6 點)
        • Email: it-help@company.com (24 小時回應)
        • Phone: 1-800-IT-HELPS (僅限緊急問題)
        • Portal: https://support.company.com

        常見問題：
        • VPN: 使用 Cisco AnyConnect，憑證 = AD 登入帳號
        • 印表機: 透過系統偏好設定 → 印表機新增
        • 軟體安裝: 在 #it-support 提出請求

        緊急事件 (P0): 系統中斷請直接撥打電話。""",
        "tags": ["IT", "support", "help", "technical", "vpn", "printer", "支援", "協助", "技術", "印表機"]
    }
}

# 儲存已建立的工單
TICKETS = {}


def search_knowledge_base(query: str) -> Dict[str, Any]:
    """
    搜尋公司知識庫以獲取資訊。

    此函式透過比對標題、內容和標籤中的關鍵字來搜尋知識庫。
    如果找到，則回傳最佳匹配的文章。

    Args:
        query: 搜尋查詢 (例如："password reset", "vacation policy", "忘記密碼")

    Returns:
        包含 'status', 'report' 以及可選的 'article' 資料的字典
    """
    try:
        query_lower = query.lower()

        # 搜尋標籤和內容
        matches = []
        for key, article in KNOWLEDGE_BASE.items():
            score = 0

            # 檢查標題是否匹配
            # 權重最高 (3分)
            if query_lower in article["title"].lower():
                score += 3

            # 檢查標籤是否匹配
            # 權重次之 (2分)
            for tag in article["tags"]:
                if query_lower in tag.lower():
                    score += 2

            # 檢查內容是否匹配
            # 權重最低 (1分)
            if query_lower in article["content"].lower():
                score += 1

            if score > 0:
                matches.append((key, article, score))

        if matches:
            # 回傳最佳匹配 (分數最高者)
            best_key, best_article, best_score = sorted(
                matches, key=lambda x: x[2], reverse=True
            )[0]

            return {
                'status': 'success',
                'report': f"找到文章：{best_article['title']}",
                'article': {
                    'title': best_article['title'],
                    'content': best_article['content']
                }
            }
        else:
            return {
                'status': 'success',
                'report': "找不到符合您查詢的文章。請嘗試搜尋：密碼 (password)、費用 (expense)、休假 (vacation)、遠端 (remote) 或 IT 支援。",
                'article': None
            }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'搜尋知識庫時發生錯誤：{str(e)}'
        }


def create_support_ticket(
    subject: str,
    description: str,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    為複雜問題建立支援工單。

    此函式建立一個可由支援團隊追蹤和管理的支援工單。

    Args:
        subject: 簡短的工單主旨
        description: 詳細的問題描述
        priority: 工單優先順序："low" (低), "normal" (一般), "high" (高), 或 "urgent" (緊急)

    Returns:
        包含工單建立狀態和工單 ID 的字典
    """
    try:
        # 驗證優先順序
        valid_priorities = ["low", "normal", "high", "urgent"]
        if priority.lower() not in valid_priorities:
            return {
                'status': 'error',
                'error': f'無效的優先順序。必須是以下之一：{", ".join(valid_priorities)}',
                'report': f'錯誤：無效的優先順序層級 "{priority}"'
            }

        # 建立工單
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        ticket = {
            'id': ticket_id,
            'subject': subject,
            'description': description,
            'priority': priority.lower(),
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }

        TICKETS[ticket_id] = ticket

        report = (
            f"✅ 支援工單已建立：**{ticket_id}**\n"
            f"主旨：{subject}\n"
            f"優先順序：{priority.upper()}\n"
            f"狀態：Open (開啟)\n\n"
            f"我們的支援團隊將很快審閱您的工單。"
            f"您可以在此追蹤：https://support.company.com/tickets/{ticket_id}"
        )

        return {
            'status': 'success',
            'report': report,
            'ticket': {
                'id': ticket_id,
                'subject': subject,
                'priority': priority,
                'created_at': ticket['created_at']
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'建立支援工單時發生錯誤：{str(e)}'
        }


# 建立具有工具的 Support Bot Agent
root_agent = Agent(
    name="support_bot",
    model="gemini-2.5-flash",
    description="協助處理公司政策與問題的團隊支援助理",
    instruction="""你是一位科技公司的團隊支援助理，樂於助人。

    你的職責：
    - 使用知識庫回答問題
    - 協助處理公司政策與程序
    - 提供 IT 支援指引
    - 為複雜問題建立支援工單

    指導方針：
    - 當使用者詢問以下內容時，務必使用 search_knowledge_base：
    * 公司政策 (特休 PTO、遠端工作、費用)
    * IT 支援 (密碼、VPN、印表機、軟體)
    * 程序與流程
    - 對於需要人工審閱的複雜問題，請使用 create_support_ticket
    - 使用列點方式清晰地格式化回應
    - 包含知識庫中的相關連結
    - 使用 Slack 格式 (*粗體*, `程式碼`, > 引用)
    - 如果找不到資訊，請誠實告知並建議聯絡相關團隊
    - 保持同理心與專業

    記住：你的目標是幫助員工提高生產力！""",
    tools=[
        search_knowledge_base,
        create_support_ticket
    ]
)

# 重點摘要 (agent.py)
# - 核心概念：定義了 Support Bot 的核心邏輯、知識庫資料與工具函式。
# - 關鍵技術：
#   - Google ADK Agent：用於定義 AI 助理的行為與指令。
#   - Python 字典：作為模擬的輕量級知識庫與資料儲存。
#   - 加權關鍵字搜尋：實作了簡單的相關性評分演算法來檢索文章。
# - 重要結論：透過結合預定義的知識庫與 LLM 的自然語言處理能力，提供即時且準確的支援。
# - 行動項目：
#   - 擴充 `KNOWLEDGE_BASE` 以涵蓋更多主題。
#   - 實作持久化的資料庫以儲存工單 (`TICKETS`)。


