"""
Pydantic 模型測試

測試所有 Pydantic 模型的結構與驗證邏輯。
"""

from pydantic import ValidationError
import pytest
import uuid


class TestRequestModel:
    """測試 Request Pydantic 模型。"""

    def test_request_model_exists(self):
        """測試 Request 模型存在。"""
        from app.utils.typing import Request

        assert Request is not None

    def test_request_creation_with_all_fields(self):
        """測試 Request 模型能被建立（包含所有欄位）。"""
        from app.utils.typing import Request
        from google.genai.types import Content
        from google.adk.events.event import Event

        content = Content(role="user", parts=[])
        events = []
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        request = Request(
            message=content,
            events=events,
            user_id=user_id,
            session_id=session_id,
        )

        assert request is not None
        assert request.message == content
        assert request.events == events
        assert request.user_id == user_id
        assert request.session_id == session_id

    def test_request_creation_with_default_ids(self):
        """測試 Request 模型使用預設 ID。"""
        from app.utils.typing import Request
        from google.genai.types import Content

        content = Content(role="user", parts=[])
        events = []

        request = Request(message=content, events=events)

        assert request is not None
        assert request.user_id is not None
        assert request.session_id is not None
        # 檢查是否為有效的 UUID 字串
        assert len(request.user_id) > 0
        assert len(request.session_id) > 0

    def test_request_has_required_fields(self):
        """測試 Request 模型必要欄位。"""
        from app.utils.typing import Request

        with pytest.raises(ValidationError):
            Request()

    def test_request_field_types(self):
        """測試 Request 模型欄位類型。"""
        from app.utils.typing import Request
        from google.genai.types import Content

        content = Content(role="user", parts=[])
        events = []

        request = Request(message=content, events=events)

        assert isinstance(request.user_id, str)
        assert isinstance(request.session_id, str)
        assert isinstance(request.events, list)


class TestFeedbackModel:
    """測試 Feedback Pydantic 模型。"""

    def test_feedback_model_exists(self):
        """測試 Feedback 模型存在。"""
        from app.utils.typing import Feedback

        assert Feedback is not None

    def test_feedback_creation_with_score(self):
        """測試 Feedback 模型建立（整數評分）。"""
        from app.utils.typing import Feedback

        feedback = Feedback(
            score=5,
            text="Great result",
            invocation_id="test-invocation-123",
            user_id="user-123",
        )

        assert feedback is not None
        assert feedback.score == 5
        assert feedback.text == "Great result"
        assert feedback.invocation_id == "test-invocation-123"
        assert feedback.user_id == "user-123"

    def test_feedback_creation_with_float_score(self):
        """測試 Feedback 模型建立（浮點數評分）。"""
        from app.utils.typing import Feedback

        feedback = Feedback(
            score=4.5,
            text="Good result",
            invocation_id="test-invocation-456",
        )

        assert feedback is not None
        assert feedback.score == 4.5
        assert isinstance(feedback.score, float)

    def test_feedback_optional_text(self):
        """測試 text 是選填欄位。"""
        from app.utils.typing import Feedback

        feedback = Feedback(
            score=3,
            invocation_id="test-invocation-789",
        )

        assert feedback.text == ""

    def test_feedback_default_log_type(self):
        """測試 log_type 預設值。"""
        from app.utils.typing import Feedback

        feedback = Feedback(
            score=5,
            invocation_id="test-invocation-123",
        )

        assert feedback.log_type == "feedback"

    def test_feedback_default_service_name(self):
        """測試 service_name 預設值。"""
        from app.utils.typing import Feedback

        feedback = Feedback(
            score=5,
            invocation_id="test-invocation-123",
        )

        assert feedback.service_name == "test-agent"

    def test_feedback_required_fields(self):
        """測試 Feedback 必要欄位。"""
        from app.utils.typing import Feedback

        with pytest.raises(ValidationError):
            Feedback()

    def test_feedback_model_dump(self):
        """測試 Feedback 模型 dump。"""
        from app.utils.typing import Feedback

        feedback = Feedback(
            score=5,
            text="Test",
            invocation_id="test-123",
            user_id="user-456",
        )

        data = feedback.model_dump()

        assert isinstance(data, dict)
        assert "score" in data
        assert "text" in data
        assert "invocation_id" in data
        assert "log_type" in data
        assert "service_name" in data
        assert "user_id" in data
