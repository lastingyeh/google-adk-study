"""
自動儲存記憶的 Agent（使用 AgentCallbacks）
"""
from google.adk.agents import Agent
from google.adk.memory import VertexAiMemoryBankService


async def save_to_memory_callback(callback_context):
    """會話結束後自動儲存到記憶體"""
    try:
        await callback_context.memory_service.add_session_to_memory(
            callback_context.session
        )
        print("✅ 會話已自動儲存到記憶體")
    except Exception as e:
        print(f"⚠️ 儲存記憶失敗: {e}")


def create_auto_save_agent() -> Agent:
    """建立會自動儲存記憶的 Agent"""
    return Agent(
        name="auto_save_agent",
        model="gemini-2.0-flash-exp",
        instruction="你是一個會記住對話的助理",
        after_agent_callback=save_to_memory_callback  # 自動儲存
    )