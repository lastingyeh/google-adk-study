"""
custom_session_agent 的入口點。

此腳本在 ADK CLI 初始化「之前」註冊自定義會話服務。
這確保當您執行 `python -m custom_session_agent web` 時，
Redis 服務即可供使用。
"""

# 匯入自定義會話服務演示類別
from custom_session_agent.agent import CustomSessionServiceDemo

try:
    # 嘗試匯入 ADK CLI 工具
    from google.adk.cli import cli_tools_click
except ImportError:
    # 若未安裝 ADK，提供備用方案以便測試/開發
    class cli_tools_click:
        @staticmethod
        def main():
            print("警告：未偵測到 google-adk，CLI 無法啟動。")

def main():
    """主入口點，在 ADK CLI 啟動前註冊服務。"""

    # 在 ADK CLI 初始化之前註冊自定義服務 (註冊順序至關重要)
    CustomSessionServiceDemo.register_redis_service()
    CustomSessionServiceDemo.register_memory_service()

    print("\n" + "=" * 70)
    print("🎯 自定義會話服務 (Custom Session Services) - 入口點")
    print("=" * 70)
    print()
    print("✅ Redis 服務已註冊並就緒！")
    print("✅ Memory 服務已註冊並就緒！")
    print()
    print("要使用自定義會話服務：")
    print("  python -m custom_session_agent web --session_service_uri=redis://")
    print()
    print("=" * 70 + "\n")

    # 現在啟動 ADK CLI，此時服務已完成註冊
    cli_tools_click.main()

if __name__ == "__main__":
    # 執行主程式
    main()

"""
### 重點摘要
- **核心概念**：確保服務註冊先於 CLI 初始化。
- **關鍵技術**：Python 進入點 (`__main__`), 服務預註冊模式。
- **重要結論**：這是自定義 ADK 會話後端的標準實作流程，避免因載入順序導致註冊失效。
- **行動項目**：始終透過此入口點啟動 Agent 以確保自定義後端生效。
"""
