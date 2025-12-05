# 教學範例 34: 具備子代理的文件處理代理
# 使用多個專門的代理 (作為工具) 來處理不同類型的文件
# 每個代理都使用 Pydantic 輸出結構描述 (Schema) 強制執行 JSON 輸出
#
# Tutorial 34: Document Processing Agent with Sub-Agents
# Uses multiple specialized agents (as tools) for different document types
# Each agent enforces JSON output using Pydantic output schemas

from __future__ import annotations

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool


# ============================================================================
# 結構化輸出結構描述 (Pydantic 模型)
# Structured Output Schemas (Pydantic Models)
# ============================================================================

class EntityExtraction(BaseModel):
    """
    從文件內容中提取的實體。
    Extracted entities from document content.
    """

    dates: list[str] = Field(
        default_factory=list,
        description="文件中發現的日期清單 (例如：2024-10-08) List of dates found in the document"
    )
    currency_amounts: list[str] = Field(
        default_factory=list,
        description="發現的貨幣數值 (例如：$1,200.50) Currency values found"
    )
    percentages: list[str] = Field(
        default_factory=list,
        description="發現的百分比數值 (例如：35%) Percentage values found"
    )
    numbers: list[str] = Field(
        default_factory=list,
        description="文件中發現的重要數字 Significant numbers found in the document"
    )


class DocumentSummary(BaseModel):
    """
    文件內容的簡明摘要。
    Concise summary of document content.
    """

    main_points: list[str] = Field(
        description="文件中的前 3-5 個主要重點 Top 3-5 main points from the document"
    )
    key_insight: str = Field(
        description="文件中最重要的洞察 The most important takeaway from the document"
    )
    summary: str = Field(
        description="整份文件的 1-2 句摘要 A 1-2 sentence summary of the entire document"
    )


class FinancialMetrics(BaseModel):
    """
    從文件中提取的財務指標。
    Financial metrics extracted from documents.
    """

    revenue: str = Field(default="", description="總營收 Total revenue")
    profit: str = Field(default="", description="總利潤 Total profit")
    margin: str = Field(default="", description="利潤率 Profit margin")
    growth_rate: str = Field(default="", description="成長率 Growth rate")
    other_metrics: list[str] = Field(
        default_factory=list,
        description="其他相關財務指標 Other relevant financial metrics"
    )


class MarketingMetrics(BaseModel):
    """
    從文件中提取的行銷指標。
    Marketing metrics extracted from documents.
    """

    engagement_rate: str = Field(default="", description="參與率 Engagement rate")
    conversion_rate: str = Field(default="", description="轉換率 Conversion rate")
    reach: str = Field(default="", description="受眾觸及率 Audience reach")
    cost: str = Field(default="", description="活動成本 Campaign cost")
    revenue: str = Field(default="", description="活動營收 Campaign revenue")
    other_metrics: list[str] = Field(
        default_factory=list,
        description="其他相關行銷指標 Other relevant marketing metrics"
    )


class Deal(BaseModel):
    """
    銷售交易資訊。
    Sales deal information.
    """

    customer: str = Field(default="", description="客戶名稱 Customer name")
    deal_value: str = Field(default="", description="交易價值/金額 Deal value/amount")
    stage: str = Field(default="", description="交易階段 (開啟、協商中、已結案等) Deal stage (open, negotiating, closed, etc.)")
    notes: str = Field(default="", description="額外交易註記 Additional deal notes")


# ============================================================================
# 特定文件類型的輸出結構描述
# Document Type-Specific Output Schemas
# ============================================================================

class FinancialAnalysisOutput(BaseModel):
    """
    財務文件分析的結構化輸出。
    Structured output for financial document analysis.
    """

    summary: DocumentSummary
    entities: EntityExtraction
    financial_metrics: FinancialMetrics = Field(
        description="關鍵財務指標 (營收、利潤、利潤率等) Key financial metrics (revenue, profit, margins, etc.)"
    )
    fiscal_periods: list[str] = Field(
        default_factory=list,
        description="提到的財政期間 (季度、年份) Fiscal periods mentioned (quarters, years)"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="財務建議 Financial recommendations"
    )


class TechnicalAnalysisOutput(BaseModel):
    """
    技術文件分析的結構化輸出。
    Structured output for technical document analysis.
    """

    summary: DocumentSummary
    entities: EntityExtraction
    technologies: list[str] = Field(
        description="提到的技術和框架 Technologies and frameworks mentioned"
    )
    components: list[str] = Field(
        description="討論的系統元件或服務 System components or services discussed"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="技術建議 Technical recommendations"
    )


class SalesAnalysisOutput(BaseModel):
    """
    銷售文件分析的結構化輸出。
    Structured output for sales document analysis.
    """

    summary: DocumentSummary
    entities: EntityExtraction
    deals: list[Deal] = Field(
        default_factory=list,
        description="交易資訊 (客戶、價值、階段) Deal information (customer, value, stage)"
    )
    pipeline_value: str = Field(
        default="",
        description="總管道價值 Total pipeline value"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="銷售建議 Sales recommendations"
    )


class MarketingAnalysisOutput(BaseModel):
    """
    行銷文件分析的結構化輸出。
    Structured output for marketing document analysis.
    """

    summary: DocumentSummary
    entities: EntityExtraction
    campaigns: list[str] = Field(
        default_factory=list,
        description="提到的行銷活動 Marketing campaigns mentioned"
    )
    metrics: MarketingMetrics = Field(
        description="行銷指標 (參與度、轉換率、觸及率) Marketing metrics (engagement, conversion, reach)"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="行銷建議 Marketing recommendations"
    )


# ============================================================================
# 每種文件類型的子代理 (使用 JSON 輸出強制執行)
# Sub-Agents for Each Document Type (Using JSON Output Enforcement)
# ============================================================================

financial_agent = LlmAgent(
    name="financial_analyzer",
    model="gemini-2.5-flash",
    description="分析財務文件和報告 Analyzes financial documents and reports",
    instruction=(
        "你是一位專業的財務分析師。分析提供的財務文件並提取所有相關資訊，包括指標、期間和建議。\n"
        "You are an expert financial analyst. Analyze the provided financial document "
        "and extract all relevant information including metrics, periods, and recommendations. "
        "提供包含以下內容的綜合分析：\n"
        "Provide a comprehensive analysis with:\n"
        "- 主要財務重點和摘要 Main financial points and summary\n"
        "- 財務指標：營收、利潤、利潤率、成長率 Financial metrics: revenue, profit, margins, growth rates\n"
        "- 提到的財政期間 (Q1, Q2, 2024 等) Fiscal periods mentioned (Q1, Q2, 2024, etc.)\n"
        "- 財務改善的關鍵建議 Key recommendations for financial improvement\n\n"
        "使用 set_model_response 工具並回傳所需的 JSON 結構。\n"
        "Return your analysis using the set_model_response tool with the required JSON structure."
    ),
    output_schema=FinancialAnalysisOutput,
)

technical_agent = LlmAgent(
    name="technical_analyzer",
    model="gemini-2.5-flash",
    description="分析技術文件和規格書 Analyzes technical documents and specifications",
    instruction=(
        "你是一位專業的技術分析師。分析提供的技術文件並提取技術、元件和技術建議。\n"
        "You are an expert technical analyst. Analyze the provided technical document "
        "and extract technologies, components, and technical recommendations. "
        "提供包含以下內容的綜合分析：\n"
        "Provide a comprehensive analysis with:\n"
        "- 技術摘要和主要重點 Technical summary and main points\n"
        "- 提到的技術和框架 Technologies and frameworks mentioned\n"
        "- 討論的系統元件和服務 System components and services discussed\n"
        "- 改善的技術建議 Technical recommendations for improvement\n\n"
        "使用 set_model_response 工具並回傳所需的 JSON 結構。\n"
        "Return your analysis using the set_model_response tool with the required JSON structure."
    ),
    output_schema=TechnicalAnalysisOutput,
)

sales_agent = LlmAgent(
    name="sales_analyzer",
    model="gemini-2.5-flash",
    description="分析銷售文件和管道資訊 Analyzes sales documents and pipeline information",
    instruction=(
        "你是一位專業的銷售分析師。分析提供的銷售文件並提取交易資訊、管道價值和銷售建議。\n"
        "You are an expert sales analyst. Analyze the provided sales document "
        "and extract deal information, pipeline value, and sales recommendations. "
        "提供包含以下內容的綜合分析：\n"
        "Provide a comprehensive analysis with:\n"
        "- 銷售摘要和主要重點 Sales summary and main points\n"
        "- 包含價值和階段的客戶交易 Customer deals with values and stages\n"
        "- 總管道價值 Total pipeline value\n"
        "- 成長的銷售建議 Sales recommendations for growth\n\n"
        "使用 set_model_response 工具並回傳所需的 JSON 結構。\n"
        "Return your analysis using the set_model_response tool with the required JSON structure."
    ),
    output_schema=SalesAnalysisOutput,
)

marketing_agent = LlmAgent(
    name="marketing_analyzer",
    model="gemini-2.5-flash",
    description="分析行銷文件和活動資訊 Analyzes marketing documents and campaign information",
    instruction=(
        "你是一位專業的行銷分析師。分析提供的行銷文件並提取活動資訊、指標和行銷建議。\n"
        "You are an expert marketing analyst. Analyze the provided marketing document "
        "and extract campaign information, metrics, and marketing recommendations. "
        "提供包含以下內容的綜合分析：\n"
        "Provide a comprehensive analysis with:\n"
        "- 行銷摘要和主要活動 Marketing summary and main campaigns\n"
        "- 參與率、轉換率、觸及率指標 Engagement rates, conversion rates, reach metrics\n"
        "- 活動成本和產生的營收 Campaign costs and revenue generated\n"
        "- 最佳化的行銷建議 Marketing recommendations for optimization\n\n"
        "使用 set_model_response 工具並回傳所需的 JSON 結構。\n"
        "Return your analysis using the set_model_response tool with the required JSON structure."
    ),
    output_schema=MarketingAnalysisOutput,
)


# ============================================================================
# 將子代理包裝為協調者代理的工具
# Wrap Sub-Agents as Tools for the Coordinator Agent
# ============================================================================

financial_tool = AgentTool(financial_agent)
technical_tool = AgentTool(technical_agent)
sales_tool = AgentTool(sales_agent)
marketing_tool = AgentTool(marketing_agent)


# ============================================================================
# 根協調者代理
# Root Coordinator Agent
# ============================================================================

root_agent = LlmAgent(
    name="pubsub_processor",
    model="gemini-2.5-flash",
    description="事件驅動的文件處理協調者，負責路由到專門的分析器",
    instruction=(
        "你是一個用於事件驅動處理管線的文件路由和協調代理。\n"
        "你的角色是：\n"
        "1. 分析傳入的文件以確定其類型\n"
        "2. 將其路由到適當的專門分析器\n"
        "3. 回傳結構化的分析結果\n\n"
        "文件類型和路由：\n"
        "- FINANCIAL (財務): 對財務報告、收益、預算使用 financial_analyzer\n"
        "- TECHNICAL (技術): 對規格書、架構、部署文件使用 technical_analyzer\n"
        "- SALES (銷售): 對管道、交易、預測、合約使用 sales_analyzer\n"
        "- MARKETING (行銷): 對活動、參與度、策略使用 marketing_analyzer\n\n"
        "指導方針：\n"
        "- 始終先識別主要文件類型\n"
        "- 路由到最適當的分析器\n"
        "- 確保所有提取的資訊準確且完整\n"
        "- 回傳所選分析器的 JSON 結構化輸出\n\n"
        "決策框架：\n"
        "- 尋找財務關鍵字 (revenue, profit, budget, fiscal, quarterly, earnings)\n"
        "- 尋找技術關鍵字 (API, deployment, database, configuration, architecture)\n"
        "- 尋找銷售關鍵字 (deal, pipeline, customer, forecast, contract, closed)\n"
        "- 尋找行銷關鍵字 (campaign, engagement, conversion, reach, audience)\n"
    ),
    tools=[financial_tool, technical_tool, sales_tool, marketing_tool],
)

### 重點摘要 (程式碼除外)
# - **核心概念**：多重代理系統 (Multi-Agent System)，包含一個協調者 (Coordinator) 和多個專家 (Specialists)。
# - **關鍵技術**：Google ADK `LlmAgent`, `AgentTool`, Pydantic 模型 (用於結構化輸出)。
# - **重要結論**：通過定義明確的 Pydantic 模型，可以強制 LLM 輸出符合預期的 JSON 格式，這對於自動化流程至關重要。
# - **行動項目**：如果需要支援新的文件類型，需定義新的 Pydantic 模型並建立相應的子代理，然後將其添加到 `root_agent` 的工具列表中。
