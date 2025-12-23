"""
深度研究代理 (Deep Research Agent) 測試

這些測試驗證配置和結構，不進行實際的 API 調用。
重點說明：
1. 驗證模組導入是否正確
2. 驗證代理配置 (API Key 處理)
3. 驗證資料結構 (Result, Progress)
4. 驗證核心方法 (Start, Poll) - 使用 Mock
5. 驗證工具函數 (引用提取)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import is_dataclass


class TestImports:
    """測試模組導入。"""

    def test_import_main_module(self):
        """測試導入主模組。"""
        from research_agent import (
            DeepResearchAgent,
            start_research,
            poll_research,
            run_research,
            DEEP_RESEARCH_AGENT_ID,
        )
        assert DeepResearchAgent is not None
        assert callable(start_research)
        assert callable(poll_research)
        assert callable(run_research)
        assert DEEP_RESEARCH_AGENT_ID == "deep-research-pro-preview-12-2025"

    def test_import_streaming(self):
        """測試導入串流工具。"""
        from research_agent import (
            stream_research,
            ResearchProgress,
        )
        assert callable(stream_research)
        assert is_dataclass(ResearchProgress)


class TestDeepResearchAgentConfig:
    """測試 DeepResearchAgent 配置。"""

    def test_agent_requires_api_key(self):
        """測試在沒有 API 密鑰的情況下代理是否會引發錯誤。"""
        from research_agent import DeepResearchAgent

        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                DeepResearchAgent()
            assert "GOOGLE_API_KEY" in str(exc_info.value)

    def test_agent_accepts_api_key(self):
        """測試代理是否接受顯式 API 密鑰。"""
        from research_agent import DeepResearchAgent

        agent = DeepResearchAgent(api_key="test-key")
        assert agent.api_key == "test-key"

    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'env-key'})
    def test_agent_uses_env_key(self):
        """測試代理是否使用環境變數密鑰。"""
        from research_agent import DeepResearchAgent

        agent = DeepResearchAgent()
        assert agent.api_key == "env-key"

    def test_client_lazy_initialization(self):
        """測試客戶端是否直到被訪問時才創建 (延遲初始化)。"""
        from research_agent import DeepResearchAgent

        agent = DeepResearchAgent(api_key="test-key")
        assert agent._client is None


class TestResearchResult:
    """測試 ResearchResult 數據類。"""

    def test_research_result_structure(self):
        """測試 ResearchResult 是否具有預期的欄位。"""
        from research_agent.agent import ResearchResult, ResearchStatus

        result = ResearchResult(
            id="test-id",
            status=ResearchStatus.COMPLETED,
            report="Test report",
            citations=["https://example.com"],
            elapsed_seconds=10.5,
        )

        assert result.id == "test-id"
        assert result.status == ResearchStatus.COMPLETED
        assert result.report == "Test report"
        assert len(result.citations) == 1
        assert result.elapsed_seconds == 10.5
        assert result.error is None

    def test_research_result_with_error(self):
        """測試帶有錯誤的 ResearchResult。"""
        from research_agent.agent import ResearchResult, ResearchStatus

        result = ResearchResult(
            id="test-id",
            status=ResearchStatus.FAILED,
            report="",
            citations=[],
            elapsed_seconds=5.0,
            error="Something went wrong",
        )

        assert result.status == ResearchStatus.FAILED
        assert result.error == "Something went wrong"


class TestResearchProgress:
    """測試 ResearchProgress 數據類。"""

    def test_progress_structure(self):
        """測試 ResearchProgress 是否具有預期的欄位。"""
        from research_agent.streaming import ResearchProgress, ProgressType

        progress = ResearchProgress(
            type=ProgressType.THOUGHT,
            content="Analyzing data...",
            interaction_id="int-123",
        )

        assert progress.type == ProgressType.THOUGHT
        assert progress.content == "Analyzing data..."
        assert progress.interaction_id == "int-123"

    def test_progress_types(self):
        """測試所有 ProgressType 值是否存在。"""
        from research_agent.streaming import ProgressType

        assert ProgressType.START.value == "start"
        assert ProgressType.THOUGHT.value == "thought"
        assert ProgressType.CONTENT.value == "content"
        assert ProgressType.COMPLETE.value == "complete"
        assert ProgressType.ERROR.value == "error"


class TestResearchMethods:
    """使用模擬客戶端測試研究方法。"""

    @patch('research_agent.agent.genai.Client')
    def test_start_research(self, mock_client_class):
        """測試 start_research 函數。"""
        from research_agent import start_research

        # Setup mock
        mock_client = MagicMock()
        mock_interaction = MagicMock()
        mock_interaction.id = "research-id-123"
        mock_interaction.status = "in_progress"
        mock_client.interactions.create.return_value = mock_interaction
        mock_client_class.return_value = mock_client

        # Test
        result = start_research("Test query", api_key="test-key")

        assert result["id"] == "research-id-123"
        assert result["status"] == "in_progress"

        # Verify correct parameters
        call_kwargs = mock_client.interactions.create.call_args[1]
        assert call_kwargs["agent"] == "deep-research-pro-preview-12-2025"
        assert call_kwargs["background"] == True

    @patch('research_agent.agent.genai.Client')
    def test_poll_research_in_progress(self, mock_client_class):
        """測試進行中的 poll_research。"""
        from research_agent import poll_research

        # Setup mock
        mock_client = MagicMock()
        mock_interaction = MagicMock()
        mock_interaction.id = "research-id-123"
        mock_interaction.status = "in_progress"
        mock_client.interactions.get.return_value = mock_interaction
        mock_client_class.return_value = mock_client

        # Test
        result = poll_research("research-id-123", api_key="test-key")

        assert result["id"] == "research-id-123"
        assert result["status"] == "in_progress"
        assert "report" not in result

    @patch('research_agent.agent.genai.Client')
    def test_poll_research_completed(self, mock_client_class):
        """測試完成後的 poll_research。"""
        from research_agent import poll_research

        # Setup mock
        mock_client = MagicMock()
        mock_output = MagicMock()
        mock_output.text = "Research findings..."
        mock_interaction = MagicMock()
        mock_interaction.id = "research-id-123"
        mock_interaction.status = "completed"
        mock_interaction.outputs = [mock_output]
        mock_client.interactions.get.return_value = mock_interaction
        mock_client_class.return_value = mock_client

        # Test
        result = poll_research("research-id-123", api_key="test-key")

        assert result["status"] == "completed"
        assert result["report"] == "Research findings..."


class TestCitationExtraction:
    """測試從研究文本中提取引用。"""

    def test_extract_citations(self):
        """測試從文本中提取 URL。"""
        from research_agent import DeepResearchAgent

        agent = DeepResearchAgent(api_key="test-key")

        text = """
        According to https://example.com/article1 and
        https://research.org/paper, the findings suggest...
        See also: http://legacy-site.com/doc
        """

        citations = agent._extract_citations(text)

        assert len(citations) == 3
        assert "https://example.com/article1" in citations
        assert "https://research.org/paper" in citations
        assert "http://legacy-site.com/doc" in citations

    def test_extract_no_citations(self):
        """測試不包含 URL 的文本。"""
        from research_agent import DeepResearchAgent

        agent = DeepResearchAgent(api_key="test-key")

        text = "This text has no citations."
        citations = agent._extract_citations(text)

        assert len(citations) == 0

    def test_extract_deduplicates_citations(self):
        """測試重複的 URL 是否被移除。"""
        from research_agent import DeepResearchAgent

        agent = DeepResearchAgent(api_key="test-key")

        text = """
        See https://example.com for more.
        As mentioned in https://example.com, this is important.
        """

        citations = agent._extract_citations(text)

        # Should only have one entry despite duplicate URLs
        assert citations.count("https://example.com") == 1


class TestStreamReconnector:
    """測試串流重新連接功能。"""

    def test_reconnector_initialization(self):
        """測試 ResearchStreamReconnector 初始化。"""
        from research_agent.streaming import ResearchStreamReconnector

        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            reconnector = ResearchStreamReconnector()

            assert reconnector.api_key == "test-key"
            assert reconnector.interaction_id is None
            assert reconnector.last_event_id is None
            assert reconnector.max_retries == 3

    def test_reconnector_with_explicit_key(self):
        """測試帶有顯式 API 密鑰的重新連接器。"""
        from research_agent.streaming import ResearchStreamReconnector

        reconnector = ResearchStreamReconnector(api_key="explicit-key")
        assert reconnector.api_key == "explicit-key"


class TestConstants:
    """測試模組常數。"""

    def test_agent_id(self):
        """測試深度研究代理 ID。"""
        from research_agent import DEEP_RESEARCH_AGENT_ID

        assert DEEP_RESEARCH_AGENT_ID == "deep-research-pro-preview-12-2025"

    def test_default_poll_interval(self):
        """測試預設輪詢間隔。"""
        from research_agent.agent import DEFAULT_POLL_INTERVAL

        assert DEFAULT_POLL_INTERVAL == 10

    def test_max_research_time(self):
        """測試最大研究時間。"""
        from research_agent.agent import MAX_RESEARCH_TIME

        assert MAX_RESEARCH_TIME == 3600  # 60 minutes
