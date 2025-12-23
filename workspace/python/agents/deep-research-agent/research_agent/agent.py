import os
import re
import time
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum

# 需求：
# - google-genai >= 1.55.0
# - GOOGLE_API_KEY 環境變數
try:
    from google import genai
except ImportError:
    raise ImportError(
        "需要安裝 google-genai >= 1.55.0。"
        "安裝指令：pip install 'google-genai>=1.55.0'"
    )

from dotenv import load_dotenv

# 從套件目錄載入 .env 檔案
import pathlib
_env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(_env_path)

# 檢查是否使用 Vertex AI
# 如果環境變數 USE_VERTEX_AI 為 "true"，則啟用 Vertex AI 支援
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
if USE_VERTEX_AI:
    try:
        import vertexai
        from google.auth import default
    except ImportError:
        raise ImportError(
            "Vertex AI 支援需要安裝 vertexai 和 google-auth 套件。"
            "安裝指令：pip install 'google-cloud-aiplatform>=1.40.0' 'google-auth>=2.0.0'"
        )

# 深度研究代理識別碼 (Deep Research Agent identifier)
DEEP_RESEARCH_AGENT_ID = "deep-research-pro-preview-12-2025"

# 預設輪詢間隔 (秒)
DEFAULT_POLL_INTERVAL = 10

# 最大研究時間 (60 分鐘)
MAX_RESEARCH_TIME = 60 * 60


def extract_citations(text: str) -> List[str]:
    """
    從文字中提取 URL 和引用。

    Args:
        text: 要提取引用的文字。

    Returns:
        text 中發現的唯一 URL 列表 (已排序)。
    """
    # 匹配 http/https URL 的正規表達式模式
    url_pattern = r'https?://[^\s\)"\'\]]+'
    citations = list(set(re.findall(url_pattern, text)))
    return sorted(citations)


class ResearchStatus(Enum):
    """研究任務的狀態 (Status of a research task)。"""
    PENDING = "pending"       # 等待中
    IN_PROGRESS = "in_progress" # 進行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失敗


@dataclass
class ResearchResult:
    """已完成研究任務的結果 (Result of a completed research task)。"""
    id: str
    status: ResearchStatus
    report: str
    citations: List[str]
    elapsed_seconds: float
    error: Optional[str] = None


class DeepResearchAgent:
    """
    深度研究代理 (Deep Research Agent) 的高階介面。

    此類別提供以下方法：
    - 啟動背景研究任務
    - 輪詢完成狀態
    - 串流結果與進度更新
    - 針對已完成的研究進行後續提問

    範例：
        >>> agent = DeepResearchAgent()
        >>> result = agent.research("Analyze AI trends in 2025")
        >>> print(result.report)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化深度研究代理。

        在所有情況下都使用 Interactions API (genai.Client)。
        對於 Vertex AI，使用應用程式預設憑證 (Application Default Credentials)。
        對於 Google AI Studio，使用提供的 API 金鑰。

        Args:
            api_key: Google API 金鑰。如果未提供，則使用 GOOGLE_API_KEY 環境變數。
                     Vertex AI 不需要此參數 (使用應用程式預設憑證)。
        """
        self.use_vertex_ai = USE_VERTEX_AI
        self._client = None

        if self.use_vertex_ai:
            # 初始化 Vertex AI 上下文以獲取憑證
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VERTEX_AI_PROJECT_ID")
            region = os.getenv("VERTEX_AI_REGION", "us-central1")

            if not project_id:
                raise ValueError(
                    "使用 Vertex AI 需要設定 GOOGLE_CLOUD_PROJECT 或 VERTEX_AI_PROJECT_ID。"
                    "設定指令：export GOOGLE_CLOUD_PROJECT='your-project-id'"
                )

            # 初始化 Vertex AI 以設定憑證上下文
            vertexai.init(project=project_id, location=region)
            self.project_id = project_id
            self.region = region

            # 對於 Vertex AI 的 genai.Client，我們將使用應用程式預設憑證
            # genai client 會自動使用 vertexai.init() 設定的憑證
            print(f"✓ 已初始化 Vertex AI (project={project_id}, region={region})")
            print(f"✓ 使用 Interactions API 搭配應用程式預設憑證 (Application Default Credentials)")
        else:
            # 使用 API 金鑰初始化 Google AI SDK
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "需要 GOOGLE_API_KEY。"
                    "在此獲取您的金鑰：https://aistudio.google.com/apikey"
                )
            print(f"✓ 使用 Interactions API 搭配 API 金鑰驗證")

    @property
    def client(self):
        """
        延遲初始化 genai.Client (Interactions API)。

        Vertex AI 和 Google AI Studio 都使用 Interactions API。
        對於 Vertex AI，憑證透過應用程式預設憑證設定。
        對於 Google AI Studio，使用提供的 API 金鑰。
        """
        if self._client is None:
            if self.use_vertex_ai:
                # 對於 Vertex AI，genai.Client 使用應用程式預設憑證
                # 不需要 API 金鑰 - 憑證來自 vertexai.init() 和 gcloud auth
                self._client = genai.Client()
            else:
                # 對於 Google AI Studio，使用明確的 API 金鑰
                self._client = genai.Client(api_key=self.api_key)
        return self._client

    def research(
        self,
        query: str,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        on_status: Optional[Callable[[str, float], None]] = None,
        timeout: int = MAX_RESEARCH_TIME,
    ) -> ResearchResult:
        """
        執行完整的研究任務並返回結果。

        此方法啟動研究，輪詢直到完成，並返回最終報告。
        若需要串流進度，請改用 research_stream。

        Args:
            query: 研究查詢/主題。
            poll_interval: 狀態檢查之間的秒數 (預設：10)。
            on_status: 用於狀態更新的可選回呼函式 (status, elapsed_time)。
            timeout: 最長等待秒數 (預設：3600)。

        Returns:
            包含報告和元資料的 ResearchResult。

        範例：
            >>> result = agent.research(
            ...     "What are the latest developments in fusion energy?"
            ... )
            >>> print(result.report[:500])
        """
        start_time = time.time()

        # 使用 Interactions API 在背景啟動研究
        # Vertex AI 和 Google AI Studio 都使用相同的 Interactions API
        print("正在使用 Interactions API 啟動研究...")

        interaction = self.client.interactions.create(
            input=query,
            agent=DEEP_RESEARCH_AGENT_ID,
            background=True
        )

        interaction_id = interaction.id

        # 使用 Interactions API 輪詢完成狀態
        while True:
            elapsed = time.time() - start_time

            # 檢查是否超時
            if elapsed > timeout:
                return ResearchResult(
                    id=interaction_id,
                    status=ResearchStatus.FAILED,
                    report="",
                    citations=[],
                    elapsed_seconds=elapsed,
                    error=f"研究在 {timeout} 秒後超時"
                )

            # 透過 Interactions API 獲取當前狀態 (Vertex AI 和 Google AI 相同)
            interaction = self.client.interactions.get(interaction_id)
            status = interaction.status

            # 通知回呼函式
            if on_status:
                on_status(status, elapsed)

            # 如果狀態為完成，處理結果
            if status == "completed":
                report_text = interaction.outputs[-1].text if interaction.outputs else ""
                citations = extract_citations(report_text)

                return ResearchResult(
                    id=interaction_id,
                    status=ResearchStatus.COMPLETED,
                    report=report_text,
                    citations=citations,
                    elapsed_seconds=elapsed,
                )

            # 如果狀態為失敗，處理錯誤
            elif status == "failed":
                error_msg = getattr(interaction, 'error', '未知錯誤')
                return ResearchResult(
                    id=interaction_id,
                    status=ResearchStatus.FAILED,
                    report="",
                    citations=[],
                    elapsed_seconds=elapsed,
                    error=str(error_msg)
                )

            # 等待下一次輪詢
            time.sleep(poll_interval)

    def research_with_format(
        self,
        query: str,
        format_instructions: str,
        **kwargs
    ) -> ResearchResult:
        """
        使用特定輸出格式執行研究。

        Args:
            query: 研究主題。
            format_instructions: 輸出的格式要求。
            **kwargs: 傳遞給 research() 的額外參數。

        Returns:
            包含格式化報告的 ResearchResult。

        範例：
            >>> result = agent.research_with_format(
            ...     "EV battery market analysis",
            ...     format_instructions='''
            ...     Format as:
            ...     1. Executive Summary
            ...     2. Key Players (table)
            ...     3. Market Trends
            ...     '''
            ... )
        """
        formatted_query = f"{query}\n\n{format_instructions}"
        return self.research(formatted_query, **kwargs)

    def follow_up(
        self,
        interaction_id: str,
        question: str,
        model: str = "gemini-3-pro-preview"
    ) -> str:
        """
        針對已完成的研究提出後續問題。

        Args:
            interaction_id: 已完成研究互動的 ID。
            question: 您的後續問題。
            model: 用於後續問題的模型 (預設：gemini-3-pro-preview)。

        Returns:
            模型對後續問題的回應。

        範例：
            >>> result = agent.research("AI trends 2025")
            >>> follow_up = agent.follow_up(
            ...     result.id,
            ...     "Elaborate on the first trend you mentioned"
            ... )
        """
        interaction = self.client.interactions.create(
            model=model,
            input=question,
            previous_interaction_id=interaction_id
        )
        return interaction.outputs[-1].text if interaction.outputs else ""

    def _extract_citations(self, text: str) -> List[str]:
        """從研究文本中提取引用 URL。"""
        import re
        # URL 提取模式 - 捕獲 URL 並去除尾隨標點符號
        url_pattern = r'https?://[^\s\)\]<>"\']+'
        urls = re.findall(url_pattern, text)
        # 去除可能被捕獲的尾隨標點符號
        cleaned_urls = [url.rstrip(',.;:!?') for url in urls]
        return list(set(cleaned_urls))  # 去除重複項


# 方便簡單使用的輔助函式 (Convenience functions for simple usage)

def start_research(
    query: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    啟動背景研究任務。

    Args:
        query: 研究查詢。
        api_key: 可選的 API 金鑰。

    Returns:
        包含 'id' 和 'status' 的字典。
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=key)

    interaction = client.interactions.create(
        input=query,
        agent=DEEP_RESEARCH_AGENT_ID,
        background=True
    )

    return {
        "id": interaction.id,
        "status": interaction.status,
    }


def poll_research(
    interaction_id: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    檢查研究任務的狀態。

    Args:
        interaction_id: 來自 start_research 的互動 ID。
        api_key: 可選的 API 金鑰。

    Returns:
        包含狀態和內容 (如果已完成) 的字典。
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=key)

    interaction = client.interactions.get(interaction_id)

    result = {
        "id": interaction.id,
        "status": interaction.status,
    }

    if interaction.status == "completed":
        result["report"] = interaction.outputs[-1].text if interaction.outputs else ""
    elif interaction.status == "failed":
        result["error"] = getattr(interaction, 'error', '未知錯誤')

    return result


def run_research(
    query: str,
    api_key: Optional[str] = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    verbose: bool = False
) -> str:
    """
    執行完整的研究任務並返回報告。

    這是使用 Deep Research 最簡單的方式 - 它為您處理所有背景執行和輪詢。

    Args:
        query: 研究查詢。
        api_key: 可選的 API 金鑰。
        poll_interval: 輪詢之間的秒數。
        verbose: 是否列印狀態更新。

    Returns:
        研究報告文字。

    範例：
        >>> report = run_research("Latest developments in quantum computing")
        >>> print(report)
    """
    def status_callback(status: str, elapsed: float):
        if verbose:
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            print(f"[{mins:02d}:{secs:02d}] Status: {status}")

    agent = DeepResearchAgent(api_key=api_key)
    result = agent.research(query, poll_interval=poll_interval, on_status=status_callback)

    if result.status == ResearchStatus.FAILED:
        raise RuntimeError(f"研究失敗: {result.error}")

    return result.report
