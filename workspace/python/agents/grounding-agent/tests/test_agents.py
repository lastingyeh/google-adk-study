"""
Grounding Agent 的完整 Pytest 測試套件。

使用以下指令執行：pytest tests/test_agent.py -v
"""

import pytest
import os
from unittest.mock import Mock
from grounding_agent.agent import (
    root_agent,
    basic_grounding_agent,
    advanced_grounding_agent,
    research_assistant,
    analyze_search_results,
    save_research_findings,
)


class TestToolFunctions:
    """獨立測試自訂工具"""

    def setup_method(self):
        """每個測試前的設定"""
        # 建立一個模擬的 ToolContext 以進行測試
        self.tool_context = Mock()

    def test_analyze_search_results_success(self):
        """測試成功的搜尋結果分析"""
        query = "quantum computing"
        content = "Quantum computing uses quantum mechanics. Recent breakthroughs include error correction. IBM announced a 1000-qubit processor."

        result = analyze_search_results(query, content, self.tool_context)

        assert result["status"] == "success"
        assert "quantum computing" in result["report"].lower()
        assert result["analysis"]["query"] == query
        assert result["analysis"]["word_count"] > 0
        assert len(result["analysis"]["key_insights"]) > 0
        assert result["analysis"]["content_quality"] in ["good", "limited"]

    def test_analyze_search_results_empty_content(self):
        """測試使用空內容進行分析"""
        result = analyze_search_results("test query", "", self.tool_context)

        assert result["status"] == "success"
        assert result["analysis"]["word_count"] == 0
        assert result["analysis"]["content_quality"] == "limited"

    def test_analyze_search_results_error_handling(self):
        """測試分析中的錯誤處理"""
        # 這不應該引發例外
        result = analyze_search_results("test", "valid content", self.tool_context)
        assert result["status"] == "success"

    def test_save_research_findings_success(self):
        """測試成功儲存研究發現"""
        topic = "AI Developments"
        findings = "Recent breakthroughs in AI include large language models."

        result = save_research_findings(topic, findings, self.tool_context)

        assert result["status"] == "success"
        assert "saved as" in result["report"]
        assert "research_ai_developments.md" in result["filename"]
        assert result["version"] == "1.0"

    def test_save_research_findings_special_chars(self):
        """測試主題中包含特殊字元的儲存"""
        topic = "Quantum Computing & AI"
        findings = "Test findings"

        result = save_research_findings(topic, findings, self.tool_context)

        assert result["status"] == "success"
        assert "research_quantum_computing_&_ai.md" in result["filename"]


class TestAgentConfiguration:
    """測試 Agent 的設定與組態"""

    def test_root_agent_is_basic_grounding_agent(self):
        """測試 root_agent 是否為 basic_grounding_agent"""
        assert root_agent is basic_grounding_agent

    def test_basic_grounding_agent_config(self):
        """測試 basic_grounding_agent 的組態"""
        assert basic_grounding_agent.name == "basic_grounding_agent"
        assert basic_grounding_agent.model == "gemini-2.0-flash"
        assert "google_search" in str(basic_grounding_agent.tools)
        assert basic_grounding_agent.output_key == "grounding_response"

    def test_advanced_grounding_agent_config(self):
        """測試 advanced_grounding_agent 的組態"""
        assert advanced_grounding_agent.name == "advanced_grounding_agent"
        assert advanced_grounding_agent.model == "gemini-2.0-flash"
        # 注意：在目前的 ADK 中，google_search 不能與自訂工具混合使用
        # 這個測試驗證了預期的組態
        tool_names = [str(tool) for tool in advanced_grounding_agent.tools]
        assert any("google_search" in name for name in tool_names)
        # 總共應該有 3 個工具：google_search + 2 個 FunctionTools
        assert len(advanced_grounding_agent.tools) == 3
        assert advanced_grounding_agent.output_key == "advanced_research_response"

    def test_research_assistant_config(self):
        """測試 research_assistant 的組態"""
        assert research_assistant.name == "research_assistant"
        assert research_assistant.model == "gemini-2.0-flash"
        assert len(research_assistant.tools) == 3  # google_search + 2 custom tools
        assert research_assistant.output_key == "research_response"

        # 檢查 generate_content_config
        config = research_assistant.generate_content_config
        assert config.temperature == 0.3
        assert config.max_output_tokens == 2048

    def test_agents_have_descriptions(self):
        """測試所有 Agent 是否都有描述"""
        agents = [basic_grounding_agent, advanced_grounding_agent, research_assistant]

        for agent in agents:
            assert agent.description is not None
            assert len(agent.description) > 0

    def test_agents_have_instructions(self):
        """測試所有 Agent 是否都有指令"""
        agents = [basic_grounding_agent, advanced_grounding_agent, research_assistant]

        for agent in agents:
            assert agent.instruction is not None
            assert len(agent.instruction) > 0
            assert "search" in agent.instruction.lower()


class TestGroundingCapabilities:
    """測試 Grounding 特定功能"""

    def test_basic_agent_has_google_search(self):
        """測試 basic_agent 是否有 google_search 工具"""
        tool_names = [str(tool) for tool in basic_grounding_agent.tools]
        assert any("google_search" in name for name in tool_names)

    def test_advanced_agent_has_search_tool(self):
        """測試 advanced_agent 是否有 google_search 工具"""
        tool_names = [str(tool) for tool in advanced_grounding_agent.tools]
        assert any("google_search" in name for name in tool_names)

    def test_research_agent_instruction_quality(self):
        """測試 research_agent 是否有完整的指令"""
        instruction = research_assistant.instruction.lower()

        # 應該提及關鍵功能（現在包含搜尋）
        assert "analyze_search_results" in instruction
        assert "save_research_findings" in instruction
        assert "research process" in instruction
        assert "web research" in instruction  # 現在包含網路研究功能


class TestIntegration:
    """多步驟工作流程的整合測試"""

    def setup_method(self):
        """每個測試前的設定"""
        self.tool_context = Mock()

    def test_research_workflow_simulation(self):
        """測試模擬的研究工作流程"""
        # 模擬 Agent 會執行的工作流程

        # 步驟 1：分析搜尋結果
        analysis_result = analyze_search_results(
            "AI trends 2025",
            "Artificial Intelligence continues to evolve rapidly. Key trends include multimodal models, agent systems, and ethical AI development.",
            self.tool_context,
        )
        assert analysis_result["status"] == "success"

        # 步驟 2：儲存發現
        save_result = save_research_findings(
            "AI Trends 2025",
            "AI is evolving with multimodal models and agent systems.",
            self.tool_context,
        )
        assert save_result["status"] == "success"

        # 驗證工作流程的一致性
        assert analysis_result["analysis"]["query"] == "AI trends 2025"
        assert "ai_trends_2025.md" in save_result["filename"]

    def test_tool_error_handling(self):
        """測試工具是否能優雅地處理錯誤"""
        # 使用無效輸入進行測試
        result = analyze_search_results("", "", self.tool_context)
        assert result["status"] == "success"  # 不應失敗

        result = save_research_findings("", "", self.tool_context)
        assert result["status"] == "success"  # 不應失敗


class TestAgentImports:
    """測試所有匯入是否正常運作"""

    def test_agent_imports(self):
        """測試所有 Agent 匯入是否正常運作"""
        from grounding_agent.agent import (
            basic_grounding_agent,
            advanced_grounding_agent,
            research_assistant,
            root_agent,
        )

        assert basic_grounding_agent is not None
        assert advanced_grounding_agent is not None
        assert research_assistant is not None
        assert root_agent is not None

    def test_tool_imports(self):
        """測試工具匯入是否正常運作"""
        from grounding_agent.agent import analyze_search_results, save_research_findings

        assert callable(analyze_search_results)
        assert callable(save_research_findings)


class TestVertexAIConditionalLogic:
    """測試條件式 VertexAI 功能"""

    def test_is_vertexai_enabled_false_by_default(self):
        """測試 VertexAI 預設為停用"""
        # 這應該在未設定任何環境變數的情況下運作
        from grounding_agent.agent import is_vertexai_enabled

        assert not is_vertexai_enabled()

    def test_is_vertexai_enabled_with_env_var(self, monkeypatch):
        """測試設定環境變數時 VertexAI 是否啟用"""
        from grounding_agent.agent import is_vertexai_enabled

        # 測試 "1"
        monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
        assert is_vertexai_enabled()

        # 測試 "true" (不應運作，只有 "1" 可以)
        monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
        assert not is_vertexai_enabled()

        # 測試 "0"
        monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "0")
        assert not is_vertexai_enabled()

    def test_get_available_grounding_tools_without_vertexai(self):
        """測試未啟用 VertexAI 時的工具載入"""
        from grounding_agent.agent import get_available_grounding_tools
        import os

        # 確保 VertexAI 已停用
        original_value = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
        try:
            if "GOOGLE_GENAI_USE_VERTEXAI" in os.environ:
                del os.environ["GOOGLE_GENAI_USE_VERTEXAI"]

            tools = get_available_grounding_tools()
            assert len(tools) == 1
            assert "google_search" in str(tools[0]).lower()
        finally:
            if original_value is not None:
                os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = original_value

    def test_get_available_grounding_tools_with_vertexai(self, monkeypatch):
        """測試啟用 VertexAI 時的工具載入"""
        from grounding_agent.agent import get_available_grounding_tools

        monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
        tools = get_available_grounding_tools()
        assert len(tools) == 2
        tool_names = [str(tool).lower() for tool in tools]
        assert any("google_search" in name for name in tool_names)
        assert any("google_maps" in name for name in tool_names)

    def test_get_agent_capabilities_description_without_vertexai(self):
        """測試未啟用 VertexAI 時的功能描述"""
        from grounding_agent.agent import get_agent_capabilities_description
        import os

        # 確保 VertexAI 已停用
        original_value = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
        try:
            if "GOOGLE_GENAI_USE_VERTEXAI" in os.environ:
                del os.environ["GOOGLE_GENAI_USE_VERTEXAI"]

            desc = get_agent_capabilities_description()
            assert "web search for current information" in desc
            assert "maps" not in desc.lower()
        finally:
            if original_value is not None:
                os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = original_value

    def test_get_agent_capabilities_description_with_vertexai(self, monkeypatch):
        """測試啟用 VertexAI 時的功能描述"""
        from grounding_agent.agent import get_agent_capabilities_description

        monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
        desc = get_agent_capabilities_description()
        assert "web search for current information" in desc
        assert "location-based queries and maps grounding" in desc

    def test_agents_include_maps_tools_with_vertexai(self, monkeypatch):
        """測試啟用 VertexAI 時 Agent 是否包含地圖工具"""
        monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")

        # 強制重新評估模組級變數
        # (在實際使用中，這些變數會在匯入時評估)
        # 在此測試中，我們將檢查函式是否正常運作
        from grounding_agent.agent import get_available_grounding_tools

        tools = get_available_grounding_tools()
        assert len(tools) == 2  # 應包含地圖 Grounding

    def test_root_agent_selection_logic(self):
        """測試 root_agent 選擇邏輯是否正常運作"""
        from grounding_agent.agent import is_vertexai_enabled

        # 測試決定使用哪個 Agent 的邏輯
        # 注意：root_agent 在匯入時設定，因此我們測試選擇邏輯

        # 當 VertexAI 停用時，應使用 basic_agent
        original_value = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
        try:
            if "GOOGLE_GENAI_USE_VERTEXAI" in os.environ:
                del os.environ["GOOGLE_GENAI_USE_VERTEXAI"]

            # 直接測試選擇邏輯
            assert not is_vertexai_enabled()
            # 在這種情況下，root_agent 會是 basic_grounding_agent
            # (我們無法在 pytest 中輕易測試模組級的賦值)

        finally:
            if original_value is not None:
                os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = original_value

    def test_agent_instructions_adapt_to_vertexai(self, monkeypatch):
        """測試 Agent 指令是否根據 VertexAI 的可用性進行調整"""
        from grounding_agent.agent import basic_grounding_agent

        # 測試未使用 VertexAI 的情況
        original_env = {}
        for key in ["GOOGLE_GENAI_USE_VERTEXAI"]:
            if key in os.environ:
                original_env[key] = os.environ[key]

        try:
            # 清除 VertexAI 環境變數
            if "GOOGLE_GENAI_USE_VERTEXAI" in os.environ:
                del os.environ["GOOGLE_GENAI_USE_VERTEXAI"]

            # 指令中不應提及地圖
            instructions = basic_grounding_agent.instruction.lower()
            assert "maps" not in instructions

            # 設定 VertexAI
            monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "1")

            # 注意：在目前的實作中，Agent 指令是在匯入時設定的
            # 因此它們不會動態改變。這個測試記錄了預期的行為。
            # 在生產系統中，您可能也希望讓指令是動態的。

        finally:
            # 還原環境
            for key, value in original_env.items():
                os.environ[key] = value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
