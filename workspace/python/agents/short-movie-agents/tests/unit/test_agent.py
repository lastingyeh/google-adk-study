"""
Agent 配置與功能測試

測試所有 Agent 的配置、屬性與功能正確性。
"""


class TestRootAgentConfiguration:
    """測試根 Agent (Director Agent) 配置。"""

    def test_root_agent_exists(self):
        """測試 root_agent 是否已正確定義。"""
        from app.agent import root_agent

        assert root_agent is not None

    def test_agent_has_correct_name(self):
        """測試 Agent 是否擁有正確名稱。"""
        from app.agent import root_agent

        assert root_agent.name == "director_agent"

    def test_agent_has_correct_model(self):
        """測試 Agent 是否使用正確的模型。"""
        from app.agent import root_agent

        assert root_agent.model == "gemini-2.5-flash"

    def test_agent_has_description(self):
        """測試 Agent 是否擁有描述。"""
        from app.agent import root_agent

        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_agent_has_instruction(self):
        """測試 Agent 是否擁有指令。"""
        from app.agent import root_agent

        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_agent_has_sub_agents(self):
        """測試 Agent 是否已配置子 Agent。"""
        from app.agent import root_agent

        assert hasattr(root_agent, "sub_agents")
        assert root_agent.sub_agents is not None
        assert len(root_agent.sub_agents) == 4


class TestStoryAgent:
    """測試故事代理 (Story Agent) 配置。"""

    def test_story_agent_exists(self):
        """測試 story_agent 是否存在。"""
        from app.story_agent import story_agent

        assert story_agent is not None

    def test_story_agent_name(self):
        """測試 story_agent 名稱。"""
        from app.story_agent import story_agent

        assert story_agent.name == "story_agent"

    def test_story_agent_model(self):
        """測試 story_agent 模型。"""
        from app.story_agent import story_agent

        assert story_agent.model == "gemini-2.5-flash"

    def test_story_agent_has_output_key(self):
        """測試 story_agent 是否有 output_key。"""
        from app.story_agent import story_agent

        assert hasattr(story_agent, "output_key")
        assert story_agent.output_key == "story"

    def test_story_agent_has_instruction(self):
        """測試 story_agent 是否有指令。"""
        from app.story_agent import story_agent

        assert story_agent.instruction is not None
        assert len(story_agent.instruction) > 0

    def test_story_agent_has_description(self):
        """測試 story_agent 是否有描述。"""
        from app.story_agent import story_agent

        assert story_agent.description is not None
        assert len(story_agent.description) > 0


class TestScreenplayAgent:
    """測試劇本代理 (Screenplay Agent) 配置。"""

    def test_screenplay_agent_exists(self):
        """測試 screenplay_agent 是否存在。"""
        from app.screenplay_agent import screenplay_agent

        assert screenplay_agent is not None

    def test_screenplay_agent_name(self):
        """測試 screenplay_agent 名稱。"""
        from app.screenplay_agent import screenplay_agent

        assert screenplay_agent.name == "screenplay_agent"

    def test_screenplay_agent_model(self):
        """測試 screenplay_agent 模型。"""
        from app.screenplay_agent import screenplay_agent

        assert screenplay_agent.model == "gemini-2.5-flash"

    def test_screenplay_agent_has_output_key(self):
        """測試 screenplay_agent 是否有 output_key。"""
        from app.screenplay_agent import screenplay_agent

        assert hasattr(screenplay_agent, "output_key")
        assert screenplay_agent.output_key == "screenplay"

    def test_screenplay_agent_has_instruction(self):
        """測試 screenplay_agent 是否有指令。"""
        from app.screenplay_agent import screenplay_agent

        assert screenplay_agent.instruction is not None
        assert len(screenplay_agent.instruction) > 0


class TestStoryboardAgent:
    """測試分鏡腳本代理 (Storyboard Agent) 配置。"""

    def test_storyboard_agent_exists(self):
        """測試 storyboard_agent 是否存在。"""
        from app.storyboard_agent import storyboard_agent

        assert storyboard_agent is not None

    def test_storyboard_agent_name(self):
        """測試 storyboard_agent 名稱。"""
        from app.storyboard_agent import storyboard_agent

        assert storyboard_agent.name == "storyboard_agent"

    def test_storyboard_agent_model(self):
        """測試 storyboard_agent 模型。"""
        from app.storyboard_agent import storyboard_agent

        assert storyboard_agent.model == "gemini-2.5-flash"

    def test_storyboard_agent_has_tools(self):
        """測試 storyboard_agent 是否有工具。"""
        from app.storyboard_agent import storyboard_agent

        assert hasattr(storyboard_agent, "tools")
        assert len(storyboard_agent.tools) > 0

    def test_storyboard_agent_has_output_key(self):
        """測試 storyboard_agent 是否有 output_key。"""
        from app.storyboard_agent import storyboard_agent

        assert hasattr(storyboard_agent, "output_key")
        assert storyboard_agent.output_key == "storyboard"

    def test_storyboard_agent_tool_exists(self):
        """測試 storyboard_generate 工具是否存在。"""
        from app.storyboard_agent import storyboard_generate

        assert callable(storyboard_generate)


class TestVideoAgent:
    """測試影片代理 (Video Agent) 配置。"""

    def test_video_agent_exists(self):
        """測試 video_agent 是否存在。"""
        from app.video_agent import video_agent

        assert video_agent is not None

    def test_video_agent_name(self):
        """測試 video_agent 名稱。"""
        from app.video_agent import video_agent

        assert video_agent.name == "video_agent"

    def test_video_agent_model(self):
        """測試 video_agent 模型。"""
        from app.video_agent import video_agent

        assert video_agent.model == "gemini-2.5-flash"

    def test_video_agent_has_tools(self):
        """測試 video_agent 是否有工具。"""
        from app.video_agent import video_agent

        assert hasattr(video_agent, "tools")
        assert len(video_agent.tools) > 0

    def test_video_agent_has_output_key(self):
        """測試 video_agent 是否有 output_key。"""
        from app.video_agent import video_agent

        assert hasattr(video_agent, "output_key")
        assert video_agent.output_key == "video"

    def test_video_agent_tool_exists(self):
        """測試 video_generate 工具是否存在。"""
        from app.video_agent import video_generate

        assert callable(video_generate)


class TestAgentIntegration:
    """測試 Agent 整合。"""

    def test_all_sub_agents_in_root_agent(self):
        """測試所有子 Agent 是否都在根 Agent 中。"""
        from app.agent import root_agent
        from app.story_agent import story_agent
        from app.screenplay_agent import screenplay_agent
        from app.storyboard_agent import storyboard_agent
        from app.video_agent import video_agent

        sub_agent_names = [agent.name for agent in root_agent.sub_agents]

        assert story_agent.name in sub_agent_names
        assert screenplay_agent.name in sub_agent_names
        assert storyboard_agent.name in sub_agent_names
        assert video_agent.name in sub_agent_names

    def test_agent_is_google_adk_agent(self):
        """測試 Agent 是否為 Google ADK Agent 實例。"""
        from app.agent import root_agent
        from google.adk.agents import Agent

        assert isinstance(root_agent, Agent)
