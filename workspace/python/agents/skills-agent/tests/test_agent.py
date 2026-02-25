# 技能代理人測試：代理人測試
# 驗證技能工具集 (SkillToolset) 與代理人設定
#
# 重點說明：
# 此測試模組涵蓋了技能代理人系統的核心配置驗證。
# 主要測試範圍包括：
# 1. Root Agent (技能使用者) 的屬性、模型與指令設定。
# 2. 兩個技能 (greeting_skill, weather_skill) 的獨立設定。
# 3. 驗證技能是否正確包裝為工具 (SkillToolset)。
# 4. 驗證技能模型 (Skill Model) 的欄位定義。
# 5. 整合測試以確保代理人可以正確使用技能工具集。

import pytest
from typing import Dict, Any


class TestAgentConfiguration:
    """測試技能代理人是否已正確設定。"""

    def test_root_agent_import(self):
        """測試 root_agent 是否可以被匯入。"""
        from skills_agent.agent import root_agent
        assert root_agent is not None

    def test_agent_is_agent_instance(self):
        """測試 root_agent 是否為 Agent 的實例。"""
        from skills_agent.agent import root_agent
        from google.adk import Agent

        assert isinstance(root_agent, Agent)

    def test_agent_name(self):
        """測試代理是否具有正確的名稱。"""
        from skills_agent.agent import root_agent

        assert hasattr(root_agent, 'name')
        assert root_agent.name == "skill_user_agent"

    def test_agent_model_is_gemini_25_flash(self):
        """測試代理是否使用 gemini-2.5-flash 模型。"""
        from skills_agent.agent import root_agent

        assert hasattr(root_agent, 'model')
        assert root_agent.model == "gemini-2.5-flash"

    def test_agent_description(self):
        """測試代理是否具有描述。"""
        from skills_agent.agent import root_agent

        assert hasattr(root_agent, 'description')
        assert len(root_agent.description) > 0
        assert "specialized skills" in root_agent.description.lower() or "skill" in root_agent.description.lower()

    def test_agent_has_tools(self):
        """測試代理是否擁有工具 (SkillToolset)。"""
        from skills_agent.agent import root_agent

        assert hasattr(root_agent, 'tools')
        assert root_agent.tools is not None
        # Should have 1 SkillToolset that contains 2 skills
        # 應具有 1 個包含 2 個技能的 SkillToolset
        assert len(root_agent.tools) == 1

    def test_agent_tool_is_skill_toolset(self):
        """測試代理的工具是否為 SkillToolset。"""
        from skills_agent.agent import root_agent
        from google.adk.tools.skill_toolset import SkillToolset

        assert len(root_agent.tools) > 0
        assert isinstance(root_agent.tools[0], SkillToolset)


class TestGreetingSkillConfiguration:
    """測試問候技能 (Greeting Skill) 是否已正確設定。"""

    def test_greeting_skill_import(self):
        """測試 greeting_skill 是否可以被匯入。"""
        from skills_agent.agent import greeting_skill
        assert greeting_skill is not None

    def test_greeting_skill_is_skill_instance(self):
        """測試 greeting_skill 是否為 Skill 的實例。"""
        from skills_agent.agent import greeting_skill
        from google.adk.skills.models import Skill

        assert isinstance(greeting_skill, Skill)

    def test_greeting_skill_has_frontmatter(self):
        """測試 greeting_skill 是否具有 frontmatter。"""
        from skills_agent.agent import greeting_skill

        assert hasattr(greeting_skill, 'frontmatter')
        assert greeting_skill.frontmatter is not None

    def test_greeting_skill_name(self):
        """測試 greeting_skill 是否具有正確的名稱。"""
        from skills_agent.agent import greeting_skill

        assert greeting_skill.frontmatter.name == "greeting-skill"

    def test_greeting_skill_description(self):
        """測試 greeting_skill 是否具有描述。"""
        from skills_agent.agent import greeting_skill

        assert greeting_skill.frontmatter.description is not None
        assert len(greeting_skill.frontmatter.description) > 0

    def test_greeting_skill_has_instructions(self):
        """測試 greeting_skill 是否具有指令。"""
        from skills_agent.agent import greeting_skill

        assert hasattr(greeting_skill, 'instructions')
        assert greeting_skill.instructions is not None
        assert len(greeting_skill.instructions) > 0

    def test_greeting_skill_has_resources(self):
        """測試 greeting_skill 是否具有資源。"""
        from skills_agent.agent import greeting_skill

        assert hasattr(greeting_skill, 'resources')
        assert greeting_skill.resources is not None

    def test_greeting_skill_has_references(self):
        """測試 greeting_skill 是否具有參考資料。"""
        from skills_agent.agent import greeting_skill

        assert hasattr(greeting_skill.resources, 'references')
        assert greeting_skill.resources.references is not None
        assert 'hello_world.txt' in greeting_skill.resources.references

    def test_greeting_skill_reference_content(self):
        """測試 greeting_skill 的參考資料內容。"""
        from skills_agent.agent import greeting_skill

        hello_content = greeting_skill.resources.references['hello_world.txt']
        assert '哈囉' in hello_content or 'Hello' in hello_content or '👋' in hello_content


class TestWeatherSkillConfiguration:
    """測試天氣技能 (Weather Skill) 是否已正確設定。"""

    def test_weather_skill_import(self):
        """測試 weather_skill 是否可以被匯入。"""
        from skills_agent.agent import weather_skill
        assert weather_skill is not None

    def test_weather_skill_is_skill_instance(self):
        """測試 weather_skill 是否為 Skill 的實例。"""
        from skills_agent.agent import weather_skill
        from google.adk.skills.models import Skill

        assert isinstance(weather_skill, Skill)

    def test_weather_skill_has_frontmatter(self):
        """測試 weather_skill 是否具有 frontmatter。"""
        from skills_agent.agent import weather_skill

        assert hasattr(weather_skill, 'frontmatter')
        assert weather_skill.frontmatter is not None

    def test_weather_skill_name(self):
        """測試 weather_skill 是否具有正確的名稱。"""
        from skills_agent.agent import weather_skill

        assert weather_skill.frontmatter.name == "weather-skill"

    def test_weather_skill_description(self):
        """測試 weather_skill 是否具有描述。"""
        from skills_agent.agent import weather_skill

        assert weather_skill.frontmatter.description is not None
        assert len(weather_skill.frontmatter.description) > 0
        assert "weather" in weather_skill.frontmatter.description.lower() or "天氣" in weather_skill.frontmatter.description

    def test_weather_skill_has_instructions(self):
        """測試 weather_skill 是否具有指令。"""
        from skills_agent.agent import weather_skill

        assert hasattr(weather_skill, 'instructions')
        assert weather_skill.instructions is not None
        assert len(weather_skill.instructions) > 0

    def test_weather_skill_loaded_from_directory(self):
        """測試 weather_skill 是否從目錄載入。"""
        from skills_agent.agent import weather_skill
        import os

        # Verify the skill directory exists
        # 驗證技能目錄是否存在
        skill_path = 'skills_agent/skills/weather-skill'
        assert os.path.isdir(skill_path)

        # Verify SKILL.md exists
        # 驗證 SKILL.md 存在
        skill_md_path = os.path.join(skill_path, 'SKILL.md')
        assert os.path.isfile(skill_md_path)


class TestSkillToolsetConfiguration:
    """測試 SkillToolset 配置。"""

    def test_skill_toolset_import(self):
        """測試 my_skill_toolset 是否可以被匯入。"""
        from skills_agent.agent import my_skill_toolset
        assert my_skill_toolset is not None

    def test_skill_toolset_is_toolset_instance(self):
        """測試 my_skill_toolset 是否為 SkillToolset 的實例。"""
        from skills_agent.agent import my_skill_toolset
        from google.adk.tools.skill_toolset import SkillToolset

        assert isinstance(my_skill_toolset, SkillToolset)

    def test_skill_toolset_has_skills(self):
        """測試 SkillToolset 是否包含技能。"""
        from skills_agent.agent import my_skill_toolset

        # SkillToolset 使用私有屬性 _skills 儲存技能（字典）
        assert hasattr(my_skill_toolset, '_skills')
        assert my_skill_toolset._skills is not None
        # Should have 2 skills: greeting and weather
        # 應有 2 個技能：greeting 和 weather
        assert len(my_skill_toolset._skills) == 2

    def test_skill_toolset_skills_are_valid(self):
        """測試 SkillToolset 中的技能是否有效。"""
        from skills_agent.agent import my_skill_toolset, greeting_skill, weather_skill
        from google.adk.skills.models import Skill

        # _skills 是一個字典，key 是技能名稱，value 是 Skill 物件
        for skill_name, skill in my_skill_toolset._skills.items():
            assert isinstance(skill, Skill)
            assert skill_name == skill.frontmatter.name

        # Verify the skills are the expected ones
        # 驗證技能是預期的技能
        skill_names = list(my_skill_toolset._skills.keys())
        assert "greeting-skill" in skill_names
        assert "weather-skill" in skill_names


class TestAgentToolIntegration:
    """測試 Agent 與工具的整合。"""

    def test_agent_has_skill_toolset_in_tools(self):
        """測試 Agent 的工具中包含 SkillToolset。"""
        from skills_agent.agent import root_agent, my_skill_toolset

        assert len(root_agent.tools) > 0
        # The first tool should be the SkillToolset
        # 第一個工具應該是 SkillToolset
        assert root_agent.tools[0] == my_skill_toolset

    def test_agent_can_access_skills_through_toolset(self):
        """測試 Agent 可以透過 SkillToolset 存取技能。"""
        from skills_agent.agent import root_agent

        skill_toolset = root_agent.tools[0]
        # SkillToolset 使用私有屬性 _skills（字典）
        assert hasattr(skill_toolset, '_skills')
        assert len(skill_toolset._skills) == 2

        skill_names = list(skill_toolset._skills.keys())
        assert "greeting-skill" in skill_names
        assert "weather-skill" in skill_names
