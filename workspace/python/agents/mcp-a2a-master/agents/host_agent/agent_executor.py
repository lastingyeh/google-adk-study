"""
重點摘要:
- **核心概念**: 代理執行器 (Agent Executor)。
- **關鍵技術**: 非同步程式設計 (`asyncio`), 事件佇列 (`EventQueue`), 狀態模式 (Task State)。
- **重要結論**: 連接 A2A 伺服器請求與 HostAgent 邏輯，處理任務生命週期（建立、更新、完成、失敗）。
"""

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agents.host_agent.agent import HostAgent
from a2a.utils import new_task, new_agent_text_message

from a2a.utils.errors import ServerError

from a2a.types import Task, TaskState, UnsupportedOperationError

import asyncio


class HostAgentExecutor(AgentExecutor):
    """
    實作 AgentExecutor 介面，將 Host Agent 整合至 A2A 框架中。
    """

    def __init__(self):
        self.agent = HostAgent()

    async def create(self):
        """
        工廠方法，用於建立並非同步初始化 HostAgentExecutor。
        """
        await self.agent.create()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        使用提供的上下文和事件佇列執行代理。
        """
        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            async for item in self.agent.invoke(query, task.context_id):
                is_task_complete = item.get("is_task_complete", False)

                if not is_task_complete:
                    message = item.get(
                        "updates",
                        "代理正在處理您的請求。 (The Agent is still working on your request.)",
                    )
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(message, task.context_id, task.id),
                    )
                else:
                    final_result = item.get(
                        "content", "未收到結果 (no result received)"
                    )
                    await updater.update_status(
                        TaskState.completed,
                        new_agent_text_message(final_result, task.context_id, task.id),
                    )

                    await asyncio.sleep(
                        0.1
                    )  # 允許訊息處理的時間 (Allow time for the message to be processed)

                    break
        except Exception as e:
            error_message = f"發生錯誤 (An error occurred): {str(e)}"
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, task.context_id, task.id),
            )
            raise

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
