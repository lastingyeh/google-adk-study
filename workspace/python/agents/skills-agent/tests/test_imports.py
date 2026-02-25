# 技能代理人測試：匯入與模組測試
# 驗證所有匯入和模組結構是否正確
#
# 重點說明：
# 此測試模組確保專案的模組結構符合預期，且所有關鍵組件皆可正確匯入。
# 主要測試範圍包括：
# 1. 驗證 skills_agent 模組及其子模組的存在性。
# 2. 確保 Google ADK 與專案內的 Skill 相關類別可被正確匯入。
# 3. 檢查模組匯出的物件類型是否正確 (如 Agent, Skill, SkillToolset)。
# 4. 驗證 __init__.py 是否正確暴露了 agent 模組。

import pytest
import sys


class TestModuleStructure:
    """測試模組結構是否正確。"""

    def test_skills_agent_module_exists(self):
        """測試 skills_agent 模組是否存在。"""
        import skills_agent
        assert skills_agent is not None

    def test_skills_agent_agent_module_exists(self):
        """測試 skills_agent.agent 模組是否存在。"""
        import skills_agent.agent
        assert skills_agent.agent is not None

    def test_agent_module_has_root_agent(self):
        """測試 agent 模組是否匯出 root_agent。"""
        from skills_agent import agent
        assert hasattr(agent, 'root_agent')

    def test_root_agent_is_exported(self):
        """測試 root_agent 是否可以直接匯入。"""
        from skills_agent.agent import root_agent
        assert root_agent is not None


class TestImports:
    """測試所有必要的匯入是否正常運作。"""

    def test_google_adk_agents_import(self):
        """測試 google.adk.Agent 是否可以被匯入。"""
        from google.adk import Agent
        assert Agent is not None

    def test_google_adk_skills_import(self):
        """測試 google.adk.skills 模組是否可以被匯入。"""
        from google.adk.skills import load_skill_from_dir, models
        assert load_skill_from_dir is not None
        assert models is not None

    def test_skill_toolset_import(self):
        """測試 SkillToolset 是否可以被匯入。"""
        from google.adk.tools.skill_toolset import SkillToolset
        assert SkillToolset is not None

    def test_skills_import(self):
        """測試 skills (greeting_skill, weather_skill) 是否可以被匯入。"""
        from skills_agent.agent import (
            greeting_skill,
            weather_skill,
            my_skill_toolset
        )
        assert greeting_skill is not None
        assert weather_skill is not None
        assert my_skill_toolset is not None

    def test_agent_import(self):
        """測試 agent 是否可以被匯入。"""
        from skills_agent.agent import root_agent
        assert root_agent is not None


class TestModuleExports:
    """測試模組是否匯出所需的項目。"""

    def test_agent_module_exports_agent_instance(self):
        """測試 agent 模組是否匯出 Agent 實例。"""
        from skills_agent.agent import root_agent
        from google.adk import Agent
        assert isinstance(root_agent, Agent)

    def test_greeting_skill_is_skill_model(self):
        """測試 greeting_skill 是否為 Skill 模型實例。"""
        from skills_agent.agent import greeting_skill
        from google.adk.skills.models import Skill

        assert isinstance(greeting_skill, Skill)

    def test_weather_skill_is_skill_model(self):
        """測試 weather_skill 是否為 Skill 模型實例。"""
        from skills_agent.agent import weather_skill
        from google.adk.skills.models import Skill

        assert isinstance(weather_skill, Skill)

    def test_skill_toolset_is_toolset_instance(self):
        """測試 my_skill_toolset 是否為 SkillToolset 實例。"""
        from skills_agent.agent import my_skill_toolset
        from google.adk.tools.skill_toolset import SkillToolset

        assert isinstance(my_skill_toolset, SkillToolset)

    def test_agent_uses_gemini_2_5_flash(self):
        """測試代理是否設定使用 gemini-2.5-flash 模型。"""
        from skills_agent.agent import root_agent

        assert hasattr(root_agent, 'model')
        assert root_agent.model == "gemini-2.5-flash"
