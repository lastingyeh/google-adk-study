"""
重點摘要:
- **核心概念**: 網站建構代理邏輯。
- **關鍵技術**: Google ADK, LLM Prompting。
- **重要結論**: 透過 Prompt 工程，使 LLM 能夠專注於生成 HTML 程式碼。
"""

from collections.abc import AsyncIterable
from utilities.common.file_loader import load_instructions_file
from google.adk.agents import LlmAgent
from google.adk import Runner

from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

from google.genai import types

from rich import print as rprint
from rich.syntax import Syntax

from pydantic import BaseModel, Field

import json
import logging
import os
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()

# 配置常數
MAX_QUERY_LENGTH = 10000  # 查詢內容的最大長度（字元）
MIN_QUERY_LENGTH = 1  # 查詢內容的最小長度（字元）

# 設定日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AgentResponse(BaseModel):
    """
    代理回應的標準化模型，使用 Pydantic 確保類型安全。
    Standardized agent response model using Pydantic for type safety.
    """

    is_task_complete: bool = Field(
        description="指示任務是否完成 (Indicates if the task is complete)"
    )
    content: str = Field(default="", description="最終結果內容 (Final result content)")
    updates: str = Field(default="", description="任務進度更新 (Task progress updates)")
    error: Optional[str] = Field(
        default=None, description="錯誤訊息（如有） (Error message if any)"
    )
    metadata: dict = Field(
        default_factory=dict, description="額外的元數據 (Additional metadata)"
    )


class WebsiteBuilderSimple:
    """
    一個簡易的網站建構代理，可以建立基本的網頁，並使用 Google 的代理開發框架構建。
    """

    def __init__(self, model_name: Optional[str] = None, user_id: Optional[str] = None):
        """
        初始化網站建構代理

        Args:
            model_name: LLM 模型名稱（預設從環境變數 WEBSITE_BUILDER_MODEL 讀取，或使用 gemini-2.0-flash-exp）
            user_id: 用戶 ID（預設從環境變數 WEBSITE_BUILDER_USER_ID 讀取，或使用預設值）
        """
        try:
            self.system_instruction = load_instructions_file(
                "agents/website_builder_simple/instructions.txt"
            )
            self.description = load_instructions_file(
                "agents/website_builder_simple/description.txt"
            )

            # 從環境變數或參數獲取配置
            self._model_name = model_name or os.getenv(
                "WEBSITE_BUILDER_MODEL", "gemini-2.0-flash-exp"
            )
            self._user_id = user_id or os.getenv(
                "WEBSITE_BUILDER_USER_ID", "website_builder_simple_agent_user"
            )

            logger.debug(
                f"初始化代理，使用模型: {self._model_name}, 用戶 ID: {self._user_id}"
            )
            logger.info("代理初始化完成")

            self._agent = self._build_agent()
            self._runner = Runner(
                app_name=self._agent.name,
                agent=self._agent,
                artifact_service=InMemoryArtifactService(),
                session_service=InMemorySessionService(),
                memory_service=InMemoryMemoryService(),
            )
        except Exception as e:
            logger.error(f"初始化代理失敗: {str(e)}", exc_info=True)
            raise

    def _build_agent(self) -> LlmAgent:
        """建立 LLM 代理實例"""
        try:
            agent = LlmAgent(
                name="website_builder_simple",
                model=self._model_name,
                instruction=self.system_instruction,
                description=self.description,
            )
            logger.info(f"成功建立代理: {agent.name}")
            return agent
        except Exception as e:
            logger.error(f"建立代理失敗: {str(e)}", exc_info=True)
            raise

    async def invoke(self, query: str, session_id: str) -> AsyncIterable[dict]:
        """
        調用代理。
        隨著代理處理查詢，回傳更新串流給呼叫者。

        Args:
            query: 用戶查詢內容
            session_id: 會話 ID

        Yields:
            {
                'is_task_complete': bool,  # 指示任務是否完成
                'content': str,  # 最終結果或空字串
                'updates': str,  # 任務進度更新
                'error': str | None,  # 錯誤訊息（如有）
                'metadata': dict  # 額外資訊
            }

        Raises:
            ValueError: 當查詢內容無效時
        """
        # 輸入驗證
        if not query or not query.strip():
            logger.warning("收到空的查詢內容")
            yield self._create_response(
                is_complete=True, error="查詢內容不能為空 (Query cannot be empty)"
            )
            return

        if len(query) < MIN_QUERY_LENGTH:
            logger.warning(f"查詢內容過短: {len(query)} 字元")
            yield self._create_response(
                is_complete=True,
                error=f"查詢內容過短，至少需要 {MIN_QUERY_LENGTH} 字元 (Query too short)",
            )
            return

        if len(query) > MAX_QUERY_LENGTH:
            logger.warning(f"查詢內容過長: {len(query)} 字元")
            yield self._create_response(
                is_complete=True,
                error=f"查詢內容過長，最多 {MAX_QUERY_LENGTH} 字元 (Query too long, max {MAX_QUERY_LENGTH} characters)",
            )
            return

        try:
            logger.info(f"開始處理查詢 - Session ID: {session_id}")
            logger.debug(f"查詢內容: {query[:100]}...")  # 只記錄前100個字元

            # 獲取或建立會話
            try:
                session = await self._runner.session_service.get_session(
                    app_name=self._agent.name,
                    session_id=session_id,
                    user_id=self._user_id,
                )

                if not session:
                    logger.info(f"建立新會話: {session_id}")
                    session = await self._runner.session_service.create_session(
                        app_name=self._agent.name,
                        session_id=session_id,
                        user_id=self._user_id,
                    )
            except Exception as e:
                logger.error(f"會話管理失敗: {str(e)}", exc_info=True)
                yield self._create_response(
                    is_complete=True, error=f"會話建立失敗: {str(e)}"
                )
                return

            user_content = types.Content(
                role="user", parts=[types.Part.from_text(text=query)]
            )

            async for event in self._runner.run_async(
                user_id=self._user_id, session_id=session_id, new_message=user_content
            ):
                if logger.isEnabledFor(logging.DEBUG):
                    print_json_response(
                        event, "================ NEW EVENT ================"
                    )
                    logger.debug(f"is_final_response: {event.is_final_response()}")

                if event.is_final_response():
                    final_response = ""
                    if (
                        event.content
                        and event.content.parts
                        and event.content.parts[-1].text
                    ):
                        final_response = event.content.parts[-1].text

                    logger.info(f"任務完成 - Session ID: {session_id}")
                    yield self._create_response(
                        is_complete=True, content=final_response
                    )
                else:
                    yield self._create_response(
                        is_complete=False,
                        updates="代理正在處理您的請求... (Agent is processing your request...)",
                    )

        except Exception as e:
            logger.error(f"調用代理時發生錯誤: {str(e)}", exc_info=True)
            yield self._create_response(
                is_complete=True, error=f"處理請求時發生錯誤: {str(e)}"
            )

    def _create_response(
        self,
        is_complete: bool,
        content: str = "",
        updates: str = "",
        error: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        建立標準化的回應格式，使用 Pydantic 模型確保類型安全。
        Creates a standardized response format using Pydantic model for type safety.
        """
        response = AgentResponse(
            is_task_complete=is_complete,
            content=content,
            updates=updates,
            error=error,
            metadata=metadata or {},
        )
        return response.model_dump()

    async def cleanup(self) -> None:
        """
        清理代理資源，包括會話、artifacts 等。
        Cleanup agent resources including sessions, artifacts, etc.
        """
        try:
            logger.info("開始清理代理資源")
            # 這裡可以添加具體的清理邏輯
            # 例如：清理會話、關閉連接等
            # await self._runner.session_service.cleanup()
            logger.info("代理資源清理完成")
        except Exception as e:
            logger.error(f"清理資源失敗: {str(e)}", exc_info=True)
            # 不拋出異常，確保清理過程不會中斷


def print_json_response(response: Any, title: str) -> None:
    # 顯示回應的格式化和顏色高亮視圖
    # Displays a formatted and color-highlighted view of the response
    print(f"\n=== {title} ===")  # 章節標題以便清晰 (Section title for clarity)
    try:
        if hasattr(
            response, "root"
        ):  # 檢查回應是否被 SDK 包裝 (Check if response is wrapped by SDK)
            data = response.root.model_dump(mode="json", exclude_none=True)
        else:
            data = response.model_dump(mode="json", exclude_none=True)

        json_str = json.dumps(
            data, indent=2, ensure_ascii=False
        )  # 將 dict 轉換為漂亮的 JSON 字串 (Convert dict to pretty JSON string)
        syntax = Syntax(
            json_str, "json", theme="monokai", line_numbers=False
        )  # 應用語法高亮 (Apply syntax highlighting)
        rprint(syntax)  # 帶顏色列印 (Print it with color)
    except Exception as e:
        # 如果失敗則列印後備文字 (Print fallback text if something fails)
        rprint(f"[red bold]Error printing JSON:[/red bold] {e}")
        rprint(repr(response))
