"""
enterprise-agent: Gemini Enterprise - 企業級 Agent 部署

本教學示範如何建立可部署到 Gemini Enterprise (前身為 Google AgentSpace) 的 ADK Agent，
用於企業規模的 Agent 管理、治理、編排與協作。

核心概念：
- 使用 ADK 建立企業級 Agent
- 企業 Agent 架構模式
- 潛在客戶資格審查與評分邏輯
- 企業整合工具設計
- 生產就緒的 Agent 設定

此 Agent 可使用以下指令部署到 Gemini Enterprise：
  adk deploy agent_engine --agent-path . --project your-project
"""

from __future__ import annotations

from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools import FunctionTool


# ============================================================================
# 企業工具函數 (Enterprise Tool Functions)
# ============================================================================

def check_company_size(company_name: str) -> Dict[str, Any]:
    """
    從企業資料庫查詢公司規模。

    在生產環境中，這將整合：
    - CRM 系統 (Salesforce, HubSpot)
    - 公司情報 API (Clearbit, ZoomInfo)
    - 內部資料庫

    Args:
        company_name: 要查詢的公司名稱

    Returns:
        包含員工數和營收等公司資訊的字典
    """
    # 模擬公司資料庫查詢
    # 在生產環境中，這將呼叫實際的 API 或資料庫
    company_db = {
        "TechCorp": {"employees": 250, "revenue": "50M", "industry": "technology"},
        "FinanceGlobal": {"employees": 1200, "revenue": "500M", "industry": "finance"},
        "HealthPlus": {"employees": 450, "revenue": "120M", "industry": "healthcare"},
        "RetailMart": {"employees": 50, "revenue": "5M", "industry": "retail"},
        "StartupXYZ": {"employees": 15, "revenue": "1M", "industry": "technology"},
    }

    # 未知公司的預設值
    company_data = company_db.get(
        company_name,
        {"employees": 0, "revenue": "Unknown", "industry": "unknown"}
    )

    return {
        "status": "success",
        "company_name": company_name,
        "data": company_data,
        "report": f"Found company data: {company_data['employees']} employees, ${company_data['revenue']} revenue"
    }


def score_lead(company_size: int, industry: str, budget: str) -> Dict[str, Any]:
    """
    根據資格標準將銷售潛在客戶評分 0-100。

    評分標準：
    - 公司規模：若 > 100 名員工則得 30 分
    - 產業適配度：目標產業得 30 分
    - 預算層級：企業預算得 40 分

    Args:
        company_size: 員工人數
        industry: 產業別 (科技、金融、醫療保健等)
        budget: 預算類別 (新創、商業、企業)

    Returns:
        包含潛在客戶分數和資格詳情的字典
    """
    score = 0
    factors = []

    # 公司規模評分
    if company_size > 100:
        score += 30
        factors.append("✅ Company size > 100 employees (+30 points)")
    else:
        factors.append("❌ Company size < 100 employees (0 points)")

    # 產業適配度評分
    target_industries = ['technology', 'finance', 'healthcare']
    if industry.lower() in target_industries:
        score += 30
        factors.append(f"✅ Target industry: {industry} (+30 points)")
    else:
        factors.append(f"❌ Non-target industry: {industry} (0 points)")

    # 預算層級評分
    if budget.lower() == 'enterprise':
        score += 40
        factors.append("✅ Enterprise budget tier (+40 points)")
    elif budget.lower() == 'business':
        score += 20
        factors.append("⚠️  Business budget tier (+20 points)")
    else:
        factors.append("❌ Startup budget tier (0 points)")

    # 決定資格狀態
    if score >= 70:
        status = "HIGHLY QUALIFIED"
        recommendation = "Schedule demo immediately"
    elif score >= 40:
        status = "QUALIFIED"
        recommendation = "Nurture lead with targeted content"
    else:
        status = "UNQUALIFIED"
        recommendation = "Add to newsletter list for future follow-up"

    return {
        "status": "success",
        "score": score,
        "qualification": status,
        "factors": factors,
        "recommendation": recommendation,
        "report": f"Lead scored {score}/100 - {status}. {recommendation}"
    }


def get_competitive_intel(company_name: str, competitor: str) -> Dict[str, Any]:
    """
    獲取將公司與競爭對手比較的競爭情報。

    在生產環境中，這將整合：
    - 市場情報平台
    - 新聞聚合 API
    - 社群聆聽工具
    - 財務數據提供商

    Args:
        company_name: 潛在客戶公司名稱
        competitor: 要比較的競爭對手名稱

    Returns:
        包含競爭分析的字典
    """
    # 模擬競爭情報
    # 在生產環境中，這將呼叫實際的市場情報 API
    intel = {
        "company": company_name,
        "competitor": competitor,
        "differentiators": [
            "Better enterprise support and SLAs (更好的企業支援和 SLA)",
            "More flexible pricing for mid-market (更靈活的中階市場定價)",
            "Stronger data security and compliance features (更強的資料安全和合規功能)",
            "Better integration with Google Cloud ecosystem (與 Google Cloud 生態系統更好的整合)"
        ],
        "competitor_weaknesses": [
            "Higher pricing for similar features (類似功能的定價較高)",
            "Limited customization options (有限的客製化選項)",
            "Slower support response times (較慢的支援回應時間)"
        ],
        "recent_news": [
            f"{competitor} raised Series C funding last quarter ({competitor} 上一季完成 C 輪融資)",
            f"{company_name} won industry award for innovation ({company_name} 贏得產業創新獎)",
            f"{competitor} facing customer retention challenges ({competitor} 面臨客戶留存挑戰)"
        ]
    }

    report = f"""
        Competitive Analysis: {company_name} vs {competitor}

        Our Differentiators:
        {chr(10).join(f'  • {d}' for d in intel['differentiators'])}

        Competitor Weaknesses:
        {chr(10).join(f'  • {w}' for w in intel['competitor_weaknesses'])}

        Recent Market Activity:
        {chr(10).join(f'  • {n}' for n in intel['recent_news'])}
    """.strip()

    return {
        "status": "success",
        "data": intel,
        "report": report
    }


# ============================================================================
# 企業 Agent 定義 (Enterprise Agent Definition)
# ============================================================================

root_agent = Agent(
    model="gemini-2.0-flash",
    name="lead_qualifier",
    description="具備公司情報和評分功能的企業銷售潛在客戶資格審查 Agent",
    instruction="""
    你是一位企業銷售潛在客戶資格審查專家。

    你的職責是：
    1. 根據公司簡介和適配度分析銷售潛在客戶
    2. 使用客觀標準將潛在客戶評分 0-100
    3. 在相關時提供競爭情報
    4. 為銷售團隊建議下一步

    資格標準：
    - 公司規模 > 100 名員工，30 分
    - 目標產業：科技、金融、醫療保健，30 分
    - 企業預算層級，40 分

    評分閾值：
    - 70分以上：高度符合資格 - 立即安排演示
    - 40-69分：符合資格 - 提供針對性內容進行培育
    - 40分以下：不符合資格 - 加入電子報以供後續追蹤

    分析潛在客戶時：
    1. 使用 check_company_size 獲取公司資訊
    2. 使用 score_lead 配合公司資料計算資格分數
    3. 如果提到競爭對手，使用 get_competitive_intel 進行定位分析
    4. 提供明確的建議和具體的下一步

    始終保持專業、數據導向，並專注於協助銷售團隊將精力優先放在最有希望的機會上。
    """.strip(),
    tools=[
        FunctionTool(check_company_size),
        FunctionTool(score_lead),
        FunctionTool(get_competitive_intel)
    ]
)

# Deployment Configuration (for reference)
# This agent would be deployed to Gemini Enterprise using:
#
# adk deploy agent_engine \
#   --agent-path ./enterprise_agent \
#   --project your-gcp-project \
#   --region us-central1 \
#   --display-name "Enterprise Lead Qualifier"
#
# Or via Python API:
# from google.adk.deployment import deploy_to_agent_engine
# deploy_to_agent_engine(
#     agent=root_agent,
#     project='your-project',
#     region='us-central1',
#     permissions=['sales-team@company.com'],
#     connectors=['salesforce-crm']
# )
