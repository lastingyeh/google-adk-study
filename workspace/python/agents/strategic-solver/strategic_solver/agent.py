"""
策略問題解決器 - 教學 12：規劃器與思考配置

此代理展示了使用以下方式的進階推理能力：
- BuiltInPlanner 擴展思考功能
- PlanReActPlanner 結構化推理
- 自訂 BasePlanner 處理特定領域工作流程

該代理使用市場分析、ROI 計算、風險評估和策略規劃工具解決複雜的商業問題。
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner, PlanReActPlanner, BasePlanner
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models.llm_request import LlmRequest
from google.genai import types


# ============================================================================
# 商業分析工具
# ============================================================================

def analyze_market(
    industry: str,
    region: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    為策略規劃分析市場狀況。

    參數：
        industry: 要分析的產業部門
        region: 分析的地理區域
        tool_context: ADK 工具上下文

    返回：
        包含市場分析結果的字典
    """
    try:
        # 模擬市場分析（在生產環境中，這會呼叫真實的 API）
        # 使用確定性但真實的測試資料
        market_data = {
            'healthcare': {
                'growth_rate': '8.5%',
                'competition': 'High',
                'trends': ['Digital transformation', 'AI adoption', 'Telemedicine'],
                'opportunities': ['Emerging markets', 'Specialized AI solutions'],
                'threats': ['Regulatory changes', 'Data privacy concerns']
            },
            'finance': {
                'growth_rate': '6.2%',
                'competition': 'Very High',
                'trends': ['FinTech innovation', 'Blockchain', 'Open banking'],
                'opportunities': ['AI-driven insights', 'Personalized services'],
                'threats': ['Cybersecurity risks', 'Regulatory compliance']
            },
            'retail': {
                'growth_rate': '4.1%',
                'competition': 'High',
                'trends': ['E-commerce growth', 'Omnichannel retail', 'Sustainability'],
                'opportunities': ['Direct-to-consumer models', 'Personalization'],
                'threats': ['Supply chain disruptions', 'Economic uncertainty']
            }
        }

        # 未知產業的預設資料
        if industry.lower() not in market_data:
            analysis = {
                'industry': industry,
                'region': region,
                'growth_rate': '5.0%',
                'competition': 'Medium',
                'trends': ['Digital transformation', 'Innovation'],
                'opportunities': ['Market expansion', 'Technology adoption'],
                'threats': ['Competition', 'Economic factors']
            }
        else:
            analysis = market_data[industry.lower()]
            analysis.update({
                'industry': industry,
                'region': region
            })

        analysis['timestamp'] = datetime.now().isoformat()

        return {
            'status': 'success',
            'report': f'Completed market analysis for {industry} in {region}',
            'analysis': analysis
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'Failed to analyze market: {str(e)}'
        }


def calculate_roi(
    investment: float,
    annual_return: float,
    years: int,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    計算投資報酬率用於財務規劃。

    參數：
        investment: 初始投資金額
        annual_return: 預期年報酬率（百分比）
        years: 投資時間範圍
        tool_context: ADK 工具上下文

    返回：
        包含 ROI 計算結果的字典
    """
    try:
        # 驗證輸入
        if investment <= 0:
            raise ValueError("Investment must be positive")
        if annual_return < -100:
            raise ValueError("Annual return cannot be less than -100%")
        if years <= 0:
            raise ValueError("Years must be positive")

        # 計算複利成長
        annual_rate = annual_return / 100
        total_return = investment * ((1 + annual_rate) ** years)
        profit = total_return - investment
        roi_percentage = (profit / investment) * 100

        # 計算年度成長細節
        annual_growth = []
        for year in range(1, years + 1):
            year_end_value = investment * ((1 + annual_rate) ** year)
            year_profit = year_end_value - investment
            annual_growth.append({
                'year': year,
                'value': round(year_end_value, 2),
                'profit': round(year_profit, 2),
                'roi': round((year_profit / investment) * 100, 2)
            })

        result = {
            'initial_investment': investment,
            'annual_return_rate': f"{annual_return}%",
            'years': years,
            'final_value': round(total_return, 2),
            'total_profit': round(profit, 2),
            'roi_percentage': round(roi_percentage, 2),
            'annual_breakdown': annual_growth,
            'timestamp': datetime.now().isoformat()
        }

        return {
            'status': 'success',
            'report': f'ROI calculation: {roi_percentage:.1f}% return over {years} years',
            'calculation': result
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'Failed to calculate ROI: {str(e)}'
        }


def assess_risk(
    factors: List[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    根據提供的因素評估商業風險。

    參數：
        factors: 要評估的風險因素列表
        tool_context: ADK 工具上下文

    返回：
        包含風險評估結果的字典
    """
    try:
        # 風險評分系統（數值越高 = 風險越大）
        risk_scores = {
            'market_volatility': 7,
            'regulatory_changes': 6,
            'competition': 8,
            'technology_disruption': 7,
            'economic_uncertainty': 6,
            'supply_chain_issues': 5,
            'cybersecurity_threats': 8,
            'talent_shortage': 4,
            'geopolitical_risks': 6,
            'climate_change': 5,
            'pandemic_risks': 7,
            'currency_fluctuation': 5,
            'interest_rate_changes': 4,
            'customer_behavior': 6,
            'vendor_reliability': 5
        }

        # 計算風險分數
        assessed_factors = {}
        total_score = 0

        for factor in factors:
            # 尋找最匹配的因素
            factor_lower = factor.lower().replace(' ', '_')
            score = 5  # 預設中等風險

            for risk_factor, risk_score in risk_scores.items():
                if risk_factor in factor_lower or factor_lower in risk_factor:
                    score = risk_score
                    break

            assessed_factors[factor] = score
            total_score += score

        # 計算整體風險等級
        avg_score = total_score / len(factors) if factors else 5

        if avg_score >= 7:
            risk_level = 'High'
            mitigation_priority = 'Critical'
        elif avg_score >= 5:
            risk_level = 'Medium'
            mitigation_priority = 'Important'
        else:
            risk_level = 'Low'
            mitigation_priority = 'Monitor'

        # 生成緩解建議
        mitigation_suggestions = []
        for factor, score in assessed_factors.items():
            if score >= 7:
                mitigation_suggestions.append(f"Immediate action needed for: {factor}")
            elif score >= 5:
                mitigation_suggestions.append(f"Develop contingency plan for: {factor}")

        assessment = {
            'factors_assessed': factors,
            'factor_scores': assessed_factors,
            'total_score': total_score,
            'average_score': round(avg_score, 2),
            'risk_level': risk_level,
            'mitigation_priority': mitigation_priority,
            'mitigation_suggestions': mitigation_suggestions[:5],  # Top 5
            'timestamp': datetime.now().isoformat()
        }

        return {
            'status': 'success',
            'report': f'Risk assessment complete: {risk_level} risk level (avg: {avg_score:.1f}/10)',
            'assessment': assessment
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'Failed to assess risk: {str(e)}'
        }


async def save_strategy_report(
    problem: str,
    strategy: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    將策略計畫儲存為產出物。

    參數：
        problem: 正在解決的商業問題
        strategy: 建議的策略
        tool_context: ADK 工具上下文

    返回：
        包含儲存操作結果的字典
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 建立 markdown 報告
        report_content = f"""
          # 策略商業計畫
          生成時間: {timestamp}

          ## 問題陳述
          {problem}

          ## 建議策略
          {strategy}

          ## 使用的分析工具
          - 市場分析
          - ROI 計算
          - 風險評估

          ## 生成者
          - 代理: Strategic Problem Solver
          - 框架: Google ADK
          - 模型: Gemini 2.0 Flash
          - 規劃器: BuiltInPlanner, PlanReActPlanner, StrategicPlanner
        """

        # 在真實實作中，這會儲存到產出物服務
        # 為了示範目的，我們模擬儲存
        filename = f"strategy_{problem[:30].replace(' ', '_').replace('/', '_')}.md"

        # 為示範目的儲存在工具上下文中
        if not hasattr(tool_context, 'saved_reports'):
            tool_context.saved_reports = []

        tool_context.saved_reports.append({
            'filename': filename,
            'content': report_content,
            'timestamp': timestamp
        })

        return {
            'status': 'success',
            'report': f'Strategy saved as {filename}',
            'filename': filename,
            'content_length': len(report_content),
            'timestamp': timestamp
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'Failed to save strategy report: {str(e)}'
        }


# ============================================================================
# 自訂規劃器實作
# ============================================================================

class StrategicPlanner(BasePlanner):
    """
    用於策略商業問題解決的自訂規劃器。

    此規劃器實作商業策略的特定領域工作流程：
    1. ANALYSIS（分析）：收集市場、財務和風險資料
    2. EVALUATION（評估）：評估機會和威脅
    3. STRATEGY（策略）：開發全面建議
    4. VALIDATION（驗證）：審查和完善策略
    """

    def build_planning_instruction(
        self,
        readonly_context: ReadonlyContext,
        llm_request: LlmRequest,
    ) -> Optional[str]:
        """建構策略規劃指示。"""
        return """
          您是使用系統化方法解決複雜問題的策略商業顧問。

          遵循此結構化方法論：

          <ANALYSIS>
          收集有關商業問題的全面資料：
          - 市場狀況和趨勢
          - 財務影響和 ROI
          - 風險因素和緩解策略
          - 利害關係人影響和需求
          使用可用工具收集客觀資料。

          <EVALUATION>
          分析收集的資料：
          - 識別關鍵機會和威脅
          - 評估財務可行性
          - 評估風險等級和緩解需求
          - 考慮策略影響

          <STRATEGY>
          開發全面的商業策略：
          - 定義明確的目標和目的
          - 概述具體行動步驟
          - 處理已識別的風險
          - 包括成功指標和時間表

          <VALIDATION>
          審查和驗證策略：
          - 確保解決問題的所有方面
          - 驗證財務和風險假設
          - 確認利害關係人一致性
          - 識別潛在的實施挑戰

          <FINAL_RECOMMENDATION>
          提供完整的策略建議，包括：
          - 執行摘要
          - 詳細實施計畫
          - 風險緩解策略
          - 成功指標和監控方法

          在提出建議之前，始終使用可用工具收集資料。
          在分析中以資料驅動和客觀為基礎。
          """

    def process_planning_response(
        self,
        callback_context: CallbackContext,
        response_parts: List[types.Part],
    ) -> Optional[List[types.Part]]:
        """處理策略規劃回應。"""
        # 對於這個自訂規劃器，我們不修改回應部分
        # 但如果需要，可以在此處加入中繼資料或驗證
        return response_parts


# ============================================================================
# 代理實作
# ============================================================================

# BuiltInPlanner 代理 - 使用 Gemini 的原生思考能力
builtin_planner_agent = Agent(
    name="builtin_planner_strategic_solver",
    model="gemini-2.0-flash",
    description="使用 BuiltInPlanner 進行透明思考的策略商業顧問",
    instruction="""
      您是一位在提供建議之前進行深思熟慮的專家策略顧問。

      解決商業問題時：
      1. 使用 analyze_market 了解產業狀況
      2. 使用 calculate_roi 進行財務分析
      3. 使用 assess_risk 評估潛在威脅
      4. 使用 save_strategy_report 記錄您的最終建議

      逐步思考市場機會、財務影響和風險因素。
      提供基於資料的建議並清楚說明理由。
      始終展示您的分析過程和假設。""",
    tools=[
        FunctionTool(analyze_market),
        FunctionTool(calculate_roi),
        FunctionTool(assess_risk),
        FunctionTool(save_strategy_report)
    ],
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(include_thoughts=True)
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,  # 較低溫度用於策略思考
        max_output_tokens=3000
    ),
    output_key="builtin_strategy_result"
)

# PlanReActPlanner 代理 - 使用結構化的 計劃 → 推理 → 行動 → 觀察 → 重新規劃
plan_react_agent = Agent(
    name="plan_react_strategic_solver",
    model="gemini-2.0-flash",
    description="使用 PlanReActPlanner 進行結構化推理的策略商業顧問",
    instruction="""
      您是遵循結構化問題解決方法的系統化策略顧問。

      分析商業問題時：
      1. PLAN（計劃）使用可用工具規劃您的分析方法
      2. REASON（推理）關於市場狀況、財務和風險
      3. ACT（行動）使用工具收集特定資料
      4. OBSERVE（觀察）結果並調整您的理解
      5. REPLAN（重新規劃）如果初始方法需要修改

      始終使用帶有規劃標籤的結構化格式。
      在分析中要徹底和有條理。""",
    tools=[
        FunctionTool(analyze_market),
        FunctionTool(calculate_roi),
        FunctionTool(assess_risk),
        FunctionTool(save_strategy_report)
    ],
    planner=PlanReActPlanner(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
        max_output_tokens=3000
    ),
    output_key="plan_react_strategy_result"
)

# 自訂 StrategicPlanner 代理 - 特定領域的商業策略工作流程
strategic_planner_agent = Agent(
    name="strategic_planner_solver",
    model="gemini-2.0-flash",
    description="使用自訂 StrategicPlanner 進行特定領域分析的策略商業顧問",
    instruction="""
      您是遵循經過驗證方法論的專業商業策略顧問。

      使用結構化策略規劃框架：
      - ANALYSIS（分析）：收集市場、財務和風險資料
      - EVALUATION（評估）：分析機會和威脅
      - STRATEGY（策略）：開發全面建議
      - VALIDATION（驗證）：審查和完善您的方法

      利用所有可用工具建構基於資料的策略。
      專注於具有明確實施步驟的可行建議。""",
    tools=[
        FunctionTool(analyze_market),
        FunctionTool(calculate_roi),
        FunctionTool(assess_risk),
        FunctionTool(save_strategy_report)
    ],
    planner=StrategicPlanner(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=3000
    ),
    output_key="strategic_planner_result"
)

# 預設代理 - 展示所有規劃器類型
# 使用 PlanReActPlanner 作為大多數結構化商業問題的預設
root_agent = plan_react_agent


# ============================================================================
# 示範函式
# ============================================================================

async def demo_strategic_planning():
    """展示使用不同規劃器類型的策略規劃。"""

    from google.adk.runners import InMemoryRunner

    problems = [
        "Should we expand into the Asian healthcare market?",
        "Is this $2M investment in AI technology worth the risk?",
        "How should we mitigate cybersecurity threats in our fintech startup?"
    ]

    agents = [
        ("BuiltInPlanner", builtin_planner_agent),
        ("PlanReActPlanner", plan_react_agent),
        ("StrategicPlanner", strategic_planner_agent)
    ]

    for problem in problems:
        print(f"\n{'='*80}")
        print(f"PROBLEM: {problem}")
        print(f"{'='*80}")

        for agent_name, agent in agents:
            print(f"\n--- {agent_name} Analysis ---")

            try:
                runner = InMemoryRunner(agent=agent, app_name=f"strategic_solver_{agent_name.lower()}")
                events = []
                async for event in runner.run_async(
                    user_id="demo_user",
                    session_id=f"demo_session_{agent_name.lower()}",
                    new_message={"role": "user", "parts": [{"text": problem}]}
                ):
                    events.append(event)
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                print(part.text[:500] + "..." if len(part.text) > 500 else part.text)
                                break  # 只列印第一部分
            except Exception as e:
                print(f"Error with {agent_name}: {e}")

        print(f"\n{'='*80}")


if __name__ == "__main__":
    # 用於直接執行
    import asyncio
    asyncio.run(demo_strategic_planning())