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

from app.utils.utils import load_prompt_from_file

# 嘗試導入 ADK 代理類別
try:
    from google.adk.agents import Agent
except ImportError:
    from adk.agents import Agent

# --- 故事代理 (Story Agent) ---
story_agent = None

try:
    # 配置常數
    MODEL = "gemini-2.5-flash"

    # 建立故事代理實例
    story_agent = Agent(
        model=MODEL,
        name="story_agent",
        # 從外部檔案載入代理描述 (用於多代理協作)
        description=load_prompt_from_file("story_agent_desc.txt"),
        # 從外部檔案載入核心指令
        instruction=load_prompt_from_file("story_agent.txt"),
        # 將生成的最終輸出存儲在工作階段狀態的 "story" 鍵下
        output_key="story",
    )
    logging.info(
        f"✅ 代理 '{story_agent.name}' 已使用模型 '{MODEL}' 建立。"
    )
except Exception as e:
    # 發生錯誤時記錄詳細資訊
    logging.error(
        f"❌ 無法建立故事代理。請檢查 API 金鑰 ({MODEL})。錯誤：{e}"
    )
