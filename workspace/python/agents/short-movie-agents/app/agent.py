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

from .screenplay_agent import screenplay_agent
from .story_agent import story_agent
from .storyboard_agent import storyboard_agent
from .utils.utils import load_prompt_from_file
from .video_agent import video_agent

# 設定日誌記錄 (Logging)
logger = logging.getLogger(__name__)

# 配置常數
MODEL = "gemini-2.5-flash"
DESCRIPTION = "根據使用者輸入，協調創作一個簡短的動畫營火故事，利用故事生成、分鏡腳本創作和影片生成的專業子代理。"

# --- 導演代理 (Director Agent / 根代理) ---

# 檢查所有必要的子代理是否已正確導入
if story_agent and screenplay_agent and storyboard_agent and video_agent:
    # 初始化根代理（導演代理）
    root_agent = Agent(
        name="director_agent",
        model=MODEL,
        description=(DESCRIPTION),
        # 從外部檔案載入提示詞指令
        instruction=load_prompt_from_file("director_agent.txt"),
        # 定義此代理下轄的子代理
        sub_agents=[
            story_agent,
            screenplay_agent,
            storyboard_agent,
            video_agent,
        ],
    )
    logger.info(f"✅ 代理 '{root_agent.name}' 已使用模型 '{MODEL}' 建立。")
else:
    # 若有任何子代理缺失，則記錄錯誤
    logger.error(
        "❌ 無法建立根代理，因為一個或多個子代理初始化失敗或缺少工具。"
    )
    if not story_agent:
        logger.error(" - 故事代理 (Story Agent) 缺失。")
    if not screenplay_agent:
        logger.error(" - 劇本代理 (Screenplay Agent) 缺失。")
    if not storyboard_agent:
        logger.error(" - 分鏡腳本代理 (Storyboard Agent) 缺失。")
    if not video_agent:
        logger.error(" - 影片代理 (Video Agent) 缺失。")
