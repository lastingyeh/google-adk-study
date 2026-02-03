"""
Pydantic 模型測試

測試 pack-bidi-streaming 專案的 Pydantic 模型。
"""

import pytest
from pydantic import ValidationError


class TestFeedbackModel:
    """測試 Feedback Pydantic 模型。"""

    def test_feedback_model_exists(self):
        """測試 Feedback 模型存在。"""
        from bidi_demo.app_utils.typing import Feedback

        assert Feedback is not None

    def test_feedback_creation_with_required_fields(self):
        """測試 Feedback 模型建立（必要欄位）。"""
        from bidi_demo.app_utils.typing import Feedback

        feedback = Feedback(score=5, text="Good response")
        assert feedback is not None
        assert feedback.score == 5
        assert feedback.text == "Good response"
        assert feedback.log_type == "feedback"

    def test_feedback_creation_with_all_fields(self):
        """測試 Feedback 模型建立（所有欄位）。"""
        from bidi_demo.app_utils.typing import Feedback

        feedback = Feedback(
            score=4,
            text="Helpful",
            log_type="feedback",
            service_name="pack-bidi-streaming",
            user_id="user123",
            session_id="session456",
        )
        assert feedback is not None
        assert feedback.score == 4
        assert feedback.text == "Helpful"
        assert feedback.log_type == "feedback"
        assert feedback.service_name == "pack-bidi-streaming"
        assert feedback.user_id == "user123"
        assert feedback.session_id == "session456"

    def test_feedback_score_accepts_int(self):
        """測試 Feedback score 接受整數。"""
        from bidi_demo.app_utils.typing import Feedback

        feedback = Feedback(score=3, text="Okay")
        assert isinstance(feedback.score, int)
        assert feedback.score == 3

    def test_feedback_score_accepts_float(self):
        """測試 Feedback score 接受浮點數。"""
        from bidi_demo.app_utils.typing import Feedback

        feedback = Feedback(score=3.5, text="Good")
        assert isinstance(feedback.score, (int, float))
        assert feedback.score == 3.5

    def test_feedback_required_fields(self):
        """測試 Feedback 必要欄位。"""
        from bidi_demo.app_utils.typing import Feedback

        # score 是必要欄位
        with pytest.raises(ValidationError):
            Feedback(text="test")  # type: ignore

    def test_feedback_user_id_default_generation(self):
        """測試 user_id 預設會自動產生。"""
        from bidi_demo.app_utils.typing import Feedback

        feedback = Feedback(score=5, text="Great")
        assert feedback.user_id is not None
        assert isinstance(feedback.user_id, str)
        assert len(feedback.user_id) > 0

    def test_feedback_session_id_default_generation(self):
        """測試 session_id 預設會自動產生。"""
        from bidi_demo.app_utils.typing import Feedback

        feedback = Feedback(score=5, text="Great")
        assert feedback.session_id is not None
        assert isinstance(feedback.session_id, str)
        assert len(feedback.session_id) > 0

    def test_feedback_log_type_literal(self):
        """測試 Feedback log_type 欄位的型別。"""
        from bidi_demo.app_utils.typing import Feedback

        feedback = Feedback(score=5, text="Test")
        assert isinstance(feedback.log_type, str)
        assert feedback.log_type == "feedback"


class TestRequestModel:
    """測試 Request Pydantic 模型。"""

    def test_request_model_exists(self):
        """測試 Request 模型存在。"""
        from bidi_demo.app_utils.typing import Request

        assert Request is not None

    def test_request_creation_with_required_fields(self):
        """測試 Request 模型建立（必要欄位）。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Hello"}])
        request = Request(message=message, events=[])
        assert request is not None
        assert request.message == message
        assert request.events == []

    def test_request_message_field(self):
        """測試 Request message 欄位型別。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Test message"}])
        request = Request(message=message, events=[])
        assert isinstance(request.message, Content)

    def test_request_events_field(self):
        """測試 Request events 欄位型別。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Test"}])
        request = Request(message=message, events=[])
        assert isinstance(request.events, list)

    def test_request_user_id_default_generation(self):
        """測試 user_id 預設會自動產生。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Test"}])
        request = Request(message=message, events=[])
        assert request.user_id is not None
        assert isinstance(request.user_id, str)
        assert len(request.user_id) > 0

    def test_request_session_id_default_generation(self):
        """測試 session_id 預設會自動產生。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Test"}])
        request = Request(message=message, events=[])
        assert request.session_id is not None
        assert isinstance(request.session_id, str)
        assert len(request.session_id) > 0

    def test_request_user_and_session_ids_are_unique(self):
        """測試不同 Request 實例的 user_id 和 session_id 是唯一的。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Test"}])
        request1 = Request(message=message, events=[])
        request2 = Request(message=message, events=[])

        assert request1.user_id != request2.user_id
        assert request1.session_id != request2.session_id

    def test_request_custom_user_and_session_ids(self):
        """測試 Request 可以設定自訂的 user_id 和 session_id。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Test"}])
        request = Request(
            message=message,
            events=[],
            user_id="custom_user",
            session_id="custom_session",
        )
        assert request.user_id == "custom_user"
        assert request.session_id == "custom_session"

    def test_request_extra_fields_allowed(self):
        """測試 Request 模型允許額外欄位。"""
        from google.genai.types import Content

        from bidi_demo.app_utils.typing import Request

        message = Content(parts=[{"text": "Test"}])
        # extra="allow" 應該允許額外欄位
        request = Request(message=message, events=[], custom_field="custom_value")  # type: ignore
        assert request.custom_field == "custom_value"
