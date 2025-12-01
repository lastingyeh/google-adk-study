"""
整合 AG-UI 的客戶支援 ADK 代理人 (Customer support ADK agent)。

此代理人提供客戶支援功能，具備知識庫搜尋、訂單狀態查詢和支援工單建立的工具。
它透過 AG-UI 協定與 Next.js 前端整合。
"""

import os
import uuid
import json
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uvicorn

# AG-UI ADK 整合匯入
try:
    from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
except ImportError:
    raise ImportError(
        "找不到 ag_ui_adk。請使用以下指令安裝：pip install ag-ui-adk"
    )

# Google ADK 匯入
from google.adk.agents import Agent

# 載入環境變數
load_dotenv()


# ============================================================================
# 工具定義 (Tool Definitions)
# ============================================================================


def search_knowledge_base(query: str) -> Dict[str, Any]:
    """
    搜尋知識庫以尋找相關資訊。

    Args:
        query: 搜尋查詢，用於尋找相關的文章

    Returns:
        包含狀態、報告和文章資料的字典
    """
    # 模擬知識庫 - 在正式環境中替換為真實資料庫/向量儲存庫
    knowledge_base = {
        "refund policy": {
            "title": "退款政策",
            "content": (
                "我們提供購買後 30 天內全額退款。"
                "請聯繫 support@company.com 進行退款。"
            ),
        },
        "shipping": {
            "title": "運送資訊",
            "content": (
                "標準運送需 5-7 個工作天。"
                "提供額外加 $15 的快遞服務 (2-3 天)。"
            ),
        },
        "warranty": {
            "title": "保固範圍",
            "content": (
                "所有產品均包含 1 年製造缺陷保固。"
                "提供延長保固服務。"
            ),
        },
        "account": {
            "title": "帳戶管理",
            "content": (
                "在 /account/reset 重設密碼。在 /account/billing 更新帳單資訊。"
                "隨時取消訂閱。"
            ),
        },
    }

    # 簡單的關鍵字比對 - 在正式環境中使用向量搜尋
    query_lower = query.lower()
    for key, article in knowledge_base.items():
        if key in query_lower:
            return {
                "status": "success",
                "report": f"找到文章：{article['title']}",
                "article": article,
            }

    # 預設回應
    return {
        "status": "success",
        "report": "未找到特定文章，提供一般支援資訊",
        "article": {
            "title": "一般支援",
            "content": (
                "請聯繫我們的支援團隊 support@company.com "
                "或撥打 1-800-SUPPORT 獲取專人協助。"
            ),
        },
    }


def lookup_order_status(order_id: str) -> Dict[str, Any]:
    """
    查詢客戶訂單的狀態。

    Args:
        order_id: 要查詢的訂單 ID (格式：ORD-XXXXX)

    Returns:
        包含狀態、報告和訂單詳情的字典
    """
    # 模擬訂單資料庫 - 在正式環境中替換為真實資料庫
    orders = {
        "ORD-12345": {
            "order_id": "ORD-12345",
            "status": "已出貨",
            "tracking": "1Z999AA10123456784",
            "estimated_delivery": "2025-10-12",
            "items": "2x Widget Pro, 1x Gadget Plus",
        },
        "ORD-67890": {
            "order_id": "ORD-67890",
            "status": "處理中",
            "tracking": None,
            "estimated_delivery": "2025-10-15",
            "items": "1x Premium Kit",
        },
        "ORD-11111": {
            "order_id": "ORD-11111",
            "status": "已送達",
            "tracking": "1Z999AA10987654321",
            "estimated_delivery": "2025-01-15",
            "items": "3x Basic Widget",
        },
    }

    order_id_upper = order_id.upper()

    if order_id_upper in orders:
        order = orders[order_id_upper]
        return {
            "status": "success",
            "report": f"找到訂單 {order_id}：{order['status']}",
            "order": order,
        }
    else:
        return {
            "status": "error",
            "report": f"找不到訂單 {order_id}",
            "error": "請檢查訂單 ID 並重試。",
        }


def create_support_ticket(
    issue_description: str, priority: str = "normal"
) -> Dict[str, Any]:
    """
    為複雜問題建立支援工單。

    Args:
        issue_description: 客戶問題描述
        priority: 優先級 (low, normal, high, urgent)

    Returns:
        包含狀態、報告和工單詳情的字典
    """
    # 產生唯一的工單 ID
    ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"

    # 根據優先級設定回應時間
    response_times = {
        "urgent": "1-2 小時",
        "high": "4-6 小時",
        "normal": "12-24 小時",
        "low": "24-48 小時",
    }

    estimated_response = response_times.get(priority, "24 小時")

    return {
        "status": "success",
        "report": f"支援工單 {ticket_id} 建立成功",
        "ticket": {
            "ticket_id": ticket_id,
            "status": "已建立",
            "priority": priority,
            "issue": issue_description,
            "estimated_response": estimated_response,
            "created_at": datetime.now().isoformat(),
        },
    }


def get_product_details(product_id: str) -> Dict[str, Any]:
    """
    從資料庫獲取產品詳情。

    回傳可顯示給使用者的產品資訊。
    前端將處理將其渲染為 ProductCard 元件。

    Args:
        product_id: 要查詢的產品 ID (格式：PROD-XXX)

    Returns:
        包含狀態、報告和產品詳情的字典
    """
    # 模擬產品資料庫 - 在正式環境中替換為真實資料庫
    products = {
        "PROD-001": {
            "name": "Widget Pro",
            "price": 99.99,
            "image": "https://placehold.co/400x400/6366f1/fff.png",
            "rating": 4.5,
            "inStock": True,
        },
        "PROD-002": {
            "name": "Gadget Plus",
            "price": 149.99,
            "image": "https://placehold.co/400x400/8b5cf6/fff.png",
            "rating": 4.8,
            "inStock": True,
        },
        "PROD-003": {
            "name": "Premium Kit",
            "price": 299.99,
            "image": "https://placehold.co/400x400/ec4899/fff.png",
            "rating": 4.9,
            "inStock": False,
        },
    }

    product_id_upper = product_id.upper()

    if product_id_upper in products:
        product = products[product_id_upper]
        return {
            "status": "success",
            "report": f"這是 {product['name']} 的詳細資訊。我會為您將其顯示為產品卡片。",
            "product": product,
        }
    else:
        return {
            "status": "error",
            "report": f"找不到產品 {product_id}",
            "error": "請檢查產品 ID 並重試。",
        }


def process_refund(order_id: str, amount: float, reason: str) -> Dict[str, Any]:
    """
    處理訂單退款。

    這是一個進階功能，展示人機協作 (HITL) -
    前端在執行此動作前會顯示確認對話框。

    重要：此函式需要前端的使用者批准。

    Args:
        order_id: 要退款的訂單 ID (格式：ORD-XXXXX)
        amount: 退款金額 (美元)
        reason: 退款原因

    Returns:
        包含狀態、報告和退款詳情的字典
    """
    # 在正式環境中，這將會：
    # 1. 驗證訂單是否存在且屬於使用者
    # 2. 檢查退款資格 (時間窗口、退貨政策)
    # 3. 透過支付處理器處理實際退款
    # 4. 更新資料庫中的訂單狀態
    # 5. 發送確認電子郵件

    # 模擬退款處理
    refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"

    return {
        "status": "success",
        "report": f"訂單 {order_id} 的退款 {refund_id} 處理成功",
        "refund": {
            "refund_id": refund_id,
            "order_id": order_id,
            "amount": amount,
            "reason": reason,
            "status": "已處理",
            "processed_at": datetime.now().isoformat(),
            "estimated_credit_date": "3-5 個工作天",
        },
    }


# ============================================================================
# 代理人設定 (Agent Configuration)
# ============================================================================

# 建立包含工具的 ADK 代理人
adk_agent = Agent(
    name="customer_support_agent",
    model="gemini-2.0-flash-exp",
    instruction="""你是一位電子商務公司的熱心客戶支援代理人。

    你的職責：
    - 清楚且簡潔地回答客戶問題
    - 需要時使用 search_knowledge_base() 搜尋知識庫
    - 當客戶詢問訂單時，使用 lookup_order_status() 查詢訂單狀態
    - 對於複雜問題，使用 create_support_ticket() 建立支援工單
    - 當客戶詢問產品時，使用 get_product_details() 獲取產品詳情
    - 保持同理心和專業
    - 適當時將複雜問題升級給人工支援
    - 絕不編造資訊 - 如果不確定，就直說

    重要 - 進階功能：

    1. **產品資訊 (生成式 UI)**：
    - 當使用者詢問產品時，請遵循以下兩步驟流程：
        a) 首先呼叫 get_product_details(product_id) 獲取產品資料
        b) 然後使用產品詳情呼叫 render_product_card(name, price, image, rating, inStock)
    - 範例："Show me product PROD-001" (顯示產品 PROD-001)
        → 呼叫 get_product_details("PROD-001")
        → 從結果中提取產品資料
        → 呼叫 render_product_card(name="Widget Pro", price=99.99, image="...", rating=4.5, inStock=True)
    - 前端將渲染一個精美的互動式 ProductCard 元件
    - 重要：請勿在回應中包含 JSON 資料。只需簡單地說：
        "這是 [產品名稱] 的產品資訊" 或 "我已在上方顯示產品卡片。"
    - 讓視覺卡片自己說話 - 不要在文字格式中重複資料

    2. **退款 (人機協作)**：
    - 當使用者請求退款時，呼叫 process_refund(order_id, amount, reason)
    - 這是一個前端動作，需要使用者批准
    - 會出現一個批准對話框，要求使用者確認或取消
    - 對話框顯示：訂單 ID、金額和原因
    - 在繼續之前等待使用者的決定
    - 如果批准：確認 "退款處理成功"
    - 如果取消：確認 "使用者取消退款"
    - 重要：在呼叫此動作之前，必須收集所有三個參數 (order_id, amount, reason)

    準則：
    - 熱情地問候客戶
    - 為每種類型的查詢使用適當的工具
    - 回答後提供後續步驟
    - 除非要求更多細節，否則回應保持在 3 段以內
    - 使用友善但專業的語氣
    - 使用 markdown 格式化回應以提高可讀性""",
    tools=[
        search_knowledge_base,
        lookup_order_status,
        create_support_ticket,
        get_product_details,
        # 注意：process_refund 僅作為前端動作可用 (非後端工具)
        # 這確保在處理之前顯示 HITL 批准對話框
    ],
)

# 使用 AG-UI 中介軟體包裝 ADK 代理人
agent = ADKAgent(
    adk_agent=adk_agent,
    app_name="customer_support_app",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

# 匯出以供測試
root_agent = adk_agent


# ============================================================================
# CopilotKit 相容性中介軟體 (Middleware for CopilotKit Compatibility)
# ============================================================================

class MessageIDMiddleware(BaseHTTPMiddleware):
    """
    用於注入訊息 ID 以實現 CopilotKit 相容性的中介軟體。

    CopilotKit 發送的訊息沒有 ID，但 AG-UI 協定需要它們。
    此中介軟體會為缺少 'id' 欄位的任何訊息加入 UUID。
    """

    async def dispatch(self, request: Request, call_next):
        """處理請求並在需要時注入訊息 ID。"""
        # 僅處理對 /api/copilotkit 的 POST 請求
        if request.method == "POST" and request.url.path == "/api/copilotkit":
            # 讀取請求本體
            body = await request.body()

            try:
                # 解析 JSON
                data = json.loads(body)

                print(f"🔍 Middleware: 收到請求，鍵值：{list(data.keys())}")
                print(f"📄 Middleware: 完整請求本體：{json.dumps(data, indent=2)[:500]}")

                # 如果缺少，則將 ID 注入訊息中
                if "messages" in data and isinstance(data["messages"], list):
                    modified = False
                    for i, msg in enumerate(data["messages"]):
                        if isinstance(msg, dict):
                            if "id" not in msg:
                                # 產生唯一 ID
                                msg["id"] = f"msg-{uuid.uuid4()}"
                                modified = True
                                print(f"✅ Middleware: 已將 ID 加入訊息 {i}：{msg.get('role', 'unknown')}")
                            else:
                                print(f"ℹ️  Middleware: 訊息 {i} 已有 ID：{msg['id']}")

                    # 如果有變更，建立包含修改後本體的新請求
                    if modified:
                        modified_body = json.dumps(data).encode()
                        print(f"📝 Middleware: 修改了 {len(data['messages'])} 條訊息")

                        # 替換請求本體
                        async def receive():
                            return {"type": "http.request", "body": modified_body}

                        request._receive = receive
                    else:
                        print("ℹ️  Middleware: 無需修改")
                else:
                    print(f"⚠️  Middleware: 請求中未找到 'messages' 欄位")

            except json.JSONDecodeError as e:
                print(f"❌ Middleware: JSON 解碼錯誤：{e}")
            except Exception as e:
                print(f"❌ Middleware: 未預期的錯誤：{e}")

        # 繼續處理請求
        response = await call_next(request)
        return response


# ============================================================================
# FastAPI 應用程式 (FastAPI Application)
# ============================================================================

# 建立 FastAPI 應用程式
app = FastAPI(
    title="Customer Support Agent API",
    description="具備 AG-UI 整合的 ADK 客戶支援代理人",
    version="1.0.0",
)

# 為前端加入 CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 預設
        "http://localhost:5173",  # Vite 預設
        "http://localhost:8000",  # 本機測試
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加入中介軟體以注入訊息 ID 實現 CopilotKit 相容性
app.add_middleware(MessageIDMiddleware)

# 加入 CopilotKit 的 ADK 端點
add_adk_fastapi_endpoint(app, agent, path="/api/copilotkit")


# 健康檢查端點
@app.get("/health")
def health_check() -> Dict[str, str]:
    """健康檢查端點。"""
    return {
        "status": "healthy",
        "agent": "customer_support_agent",
        "version": "1.0.0",
    }


@app.get("/")
def root() -> Dict[str, str]:
    """包含 API 資訊的根端點。"""
    return {
        "message": "Customer Support Agent API",
        "endpoints": {
            "health": "/health",
            "copilotkit": "/api/copilotkit",
            "docs": "/docs",
        },
    }


# ============================================================================
# 主要進入點 (Main Entry Point)
# ============================================================================

if __name__ == "__main__":
    # 從環境變數獲取設定
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print("=" * 60)
    print("🤖 客戶支援代理人 API (Customer Support Agent API)")
    print("=" * 60)
    print(f"🌐 伺服器：http://{host}:{port}")
    print(f"📚 文件：http://{host}:{port}/docs")
    print(f"💬 CopilotKit：http://{host}:{port}/api/copilotkit")
    print("=" * 60)

    # 使用 uvicorn 執行
    uvicorn.run(
        "agent:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
