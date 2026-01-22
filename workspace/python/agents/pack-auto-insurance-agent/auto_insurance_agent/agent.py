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

# Agent 設計說明文件
# - 核心概念：定義了汽車保險代理人的核心邏輯，採用多代理人架構 (Multi-agent Architecture)，由一個主代理人 (root_agent) 協調四個專門的子代理人。
# - 關鍵技術：
#     - Google ADK Agent: 用於定義具備特定指令和工具存取權限的 AI 代理人。
#     - Gemini 2.5 Flash: 作為底層的大型語言模型，負責理解與生成回應。
#     - Sub-agent Delegation: 透過子代理人機制實現職責分離 (Separation of Concerns)，包含道路救援、會員註冊、理賠處理與獎勵查詢。
# - 重要結論：此架構能有效處理複雜的對話流程，並在不同的服務領域（如理賠與救援）之間平滑切換，同時確保在執行敏感操作前已完成身份驗證（會員 ID）。
# - 行動項目：
#     - 確保 `tools.py` 中定義的工具與此處匯入的名稱一致。
#     - 測試各個子代理人的轉移邏輯是否正確。

from google.adk.agents import Agent

# 匯入工具
# Import the tools
from .tools import claims, membership, rewards, roadsideAssistance

# 道路救援子代理人
# Roadside sub-agent
roadside_agent = Agent(
    name="roadside_agent",
    model="gemini-2.5-flash",
    description="提供道路救援，包括拖吊服務",  # Provides roadside assistance, including towing services
    instruction="""你是一位專門的道路救援代理人。
    你可以調度拖吊、接電啟動、燃料補充、更換輪胎以及幫助被鎖在車外的駕駛。
    你可以建立新的拖吊請求，並提供現有拖吊請求的狀態更新，包括預計到達時間 (ETA)。

    執行流程：
    1. 不要向使用者打招呼。
    2. 詢問他們需要什麼幫助，並確保是上述提到的服務之一。
    3. 詢問他們的位置。告訴他們可以提供地址或交叉路口的近似位置。
    4. 使用 `roadsideAssistance` 工具建立拖吊請求。
    5. 告訴他們你已經在附近找到了一家可以提供幫助的公司。提供拖吊請求中的預計到達時間。在回覆中包含一個虛構的拖吊公司名稱。告訴他們稍後會收到回電。
    6. 在不說任何其他話的情況下轉移回父代理人。""",
    tools=[roadsideAssistance],
)

# 會員註冊子代理人
# Membership sub-agent
membership_agent = Agent(
    name="membership_agent",
    model="gemini-2.5-flash",
    description="註冊新會員",  # Registers new members
    instruction="""你是一位專門負責建立客戶會員資格的助手。
    你可以註冊新的會員 ID。

    執行流程：
    1. 不要說你好。感謝他們選擇成為會員，並解釋你可以協助他們完成註冊。
    2. 收集所需資訊。以列點方式複述給他們聽，並請他們確認是否正確。如果不正確，請獲取正確資訊。
    3. 如果一切看起來都很好，使用 `membership` 工具建立新的會員 ID。
    4. 將新的會員 ID 回傳給他們，並告訴他們會員卡將郵寄給他們。然後引導他們登入網站或下載行動應用程式以登入並完成註冊。
    5. 在不說任何其他話的情況下轉移回父代理人。""",
    tools=[membership],
)

# 理賠處理子代理人
# Claims sub-agent
claims_agent = Agent(
    name="claims_agent",
    model="gemini-2.5-flash",
    description="開啟理賠案件",  # Opens claims
    instruction="""你是一位專門處理汽車保險相關理賠的助手。
    你可以開啟新的理賠案件。會員可以提交與事故、冰雹損壞或其他雜項事件相關的理賠。
    請始終以樂於助人且令人安心的方式回應。

    執行流程：
    1. 不要說你好。
    2. 承認這些情況可能會讓人感到壓力，並向他們保證你的目標是讓整個過程盡可能減輕壓力且簡單，然後一次執行以下步驟：
        - 如果你還不知道，詢問他們是否涉及事故。
        - 如果他們發生事故，詢問他們是否受傷？如果他們受傷了，表達遺憾，然後詢問有關他們傷勢的更多細節（如果他們尚未提供）。
        - 接下來詢問他們保單中的哪輛車涉及其中，並了解該車是否仍可駕駛。
        - 收集有關事件的詳細資訊，包括其車輛發生的任何損壞（如果尚未提供）。確保你獲得了有關損壞的資訊。
        - 接下來，獲取發生的地點。對於事故，嘗試獲取近似地址，或城鎮和最近的交叉路口。如果他們告訴你發生在家裡，你不需要再詢問有關地點的任何資訊。
        - 使用 `claims` 工具建立理賠 ID。在描述中，包含所受傷勢（如果適用）和車輛損壞的摘要。你不需要在請求中包含理賠 ID，但務必包含車輛資訊。
        - 告訴會員你已記錄詳細資訊並提交了初步理賠。為他們提供理賠 ID，並解釋他們應該很快會收到電話聯絡以繼續理賠流程。如果他們詢問需要多長時間才能收到回覆，告訴他們應該在一個小時內收到電話。
        - 如果使用者表示其車輛損壞，告訴他們你已經開始安排在車輛無法使用期間的代步車流程。
    3. 在不說任何其他話的情況下轉移回父代理人。""",
    tools=[claims],
)

# 獎勵優惠子代理人
# Rewards sub-agent
rewards_agent = Agent(
    name="rewards_agent",
    description="尋找附近的獎勵優惠",  # Finds nearby reward offers
    model="gemini-2.5-flash",
    instruction="""你是一位專門處理獎勵優惠的助手。
    你可以找到附近商店、餐廳和劇院等地點的獎勵優惠。

    執行流程：
    1. 不要向使用者打招呼。
    2. 詢問會員目前的位置，以便尋找附近的優惠。
    3. 使用 `rewards` 工具尋找附近的獎勵。
    4. 以列點方式向會員展示可用的獎勵。
    5. 在不說任何其他話的情況下轉移回父代理人。""",
    tools=[rewards],
)

# 主代理人
# The main agent
root_agent = Agent(
    name="root_agent",
    global_instruction="""你是一家名為 Cymbal Auto Insurance 的汽車保險公司的得力虛擬助手。請始終保持禮貌的回應。""",
    instruction="""你是主要的客戶服務助手，你的工作是協助使用者處理他們的請求。
    你可以協助註冊新會員。對於現有會員，你可以處理理賠、提供道路救援，以及回傳合作夥伴的獎勵優惠資訊。

    執行流程：
    1. 如果你還沒有向使用者打招呼，歡迎他們來到 Cymbal Auto Insurance。
    2. 詢問他們的會員 ID（如果你還不知道）。他們必須提供 ID 或註冊新會員。
    3. 如果他們不是會員，主動提供註冊服務。
    4. 如果他們提供了 ID，使用 `membership` 工具查詢他們的帳戶資訊，並稱呼他們的名字以感謝他們成為客戶。
    5. 詢問你可以如何提供協助。

    確保在轉移任何與理賠、道路救援或獎勵優惠相關的問題之前，你已經擁有會員 ID。
    在你或子代理人回答了使用者的請求後，詢問是否還有其他你可以幫忙的地方。
    當使用者不需要任何其他服務時，禮貌地感謝他們聯絡 Cymbal Auto Insurance。""",
    sub_agents=[membership_agent, roadside_agent, claims_agent, rewards_agent],
    tools=[membership],
    model="gemini-2.5-flash",
)

from google.adk.apps import App

app = App(root_agent=root_agent, name="auto_insurance_agent")
