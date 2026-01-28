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

from google.adk.agents import Agent

from .utils.utils import load_prompt_from_file

# 設定日誌記錄 (Logging)
logger = logging.getLogger(__name__)

# 配置常數
MODEL = "gemini-2.5-flash"
DESCRIPTION = "負責根據故事撰寫劇本的代理"

# --- 劇本代理 (Screenplay Agent) ---
screenplay_agent = None
try:
    # 建立劇本代理實例
    screenplay_agent = Agent(
        # 對於簡單任務使用潛在的較便宜/快速模型
        model=MODEL,
        name="screenplay_agent",
        description=(DESCRIPTION),
        # 從外部檔案載入劇本創作指令
        instruction=load_prompt_from_file("screenplay_agent.txt"),
        # 將生成的劇本內容存儲在工作階段狀態的 "screenplay" 鍵下
        output_key="screenplay",
    )
    logger.info(
        f"✅ 代理 '{screenplay_agent.name}' 已使用模型 '{MODEL}' 建立。"
    )
except Exception as e:
    # 發生錯誤時記錄詳細資訊
    logger.error(
        f"❌ 無法建立劇本代理。請檢查 API 金鑰 ({MODEL})。錯誤：{e}"
    )
