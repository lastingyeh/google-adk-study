"""
File Search 文件組織的 Metadata 結構與實用工具。

定義不同政策類型的 metadata 結構，並提供新增、過濾與管理 metadata 的實用功能。
"""

from typing import Any, Dict, List
from enum import Enum
from datetime import datetime


class PolicyDepartment(str, Enum):
    """支援的政策部門。"""

    HR = "HR"
    IT = "IT"
    LEGAL = "Legal"
    SAFETY = "Safety"
    GENERAL = "General"


class PolicyType(str, Enum):
    """支援的政策類型。"""

    HANDBOOK = "handbook"
    PROCEDURE = "procedure"
    CODE_OF_CONDUCT = "code_of_conduct"
    GUIDELINE = "guideline"
    COMPLIANCE = "compliance"


class Sensitivity(str, Enum):
    """資料敏感度等級。"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class MetadataSchema:
    """File Search 文件的 Metadata 結構描述。"""

    @staticmethod
    def get_schema() -> Dict[str, str]:
        """
        取得 metadata 結構定義。

        Returns:
            dict: 欄位名稱對應型別的結構定義
        """
        return {
            "department": "string",  # HR, IT, Legal, Safety, General
            "policy_type": "string",  # handbook, procedure, code_of_conduct, guideline
            "effective_date": "date",  # YYYY-MM-DD
            "jurisdiction": "string",  # US, EU, CA, etc.
            "sensitivity": "string",  # public, internal, confidential
            "version": "numeric",  # 1, 2, 3, etc.
            "owner": "string",  # 政策擁有者 Email
            "review_cycle_months": "numeric",  # 審核週期月數
        }

    @staticmethod
    def create_metadata(
        department: str,
        policy_type: str,
        effective_date: str = None,
        jurisdiction: str = "US",
        sensitivity: str = "internal",
        version: int = 1,
        owner: str = "hr@company.com",
        review_cycle_months: int = 12,
    ) -> List[Dict[str, Any]]:
        """
        建立用於 File Search 匯入的 metadata 列表。

        Args:
            department: 政策部門 (HR, IT, Legal, Safety, General)
            policy_type: 政策類型 (handbook, procedure, etc.)
            effective_date: 政策生效日期 (YYYY-MM-DD)
            jurisdiction: 法律管轄區 (US, EU, CA, etc.)
            sensitivity: 資料敏感度 (public, internal, confidential)
            version: 政策版本號
            owner: 政策擁有者 Email
            review_cycle_months: 政策審核週期月數

        Returns:
            list: 適用於 File Search import_file() 的 Metadata 項目
        """
        if effective_date is None:
            effective_date = datetime.now().strftime("%Y-%m-%d")

        metadata = [
            {"key": "department", "string_value": department},
            {"key": "policy_type", "string_value": policy_type},
            {"key": "effective_date", "string_value": effective_date},
            {"key": "jurisdiction", "string_value": jurisdiction},
            {"key": "sensitivity", "string_value": sensitivity},
            {"key": "version", "numeric_value": version},
            {"key": "owner", "string_value": owner},
            {"key": "review_cycle_months", "numeric_value": review_cycle_months},
        ]

        return metadata

    @staticmethod
    def hr_metadata(version: int = 1) -> List[Dict[str, Any]]:
        """建立 HR 政策的 metadata。"""
        return MetadataSchema.create_metadata(
            department="HR",
            policy_type="handbook",
            jurisdiction="US",
            sensitivity="internal",
            version=version,
            owner="hr@company.com",
            review_cycle_months=12,
        )

    @staticmethod
    def it_metadata(version: int = 1) -> List[Dict[str, Any]]:
        """建立 IT 安全政策的 metadata。"""
        return MetadataSchema.create_metadata(
            department="IT",
            policy_type="procedure",
            jurisdiction="US",
            sensitivity="confidential",
            version=version,
            owner="security@company.com",
            review_cycle_months=6,
        )

    @staticmethod
    def remote_work_metadata(version: int = 1) -> List[Dict[str, Any]]:
        """建立遠端工作政策的 metadata。"""
        return MetadataSchema.create_metadata(
            department="HR",
            policy_type="procedure",
            jurisdiction="US",
            sensitivity="internal",
            version=version,
            owner="hr@company.com",
            review_cycle_months=12,
        )

    @staticmethod
    def code_of_conduct_metadata(version: int = 1) -> List[Dict[str, Any]]:
        """建立行為準則的 metadata。"""
        return MetadataSchema.create_metadata(
            department="General",
            policy_type="code_of_conduct",
            jurisdiction="US",
            sensitivity="internal",
            version=version,
            owner="legal@company.com",
            review_cycle_months=24,
        )

    @staticmethod
    def build_metadata_filter(
        department: str = None,
        policy_type: str = None,
        sensitivity: str = None,
        jurisdiction: str = None,
    ) -> str:
        """
        建立用於 File Search 查詢的 AIP-160 metadata 過濾字串。

        Args:
            department: 依部門過濾
            policy_type: 依政策類型過濾
            sensitivity: 依敏感度等級過濾
            jurisdiction: 依管轄區過濾

        Returns:
            str: AIP-160 過濾字串 (例如：'department="HR" AND sensitivity="internal"')
        """
        filters = []

        if department:
            filters.append(f'department="{department}"')
        if policy_type:
            filters.append(f'policy_type="{policy_type}"')
        if sensitivity:
            filters.append(f'sensitivity="{sensitivity}"')
        if jurisdiction:
            filters.append(f'jurisdiction="{jurisdiction}"')

        return " AND ".join(filters) if filters else ""
