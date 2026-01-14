"""
Orchestrator Agent - 主要入口點
負責分析使用者輸入並將任務委派給適當的專門 Agent
"""

from __future__ import annotations

import sys
import os
# 添加 backend 目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from google.adk.agents import Agent  # 匯入 ADK 提供的 Agent 類別，用來建立代理核心物件
from .conversation_agent.agent import conversation_agent  # 匯入對話代理
from .strategic_planner_agent.agent import strategic_planner_agent  # 匯入策略規劃代理
from guardrails.guardrails import before_model_callback  # 匯入安全防護回調函數

# ============================================================================
# ORCHESTRATOR AGENT DEFINITION
# ============================================================================

# 定義主協調代理：按照框架規則，變數必須命名為 'root_agent' 才會被自動載入。
# 
# 架構說明：
# - 此 Agent 作為系統的純粹路由器，**不直接回應使用者**
# - 分析使用者意圖後，**必須委派**給對應的專門 Agent 處理
# - 根據使用者輸入的特定指令（如 #think）決定使用哪個專門的 Agent
# - 支援多種思考模式：一般對話模式與策略規劃模式
#
# 參數說明：
# - name: 顯示於介面的協調器名稱
# - model: 使用 Gemini 2.0 Flash，確保快速的意圖分析與任務分派
# - description: 描述此協調器的核心功能
# - instruction: 詳細的系統指令，定義純粹的委派邏輯，禁止直接回應

root_agent = Agent(
    name="OrchestratorAgent",  # 協調器代理名稱
    model="gemini-2.0-flash",  # 高速模型，適合快速意圖分析
    description="智能任務路由器，負責分析使用者需求並委派給專門的 AI 助理，不直接回應。",  # 協調器功能描述
    instruction=(  # 系統指令：定義純粹的委派邏輯
        """
        你是一個智能任務路由器 (Router)，你的**唯一職責**是分析使用者輸入並委派給最適合的專門 AI 助理。

        ## 重要限制
        **你絕對不可以直接回應使用者的問題**。你必須將所有任務委派給子代理 (sub-agents)。

        ## 委派規則

        ### 策略規劃模式委派條件
        當使用者輸入符合以下**任一條件**時，委派給 `strategic_planner_agent`：
        - 包含 `#think` 指令
        - 包含關鍵詞：「規劃」、「計畫」、「策略」、「分析」、「步驟」、「如何做」、「方法」
        - 請求多步驟解決方案
        - 涉及專案管理、系統設計、問題分解等複雜任務
        - 需要結構化思考過程的問題

        ### 一般對話模式委派條件
        當使用者輸入**不符合**策略規劃條件時，委派給 `conversation_agent`：
        - 日常問答與閒聊
        - 簡單的資訊查詢
        - 知識解釋與學習支援
        - 情感支持或一般性討論

        ## 委派行為
        1. **靜默分析**：快速識別使用者意圖，不向使用者說明分析過程
        2. **直接委派**：根據分析結果，立即將任務委派給對應的子代理
        3. **無縫轉移**：確保使用者感受到的是統一的 AI 體驗

        ## 禁止行為
        - ❌ 不可直接回答使用者問題
        - ❌ 不可說明委派過程
        - ❌ 不可與使用者進行對話
        - ❌ 不可提供任何形式的直接回應

        ## 委派格式
        你必須使用內建的委派機制，將控制權完全轉移給選定的子代理。讓子代理處理所有與使用者的互動。

        記住：你是一個透明的路由器，使用者應該感覺不到你的存在，只會與專門的子代理互動。
        """
    ),
    sub_agents=[  # 子代理列表：協調器可委派任務的專門代理
        conversation_agent,
        strategic_planner_agent,
    ],
    before_model_callback=before_model_callback,  # 呼叫前的安全防護回調
)
