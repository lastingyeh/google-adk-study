"""
Interactions API 基礎 Agent 的測試

這些測試驗證：
- 模組匯入
- 工具定義
- Agent 設定（不進行 API 呼叫）
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestImports:
    """測試所有模組匯入是否正常運作。"""

    def test_import_main_module(self):
        """測試匯入主模組。"""
        from interactions_basic_agent import (
            create_basic_interaction,
            create_stateful_conversation,
            create_streaming_interaction,
            create_function_calling_interaction,
        )
        assert callable(create_basic_interaction)
        assert callable(create_stateful_conversation)
        assert callable(create_streaming_interaction)
        assert callable(create_function_calling_interaction)

    def test_import_tools(self):
        """測試匯入工具模組。"""
        from interactions_basic_agent import (
            get_weather_tool,
            calculate_tool,
            AVAILABLE_TOOLS,
        )
        assert callable(get_weather_tool)
        assert callable(calculate_tool)
        assert isinstance(AVAILABLE_TOOLS, list)

    def test_import_constants(self):
        """測試匯入常數。"""
        from interactions_basic_agent import SUPPORTED_MODELS
        assert isinstance(SUPPORTED_MODELS, list)
        assert "gemini-2.5-flash" in SUPPORTED_MODELS


class TestToolDefinitions:
    """測試工具 schema 定義。"""

    def test_weather_tool_schema(self):
        """測試天氣工具具有正確的 schema。"""
        from interactions_basic_agent import get_weather_tool

        tool = get_weather_tool()
        assert tool["type"] == "function"
        assert tool["name"] == "get_weather"
        assert "description" in tool
        assert "parameters" in tool
        assert "location" in tool["parameters"]["properties"]

    def test_calculate_tool_schema(self):
        """測試計算器工具具有正確的 schema。"""
        from interactions_basic_agent import calculate_tool

        tool = calculate_tool()
        assert tool["type"] == "function"
        assert tool["name"] == "calculate"
        assert "expression" in tool["parameters"]["properties"]

    def test_available_tools_not_empty(self):
        """測試 AVAILABLE_TOOLS 包含工具。"""
        from interactions_basic_agent import AVAILABLE_TOOLS

        assert len(AVAILABLE_TOOLS) > 0
        for tool in AVAILABLE_TOOLS:
            assert "type" in tool
            assert "name" in tool
            assert "parameters" in tool


class TestToolExecution:
    """測試工具執行 mock 實作。"""

    def test_execute_weather_tool(self):
        """測試天氣工具執行。"""
        from interactions_basic_agent.tools import execute_tool

        result = execute_tool("get_weather", {"location": "Paris"})
        assert "Paris" in result
        assert "weather" in result.lower()

    def test_execute_calculate_tool(self):
        """測試計算器工具執行。"""
        from interactions_basic_agent.tools import execute_tool

        result = execute_tool("calculate", {"expression": "2 + 2"})
        assert "4" in result

    def test_execute_calculate_percentage(self):
        """測試帶百分比的計算器。"""
        from interactions_basic_agent.tools import execute_tool

        result = execute_tool("calculate", {"expression": "10% of 200"})
        assert "20" in result

    def test_execute_unknown_tool(self):
        """測試未知工具返回錯誤訊息。"""
        from interactions_basic_agent.tools import execute_tool

        result = execute_tool("unknown_tool", {})
        assert "Unknown tool" in result


class TestAgentConfiguration:
    """測試 Agent 設定而不進行 API 呼叫。"""

    def test_supported_models(self):
        """測試支援的模型列表。"""
        from interactions_basic_agent.agent import SUPPORTED_MODELS, DEFAULT_MODEL

        assert len(SUPPORTED_MODELS) >= 4
        assert DEFAULT_MODEL in SUPPORTED_MODELS
        assert "gemini-2.5-flash" in SUPPORTED_MODELS
        assert "gemini-3-pro-preview" in SUPPORTED_MODELS

    def test_get_client_without_key_raises(self):
        """測試在沒有 API 金鑰的情況下 get_client 會引發異常。"""
        from interactions_basic_agent.agent import get_client

        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_client()
            assert "GOOGLE_API_KEY" in str(exc_info.value)

    @patch('interactions_basic_agent.agent.genai.Client')
    def test_get_client_with_key(self, mock_client):
        """測試使用 API 金鑰取得 client。"""
        from interactions_basic_agent.agent import get_client

        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            client = get_client()
            mock_client.assert_called_once_with(api_key='test-key')

    @patch('interactions_basic_agent.agent.genai.Client')
    def test_get_client_with_explicit_key(self, mock_client):
        """測試使用明確的 API 金鑰參數取得 client。"""
        from interactions_basic_agent.agent import get_client

        client = get_client(api_key='explicit-key')
        mock_client.assert_called_once_with(api_key='explicit-key')


class TestInteractionFunctions:
    """測試使用 mock client 的互動功能。"""

    @patch('interactions_basic_agent.agent.get_client')
    def test_create_basic_interaction(self, mock_get_client):
        """測試建立基本互動。"""
        from interactions_basic_agent import create_basic_interaction

        # 設定 mock
        mock_client = MagicMock()
        mock_interaction = MagicMock()
        mock_interaction.id = "test-interaction-id"
        mock_interaction.status = "completed"
        mock_interaction.outputs = [MagicMock(text="Test response")]
        mock_client.interactions.create.return_value = mock_interaction
        mock_get_client.return_value = mock_client

        # 測試
        result = create_basic_interaction("Test prompt")

        assert result["id"] == "test-interaction-id"
        assert result["text"] == "Test response"
        assert result["status"] == "completed"
        mock_client.interactions.create.assert_called_once()

    @patch('interactions_basic_agent.agent.get_client')
    def test_create_stateful_conversation(self, mock_get_client):
        """測試建立有狀態的對話。"""
        from interactions_basic_agent import create_stateful_conversation

        # 設定 mock
        mock_client = MagicMock()

        # 建立 mock 互動
        mock_int1 = MagicMock()
        mock_int1.id = "id-1"
        mock_int1.outputs = [MagicMock(text="Response 1")]

        mock_int2 = MagicMock()
        mock_int2.id = "id-2"
        mock_int2.outputs = [MagicMock(text="Response 2")]

        mock_client.interactions.create.side_effect = [mock_int1, mock_int2]
        mock_get_client.return_value = mock_client

        # 測試
        results = create_stateful_conversation(["Message 1", "Message 2"])

        assert len(results) == 2
        assert results[0]["id"] == "id-1"
        assert results[1]["id"] == "id-2"
        assert results[0]["previous_id"] is None
        assert results[1]["previous_id"] == "id-1"

    @patch('interactions_basic_agent.agent.get_client')
    def test_create_function_calling_interaction(self, mock_get_client):
        """測試函式呼叫互動。"""
        from interactions_basic_agent import create_function_calling_interaction

        # 設定 mock - 工具呼叫回應
        mock_client = MagicMock()
        mock_output = MagicMock()
        mock_output.type = "function_call"
        mock_output.name = "get_weather"
        mock_output.arguments = {"location": "Paris"}
        mock_output.id = "call-id-1"

        mock_interaction = MagicMock()
        mock_interaction.id = "int-id"
        mock_interaction.outputs = [mock_output]
        mock_client.interactions.create.return_value = mock_interaction
        mock_get_client.return_value = mock_client

        # 測試不使用執行器 (executor)
        tools = [{"type": "function", "name": "get_weather"}]
        result = create_function_calling_interaction("Weather?", tools=tools)

        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["name"] == "get_weather"


class TestBuiltInTools:
    """測試內建工具設定。"""

    @patch('interactions_basic_agent.agent.get_client')
    def test_google_search_tool(self, mock_get_client):
        """測試 Google 搜尋內建工具。"""
        from interactions_basic_agent.agent import create_interaction_with_builtin_tools

        # 設定 mock
        mock_client = MagicMock()
        mock_output = MagicMock()
        mock_output.type = "text"
        mock_output.text = "Search result"

        mock_interaction = MagicMock()
        mock_interaction.id = "search-int-id"
        mock_interaction.status = "completed"
        mock_interaction.outputs = [mock_output]
        mock_client.interactions.create.return_value = mock_interaction
        mock_get_client.return_value = mock_client

        # 測試
        result = create_interaction_with_builtin_tools(
            "Who won the Super Bowl?",
            tool_type="google_search"
        )

        assert result["id"] == "search-int-id"
        assert result["text"] == "Search result"

        # 驗證工具是否正確傳遞
        call_kwargs = mock_client.interactions.create.call_args[1]
        assert {"type": "google_search"} in call_kwargs["tools"]

    def test_invalid_builtin_tool_raises(self):
        """測試無效的內建工具會引發錯誤。"""
        from interactions_basic_agent.agent import create_interaction_with_builtin_tools

        with patch('interactions_basic_agent.agent.get_client'):
            with pytest.raises(ValueError) as exc_info:
                create_interaction_with_builtin_tools(
                    "Test",
                    tool_type="invalid_tool"
                )
            assert "tool_type must be one of" in str(exc_info.value)
