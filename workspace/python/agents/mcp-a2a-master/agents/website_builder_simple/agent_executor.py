"""
重點摘要:
- **核心概念**: 網站建構代理執行器 (Website Builder Agent Executor)。
- **關鍵技術**: 非同步任務執行, A2A 整合。
- **重要結論**: 處理從 A2A 伺服器接收到的請求，並調用 WebsiteBuilderSimple 代理來執行任務。
"""

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agents.website_builder_simple.agent import WebsiteBuilderSimple
from a2a.utils import new_task, new_agent_text_message

from a2a.utils.errors import ServerError

from a2a.types import Task, TaskState, UnsupportedOperationError

import asyncio
import logging

# 配置常數
TASK_EXECUTION_TIMEOUT = 60  # 秒，LLM 任務執行的最大超時時間
MESSAGE_PROCESSING_DELAY = 0.1  # 秒，確保事件佇列有足夠時間處理訊息

# 設定日誌
logger = logging.getLogger(__name__)


class WebsiteBuilderSimpleAgentExecutor(AgentExecutor):
    """
    實作 AgentExecutor 介面，將簡易網站建構代理整合至 A2A 框架中。
    Implements the AgentExecutor interface to integrate the
    website builder simple agent with the A2A framework.
    """

    def __init__(self):
        self.agent = WebsiteBuilderSimple()
        self._cancel_requested = False  # 取消標記

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        使用提供的上下文和事件佇列執行代理。
        Executes the agent with the provided context and event queue.

        執行流程：
        1. 提取用戶輸入 (query)
        2. 建立或獲取任務 (task)
        3. 初始化 TaskUpdater（用於更新任務狀態）
        4. 調用 Agent.invoke() 處理查詢
        5. 根據 Agent 回傳的狀態更新任務
        6. 處理各種異常情況

        任務狀態轉換：
        created → working → completed (or failed/cancelled)

        錯誤處理策略：
        - TimeoutError: 任務執行超時 (60s)
        - ConnectionError: 網路連線問題
        - ValueError: 無效輸入數據
        - Exception: 其他未預期錯誤

        可靠性設計：
        - 使用 asyncio.timeout 防止無限等待
        - 支援取消機制（_cancel_requested）
        - 所有錯誤均更新任務狀態，不會默默失敗
        """
        # ========== 步驟 1: 提取用戶輸入 ==========
        query = context.get_user_input()
        task = context.current_task

        # 如果沒有現有任務，建立新任務
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)  # 將任務發送到事件佇列

        # ========== 步驟 2: 初始化 TaskUpdater ==========
        # TaskUpdater 負責將任務狀態更新推送到 EventQueue
        # 然後由 EventQueue 透過 SSE 推送給客戶端
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        self._cancel_requested = False  # 重置取消標記

        try:
            # ========== 步驟 3: 執行 Agent 並處理回應 ==========
            # 使用 asyncio.timeout 添加超時保護
            # 防止 LLM 請求卡死或無限等待
            async with asyncio.timeout(TASK_EXECUTION_TIMEOUT):
                # invoke() 回傳 AsyncIterable，支援串流處理
                async for item in self.agent.invoke(query, task.contextId):
                    # ========== 步驟 3.1: 檢查取消請求 ==========
                    # 用戶可能在任務執行期間調用 cancel() 方法
                    if self._cancel_requested:
                        logger.info(f"任務被取消 - Task ID: {task.id}")
                        await updater.update_status(
                            TaskState.cancelled,  # 更新為取消狀態
                            new_agent_text_message(
                                "任務已被用戶取消 (Task cancelled by user)",
                                task.contextId,
                                task.id,
                            ),
                        )
                        return  # 立即結束執行

                    # ========== 步驟 3.2: 處理 Agent 回應 ==========
                    # item 的結構：
                    # {
                    #   'is_task_complete': bool,
                    #   'content': str,     # 最終結果
                    #   'updates': str,     # 進度更新
                    #   'error': str | None,
                    #   'metadata': dict
                    # }
                    is_task_complete = item.get("is_task_complete", False)

                    if not is_task_complete:
                        # 任務還在處理中，回傳進度更新
                        message = item.get(
                            "updates",
                            "代理正在處理您的請求。 (The Agent is still working on your request.)",
                        )
                        await updater.update_status(
                            TaskState.working,  # 狀態: 執行中
                            new_agent_text_message(message, task.contextId, task.id),
                        )
                    else:
                        # 任務完成，回傳最終結果
                        final_result = item.get(
                            "content", "未收到結果 (no result received)"
                        )
                        await updater.update_status(
                            TaskState.completed,  # 狀態: 完成
                            new_agent_text_message(
                                final_result, task.contextId, task.id
                            ),
                        )

                        # 等待一小段時間，確保事件佇列處理完成
                        # 這可以防止競爭條件 (race condition)
                        await asyncio.sleep(MESSAGE_PROCESSING_DELAY)
                        break  # 結束迴圈

        except asyncio.TimeoutError:
            # ========== 錯誤處理 1: 超時錯誤 ==========
            # 當任務執行超過 TASK_EXECUTION_TIMEOUT (60s) 時觸發
            # 原因可能：
            # - LLM 回應過慢
            # - 網路延遲過高
            # - Agent 內部邏輯錯誤導致卡死
            error_message = (
                f"任務執行超時 (Task execution timeout after {TASK_EXECUTION_TIMEOUT}s)"
            )
            logger.error(f"{error_message} - Task ID: {task.id}")
            await updater.update_status(
                TaskState.failed,  # 狀態: 失敗
                new_agent_text_message(error_message, task.contextId, task.id),
            )
            raise  # 重新拋出異常，讓上層處理

        except ConnectionError as e:
            # ========== 錯誤處理 2: 網路連線錯誤 ==========
            # 當無法連接到 LLM API 或外部服務時觸發
            # 原因可能：
            # - 網路中斷
            # - API 伺服器當機
            # - DNS 解析失敗
            error_message = f"網路連線失敗 (Network connection failed): {str(e)}"
            logger.error(f"{error_message} - Task ID: {task.id}", exc_info=True)
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, task.contextId, task.id),
            )
            raise

        except ValueError as e:
            # ========== 錯誤處理 3: 無效輸入錯誤 ==========
            # 當輸入數據不符合預期時觸發
            # 例如：
            # - query 太長或太短
            # - session_id 格式錯誤
            # - 缺少必要參數
            error_message = f"無效輸入 (Invalid input): {str(e)}"
            logger.error(f"{error_message} - Task ID: {task.id}", exc_info=True)
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, task.contextId, task.id),
            )
            raise

        except Exception as e:
            # ========== 錯誤處理 4: 其他未預期錯誤 ==========
            # 捕獲所有未被上面處理的異常
            # 使用 logger.exception 會自動記錄 stack trace
            error_message = f"系統錯誤 (System error): {str(e)}"
            logger.exception(f"未預期的錯誤 - Task ID: {task.id}")
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, task.contextId, task.id),
            )
            raise

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        """
        取消當前正在執行的任務。
        Cancels the currently executing task.

        Args:
            request: 請求上下文
            event_queue: 事件佇列

        Returns:
            被取消的任務，如果沒有任務則返回 None
        """
        task = request.current_task
        if not task:
            logger.warning("嘗試取消不存在的任務")
            return None

        logger.info(f"收到取消請求 - Task ID: {task.id}")
        self._cancel_requested = True

        # 給予一些時間讓執行循環檢測到取消標記
        await asyncio.sleep(MESSAGE_PROCESSING_DELAY)

        return task
