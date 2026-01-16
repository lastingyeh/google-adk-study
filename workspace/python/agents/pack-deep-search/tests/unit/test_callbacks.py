"""
回調函式測試
"""

from unittest.mock import MagicMock, Mock
import pytest


class TestCollectResearchSourcesCallback:
    """測試 collect_research_sources_callback 函式。"""

    def test_callback_exists(self):
        """測試回調函式存在。"""
        from app.agent import collect_research_sources_callback

        assert callable(collect_research_sources_callback)

    def test_callback_with_empty_state(self):
        """測試回調處理空狀態。"""
        from app.agent import collect_research_sources_callback

        mock_context = Mock()
        mock_context.state = {}
        mock_context._invocation_context = Mock()
        mock_context._invocation_context.session = Mock()
        mock_context._invocation_context.session.events = []

        # 不應拋出異常
        collect_research_sources_callback(mock_context)

        assert "url_to_short_id" in mock_context.state
        assert "sources" in mock_context.state

    def test_callback_initializes_state(self):
        """測試回調初始化狀態。"""
        from app.agent import collect_research_sources_callback

        mock_context = Mock()
        mock_context.state = {}
        mock_context._invocation_context = Mock()
        mock_context._invocation_context.session = Mock()
        mock_context._invocation_context.session.events = []

        collect_research_sources_callback(mock_context)

        assert isinstance(mock_context.state.get("url_to_short_id"), dict)
        assert isinstance(mock_context.state.get("sources"), dict)


class TestCitationReplacementCallback:
    """測試 citation_replacement_callback 函式。"""

    def test_callback_exists(self):
        """測試回調函式存在。"""
        from app.agent import citation_replacement_callback

        assert callable(citation_replacement_callback)

    def test_callback_with_empty_report(self):
        """測試回調處理空報告。"""
        from app.agent import citation_replacement_callback

        mock_context = Mock()
        mock_context.state = {"final_cited_report": "", "sources": {}}

        result = citation_replacement_callback(mock_context)

        assert result is not None
        assert "final_report_with_citations" in mock_context.state

    def test_callback_replaces_citation_tags(self):
        """測試回調替換引用標籤。"""
        from app.agent import citation_replacement_callback

        mock_context = Mock()
        mock_context.state = {
            "final_cited_report": 'Test report <cite source="src-1"/>',
            "sources": {
                "src-1": {
                    "title": "Example Source",
                    "url": "https://example.com",
                    "domain": "example.com",
                }
            },
        }

        result = citation_replacement_callback(mock_context)

        processed = mock_context.state["final_report_with_citations"]
        assert "[Example Source]" in processed
        assert "(https://example.com)" in processed
        assert "<cite" not in processed

    def test_callback_handles_invalid_citation(self):
        """測試回調處理無效引用。"""
        from app.agent import citation_replacement_callback

        mock_context = Mock()
        mock_context.state = {
            "final_cited_report": 'Test report <cite source="src-999"/>',
            "sources": {},
        }

        result = citation_replacement_callback(mock_context)

        # 無效引用應被移除
        processed = mock_context.state["final_report_with_citations"]
        assert "<cite" not in processed

    def test_callback_fixes_punctuation_spacing(self):
        """測試回調修正標點符號間距。"""
        from app.agent import citation_replacement_callback

        mock_context = Mock()
        mock_context.state = {
            "final_cited_report": "Test report  , with spaces .",
            "sources": {},
        }

        result = citation_replacement_callback(mock_context)

        processed = mock_context.state["final_report_with_citations"]
        assert "  ," not in processed
        assert ", " in processed or "," in processed

    def test_callback_returns_content_type(self):
        """測試回調返回正確的 Content 類型。"""
        from app.agent import citation_replacement_callback
        from google.genai import types as genai_types

        mock_context = Mock()
        mock_context.state = {"final_cited_report": "Test", "sources": {}}

        result = citation_replacement_callback(mock_context)

        assert isinstance(result, genai_types.Content)

    def test_callback_with_multiple_citations(self):
        """測試回調處理多個引用。"""
        from app.agent import citation_replacement_callback

        mock_context = Mock()
        mock_context.state = {
            "final_cited_report": 'Source 1 <cite source="src-1"/> and source 2 <cite source="src-2"/>',
            "sources": {
                "src-1": {"title": "Source 1", "url": "https://example1.com"},
                "src-2": {"title": "Source 2", "url": "https://example2.com"},
            },
        }

        result = citation_replacement_callback(mock_context)

        processed = mock_context.state["final_report_with_citations"]
        assert "[Source 1]" in processed
        assert "[Source 2]" in processed
        assert "(https://example1.com)" in processed
        assert "(https://example2.com)" in processed


class TestCallbackIntegration:
    """測試回調函式整合。"""

    def test_callbacks_are_assigned_to_agents(self):
        """測試回調已分配給 Agent。"""
        from app.agent import (
            enhanced_search_executor,
            report_composer,
            section_researcher,
        )

        assert section_researcher.after_agent_callback is not None
        assert enhanced_search_executor.after_agent_callback is not None
        assert report_composer.after_agent_callback is not None

    def test_correct_callbacks_assigned(self):
        """測試正確的回調已分配。"""
        from app.agent import (
            citation_replacement_callback,
            collect_research_sources_callback,
            report_composer,
            section_researcher,
        )

        assert section_researcher.after_agent_callback == collect_research_sources_callback
        assert report_composer.after_agent_callback == citation_replacement_callback
