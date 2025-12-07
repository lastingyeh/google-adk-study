"""
Policy Navigator 的實用功能函式。

用於檔案處理、日誌記錄和常見操作的輔助函式。
"""

import os
from pathlib import Path
from typing import List
from loguru import logger


def get_sample_policies_dir() -> str:
    """
    取得範例政策目錄路徑。

    Returns:
        str: sample_policies 目錄的絕對路徑
    """
    current_dir = Path(__file__).parent.parent
    return str(current_dir / "sample_policies")


def get_policy_files(
    directory: str = None,
    file_types: List[str] = None,
) -> List[str]:
    """
    從目錄中取得政策檔案列表。

    Args:
        directory: 要搜尋的目錄 (若為 None 則使用 sample_policies)
        file_types: 要包含的副檔名列表 (預設：['.md', '.txt', '.pdf'])

    Returns:
        list: 絕對檔案路徑的列表
    """
    if directory is None:
        directory = get_sample_policies_dir()

    if file_types is None:
        file_types = [".md", ".txt", ".pdf"]

    if not os.path.exists(directory):
        logger.warning(f"找不到目錄: {directory}")
        return []

    policy_files = []
    for file in os.listdir(directory):
        if any(file.endswith(ftype) for ftype in file_types):
            full_path = os.path.join(directory, file)
            policy_files.append(full_path)

    logger.info(f"在 {directory} 中找到 {len(policy_files)} 個政策檔案")
    return sorted(policy_files)


def get_specific_policy(
    policy_name: str,
    directory: str = None,
) -> str:
    """
    取得特定政策檔案的絕對路徑。

    Args:
        policy_name: 政策名稱 (例如：'hr_handbook.md')
        directory: 要搜尋的目錄 (若為 None 則使用 sample_policies)

    Returns:
        str: 政策檔案的絕對路徑，若找不到則為空字串
    """
    if directory is None:
        directory = get_sample_policies_dir()

    full_path = os.path.join(directory, policy_name)

    if os.path.exists(full_path):
        return full_path

    logger.warning(f"找不到政策檔案: {policy_name}")
    return ""


def validate_api_key() -> bool:
    """
    驗證是否已設定 GOOGLE_API_KEY。

    Returns:
        bool: 如果 API 金鑰已設定則為 True
    """
    from policy_navigator.config import Config

    if not Config.GOOGLE_API_KEY:
        logger.error(
            "GOOGLE_API_KEY 未設定。請在 .env 檔案或環境變數中設定。"
        )
        return False

    return True


def get_store_name_for_policy(policy_file: str) -> str:
    """
    根據政策檔案決定適當的 store 類型。

    Args:
        policy_file: 政策檔案的路徑或名稱

    Returns:
        str: Store 類型 (例如：'hr', 'it', 'legal', 'safety')
    """
    policy_lower = policy_file.lower()

    if "hr" in policy_lower or "handbook" in policy_lower:
        return "hr"
    elif "it" in policy_lower or "security" in policy_lower:
        return "it"
    elif "legal" in policy_lower or "compliance" in policy_lower:
        return "legal"
    elif "safety" in policy_lower or "conduct" in policy_lower:
        return "safety"
    elif "remote" in policy_lower:
        return "hr"  # 遠端工作與 HR 相關
    else:
        return "hr"  # 預設為 HR


def format_response(
    status: str,
    message: str,
    details: dict = None,
) -> str:
    """
    格式化回應訊息以供顯示。

    Args:
        status: 狀態 ('success', 'error', 'warning')
        message: 主要訊息
        details: 選擇性的詳細資訊字典

    Returns:
        str: 格式化後的訊息
    """
    prefix = {
        "success": "✓",
        "error": "✗",
        "warning": "⚠",
    }.get(status, "→")

    result = f"{prefix} {message}\n"

    if details:
        for key, value in details.items():
            if isinstance(value, list):
                result += f"  {key}:\n"
                for item in value:
                    result += f"    - {item}\n"
            else:
                result += f"  {key}: {value}\n"

    return result
