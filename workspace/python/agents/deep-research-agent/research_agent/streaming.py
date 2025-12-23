import os
from typing import Optional, Generator, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from google import genai
except ImportError:
    raise ImportError("需要 google-genai >= 1.55.0")

from dotenv import load_dotenv

load_dotenv()

# 代理 ID
DEEP_RESEARCH_AGENT_ID = "deep-research-pro-preview-12-2025"


class ProgressType(Enum):
    """研究期間的進度更新類型 (Types of progress updates during research)。"""
    START = "start"       # 開始
    THOUGHT = "thought"   # 思考
    CONTENT = "content"   # 內容
    COMPLETE = "complete" # 完成
    ERROR = "error"       # 錯誤


@dataclass
class ResearchProgress:
    """來自研究串流的進度更新 (A progress update from the research stream)。"""
    type: ProgressType
    content: str = ""
    interaction_id: Optional[str] = None
    event_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def stream_research(
    query: str,
    api_key: Optional[str] = None,
    include_thoughts: bool = True,
) -> Generator[ResearchProgress, None, None]:
    """
    串流研究進度並提供即時更新。

    此產生器 (generator) 會在深度研究代理執行研究任務時產出進度更新，包括：
    - 帶有互動 ID 的開始事件
    - 思考摘要 (推理步驟)
    - 內容區塊 (報告文字)
    - 完成事件

    Args:
        query: 研究查詢。
        api_key: 可選的 API 金鑰。
        include_thoughts: 是否啟用思考摘要。

    Yields:
        ResearchProgress 物件，包含更新資訊。

    範例：
        >>> for progress in stream_research("AI trends 2025"):
        ...     if progress.type == ProgressType.THOUGHT:
        ...         print(f"💭 {progress.content}")
        ...     elif progress.type == ProgressType.CONTENT:
        ...         print(progress.content, end="")
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("需要 GOOGLE_API_KEY")

    client = genai.Client(api_key=key)

    # 建構代理設定
    agent_config = {"type": "deep-research"}
    if include_thoughts:
        agent_config["thinking_summaries"] = "auto"

    # 啟動串流請求
    stream = client.interactions.create(
        input=query,
        agent=DEEP_RESEARCH_AGENT_ID,
        background=True,
        stream=True,
        agent_config=agent_config
    )

    interaction_id = None
    last_event_id = None

    for chunk in stream:
        # 追蹤互動 ID
        if chunk.event_type == "interaction.start":
            interaction_id = chunk.interaction.id
            yield ResearchProgress(
                type=ProgressType.START,
                content=f"研究已開始",
                interaction_id=interaction_id,
            )

        # 追蹤事件 ID 以供潛在的重連使用
        if hasattr(chunk, 'event_id') and chunk.event_id:
            last_event_id = chunk.event_id

        # 處理內容增量 (content deltas)
        if chunk.event_type == "content.delta":
            if hasattr(chunk.delta, 'type'):
                if chunk.delta.type == "text":
                    yield ResearchProgress(
                        type=ProgressType.CONTENT,
                        content=chunk.delta.text,
                        interaction_id=interaction_id,
                        event_id=last_event_id,
                    )
                elif chunk.delta.type == "thought_summary":
                    thought_text = ""
                    if hasattr(chunk.delta, 'content') and hasattr(chunk.delta.content, 'text'):
                        thought_text = chunk.delta.content.text
                    yield ResearchProgress(
                        type=ProgressType.THOUGHT,
                        content=thought_text,
                        interaction_id=interaction_id,
                        event_id=last_event_id,
                    )

        # 處理完成事件
        if chunk.event_type == "interaction.complete":
            yield ResearchProgress(
                type=ProgressType.COMPLETE,
                content="研究完成",
                interaction_id=interaction_id,
            )

        # 處理錯誤
        if chunk.event_type == "error":
            error_msg = getattr(chunk, 'message', '未知錯誤')
            yield ResearchProgress(
                type=ProgressType.ERROR,
                content=str(error_msg),
                interaction_id=interaction_id,
            )


def stream_research_with_callback(
    query: str,
    on_thought: Optional[Callable[[str], None]] = None,
    on_content: Optional[Callable[[str], None]] = None,
    on_complete: Optional[Callable[[str], None]] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    使用回呼處理程式 (callback handlers) 進行串流研究。

    一個方便的函式，處理串流並針對不同的事件類型呼叫您的回呼函式。

    Args:
        query: 研究查詢。
        on_thought: 思考摘要的回呼函式。
        on_content: 內容區塊的回呼函式。
        on_complete: 研究完成時的回呼函式。
        api_key: 可選的 API 金鑰。

    Returns:
        完整的研究報告。

    範例：
        >>> report = stream_research_with_callback(
        ...     "Quantum computing advances",
        ...     on_thought=lambda t: print(f"💭 {t}"),
        ...     on_content=lambda c: print(c, end=""),
        ... )
    """
    full_content = []

    for progress in stream_research(query, api_key=api_key):
        if progress.type == ProgressType.THOUGHT and on_thought:
            on_thought(progress.content)
        elif progress.type == ProgressType.CONTENT:
            full_content.append(progress.content)
            if on_content:
                on_content(progress.content)
        elif progress.type == ProgressType.COMPLETE and on_complete:
            on_complete(progress.interaction_id or "")

    return "".join(full_content)


class ResearchStreamReconnector:
    """
    處理研究串流斷線後的重連 (Handles reconnection to a research stream after disconnection)。

    在長時間的研究任務中可能會發生網路中斷。
    此類別有助於從中斷處恢復。

    範例：
        >>> reconnector = ResearchStreamReconnector(api_key)
        >>> for progress in reconnector.stream(query):
        ...     process(progress)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.interaction_id: Optional[str] = None
        self.last_event_id: Optional[str] = None
        self.max_retries = 3
        self.retry_delay = 2

    def stream(
        self,
        query: str,
        include_thoughts: bool = True
    ) -> Generator[ResearchProgress, None, None]:
        """
        具有自動失敗重連功能的串流研究。

        Args:
            query: 研究查詢。
            include_thoughts: 是否包含思考摘要。

        Yields:
            ResearchProgress 物件。
        """
        import time

        retries = 0
        is_complete = False

        while not is_complete and retries <= self.max_retries:
            try:
                # 第一次嘗試：開始新的研究
                if self.interaction_id is None:
                    for progress in self._initial_stream(query, include_thoughts):
                        yield progress
                        if progress.type == ProgressType.COMPLETE:
                            is_complete = True
                else:
                    # 重連：從最後一個事件恢復
                    for progress in self._resume_stream():
                        yield progress
                        if progress.type == ProgressType.COMPLETE:
                            is_complete = True

            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    yield ResearchProgress(
                        type=ProgressType.ERROR,
                        content=f"超過最大重試次數: {e}"
                    )
                    break
                time.sleep(self.retry_delay)

    def _initial_stream(
        self,
        query: str,
        include_thoughts: bool
    ) -> Generator[ResearchProgress, None, None]:
        """開始初始串流請求。"""
        for progress in stream_research(query, self.api_key, include_thoughts):
            # 追蹤 ID 以供潛在的重連使用
            if progress.interaction_id:
                self.interaction_id = progress.interaction_id
            if progress.event_id:
                self.last_event_id = progress.event_id
            yield progress

    def _resume_stream(self) -> Generator[ResearchProgress, None, None]:
        """從最後已知位置恢復串流。"""
        if not self.interaction_id:
            raise ValueError("沒有互動 ID 可供恢復")

        client = genai.Client(api_key=self.api_key)

        # 使用 last_event_id 恢復，以從中斷處繼續
        kwargs = {"id": self.interaction_id, "stream": True}
        if self.last_event_id:
            kwargs["last_event_id"] = self.last_event_id

        stream = client.interactions.get(**kwargs)

        for chunk in stream:
            if hasattr(chunk, 'event_id') and chunk.event_id:
                self.last_event_id = chunk.event_id

            if chunk.event_type == "content.delta":
                if hasattr(chunk.delta, 'type'):
                    if chunk.delta.type == "text":
                        yield ResearchProgress(
                            type=ProgressType.CONTENT,
                            content=chunk.delta.text,
                            interaction_id=self.interaction_id,
                        )
                    elif chunk.delta.type == "thought_summary":
                        yield ResearchProgress(
                            type=ProgressType.THOUGHT,
                            content=getattr(chunk.delta.content, 'text', ''),
                            interaction_id=self.interaction_id,
                        )

            if chunk.event_type == "interaction.complete":
                yield ResearchProgress(
                    type=ProgressType.COMPLETE,
                    content="研究完成",
                    interaction_id=self.interaction_id,
                )
