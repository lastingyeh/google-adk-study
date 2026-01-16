"""
Pydantic 模型測試
"""

from pydantic import ValidationError
import pytest


class TestSearchQueryModel:
    """測試 SearchQuery Pydantic 模型。"""

    def test_search_query_model_exists(self):
        """測試 SearchQuery 模型存在。"""
        from app.agent import SearchQuery

        assert SearchQuery is not None

    def test_search_query_creation(self):
        """測試 SearchQuery 模型能被建立。"""
        from app.agent import SearchQuery

        query = SearchQuery(search_query="test query")
        assert query is not None
        assert query.search_query == "test query"

    def test_search_query_has_required_field(self):
        """測試 SearchQuery 模型必要欄位。"""
        from app.agent import SearchQuery

        with pytest.raises(ValidationError):
            SearchQuery()

    def test_search_query_field_type(self):
        """測試 SearchQuery 模型欄位類型。"""
        from app.agent import SearchQuery

        query = SearchQuery(search_query="test query")
        assert isinstance(query.search_query, str)

    def test_search_query_model_schema(self):
        """測試 SearchQuery 模型 schema。"""
        from app.agent import SearchQuery

        schema = SearchQuery.model_json_schema()
        assert "search_query" in schema["properties"]
        assert schema["properties"]["search_query"]["type"] == "string"


class TestFeedbackModel:
    """測試 Feedback Pydantic 模型。"""

    def test_feedback_model_exists(self):
        """測試 Feedback 模型存在。"""
        from app.agent import Feedback

        assert Feedback is not None

    def test_feedback_creation_pass(self):
        """測試 Feedback 模型建立（grade=pass）。"""
        from app.agent import Feedback

        feedback = Feedback(grade="pass", comment="Good research")
        assert feedback is not None
        assert feedback.grade == "pass"
        assert feedback.comment == "Good research"
        assert feedback.follow_up_queries is None

    def test_feedback_creation_fail(self):
        """測試 Feedback 模型建立（grade=fail）。"""
        from app.agent import Feedback, SearchQuery

        queries = [SearchQuery(search_query="query 1")]
        feedback = Feedback(
            grade="fail", comment="Needs improvement", follow_up_queries=queries
        )
        assert feedback is not None
        assert feedback.grade == "fail"
        assert feedback.comment == "Needs improvement"
        assert len(feedback.follow_up_queries) == 1

    def test_feedback_grade_literal(self):
        """測試 Feedback grade 只接受 pass 或 fail。"""
        from app.agent import Feedback

        with pytest.raises(ValidationError):
            Feedback(grade="invalid", comment="test")

    def test_feedback_required_fields(self):
        """測試 Feedback 必要欄位。"""
        from app.agent import Feedback

        with pytest.raises(ValidationError):
            Feedback()

    def test_feedback_optional_follow_up_queries(self):
        """測試 follow_up_queries 是選填欄位。"""
        from app.agent import Feedback

        feedback = Feedback(grade="pass", comment="Good")
        assert feedback.follow_up_queries is None

    def test_feedback_with_multiple_queries(self):
        """測試 Feedback 包含多個 follow-up queries。"""
        from app.agent import Feedback, SearchQuery

        queries = [
            SearchQuery(search_query="query 1"),
            SearchQuery(search_query="query 2"),
            SearchQuery(search_query="query 3"),
        ]
        feedback = Feedback(
            grade="fail", comment="Needs more research", follow_up_queries=queries
        )
        assert len(feedback.follow_up_queries) == 3

    def test_feedback_model_schema(self):
        """測試 Feedback 模型 schema。"""
        from app.agent import Feedback

        schema = Feedback.model_json_schema()
        assert "grade" in schema["properties"]
        assert "comment" in schema["properties"]
        assert "follow_up_queries" in schema["properties"]

    def test_feedback_to_dict(self):
        """測試 Feedback 模型轉換為字典。"""
        from app.agent import Feedback

        feedback = Feedback(grade="pass", comment="Good research")
        data = feedback.model_dump()
        assert data["grade"] == "pass"
        assert data["comment"] == "Good research"
        assert data["follow_up_queries"] is None

    def test_feedback_from_dict(self):
        """測試從字典建立 Feedback 模型。"""
        from app.agent import Feedback

        data = {"grade": "pass", "comment": "Excellent work"}
        feedback = Feedback(**data)
        assert feedback.grade == "pass"
        assert feedback.comment == "Excellent work"


class TestModelIntegration:
    """測試模型整合。"""

    def test_feedback_with_search_query_integration(self):
        """測試 Feedback 與 SearchQuery 整合。"""
        from app.agent import Feedback, SearchQuery

        queries = [
            SearchQuery(search_query="What is AI?"),
            SearchQuery(search_query="History of machine learning"),
        ]
        feedback = Feedback(
            grade="fail", comment="Need more depth", follow_up_queries=queries
        )

        assert isinstance(feedback.follow_up_queries[0], SearchQuery)
        assert feedback.follow_up_queries[0].search_query == "What is AI?"

    def test_model_serialization(self):
        """測試模型序列化。"""
        from app.agent import Feedback, SearchQuery

        queries = [SearchQuery(search_query="test")]
        feedback = Feedback(
            grade="fail", comment="test comment", follow_up_queries=queries
        )

        json_str = feedback.model_dump_json()
        assert isinstance(json_str, str)
        assert "fail" in json_str
        assert "test comment" in json_str
