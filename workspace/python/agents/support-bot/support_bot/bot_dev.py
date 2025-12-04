"""
Slack 機器人開發伺服器 (Socket Mode)

此模組以 Socket Mode 執行支援機器人，非常適合開發使用。
Socket Mode 允許您的機器人接收來自 Slack 的事件，而無需公開的 HTTP webhook。

用法：
    python -m support_bot.bot_dev

需求：
    - support_bot/ 目錄下需有 .env 檔案，並包含：
      * SLACK_BOT_TOKEN (以 xoxb- 開頭)
      * SLACK_APP_TOKEN (以 xapp- 開頭)
      * GOOGLE_API_KEY (用於 Gemini API)
"""

import os
import sys
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 設定日誌記錄 (logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 從 .env 檔案載入環境變數
load_dotenv()

# 從環境變數取得憑證
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# 驗證憑證
if not all([SLACK_BOT_TOKEN, SLACK_APP_TOKEN, GOOGLE_API_KEY]):
    logger.error("❌ 缺少必要的環境變數！")
    logger.error("   需求：SLACK_BOT_TOKEN, SLACK_APP_TOKEN, GOOGLE_API_KEY")
    logger.error("   請檢查您的 support_bot/.env 檔案")
    sys.exit(1)

# 初始化 Slack app
app = App(token=SLACK_BOT_TOKEN)

# 匯入 agent
try:
    from support_bot.agent import root_agent
    logger.info("✅ 成功載入 support_bot agent")
except ImportError as e:
    logger.error(f"❌ 匯入 agent 失敗：{e}")
    sys.exit(1)


@app.event("app_mention")
def handle_mention(body, say, logger):
    """
    處理機器人在訊息中被提及 (mention) 的事件。

    此函式：
    1. 提取使用者的訊息
    2. 將其發送給 ADK agent
    3. 將 agent 的回應發送回 Slack
    """
    try:
        # 取得訊息文字並移除機器人提及
        message_text = body["event"]["text"]

        # 從訊息中移除機器人提及 (@Support Bot)
        user_message = message_text.split(">", 1)[-1].strip()

        logger.info(f"📨 收到訊息：{user_message}")

        # 顯示正在輸入的提示
        say(f"⏳ 正在處理您的請求：`{user_message}`")

        # 發送給 ADK agent (在真實應用程式中，您會使用 agent.generate() 方法)
        # 目前，我們將展示 agent 如何被使用
        logger.info(f"✓ Agent 將處理：{user_message}")

        # 發送回應
        response = (
            f"✅ Agent 已處理您的訊息：\n"
            f"*訊息：* {user_message}\n"
            f"*狀態：* 準備與 ADK agent 整合\n\n"
            f"_在生產環境中，這將呼叫 agent 的工具，例如：_\n"
            f"  • 搜尋知識庫\n"
            f"  • 建立支援工單\n"
            f"  • 取得公司資訊"
        )

        say(response)
        logger.info("✓ 回應已發送至 Slack")

    except Exception as e:
        logger.error(f"處理訊息時發生錯誤：{e}", exc_info=True)
        say(f"❌ 錯誤：{str(e)}")


@app.event("message")
def handle_message(body, say, logger):
    """處理傳送給機器人的直接訊息 (Direct Messages)。"""
    try:
        if "text" in body["event"]:
            message_text = body["event"]["text"]
            logger.info(f"💬 直接訊息：{message_text}")

            # 發送回應
            response = (
                f"✅ 已收到您的訊息：\n"
                f"*訊息：* {message_text}\n\n"
                f"💡 試著在頻道中使用 `@Support Bot` 提及我以使用完整功能！"
            )
            say(response)
    except Exception as e:
        logger.error(f"處理訊息時發生錯誤：{e}", exc_info=True)


def main():
    """啟動 Socket Mode 處理常式 (handler)。"""
    logger.info("🚀 正在以 Socket Mode 啟動 Support Bot...")
    logger.info("📡 正在使用 Socket Mode 連線至 Slack...")

    # 建立 Socket Mode handler
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)

    try:
        logger.info("✅ 機器人運作中！正在監聽提及 (mentions)...")
        logger.info("📝 試著在 Slack 中提及機器人：@Support Bot help")
        logger.info("⏹️  按 Ctrl+C 停止機器人")

        handler.start()
    except KeyboardInterrupt:
        logger.info("⏹️  正在關閉機器人...")
        handler.close()
        logger.info("✅ 機器人已停止")
    except Exception as e:
        logger.error(f"❌ 錯誤：{e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

# 重點摘要 (bot_dev.py)
# - 核心概念：使用 Slack Socket Mode 進行本地開發的伺服器腳本。
# - 關鍵技術：Slack Bolt (Socket Mode), Python logging, python-dotenv。
# - 重要結論：允許開發者在不需要公開 Webhook 的情況下，即時接收 Slack 事件並測試機器人邏輯。
# - 行動項目：執行此檔案以啟動開發伺服器。
