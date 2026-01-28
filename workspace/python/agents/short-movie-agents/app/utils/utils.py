# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，不附帶任何形式的明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理權限和限制的特定語言。

import logging
import os

# 設定日誌記錄 (Logging)
logger = logging.getLogger(__name__)
# 提示詞檔案相對於此腳本的預設路徑
PROMPTS_PATH = "../prompts/"


def load_prompt_from_file(
    filename: str, default_instruction: str = "預設指令。"
) -> str:
    """從相對於此腳本的檔案中讀取指令文字。

    參數：
        filename (str): 要讀取的提示詞檔案名稱。
        default_instruction (str): 若讀取失敗則使用的預設指令。

    返回：
        str: 檔案中的指令內容或預設指令。
    """
    instruction = default_instruction
    try:
        # 建構相對於當前腳本檔案 (__file__) 的完整路徑
        filepath = os.path.join(
            os.path.dirname(__file__), PROMPTS_PATH, filename
        )
        # 以 utf-8 編碼開啟並讀取檔案
        with open(filepath, encoding="utf-8") as f:
            instruction = f.read()
        logger.info(f"成功從 {filename} 載入指令")
    except FileNotFoundError:
        # 若找不到檔案則記錄警告並使用預設值
        logger.warning(
            f"警告：找不到指令檔案：{filepath}。將使用預設值。"
        )
    except Exception as e:
        # 處理其他潛在錯誤
        logger.error(
            f"錯誤：載入指令檔案 {filepath} 時發生異常：{e}。將使用預設值。"
        )
    return instruction
