# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from auto_insurance_agent.agent import (
    claims_agent,
    membership_agent,
    rewards_agent,
    roadside_agent,
    root_agent,
)


class TestAgentConfiguration:
    """測試 Agent 配置"""

    def test_root_agent_attributes(self):
        """驗證 Root Agent 的基本屬性"""
        assert root_agent.name == "root_agent"
        assert root_agent.model == "gemini-2.5-flash"
        # Root agent 只有 membership 工具
        assert len(root_agent.tools) == 1
        assert root_agent.tools[0].name == "cymbal-auto-membership-api"

    def test_sub_agents_structure(self):
        """驗證子 Agent 的層級結構"""
        assert len(root_agent.sub_agents) == 4
        sub_agent_names = [agent.name for agent in root_agent.sub_agents]
        expected_sub_agents = [
            "membership_agent",
            "roadside_agent",
            "claims_agent",
            "rewards_agent",
        ]
        assert set(sub_agent_names) == set(expected_sub_agents)

    def test_membership_agent_attributes(self):
        """驗證 Membership Agent 的屬性與工具"""
        assert membership_agent.name == "membership_agent"
        assert membership_agent.model == "gemini-2.5-flash"
        assert len(membership_agent.tools) == 1
        assert membership_agent.tools[0].name == "cymbal-auto-membership-api"

    def test_roadside_agent_attributes(self):
        """驗證 Roadside Agent 的屬性與工具"""
        assert roadside_agent.name == "roadside_agent"
        assert roadside_agent.model == "gemini-2.5-flash"
        assert len(roadside_agent.tools) == 1
        assert roadside_agent.tools[0].name == "cymbal-auto-roadside-assistance-api"

    def test_claims_agent_attributes(self):
        """驗證 Claims Agent 的屬性與工具"""
        assert claims_agent.name == "claims_agent"
        assert claims_agent.model == "gemini-2.5-flash"
        assert len(claims_agent.tools) == 1
        assert claims_agent.tools[0].name == "cymbal-auto-claims-api"

    def test_rewards_agent_attributes(self):
        """驗證 Rewards Agent 的屬性與工具"""
        assert rewards_agent.name == "rewards_agent"
        assert rewards_agent.model == "gemini-2.5-flash"
        assert len(rewards_agent.tools) == 1
        assert rewards_agent.tools[0].name == "cymbal-auto-rewards-api"
