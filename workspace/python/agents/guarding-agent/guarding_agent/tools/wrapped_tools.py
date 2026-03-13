"""
包裝後的工具範例

展示如何使用 RiskToolRegistry 包裝工具，並實作進階確認邏輯。
"""

from typing import Dict, Any, List
from google.adk.tools.tool_context import ToolContext
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 低風險工具（無需確認）
# ============================================================================

def search(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """搜尋資訊（唯讀操作）

    Args:
        query: 搜尋關鍵字
        tool_context: 工具上下文

    Returns:
        搜尋結果
    """
    logger.info(f"執行搜尋：{query}")
    # 實際實作會調用搜尋服務
    return {
        'status': 'success',
        'query': query,
        'results': [
            {'title': '結果 1', 'url': 'https://example.com/1'},
            {'title': '結果 2', 'url': 'https://example.com/2'},
        ],
    }


def get_user_info(user_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """獲取用戶資訊（唯讀）

    Args:
        user_id: 用戶 ID
        tool_context: 工具上下文

    Returns:
        用戶資訊
    """
    logger.info(f"獲取用戶資訊：{user_id}")
    # 實際實作會從資料庫查詢
    return {
        'status': 'success',
        'user_id': user_id,
        'name': '測試用戶',
        'email': 'test@example.com',
    }


# ============================================================================
# 中等風險工具（條件確認）
# ============================================================================

def update_profile(
    user_id: str,
    updates: Dict[str, Any],
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """更新用戶個人資料

    根據 RiskToolRegistry 的配置，當修改欄位超過 3 個時需要確認。

    Args:
        user_id: 用戶 ID
        updates: 更新的欄位字典
        tool_context: 工具上下文

    Returns:
        更新結果
    """
    logger.info(f"更新用戶資料：{user_id}，欄位數：{len(updates)}")

    # 實際實作會更新資料庫
    return {
        'status': 'success',
        'user_id': user_id,
        'updated_fields': list(updates.keys()),
        'message': f'成功更新 {len(updates)} 個欄位',
    }


def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """發送電子郵件

    根據 RiskToolRegistry 的配置，當收件人超過 5 個時需要確認。

    Args:
        recipients: 收件人列表
        subject: 郵件主題
        body: 郵件內容
        tool_context: 工具上下文

    Returns:
        發送結果
    """
    logger.info(f"發送郵件給 {len(recipients)} 個收件人")

    # 實際實作會調用郵件服務
    return {
        'status': 'success',
        'recipients_count': len(recipients),
        'message': f'郵件已發送給 {len(recipients)} 個收件人',
    }


# ============================================================================
# 高風險工具（始終需要確認）
# ============================================================================

def delete_user(
    user_id: str,
    reason: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """刪除用戶帳號（高風險操作）

    使用進階確認機制，需要審核者提供核准決策。

    Args:
        user_id: 用戶 ID
        reason: 刪除原因
        tool_context: 工具上下文

    Returns:
        刪除結果或待審核狀態
    """
    tool_confirmation = tool_context.tool_confirmation

    # 第一次調用：請求確認
    if not tool_confirmation:
        logger.info(f"請求刪除用戶確認：{user_id}")
        tool_context.request_confirmation(
            hint=(
                f'請確認刪除用戶操作：\n'
                f'- 用戶 ID: {user_id}\n'
                f'- 原因: {reason}\n\n'
                f'請透過 FunctionResponse 回覆，payload 需包含：\n'
                f'{{"approved": true/false, "approver": "審核者ID", "reason": "決策理由"}}'
            ),
            payload={
                'approved': False,
                'approver': '',
                'reason': '',
            },
        )
        return {
            'status': 'pending',
            'message': '等待主管審核',
            'user_id': user_id,
        }

    # 第二次調用：處理確認結果
    approved = tool_confirmation.payload.get('approved', False)
    approver = tool_confirmation.payload.get('approver', 'unknown')
    decision_reason = tool_confirmation.payload.get('reason', '')

    if not approved:
        logger.info(f"刪除用戶請求被拒絕：{user_id}，審核者：{approver}")
        return {
            'status': 'rejected',
            'message': '刪除請求已被拒絕',
            'user_id': user_id,
            'approver': approver,
            'reason': decision_reason,
        }

    # 執行刪除操作
    logger.info(f"執行刪除用戶：{user_id}，審核者：{approver}")
    # 實際實作會刪除資料庫記錄

    return {
        'status': 'success',
        'message': '用戶已成功刪除',
        'user_id': user_id,
        'approver': approver,
        'deletion_reason': reason,
    }


def bulk_update(
    table: str,
    filter_conditions: Dict[str, Any],
    updates: Dict[str, Any],
    reason: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """批量更新資料（高風險操作）

    Args:
        table: 資料表名稱
        filter_conditions: 篩選條件
        updates: 更新內容
        reason: 操作原因
        tool_context: 工具上下文

    Returns:
        更新結果或待審核狀態
    """
    tool_confirmation = tool_context.tool_confirmation

    if not tool_confirmation:
        logger.info(f"請求批量更新確認：{table}")
        tool_context.request_confirmation(
            hint=(
                f'請確認批量更新操作：\n'
                f'- 資料表: {table}\n'
                f'- 篩選條件: {filter_conditions}\n'
                f'- 更新內容: {updates}\n'
                f'- 原因: {reason}\n\n'
                f'請提供審核決策。'
            ),
            payload={
                'approved': False,
                'approver': '',
                'estimated_affected_rows': 'unknown',
            },
        )
        return {
            'status': 'pending',
            'message': '等待主管審核',
            'table': table,
        }

    approved = tool_confirmation.payload.get('approved', False)
    approver = tool_confirmation.payload.get('approver', 'unknown')

    if not approved:
        return {
            'status': 'rejected',
            'message': '批量更新請求已被拒絕',
            'approver': approver,
        }

    # 執行批量更新
    logger.info(f"執行批量更新：{table}，審核者：{approver}")
    # 實際實作會執行資料庫更新
    affected_rows = 42  # 模擬

    return {
        'status': 'success',
        'message': f'成功更新 {affected_rows} 筆資料',
        'table': table,
        'affected_rows': affected_rows,
        'approver': approver,
    }


# ============================================================================
# 關鍵工具（必須確認並記錄）
# ============================================================================

def execute_payment(
    amount: float,
    currency: str,
    recipient: str,
    purpose: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """執行付款交易（關鍵操作）

    Args:
        amount: 付款金額
        currency: 貨幣類型
        recipient: 收款人
        purpose: 付款目的
        tool_context: 工具上下文

    Returns:
        交易結果或待審核狀態
    """
    tool_confirmation = tool_context.tool_confirmation

    if not tool_confirmation:
        logger.info(f"請求付款確認：{amount} {currency} to {recipient}")
        tool_context.request_confirmation(
            hint=(
                f'⚠️ 付款交易需要管理員審核 ⚠️\n\n'
                f'- 金額: {amount} {currency}\n'
                f'- 收款人: {recipient}\n'
                f'- 目的: {purpose}\n\n'
                f'請確認此交易是否合法且必要。'
            ),
            payload={
                'approved': False,
                'approver': '',
                'transaction_id': '',
            },
        )
        return {
            'status': 'pending',
            'message': '等待管理員審核',
            'amount': amount,
            'currency': currency,
            'recipient': recipient,
        }

    approved = tool_confirmation.payload.get('approved', False)
    approver = tool_confirmation.payload.get('approver', 'unknown')

    if not approved:
        return {
            'status': 'rejected',
            'message': '付款交易已被拒絕',
            'approver': approver,
        }

    # 執行付款
    logger.info(f"執行付款：{amount} {currency}，審核者：{approver}")
    transaction_id = f"TXN-{hash((amount, recipient, approver)) % 1000000:06d}"

    return {
        'status': 'success',
        'message': '付款成功',
        'transaction_id': transaction_id,
        'amount': amount,
        'currency': currency,
        'recipient': recipient,
        'approver': approver,
    }


def modify_system_config(
    config_key: str,
    new_value: Any,
    reason: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """修改系統配置（關鍵操作）

    Args:
        config_key: 配置鍵
        new_value: 新值
        reason: 修改原因
        tool_context: 工具上下文

    Returns:
        修改結果或待審核狀態
    """
    tool_confirmation = tool_context.tool_confirmation

    if not tool_confirmation:
        logger.info(f"請求系統配置修改確認：{config_key}")
        tool_context.request_confirmation(
            hint=(
                f'⚠️ 系統配置修改需要管理員審核 ⚠️\n\n'
                f'- 配置鍵: {config_key}\n'
                f'- 新值: {new_value}\n'
                f'- 原因: {reason}\n\n'
                f'警告：此操作可能影響系統穩定性。'
            ),
            payload={
                'approved': False,
                'approver': '',
            },
        )
        return {
            'status': 'pending',
            'message': '等待管理員審核',
            'config_key': config_key,
        }

    approved = tool_confirmation.payload.get('approved', False)
    approver = tool_confirmation.payload.get('approver', 'unknown')

    if not approved:
        return {
            'status': 'rejected',
            'message': '配置修改請求已被拒絕',
            'approver': approver,
        }

    # 執行配置修改
    logger.info(f"修改系統配置：{config_key}={new_value}，審核者：{approver}")
    # 實際實作會更新配置系統

    return {
        'status': 'success',
        'message': '系統配置已更新',
        'config_key': config_key,
        'new_value': new_value,
        'approver': approver,
    }
