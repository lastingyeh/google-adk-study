"""
風險等級定義模組

定義工具操作的風險等級分類，用於決定是否需要人工審核。
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


class RiskLevel(str, Enum):
    """工具風險等級枚舉

    風險等級決定工具調用的審核策略：
    - LOW: 低風險操作，無需確認（如查詢、讀取）
    - MEDIUM: 中等風險操作，條件確認（如有限範圍的修改）
    - HIGH: 高風險操作，需要確認（如大範圍修改、刪除）
    - CRITICAL: 關鍵操作，必須確認並記錄（如系統配置、金融交易）
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskMetadata:
    """風險元數據

    記錄工具的風險相關資訊，用於審核決策和審計追蹤。
    """
    level: RiskLevel
    description: str
    require_confirmation: bool = False
    require_reason: bool = False  # 是否需要操作原因
    require_approval_from: Optional[str] = None  # 需要哪個角色審批
    max_auto_approve_threshold: Optional[Dict[str, Any]] = None  # 自動核准閾值

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'level': self.level.value,
            'description': self.description,
            'require_confirmation': self.require_confirmation,
            'require_reason': self.require_reason,
            'require_approval_from': self.require_approval_from,
            'max_auto_approve_threshold': self.max_auto_approve_threshold,
        }


@dataclass
class ApprovalRequest:
    """審核請求數據結構

    包含人工審核所需的所有上下文資訊。
    """
    tool_name: str
    tool_args: Dict[str, Any]
    risk_level: RiskLevel
    requester: str  # 請求者 ID
    invocation_id: str  # ADK 調用 ID（用於 Resume）
    session_id: str
    timestamp: datetime
    reason: Optional[str] = None  # 操作原因
    context: Optional[Dict[str, Any]] = None  # 額外上下文

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'tool_name': self.tool_name,
            'tool_args': self.tool_args,
            'risk_level': self.risk_level.value,
            'requester': self.requester,
            'invocation_id': self.invocation_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason,
            'context': self.context,
        }


@dataclass
class ApprovalDecision:
    """審核決策數據結構

    記錄審核者的決策和理由。
    """
    approved: bool
    approver: str  # 審核者 ID
    decision_time: datetime
    reason: Optional[str] = None  # 決策理由
    modified_args: Optional[Dict[str, Any]] = None  # 修改後的參數（部分核准）

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'approved': self.approved,
            'approver': self.approver,
            'decision_time': self.decision_time.isoformat(),
            'reason': self.reason,
            'modified_args': self.modified_args,
        }


# 預定義的風險配置範例
DEFAULT_RISK_CONFIGS = {
    # 低風險：查詢操作
    'search': RiskMetadata(
        level=RiskLevel.LOW,
        description='搜尋資訊（唯讀操作）',
        require_confirmation=False,
    ),
    'get_user_info': RiskMetadata(
        level=RiskLevel.LOW,
        description='獲取用戶資訊（唯讀）',
        require_confirmation=False,
    ),

    # 中等風險：有限範圍的修改
    'update_profile': RiskMetadata(
        level=RiskLevel.MEDIUM,
        description='更新用戶個人資料',
        require_confirmation=False,  # 使用條件確認
        max_auto_approve_threshold={'fields': 3},  # 最多修改 3 個欄位
    ),
    'send_email': RiskMetadata(
        level=RiskLevel.MEDIUM,
        description='發送電子郵件',
        require_confirmation=False,  # 使用條件確認
        max_auto_approve_threshold={'recipients': 5},  # 最多 5 個收件人
    ),

    # 高風險：批量操作或刪除
    'delete_user': RiskMetadata(
        level=RiskLevel.HIGH,
        description='刪除用戶帳號',
        require_confirmation=True,
        require_reason=True,
        require_approval_from='manager',
    ),
    'bulk_update': RiskMetadata(
        level=RiskLevel.HIGH,
        description='批量更新資料',
        require_confirmation=True,
        require_reason=True,
        require_approval_from='manager',
    ),

    # 關鍵：系統配置或金融交易
    'execute_payment': RiskMetadata(
        level=RiskLevel.CRITICAL,
        description='執行付款交易',
        require_confirmation=True,
        require_reason=True,
        require_approval_from='admin',
    ),
    'modify_system_config': RiskMetadata(
        level=RiskLevel.CRITICAL,
        description='修改系統配置',
        require_confirmation=True,
        require_reason=True,
        require_approval_from='admin',
    ),
}
