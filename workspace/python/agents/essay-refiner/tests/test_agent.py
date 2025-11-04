import pytest
from unittest.mock import Mock, patch
from essay_refiner.agent import (
    root_agent,
    essay_refinement_system,
    refinement_loop,
    initial_writer,
    critic,
    refiner,
    exit_loop
)


class TestIndividualAgents:
    """測試獨立代理的設定與屬性。"""

    def test_root_agent_configuration(self):
        """測試 `root_agent` 是否已正確設定。"""
        assert root_agent.name == "EssayRefinementSystem"
        assert len(root_agent.sub_agents) == 2
        assert root_agent.sub_agents[0].name == "InitialWriter"
        assert root_agent.sub_agents[1].name == "RefinementLoop"

    def test_initial_writer_agent(self):
        """測試 `InitialWriter` 代理的設定。"""
        assert initial_writer.name == "InitialWriter"
        assert initial_writer.model == "gemini-2.0-flash"
        assert initial_writer.output_key == "current_essay"
        assert "first draft" in initial_writer.instruction.lower()
        assert "3-4 paragraphs" in initial_writer.instruction

    def test_critic_agent(self):
        """測試 `Critic` 代理的設定。"""
        assert critic.name == "Critic"
        assert critic.model == "gemini-2.0-flash"
        assert critic.output_key == "critique"
        assert "evaluation criteria" in critic.instruction.lower()
        assert "approved - essay is complete" in critic.instruction.lower()

    def test_refiner_agent(self):
        """測試 `Refiner` 代理的設定。"""
        assert refiner.name == "Refiner"
        assert refiner.model == "gemini-2.0-flash"
        assert refiner.output_key == "current_essay"
        assert len(refiner.tools) == 1
        assert "exit_loop" in refiner.instruction.lower()
        assert "APPROVED - Essay is complete" in refiner.instruction

    def test_refinement_loop_agent(self):
        """測試 `LoopAgent` 的設定。"""
        assert refinement_loop.name == "RefinementLoop"
        assert len(refinement_loop.sub_agents) == 2
        assert refinement_loop.max_iterations == 5
        assert refinement_loop.sub_agents[0].name == "Critic"
        assert refinement_loop.sub_agents[1].name == "Refiner"


class TestSequentialAgentStructure:
    """測試整體的 `SequentialAgent` 結構。"""

    def test_essay_refinement_system_structure(self):
        """測試完整系統是否具有正確的結構。"""
        assert essay_refinement_system.name == "EssayRefinementSystem"
        assert len(essay_refinement_system.sub_agents) == 2

        # 階段一：初始寫手
        phase1 = essay_refinement_system.sub_agents[0]
        assert phase1.name == "InitialWriter"

        # 階段二：優化循環
        phase2 = essay_refinement_system.sub_agents[1]
        assert phase2.name == "RefinementLoop"
        assert hasattr(phase2, 'max_iterations')
        assert phase2.max_iterations == 5


class TestLoopAgentLogic:
    """測試 `LoopAgent` 的特定邏輯與終止條件。"""

    def test_loop_max_iterations(self):
        """測試循環是否有適當的安全限制。"""
        assert refinement_loop.max_iterations == 5

    def test_exit_loop_tool_function(self):
        """測試 `exit_loop` 工具函式。"""
        mock_context = Mock()
        mock_context.agent_name = "TestRefiner"

        # 呼叫 exit_loop 函式
        result = exit_loop(mock_context)

        # 驗證 end_of_agent 已設為 True
        assert mock_context.actions.end_of_agent is True
        # 驗證返回有效的內容字典（以防止一般性錯誤）
        expected_content = {"text": "Loop exited successfully. The agent has determined the task is complete."}
        assert result == expected_content

    @patch('builtins.print')
    def test_exit_loop_tool_print(self, mock_print):
        """測試 `exit_loop` 是否印出預期的訊息。"""
        mock_context = Mock()
        mock_context.agent_name = "TestRefiner"

        exit_loop(mock_context)

        mock_print.assert_called_once_with(
            "  [Exit Loop] Called by TestRefiner - Essay approved!"
        )


class TestStateManagement:
    """測試狀態鍵管理與資料流。"""

    def test_output_keys_consistency(self):
        """測試輸出鍵是否一致地用於狀態管理。"""
        # 初始寫手建立 current_essay
        assert initial_writer.output_key == "current_essay"

        # 優化器覆寫 current_essay (狀態版本控制)
        assert refiner.output_key == "current_essay"

        # 評論家建立 critique
        assert critic.output_key == "critique"

    def test_state_key_usage_pattern(self):
        """測試用於迭代優化的狀態覆寫模式。"""
        # 此模式允許：
        # 1. 初始寫手建立 v1
        # 2. 優化器以 v2, v3 等版本覆寫
        # 3. 評論家總是評估最新版本

        # 驗證此模式已實現
        writer_key = initial_writer.output_key
        refiner_key = refiner.output_key

        assert writer_key == refiner_key == "current_essay"

        # 評論家透過模板讀取目前的文章
        assert "{current_essay}" in critic.instruction
        assert "{critique}" in refiner.instruction


class TestAgentInstructions:
    """測試代理指令是否包含必要元素。"""

    def test_initial_writer_instruction_completeness(self):
        """測試初始寫手的指令是否完整。"""
        instr = initial_writer.instruction

        required_phrases = [
            "creative writer",
            "first draft",
            "3-4 paragraphs",
            "opening paragraph",
            "body paragraphs",
            "concluding paragraph",
            "output only the essay text"
        ]

        for phrase in required_phrases:
            assert phrase in instr.lower()

    def test_critic_instruction_completeness(self):
        """測試評論家是否有完整的評估指令。"""
        instr = critic.instruction

        required_phrases = [
            "essay critic",
            "evaluation criteria",
            "clear thesis",
            "supporting arguments",
            "grammar and style",
            "approved - essay is complete",
            "specific, actionable improvements"
        ]

        for phrase in required_phrases:
            assert phrase in instr.lower()

    def test_refiner_instruction_completeness(self):
        """測試優化器是否有完整的改進指令。"""
        instr = refiner.instruction

        required_phrases = [
            "essay editor",
            "exit_loop",
            "approved - essay is complete",
            "apply the suggested improvements",
            "output only the improved essay",
            "either call exit_loop or output improved essay"
        ]

        for phrase in required_phrases:
            assert phrase in instr.lower()


class TestToolIntegration:
    """測試工具整合與函式呼叫。"""

    def test_refiner_has_exit_tool(self):
        """測試優化器代理是否擁有 `exit_loop` 工具。"""
        assert len(refiner.tools) == 1
        # 該工具應為 exit_loop 函式
        assert refiner.tools[0] == exit_loop

    def test_exit_tool_context_handling(self):
        """測試 `exit_loop` 是否能正確處理 `ToolContext`。"""
        mock_context = Mock()
        mock_context.actions = Mock()

        exit_loop(mock_context)

        # 驗證 end_of_agent 已被設定
        assert mock_context.actions.end_of_agent is True


class TestSystemIntegration:
    """測試完整的系統整合與匯入。"""

    def test_all_agents_importable(self):
        """測試所有代理是否能無誤地匯入。"""
        # 此測試確保模組能正確載入
        from essay_refiner.agent import (
            root_agent,
            essay_refinement_system,
            refinement_loop,
            initial_writer,
            critic,
            refiner,
            exit_loop
        )

        # 驗證所有代理皆已定義
        assert root_agent is not None
        assert essay_refinement_system is not None
        assert refinement_loop is not None
        assert initial_writer is not None
        assert critic is not None
        assert refiner is not None
        assert exit_loop is not None

    def test_agent_type_consistency(self):
        """測試代理的類型是否正確。"""
        from google.adk.agents import Agent, LoopAgent, SequentialAgent

        # 測試代理類型
        assert isinstance(initial_writer, Agent)
        assert isinstance(critic, Agent)
        assert isinstance(refiner, Agent)
        assert isinstance(refinement_loop, LoopAgent)
        assert isinstance(essay_refinement_system, SequentialAgent)
        assert isinstance(root_agent, SequentialAgent)

    def test_nested_agent_structure(self):
        """測試巢狀代理結構是否正確。"""
        # 根代理包含循序系統
        assert root_agent == essay_refinement_system

        # 循序系統包含初始寫手 + 循環
        assert len(essay_refinement_system.sub_agents) == 2
        assert essay_refinement_system.sub_agents[0] == initial_writer
        assert essay_refinement_system.sub_agents[1] == refinement_loop

        # 循環包含評論家 + 優化器
        assert len(refinement_loop.sub_agents) == 2
        assert refinement_loop.sub_agents[0] == critic
        assert refinement_loop.sub_agents[1] == refiner


class TestConfigurationValidation:
    """測試設定相關的驗證。"""

    def test_model_consistency(self):
        """測試所有代理是否使用相同的模型。"""
        expected_model = "gemini-2.0-flash"

        assert initial_writer.model == expected_model
        assert critic.model == expected_model
        assert refiner.model == expected_model

    def test_agent_descriptions_exist(self):
        """測試所有代理是否都有描述。"""
        assert initial_writer.description is not None
        assert critic.description is not None
        assert refiner.description is not None
        assert refinement_loop.description is not None
        assert essay_refinement_system.description is not None

        # 描述應具有意義
        assert len(initial_writer.description) > 10
        assert len(critic.description) > 10
        assert len(refiner.description) > 10

    def test_agent_names_uniqueness(self):
        """測試所有代理的名稱是否唯一。"""
        names = [
            initial_writer.name,
            critic.name,
            refiner.name,
            refinement_loop.name,
            essay_refinement_system.name
        ]

        assert len(names) == len(set(names)), f"Duplicate names found: {names}"


if __name__ == "__main__":
    pytest.main([__file__])
