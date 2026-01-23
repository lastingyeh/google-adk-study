from typing import Dict, Any

from google.adk.tools import load_memory # Tool to query memory
from google.adk.tools.tool_context import ToolContext
from factory import memory_service_factory

memory_service = memory_service_factory()

async def remember_long_term_knowledge(tool_context: ToolContext
) -> Dict[str, Any]:
    """儲存長期資訊至記憶服務中，跨工作階段保存。"""
    # 將當前工作階段加入記憶服務
    await memory_service.add_session_to_memory(session=tool_context.session)
    return {"status": "success", "message": "已將長期資訊儲存至記憶服務"}

MEMORY_TOOLS = [
    remember_long_term_knowledge, load_memory,
]
