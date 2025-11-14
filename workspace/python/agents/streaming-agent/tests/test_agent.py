"""
教學 14：串流代理程式的測試套件

重點：測試代理程式的設定、串流功能以及工具函式。
"""

import pytest
import asyncio
from streaming_agent.agent import (
    create_streaming_agent,
    root_agent,
    stream_agent_response,
    get_complete_response,
    format_streaming_info,
    analyze_streaming_performance
)


class TestAgentConfiguration:
    """測試代理程式的建立與設定。"""

    def test_create_streaming_agent(self):
        """測試：串流代理程式是否以正確的設定建立。"""
        agent = create_streaming_agent()

        assert agent is not None
        assert agent.name == 'streaming_assistant'
        assert 'streaming' in agent.description.lower()
        assert agent.model == 'gemini-2.0-flash'

    def test_root_agent_exists(self):
        """測試：root_agent 是否已正確實例化。"""
        assert root_agent is not None
        assert hasattr(root_agent, 'name')
        assert hasattr(root_agent, 'model')


class TestStreamingFunctionality:
    """測試串流回應功能。"""

    @pytest.mark.asyncio
    async def test_stream_agent_response_basic(self):
        """測試：基本串流回應功能。"""
        query = "Hello world"
        chunks = []

        async for chunk in stream_agent_response(query):
            chunks.append(chunk)

        assert len(chunks) > 0
        response_text = ''.join(chunks)
        # 檢查：回應應包含一些文字（真實的 AI 回應或備用方案）
        assert len(response_text.strip()) > 0

    @pytest.mark.asyncio
    async def test_stream_agent_response_empty_query(self):
        """測試：使用空查詢進行串流。"""
        query = ""
        chunks = []

        async for chunk in stream_agent_response(query):
            chunks.append(chunk)

        assert len(chunks) > 0
        response_text = ''.join(chunks)
        # 檢查：應能優雅地處理空查詢
        assert len(response_text.strip()) > 0

    @pytest.mark.asyncio
    async def test_get_complete_response(self):
        """測試：完整回應功能。"""
        query = "Test query"
        response = await get_complete_response(query)

        assert isinstance(response, str)
        # 檢查：回應應包含一些文字（真實的 AI 回應或備用方案）
        assert len(response.strip()) > 0


class TestToolFunctions:
    """測試工具函式。"""

    def test_format_streaming_info(self):
        """測試：串流資訊工具。"""
        result = format_streaming_info()

        assert result['status'] == 'success'
        assert 'streaming_modes' in result['data']
        assert 'SSE' in result['data']['streaming_modes']
        assert 'benefits' in result['data']
        assert 'use_cases' in result['data']

    def test_analyze_streaming_performance_default(self):
        """測試：使用預設參數的效能分析。"""
        result = analyze_streaming_performance()

        assert result['status'] == 'success'
        assert 'estimated_chunks' in result['data']
        assert 'estimated_total_time_seconds' in result['data']
        assert result['data']['memory_efficient'] is True

    def test_analyze_streaming_performance_custom_length(self):
        """測試：使用自訂查詢長度的效能分析。"""
        query_length = 500
        result = analyze_streaming_performance(query_length)

        assert result['status'] == 'success'
        assert result['data']['estimated_chunks'] >= 1
        assert result['data']['estimated_total_time_seconds'] > 0

    def test_analyze_streaming_performance_zero_length(self):
        """測試：使用零查詢長度的效能分析。"""
        result = analyze_streaming_performance(0)

        assert result['status'] == 'success'
        assert result['data']['estimated_chunks'] == 1  # 檢查：最小 1 個區塊


class TestIntegration:
    """代理程式功能的整合測試。"""

    def test_agent_has_tools(self):
        """測試：代理程式是否擁有預期的工具。"""
        assert hasattr(root_agent, 'tools')
        assert len(root_agent.tools) == 2

        tool_names = [tool.__name__ for tool in root_agent.tools]
        assert 'format_streaming_info' in tool_names
        assert 'analyze_streaming_performance' in tool_names

    def test_agent_instruction_content(self):
        """測試：代理程式是否具有適當的指令。"""
        # 檢查：指令是否包含關鍵片語
        instruction = root_agent.instruction
        assert 'helpful' in instruction.lower()
        assert 'streaming' in instruction.lower()
        assert 'conversational' in instruction.lower()


if __name__ == '__main__':
    pytest.main([__file__])
