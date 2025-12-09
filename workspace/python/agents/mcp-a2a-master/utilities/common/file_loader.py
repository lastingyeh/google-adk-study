"""
重點摘要:
- **核心概念**: 檔案讀取工具。
- **關鍵技術**: Python 檔案 I/O。
- **重要結論**: 提供了一個安全讀取指令檔案的輔助函式，並處理了檔案不存在的情況。
"""

import os


def load_instructions_file(filename: str, default: str = ""):
    """
    從檔案載入指令。如果檔案不存在，則回傳預設指令。
    Load instructions from a file. If the file does not exist, return the default instructions.

    Args:
        filename (str): 指令檔案的路徑。 (The path to the instructions file.)
        default (str): 如果檔案不存在時要回傳的預設指令。 (Default instructions to return if the file does not exist.)

    Returns:
        str: 指令檔案的內容或預設指令。 (The content of the instructions file or the default instructions.)
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    return default
