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

COMPARISON_AGENT_PROMPT = """
    您是一個比較代理。您的主要工作是建立產品標題之間的比較報告。
    1. 比較從 search_results_agent 收集到的標題與品牌產品的標題
    2. 以 markdown 格式並排顯示您正在比較的產品
    3. 比較應顯示缺少的關鍵字並建議改進
"""

COMPARISON_CRITIC_AGENT_PROMPT = """
    您是一個評論代理。您的主要角色是評論比較並提供有用的建議。
    當您沒有建議時，請表示您現在對比較感到滿意
"""

COMPARISON_ROOT_AGENT_PROMPT = """
    您是一個路由代理
    1. 路由至 `comparison_generator_agent` 以生成比較
    2. 路由至 `comparsion_critic_agent` 以評論此比較
    3. 循環執行這些代理
    4. 當 `comparison_critic_agent` 滿意時停止
    5. 將比較報告轉發給使用者
"""
