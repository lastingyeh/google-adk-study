"""
Pydantic 模型測試
"""

import uuid

import pytest
from pydantic import ValidationError


class TestRequestModel:
    """
    測試 Request Pydantic 模型。

    重點說明:
    1. 驗證請求模型欄位驗證 (message, events)
    2. 驗證自動生成的欄位 (user_id, session_id)
    """

    def test_request_model_exists(self):
        """
        測試 Request 模型存在。

        驗證點:
        1. Request 類別可被匯入
        """
        from rag.app_utils.typing import Request

        assert Request is not None

    def test_request_creation_with_required_fields(self):
        """
        測試使用必要欄位建立 Request 模型。

        驗證點:
        1. 使用 message 和 events 初始化成功
        """
        from google.genai.types import Content, Part

        from rag.app_utils.typing import Request

        message = Content(parts=[Part(text="test message")])
        request = Request(message=message, events=[])

        assert request is not None
        assert request.message == message
        assert request.events == []

    def test_request_has_default_user_id(self):
        """測試 Request 模型自動產生 user_id。"""
        from google.genai.types import Content, Part

        from rag.app_utils.typing import Request

        message = Content(parts=[Part(text="test")])
        request = Request(message=message, events=[])

        assert hasattr(request, "user_id")
        assert request.user_id is not None
        # 驗證是否為有效的 UUID 字串
        try:
            uuid.UUID(request.user_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False
        assert is_valid_uuid, "user_id 應為有效的 UUID 字串"

    def test_request_has_default_session_id(self):
        """測試 Request 模型自動產生 session_id。"""
        from google.genai.types import Content, Part

        from rag.app_utils.typing import Request

        message = Content(parts=[Part(text="test")])
        request = Request(message=message, events=[])

        assert hasattr(request, "session_id")
        assert request.session_id is not None
        # 驗證是否為有效的 UUID 字串
        try:
            uuid.UUID(request.session_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False
        assert is_valid_uuid, "session_id 應為有效的 UUID 字串"

    def test_request_custom_user_id(self):
        """測試 Request 模型可自訂 user_id。"""
        from google.genai.types import Content, Part

        from rag.app_utils.typing import Request

        custom_user_id = "custom-user-123"
        message = Content(parts=[Part(text="test")])
        request = Request(message=message, events=[], user_id=custom_user_id)

        assert request.user_id == custom_user_id

    def test_request_custom_session_id(self):
        """測試 Request 模型可自訂 session_id。"""
        from google.genai.types import Content, Part

        from rag.app_utils.typing import Request

        custom_session_id = "custom-session-456"
        message = Content(parts=[Part(text="test")])
        request = Request(message=message, events=[], session_id=custom_session_id)

        assert request.session_id == custom_session_id

    def test_request_allows_extra_fields(self):
        """測試 Request 模型允許額外欄位。"""
        from google.genai.types import Content, Part

        from rag.app_utils.typing import Request

        message = Content(parts=[Part(text="test")])
        # 測試 model_config 是否允許額外欄位
        request = Request(message=message, events=[])
        request = Request(message=message, events=[])
        if isinstance(request.model_extra, dict):
            request.model_extra["extra_field"] = "extra_value"
            assert "extra_field" in request.model_extra
            assert request.model_extra["extra_field"] == "extra_value"
        else:
            assert False, "model_extra 應為 dict"

    def test_request_model_schema(self):
        """測試 Request 模型 schema。"""
        from rag.app_utils.typing import Request

        schema = Request.model_json_schema()
        assert "properties" in schema
        properties = schema["properties"]

        assert "message" in properties
        assert "events" in properties
        assert "user_id" in properties
        assert "session_id" in properties


class TestFeedbackModel:
    """測試 Feedback Pydantic 模型。"""

    def test_feedback_model_exists(self):
        """測試 Feedback 模型存在。"""
        from rag.app_utils.typing import Feedback

        assert Feedback is not None

    def test_feedback_creation_with_score(self):
        """測試使用評分建立 Feedback 模型。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=5)
        assert feedback is not None
        assert feedback.score == 5

    def test_feedback_score_accepts_int(self):
        """測試 Feedback 接受整數評分。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=10)
        assert isinstance(feedback.score, int)
        assert feedback.score == 10

    def test_feedback_score_accepts_float(self):
        """測試 Feedback 接受浮點數評分。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=4.5)
        assert isinstance(feedback.score, float)
        assert feedback.score == 4.5

    def test_feedback_has_default_text(self):
        """測試 Feedback 有預設的 text 欄位。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=5)
        assert hasattr(feedback, "text")
        assert feedback.text == ""

    def test_feedback_custom_text(self):
        """測試 Feedback 可自訂 text。"""
        from rag.app_utils.typing import Feedback

        custom_text = "Great answer!"
        feedback = Feedback(score=5, text=custom_text)
        assert feedback.text == custom_text

    def test_feedback_text_optional(self):
        """測試 Feedback text 為選填欄位。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=3, text=None)
        assert feedback.text is None

    def test_feedback_has_log_type(self):
        """測試 Feedback 有 log_type 欄位且預設為 'feedback'。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=5)
        assert hasattr(feedback, "log_type")
        assert feedback.log_type == "feedback"

    def test_feedback_has_service_name(self):
        """測試 Feedback 有 service_name 欄位且預設為 'pack-rag'。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=5)
        assert hasattr(feedback, "service_name")
        assert feedback.service_name == "pack-rag"

    def test_feedback_has_default_user_id(self):
        """測試 Feedback 自動產生 user_id。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=5)
        assert hasattr(feedback, "user_id")
        assert feedback.user_id is not None
        # 驗證是否為有效的 UUID 字串
        try:
            uuid.UUID(feedback.user_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False
        assert is_valid_uuid, "user_id 應為有效的 UUID 字串"

    def test_feedback_has_default_session_id(self):
        """測試 Feedback 自動產生 session_id。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=5)
        assert hasattr(feedback, "session_id")
        assert feedback.session_id is not None
        # 驗證是否為有效的 UUID 字串
        try:
            uuid.UUID(feedback.session_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False
        assert is_valid_uuid, "session_id 應為有效的 UUID 字串"

    def test_feedback_custom_user_id(self):
        """測試 Feedback 可自訂 user_id。"""
        from rag.app_utils.typing import Feedback

        custom_user_id = "user-789"
        feedback = Feedback(score=4, user_id=custom_user_id)
        assert feedback.user_id == custom_user_id

    def test_feedback_custom_session_id(self):
        """測試 Feedback 可自訂 session_id。"""
        from rag.app_utils.typing import Feedback

        custom_session_id = "session-789"
        feedback = Feedback(score=4, session_id=custom_session_id)
        assert feedback.session_id == custom_session_id

    def test_feedback_required_fields(self):
        """測試 Feedback 必要欄位。"""
        from rag.app_utils.typing import Feedback

        # score 是必要欄位
        with pytest.raises(ValidationError):
            Feedback(text="Good")  # type: ignore[call-arg]

    def test_feedback_model_dump(self):
        """測試 Feedback 模型可轉換為字典。"""
        from rag.app_utils.typing import Feedback

        feedback = Feedback(score=5, text="Good")
        data = feedback.model_dump()

        assert isinstance(data, dict)
        assert "score" in data
        assert "text" in data
        assert "log_type" in data
        assert "service_name" in data
        assert "user_id" in data
        assert "session_id" in data

    def test_feedback_model_schema(self):
        """測試 Feedback 模型 schema。"""
        from rag.app_utils.typing import Feedback

        schema = Feedback.model_json_schema()
        assert "properties" in schema
        properties = schema["properties"]

        assert "score" in properties
        assert "text" in properties
        assert "log_type" in properties
        assert "service_name" in properties
        assert "user_id" in properties
        assert "session_id" in properties
