# Copyright 2026 Google LLC
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

"""展示如何使用技能工具集 (SkillToolset) 的代理人範例。"""

import pathlib

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.skills import models
from google.adk.tools.skill_toolset import SkillToolset

# 定義問候技能 (Greeting skill)
# 流程說明：
# ```mermaid
# graph TD
#     A[讀取 references/hello_world.txt] --> B[根據參考內容回傳問候語]
# ```
greeting_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="greeting-skill",
        description=("一個友善的問候技能，可以向特定的人打招呼。"),
    ),
    instructions=(
        "步驟 1：讀取 'references/hello_world.txt' 檔案以瞭解如何"
        " 向使用者打招呼。步驟 2：根據參考內容回傳問候語。"
    ),
    resources=models.Resources(
        references={
            "hello_world.txt": "哈囉！ 👋👋👋 很高興見到你！ ✨✨✨",
            "example.md": "這是一個範例參考資料。",
        },
    ),
)

print(pathlib.Path(__file__).parent / "skills" / "weather-skill")

# 從目錄載入天氣技能 (Weather skill)
weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather-skill"
)

# 建立技能工具集 (Skill Toolset)
my_skill_toolset = SkillToolset(skills=[greeting_skill, weather_skill])

# 初始化根代理人 (Root Agent)
root_agent = Agent(
    model="gemini-2.5-flash",
    name="skill_user_agent",
    description="一個可以使用專業技能 (Specialized skills) 的代理人。",
    tools=[
        my_skill_toolset,
    ],
)
