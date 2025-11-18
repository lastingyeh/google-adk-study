# 教學 20：YAML 設定 - 客戶支援工具
# 客戶支援系統的工具實作
# 這些函數由 root_agent.yaml 中的名稱引用

from typing import Dict, Any


def check_customer_status(customer_id: str) -> Dict[str, Any]:
    """
    檢查客戶是否為高級會員。

    Args:
        customer_id: 客戶識別碼

    Returns:
        包含狀態、報告和客戶層級資訊的字典
    """
    # 模擬查詢 - 在生產環境中，將查詢資料庫
    premium_customers = ['CUST-001', 'CUST-003', 'CUST-005']

    is_premium = customer_id in premium_customers
    tier = 'premium' if is_premium else 'standard'

    return {
        'status': 'success',
        'report': f'客戶 {customer_id} 是 {tier} 會員',
        'data': {
            'customer_id': customer_id,
            'tier': tier,
            'is_premium': is_premium
        }
    }


def log_interaction(customer_id: str, interaction_type: str, summary: str) -> Dict[str, Any]:
    """
    記錄客戶互動以供存檔。

    Args:
        customer_id: 客戶識別碼
        interaction_type: 互動類型（詢問、投訴等）
        summary: 互動簡短摘要

    Returns:
        包含狀態和確認的字典
    """
    # 在生產環境中，將記錄到資料庫或 CRM 系統
    print(f"[LOG] {customer_id} - {interaction_type}: {summary}")

    return {
        'status': 'success',
        'report': '互動記錄成功',
        'data': {
            'customer_id': customer_id,
            'interaction_type': interaction_type,
            'summary': summary,
            'timestamp': '2025-10-13T10:00:00Z'  # 應為實際時間戳
        }
    }


def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    透過 ID 取得訂單狀態。

    Args:
        order_id: 訂單識別碼

    Returns:
        包含訂單狀態資訊的字典
    """
    # 模擬訂單查詢 - 在生產環境中，將查詢訂單資料庫
    orders = {
        'ORD-001': {'status': 'shipped', 'date': '2025-10-08'},
        'ORD-002': {'status': 'processing', 'date': '2025-10-10'},
        'ORD-003': {'status': 'delivered', 'date': '2025-10-07'},
        'ORD-004': {'status': 'cancelled', 'date': '2025-10-09'}
    }

    order = orders.get(order_id)
    if not order:
        return {
            'status': 'error',
            'error': f'找不到訂單 {order_id}',
            'report': f'找不到 ID 為 {order_id} 的訂單'
        }

    return {
        'status': 'success',
        'report': f'訂單 {order_id} 狀態：{order["status"]}',
        'data': {
            'order_id': order_id,
            'status': order['status'],
            'order_date': order['date']
        }
    }


def track_shipment(order_id: str) -> Dict[str, Any]:
    """
    取得運送追蹤資訊。

    Args:
        order_id: 訂單識別碼

    Returns:
        包含追蹤資訊的字典
    """
    # 模擬追蹤查詢 - 在生產環境中，將查詢物流 API
    tracking = {
        'ORD-001': {
            'carrier': 'UPS',
            'tracking_number': '1Z999AA10123456784',
            'estimated_delivery': '2025-10-10',
            'status': '運送中'
        },
        'ORD-003': {
            'carrier': 'FedEx',
            'tracking_number': '7898765432109',
            'estimated_delivery': '已於 2025-10-07 送達',
            'status': '已送達'
        }
    }

    info = tracking.get(order_id)
    if not info:
        return {
            'status': 'error',
            'error': f'無訂單 {order_id} 的追蹤資訊',
            'report': f'找不到 {order_id} 的追蹤資訊'
        }

    return {
        'status': 'success',
        'report': f'追蹤：{info["carrier"]} {info["tracking_number"]}，預計到達時間：{info["estimated_delivery"]}',
        'data': {
            'order_id': order_id,
            'carrier': info['carrier'],
            'tracking_number': info['tracking_number'],
            'estimated_delivery': info['estimated_delivery'],
            'status': info['status']
        }
    }


def cancel_order(order_id: str, reason: str) -> Dict[str, Any]:
    """
    取消訂單（需要授權）。

    Args:
        order_id: 訂單識別碼
        reason: 取消原因

    Returns:
        包含取消狀態的字典
    """
    # 模擬訂單取消 - 在生產環境中，將進行授權檢查
    cancellable_orders = ['ORD-001', 'ORD-002']  # 只有處理中/運送中的訂單可以取消

    if order_id not in cancellable_orders:
        return {
            'status': 'error',
            'error': f'訂單 {order_id} 無法取消',
            'report': f'訂單 {order_id} 不符合取消資格'
        }

    return {
        'status': 'success',
        'report': f'訂單 {order_id} 已取消。原因：{reason}',
        'data': {
            'order_id': order_id,
            'reason': reason,
            'refund_status': 'pending',
            'cancelled_at': '2025-10-13T10:00:00Z'
        }
    }


def search_knowledge_base(query: str) -> Dict[str, Any]:
    """
    搜尋技術文件。

    Args:
        query: 搜尋查詢

    Returns:
        包含相關文件的字典
    """
    # 模擬知識庫搜尋 - 在生產環境中，將查詢文件系統
    kb = {
        'login': '若要重設密碼，請前往 設定 > 安全性 > 重設密碼',
        'connection': '檢查網際網路連線並重新啟動應用程式',
        'error': '清除應用程式快取：設定 > 應用程式 > 清除快取',
        'update': '前往 設定 > 更新 > 檢查更新',
        'sync': '確保裝置已連線並嘗試 設定 > 同步 > 立即同步'
    }

    query_lower = query.lower()
    results = []

    for key, value in kb.items():
        if key in query_lower:
            results.append({
                'topic': key,
                'solution': value
            })

    if not results:
        return {
            'status': 'success',
            'report': '未找到符合的文章',
            'data': {
                'query': query,
                'results': [],
                'suggestion': '試著搜尋：login, connection, error, update, sync'
            }
        }

    return {
        'status': 'success',
        'report': f'找到 {len(results)} 篇相關文章',
        'data': {
            'query': query,
            'results': results
        }
    }


def run_diagnostic(issue_type: str) -> Dict[str, Any]:
    """
    執行診斷測試。

    Args:
        issue_type: 要診斷的問題類型

    Returns:
        包含診斷結果的字典
    """
    # 模擬診斷 - 在生產環境中，將執行實際的診斷測試
    diagnostics = {
        'connection': {
            'tests': ['網路連線', '伺服器回應', 'DNS 解析'],
            'result': '所有系統運作正常',
            'recommendation': '清除快取並重新啟動'
        },
        'performance': {
            'tests': ['記憶體使用量', 'CPU 使用量', '磁碟空間'],
            'result': '效能在正常範圍內',
            'recommendation': '關閉未使用的應用程式'
        },
        'login': {
            'tests': ['驗證服務', '工作階段管理', '密碼驗證'],
            'result': '驗證系統運作正常',
            'recommendation': '檢查密碼並重試'
        }
    }

    diagnostic = diagnostics.get(issue_type.lower())
    if not diagnostic:
        return {
            'status': 'error',
            'error': f'未知問題類型：{issue_type}',
            'report': f'無 {issue_type} 的診斷可用'
        }

    return {
        'status': 'success',
        'report': f'{issue_type} 的診斷：{diagnostic["result"]}。建議：{diagnostic["recommendation"]}',
        'data': {
            'issue_type': issue_type,
            'tests_run': diagnostic['tests'],
            'result': diagnostic['result'],
            'recommendation': diagnostic['recommendation']
        }
    }


def create_ticket(customer_id: str, issue: str, priority: str) -> Dict[str, Any]:
    """
    建立支援工單以進行升級處理。

    Args:
        customer_id: 客戶識別碼
        issue: 問題描述
        priority: 優先級別（low, medium, high, urgent）

    Returns:
        包含工單資訊的字典
    """
    # 模擬工單建立 - 在生產環境中，將在票務系統中建立
    import random
    ticket_id = f"TKT-{random.randint(1000, 9999):04d}"

    valid_priorities = ['low', 'medium', 'high', 'urgent']
    if priority.lower() not in valid_priorities:
        priority = 'medium'  # 預設為 medium

    return {
        'status': 'success',
        'report': f'支援工單 {ticket_id} 已建立，優先級別為 {priority}',
        'data': {
            'ticket_id': ticket_id,
            'customer_id': customer_id,
            'issue': issue,
            'priority': priority,
            'status': 'open',
            'created_at': '2025-10-13T10:00:00Z',
            'estimated_response': '2 小時' if priority in ['high', 'urgent'] else '24 小時'
        }
    }


def get_billing_history(customer_id: str) -> Dict[str, Any]:
    """
    檢索帳單歷史記錄。

    Args:
        customer_id: 客戶識別碼

    Returns:
        包含帳單歷史記錄的字典
    """
    # 模擬帳單查詢 - 在生產環境中，將查詢帳單資料庫
    billing_history = {
        'CUST-001': [
            {'date': '2025-09-01', 'amount': 49.99, 'description': '月度訂閱'},
            {'date': '2025-08-01', 'amount': 49.99, 'description': '月度訂閱'},
            {'date': '2025-07-15', 'amount': 29.99, 'description': '一次性購買'}
        ],
        'CUST-002': [
            {'date': '2025-09-15', 'amount': 19.99, 'description': '基本方案'},
            {'date': '2025-08-15', 'amount': 19.99, 'description': '基本方案'}
        ]
    }

    history = billing_history.get(customer_id, [])

    if not history:
        return {
            'status': 'error',
            'error': f'找不到 {customer_id} 的帳單歷史記錄',
            'report': f'找不到客戶 {customer_id} 的帳單記錄'
        }

    total = sum(item['amount'] for item in history)

    return {
        'status': 'success',
        'report': f'找到 {len(history)} 筆 {customer_id} 的帳單記錄',
        'data': {
            'customer_id': customer_id,
            'transactions': history,
            'total_amount': total,
            'currency': 'USD'
        }
    }


def process_refund(order_id: str, amount: float) -> Dict[str, Any]:
    """
    處理退款（金額超過 $100 需要批准）。

    Args:
        order_id: 訂單識別碼
        amount: 退款金額

    Returns:
        包含退款狀態的字典
    """
    if amount > 100:
        return {
            'status': 'error',
            'error': 'REQUIRES_APPROVAL',
            'report': f'{order_id} 的 ${amount} 退款需要經理批准',
            'data': {
                'order_id': order_id,
                'amount': amount,
                'status': 'pending_approval',
                'approval_required': True
            }
        }

    return {
        'status': 'success',
        'report': f'{order_id} 的 ${amount} 退款已批准。款項將在 3-5 個工作日內入帳。',
        'data': {
            'order_id': order_id,
            'amount': amount,
            'status': 'approved',
            'processing_time': '3-5 個工作日',
            'refund_id': f'REF-{order_id}-{amount:.0f}'
        }
    }


def update_payment_method(customer_id: str, payment_type: str) -> Dict[str, Any]:
    """
    更新儲存的付款方式。

    Args:
        customer_id: 客戶識別碼
        payment_type: 新的付款方式類型

    Returns:
        包含更新確認的字典
    """
    # 模擬付款方式更新 - 在生產環境中，將更新支付系統
    valid_types = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']

    if payment_type.lower() not in valid_types:
        return {
            'status': 'error',
            'error': f'無效的付款類型：{payment_type}',
            'report': f'付款類型必須是以下之一：{", ".join(valid_types)}'
        }

    return {
        'status': 'success',
        'report': f'{customer_id} 的付款方式已更新為 {payment_type}',
        'data': {
            'customer_id': customer_id,
            'payment_type': payment_type,
            'updated_at': '2025-10-13T10:00:00Z',
            'verification_required': True,
            'status': 'pending_verification'
        }
    }

# 重點摘要
# - **核心概念**：實作一組用於客戶支援的工具函數，模擬與後端系統（如資料庫、CRM、支付網關）的互動。
# - **關鍵技術**：Python 函數、型別提示 (Type Hinting)、字典回傳格式。
# - **重要結論**：
#   - 所有工具函數都遵循一致的介面：接收參數並返回包含 `status`, `report` 和 `data` 的字典。
#   - 模擬了多種業務邏輯，如會員狀態檢查、訂單查詢、退款處理（含審核邏輯）和工單建立。
#   - 這些函數被設計為無狀態且獨立，便於 LLM 調用和測試。
# - **行動項目**：在實際生產環境中，需將模擬邏輯替換為真實的 API 調用或資料庫查詢。
