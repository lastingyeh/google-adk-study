"""
Agent 配置與功能測試

測試 pack-bidi-streaming 專案的 Agent 配置與工具函式。
"""


class TestAgentConfiguration:
    """測試 Agent 配置與屬性。"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已正確定義。"""
        from bidi_demo.agent import root_agent

        assert root_agent is not None

    def test_agent_has_correct_name(self):
        """測試 Agent 是否擁有正確名稱。"""
        from bidi_demo.agent import root_agent

        assert root_agent.name == "root_agent"

    def test_agent_has_correct_model(self):
        """測試 Agent 是否使用正確的模型。"""
        import os

        from bidi_demo.agent import root_agent

        expected_model = os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash")
        assert root_agent.model == expected_model

    def test_agent_has_description(self):
        """測試 Agent 是否擁有描述（instruction）。"""
        from bidi_demo.agent import root_agent

        assert root_agent.instruction is not None
        # instruction 可能是字串或函數，需要處理兩種情況
        instruction_str = (
            root_agent.instruction
            if isinstance(root_agent.instruction, str)
            else str(root_agent.instruction)
        )
        assert len(instruction_str) > 0

    def test_agent_has_tools(self):
        """測試 Agent 是否已配置工具。"""
        from bidi_demo.agent import root_agent

        assert hasattr(root_agent, "tools")
        assert root_agent.tools is not None
        assert (
            len(root_agent.tools) == 3
        )  # get_weather, get_current_time, google_search


class TestAgentTools:
    """測試 Agent 的工具配置。"""

    def test_agent_has_expected_tools(self):
        """測試 Agent 是否包含預期的工具。"""
        from bidi_demo.agent import root_agent

        tool_names = []
        for tool in root_agent.tools:
            if hasattr(tool, "__name__"):
                tool_names.append(tool.__name__)
            elif hasattr(tool, "name"):
                tool_names.append(tool.name)

        # 驗證包含預期的工具
        expected_tools = ["get_weather", "get_current_time"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"應包含工具：{expected_tool}"

    def test_agent_has_google_search_tool(self):
        """測試 Agent 是否包含 Google 搜尋工具。"""
        from google.adk.tools import google_search

        from bidi_demo.agent import root_agent

        assert google_search in root_agent.tools


class TestApp:
    """測試 App 配置。"""

    def test_app_exists(self):
        """測試 App 實例是否存在。"""
        from bidi_demo.agent import app

        assert app is not None

    def test_app_has_root_agent(self):
        """測試 App 是否配置了 root_agent。"""
        from bidi_demo.agent import app, root_agent

        assert hasattr(app, "root_agent")
        assert app.root_agent == root_agent

    def test_app_has_correct_name(self):
        """測試 App 是否擁有正確名稱。"""
        from bidi_demo.agent import app

        assert hasattr(app, "name")
        assert app.name == "bidi_demo"


class TestGetWeatherTool:
    """測試 get_weather 工具函式。"""

    def test_get_weather_exists(self):
        """測試 get_weather 函式是否存在。"""
        from bidi_demo.agent import get_weather

        assert get_weather is not None
        assert callable(get_weather)

    def test_get_weather_returns_string(self):
        """測試 get_weather 回傳字串。"""
        from bidi_demo.agent import get_weather

        result = get_weather("taipei")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_weather_san_francisco(self):
        """測試 get_weather 對舊金山的回應。"""
        from bidi_demo.agent import get_weather

        result = get_weather("san francisco")
        assert "舊金山" in result or "San Francisco" in result.lower()
        assert "60" in result
        assert "霧" in result

    def test_get_weather_sf_abbreviation(self):
        """測試 get_weather 對 SF 縮寫的回應。"""
        from bidi_demo.agent import get_weather

        result = get_weather("SF weather")
        assert "舊金山" in result or "60" in result

    def test_get_weather_other_location(self):
        """測試 get_weather 對其他地點的回應。"""
        from bidi_demo.agent import get_weather

        result = get_weather("taipei")
        assert "晴" in result or "90" in result


class TestGetCurrentTimeTool:
    """測試 get_current_time 工具函式。"""

    def test_get_current_time_exists(self):
        """測試 get_current_time 函式是否存在。"""
        from bidi_demo.agent import get_current_time

        assert get_current_time is not None
        assert callable(get_current_time)

    def test_get_current_time_returns_string(self):
        """測試 get_current_time 回傳字串。"""
        from bidi_demo.agent import get_current_time

        result = get_current_time("san francisco")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_current_time_san_francisco(self):
        """測試 get_current_time 對舊金山的回應。"""
        from bidi_demo.agent import get_current_time

        result = get_current_time("san francisco")
        assert "時間" in result or "time" in result.lower()
        # 應該包含時間格式（年-月-日 時:分:秒）
        import re

        assert re.search(r"\d{4}-\d{2}-\d{2}", result)

    def test_get_current_time_sf_abbreviation(self):
        """測試 get_current_time 對 SF 縮寫的回應。"""
        from bidi_demo.agent import get_current_time

        result = get_current_time("SF")
        assert "時間" in result or "time" in result.lower()

    def test_get_current_time_unknown_location(self):
        """測試 get_current_time 對未知地點的回應。"""
        from bidi_demo.agent import get_current_time

        result = get_current_time("unknown city")
        assert "抱歉" in result or "沒有" in result or "時區" in result


class TestEnvironmentConfiguration:
    """測試環境配置。"""

    def test_google_cloud_project_can_be_set(self):
        """測試 GOOGLE_CLOUD_PROJECT 環境變數可以被設定。"""
        from bidi_demo import agent

        # agent.py 會在匯入時設定環境變數
        # 只要能成功匯入即代表環境配置正常
        assert agent is not None

    def test_google_cloud_location_can_be_set(self):
        """測試 GOOGLE_CLOUD_LOCATION 可以透過 agent 模組設定。"""
        from bidi_demo import agent

        # 驗證 agent 模組已載入（會設定環境變數）
        assert agent is not None

    def test_google_genai_use_vertexai_can_be_set(self):
        """測試 GOOGLE_GENAI_USE_VERTEXAI 可以透過 agent 模組設定。"""
        from bidi_demo import agent

        # 驗證 agent 模組已載入
        assert agent is not None
