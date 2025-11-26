"""
Tutorial 26 的測試套件：企業代理工具函數。
"""

import pytest
from enterprise_agent.agent import (
    check_company_size,
    score_lead,
    get_competitive_intel
)


class TestCheckCompanySize:
    """測試 check_company_size 工具函數。"""

    def test_check_company_size_known_company(self):
        """測試查詢已知的公司。"""
        result = check_company_size("TechCorp")

        assert result["status"] == "success"
        assert result["company_name"] == "TechCorp"
        assert "data" in result
        assert result["data"]["employees"] == 250
        assert result["data"]["revenue"] == "50M"
        assert result["data"]["industry"] == "technology"

    def test_check_company_size_finance(self):
        """測試查詢金融公司。"""
        result = check_company_size("FinanceGlobal")

        assert result["status"] == "success"
        assert result["data"]["employees"] == 1200
        assert result["data"]["industry"] == "finance"

    def test_check_company_size_healthcare(self):
        """測試查詢醫療保健公司。"""
        result = check_company_size("HealthPlus")

        assert result["status"] == "success"
        assert result["data"]["employees"] == 450
        assert result["data"]["industry"] == "healthcare"

    def test_check_company_size_unknown_company(self):
        """測試查詢未知公司返回預設值。"""
        result = check_company_size("UnknownCompany")

        assert result["status"] == "success"
        assert result["company_name"] == "UnknownCompany"
        assert result["data"]["employees"] == 0
        assert result["data"]["revenue"] == "Unknown"

    def test_check_company_size_has_report(self):
        """測試函數返回人類可讀的報告。"""
        result = check_company_size("TechCorp")

        assert "report" in result
        assert len(result["report"]) > 0


class TestScoreLead:
    """測試 score_lead 工具函數。"""

    def test_score_lead_highly_qualified(self):
        """測試評分高資格的潛在客戶（70+ 分）。"""
        result = score_lead(
            company_size=250,
            industry="technology",
            budget="enterprise"
        )

        assert result["status"] == "success"
        assert result["score"] >= 70
        assert result["qualification"] == "HIGHLY QUALIFIED"
        assert "demo" in result["recommendation"].lower()

    def test_score_lead_qualified(self):
        """測試評分合格的潛在客戶（40-69 分）。"""
        result = score_lead(
            company_size=150,
            industry="retail",
            budget="business"
        )

        assert result["status"] == "success"
        assert 40 <= result["score"] < 70
        assert result["qualification"] == "QUALIFIED"

    def test_score_lead_unqualified(self):
        """測試評分不合格的潛在客戶（<40 分）。"""
        result = score_lead(
            company_size=20,
            industry="retail",
            budget="startup"
        )

        assert result["status"] == "success"
        assert result["score"] < 40
        assert result["qualification"] == "UNQUALIFIED"

    def test_score_lead_large_company_bonus(self):
        """測試大公司獲得額外加分。"""
        result = score_lead(
            company_size=150,
            industry="other",
            budget="startup"
        )

        # 公司規模應獲得 30 分
        assert result["score"] == 30

    def test_score_lead_target_industry_bonus(self):
        """測試目標產業獲得額外加分。"""
        result = score_lead(
            company_size=50,
            industry="finance",
            budget="startup"
        )

        # 金融產業應獲得 30 分
        assert result["score"] == 30

    def test_score_lead_healthcare_industry(self):
        """測試醫療保健作為目標產業。"""
        result = score_lead(
            company_size=50,
            industry="healthcare",
            budget="startup"
        )

        # 醫療保健產業應獲得 30 分
        assert result["score"] == 30

    def test_score_lead_enterprise_budget(self):
        """測試企業預算層級評分。"""
        result = score_lead(
            company_size=50,
            industry="retail",
            budget="enterprise"
        )

        # 企業預算應獲得 40 分
        assert result["score"] == 40

    def test_score_lead_business_budget(self):
        """測試商業預算層級評分。"""
        result = score_lead(
            company_size=50,
            industry="retail",
            budget="business"
        )

        # 商業預算應獲得 20 分
        assert result["score"] == 20

    def test_score_lead_perfect_score(self):
        """測試完美資格（100 分）。"""
        result = score_lead(
            company_size=500,
            industry="finance",
            budget="enterprise"
        )

        assert result["score"] == 100
        assert result["qualification"] == "HIGHLY QUALIFIED"

    def test_score_lead_has_factors(self):
        """測試評分提供詳細的因素。"""
        result = score_lead(
            company_size=250,
            industry="technology",
            budget="enterprise"
        )

        assert "factors" in result
        assert len(result["factors"]) > 0
        assert isinstance(result["factors"], list)

    def test_score_lead_has_report(self):
        """測試評分返回人類可讀的報告。"""
        result = score_lead(
            company_size=250,
            industry="technology",
            budget="enterprise"
        )

        assert "report" in result
        assert len(result["report"]) > 0
        assert str(result["score"]) in result["report"]


class TestGetCompetitiveIntel:
    """測試 get_competitive_intel 工具函數。"""

    def test_get_competitive_intel_basic(self):
        """測試獲取競爭情報。"""
        result = get_competitive_intel("OurCompany", "CompetitorX")

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["company"] == "OurCompany"
        assert result["data"]["competitor"] == "CompetitorX"

    def test_get_competitive_intel_has_differentiators(self):
        """測試競爭情報包含差異化因素。"""
        result = get_competitive_intel("OurCompany", "CompetitorX")

        assert "differentiators" in result["data"]
        assert len(result["data"]["differentiators"]) > 0

    def test_get_competitive_intel_has_weaknesses(self):
        """測試競爭情報包含競爭對手弱點。"""
        result = get_competitive_intel("OurCompany", "CompetitorX")

        assert "competitor_weaknesses" in result["data"]
        assert len(result["data"]["competitor_weaknesses"]) > 0

    def test_get_competitive_intel_has_news(self):
        """測試競爭情報包含最新消息。"""
        result = get_competitive_intel("OurCompany", "CompetitorX")

        assert "recent_news" in result["data"]
        assert len(result["data"]["recent_news"]) > 0

    def test_get_competitive_intel_has_report(self):
        """測試競爭情報返回格式化的報告。"""
        result = get_competitive_intel("OurCompany", "CompetitorX")

        assert "report" in result
        assert len(result["report"]) > 0
        assert "OurCompany" in result["report"]
        assert "CompetitorX" in result["report"]


class TestToolIntegration:
    """測試工具是否協同工作以進行潛在客戶資格審查流程。"""

    def test_full_qualification_workflow(self):
        """測試完整的潛在客戶資格審查流程。"""
        # 步驟 1：檢查公司規模
        company_result = check_company_size("TechCorp")
        assert company_result["status"] == "success"

        # 步驟 2：評分潛在客戶
        company_data = company_result["data"]
        score_result = score_lead(
            company_size=company_data["employees"],
            industry=company_data["industry"],
            budget="enterprise"
        )
        assert score_result["status"] == "success"
        assert score_result["score"] == 100  # TechCorp: 250 員工, 科技業, 企業預算

        # 步驟 3：獲取競爭情報
        intel_result = get_competitive_intel("TechCorp", "CompetitorX")
        assert intel_result["status"] == "success"

    def test_tools_return_consistent_format(self):
        """測試所有工具返回一致的回應格式。"""
        tools = [
            check_company_size("TechCorp"),
            score_lead(250, "technology", "enterprise"),
            get_competitive_intel("OurCompany", "CompetitorX")
        ]

        for result in tools:
            assert "status" in result
            assert result["status"] == "success"
            assert "report" in result
            assert len(result["report"]) > 0
