"""
以模組方式執行 support_bot 的進入點 (Entry point)。

這允許透過以下方式執行機器人：
    python -m support_bot
    python -m support_bot.bot_dev
"""

from support_bot.bot_dev import main

# 如果此檔案被直接執行 (例如 python -m support_bot)，則執行 main 函式
if __name__ == "__main__":
    main()

# 重點摘要 (__main__.py)
# - 核心概念：模組的執行進入點，使套件可被視為腳本執行。
# - 關鍵技術：`if __name__ == "__main__":` 慣用法。
# - 重要結論：將執行邏輯導向 `bot_dev.py` 的 `main` 函式，確保開發模式下的啟動流程。
