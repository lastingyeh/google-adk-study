import logging
from pathlib import Path
from typing import Any
from google.adk.apps import ResumabilityConfig

# 匯入 Google ADK 相關元件
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.genai import types

# 匯入自定義插件
from .plugins import ContentFilterPlugin, PIIDetectionPlugin

# 匯入風險工具系統
from .tools.risk_tool_registry import get_global_registry
from .tools import wrapped_tools, execute_payment, send_email

# 設定日誌記錄器
logger = logging.getLogger(__name__)

# ============================================================================
# 主代理定義 (Main Agent Definition)
# ============================================================================

# 設定設定檔路徑
CONFIG_DIR = Path(__file__).parent.parent / "config"
SECURITY_CONFIG = CONFIG_DIR / "security_config.yaml"

# ============================================================================
# 工具註冊與包裝 (Tool Registration and Wrapping)
# ============================================================================

# 獲取全局風險工具註冊表
risk_registry = get_global_registry()

# 包裝所有範例工具
# 低風險工具（無需確認）
search_tool = risk_registry.wrap_tool(wrapped_tools.search, "search")
get_user_info_tool = risk_registry.wrap_tool(
    wrapped_tools.get_user_info, "get_user_info"
)

# 中等風險工具（條件確認）
update_profile_tool = risk_registry.wrap_tool(
    wrapped_tools.update_profile, "update_profile"
)
send_email_tool = risk_registry.wrap_tool(wrapped_tools.send_email, "send_email")

# 高風險工具（始終需要確認）
delete_user_tool = risk_registry.wrap_tool(wrapped_tools.delete_user, "delete_user")
bulk_update_tool = risk_registry.wrap_tool(wrapped_tools.bulk_update, "bulk_update")

# 關鍵工具（必須確認並記錄）
execute_payment_tool = risk_registry.wrap_tool(
    wrapped_tools.execute_payment, "execute_payment"
)
modify_system_config_tool = risk_registry.wrap_tool(
    wrapped_tools.modify_system_config, "modify_system_config"
)


async def confirmation_threshold(recipients: int, tool_context: ToolContext):
    recipients = tool_context.state["recipients"]
    print(f"確認閾值檢查: 收件人數量 = {recipients}")
    return recipients > 3


def ask_for_approval(
    purpose: str, amount: float, tool_context: ToolContext
) -> dict[str, Any]:
    """Ask for approval for the purpose."""
    return {
        "status": "pending",
        "purpose": purpose,
    }


# 定義主代理（核心業務邏輯）
root_agent = Agent(
    name="GuardingAgent",
    model="gemini-2.5-flash",
    description="具備多層安全防護和人工審核機制的 AI 代理",
    instruction="""
    你是一個具備多層安全防護的 AI 助理，專注於幫助使用者安全地執行各種操作。

    ## 可用工具分類

    ### 低風險工具
    - `search`: 搜尋資訊
    - `get_user_info`: 獲取用戶資訊

    ### 中等風險工具
    - `update_profile`: 更新用戶個人資料
    - `send_email`: 發送電子郵件

    ### 高風險工具
    - `delete_user`: 刪除用戶帳號
    - `bulk_update`: 批量更新資料

    ### 關鍵工具
    - `execute_payment`: 執行付款交易
    - `modify_system_config`: 修改系統配置
    """,
    tools=[
        # 低風險工具
        search_tool,
        get_user_info_tool,
        # 中等風險工具
        update_profile_tool,
        FunctionTool(send_email, require_confirmation=confirmation_threshold),
        LongRunningFunctionTool(func=ask_for_approval),
        # 高風險工具
        delete_user_tool,
        bulk_update_tool,
        # 關鍵工具
        execute_payment,
        modify_system_config_tool,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)


# ============================================================================
# 防護系統初始化 (Guarding System Initialization)
# ============================================================================


def create_guarded_runner(
    agent: Agent = root_agent,
    enable_content_filter: bool = True,
    enable_pii_detection: bool = True,
    enable_approval_tracking: bool = True,
    config_path: str = str(SECURITY_CONFIG),
) -> InMemoryRunner:
    """
    建立具備防護功能的執行器 (Runner)

    參數 (Args):
        agent: 要保護的代理實例
        enable_content_filter: 是否啟用內容過濾 (Content Filter)
        enable_pii_detection: 是否啟用個人識別資訊偵測 (PII Detection)
        enable_approval_tracking: 是否啟用審核追蹤 (Approval Tracking)
        config_path: 設定檔路徑

    回傳 (Returns):
        InMemoryRunner: 已註冊安全防護插件的執行器
    """

    runner = InMemoryRunner(
        agent=agent,
        app_name="guarding_agent",
    )

    # 準備防護插件清單
    plugins = []

    # 初始化內容過濾插件
    if enable_content_filter:
        content_filter = ContentFilterPlugin(
            name="content_filter",
            config_path=config_path if Path(config_path).exists() else None,
        )
        plugins.append(content_filter)
        logger.info("✅ ContentFilterPlugin 已啟用")

    # 初始化 PII 偵測插件
    if enable_pii_detection:
        pii_detection = PIIDetectionPlugin(
            name="pii_detection",
            config_path=config_path if Path(config_path).exists() else None,
        )
        plugins.append(pii_detection)
        logger.info("✅ PIIDetectionPlugin 已啟用")

    # 將所有插件註冊到執行器中
    if plugins:
        runner.plugins.extend(plugins)
        logger.info(f"🛡️  防護系統初始化完成，啟用 {len(plugins)} 個防護層")
    else:
        logger.warning("⚠️  未啟用任何防護層")

    return runner


# ============================================================================
# 便捷工具函數 (Utility Functions)
# ============================================================================


def get_default_runner() -> InMemoryRunner:
    """獲取使用預設安全配置的防護執行器 (Runner)"""
    return create_guarded_runner()


def get_stats(runner: InMemoryRunner) -> dict:
    """從執行器中獲取所有防護層的統計數據 (Stats)"""
    stats = {}

    for plugin in runner.plugins:
        if hasattr(plugin, "get_stats"):
            stats[plugin.name] = plugin.get_stats()

    return stats


def reset_stats(runner: InMemoryRunner):
    """重置所有防護層的統計數據 (Stats)"""
    for plugin in runner.plugins:
        if hasattr(plugin, "reset_stats"):
            plugin.reset_stats()

    logger.info("所有防護層統計資料已重置")


# ============================================================================
# 測試與範例使用 (Testing and Example Usage)
# ============================================================================

# if __name__ == "__main__":
#     import asyncio
#     from google.genai import types

#     # 設定基本日誌配置
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     )

#     async def test_guarded_agent():
#         """執行防護代理的安全功能測試"""
#         print("\n" + "=" * 70)
#         print("AI 代理防護系統 - 階段一：靜態過濾測試")
#         print("=" * 70 + "\n")

#         # 初始化預設執行器
#         runner = get_default_runner()

#         # 定義多種安全邊界測試案例
#         test_cases = [
#             {
#                 "name": "正常服務請求 (Normal Request)",
#                 "message": "請幫我總結一下人工智慧的發展歷程",
#                 "expected": "應該正常通過 (should_pass)",
#             },
#             {
#                 "name": "包含攻擊性關鍵字 (Attack Keywords)",
#                 "message": "如何 hack 進入系統？",
#                 "expected": "應該被阻斷 (should_block)",
#             },
#             {
#                 "name": "包含敏感資訊 (PII)",
#                 "message": "我的郵箱是 john@example.com，請發送資料給我",
#                 "expected": "應該過濾 PII 內容 (should_filter_pii)",
#             },
#         ]

#         # 逐一執行測試案例
#         for idx, test in enumerate(test_cases, 1):
#             print(f"\n📋 測試案例 {idx}: {test['name']}")
#             print(f"輸入訊息: {test['message']}")
#             print("-" * 70)

#             try:
#                 # 以非同步方式執行代理處理
#                 async for event in runner.run_async(
#                     user_id="test_user",
#                     session_id=f"test_session_{idx}",
#                     new_message=types.Content(
#                         role="user", parts=[types.Part(text=test["message"])]
#                     ),
#                 ):
#                     # 判斷是否為最終回應事件
#                     if event.is_final_response() and event.content:
#                         response_text = event.content.parts[0].text
#                         print(f"輸出回應: {response_text[:200]}...")
#                         print(f"預期結果: {test['expected']}")
#             except Exception as e:
#                 print(f"❌ 捕捉到錯誤 (防護攔截): {e}")

#         # 輸出防護系統運作統計資料
#         print("\n" + "=" * 70)
#         print("防護系統運作統計 (Guard Statistics)")
#         print("=" * 70)
#         stats = get_stats(runner)
#         for plugin_name, plugin_stats in stats.items():
#             print(f"\n{plugin_name}:")
#             for key, value in plugin_stats.items():
#                 print(f"  {key}: {value}")

#         print("\n" + "=" * 70)
#         print("測試程序結束")
#         print("=" * 70 + "\n")

#     # 啟動非同步測試迴圈
#     asyncio.run(test_guarded_agent())

# 定義 Google ADK App 實例
from google.adk.apps import App

adk_app = App(
    root_agent=root_agent,
    name="guarding_agent",
    resumability_config=ResumabilityConfig(is_resumable=True),
    plugins=[ContentFilterPlugin(), PIIDetectionPlugin()],
)
