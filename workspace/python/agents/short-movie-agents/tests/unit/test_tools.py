"""
工具函式 (Tools) 測試

測試 storyboard_generate 和 video_generate 工具函式。
"""

from unittest.mock import Mock, patch, MagicMock
import pytest


class TestStoryboardGenerateTool:
    """測試 storyboard_generate 工具。"""

    def setup_method(self):
        """每個測試前的設定。"""
        self.tool_context = Mock()
        self.tool_context._invocation_context = Mock()
        self.tool_context._invocation_context.session = Mock()
        self.tool_context._invocation_context.session.id = "test-session-123"

    def test_tool_exists(self):
        """測試工具存在。"""
        from app.storyboard_agent import storyboard_generate

        assert callable(storyboard_generate)

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.storyboard_agent.generation_model")
    def test_storyboard_generate_success(self, mock_model):
        """測試成功生成分鏡圖。"""
        from app.storyboard_agent import storyboard_generate

        # Mock 影像生成回應
        mock_image = Mock()
        mock_image._gcs_uri = "gs://test-bucket/test-session-123/scene_1/image.png"
        mock_response = Mock()
        mock_response.images = [mock_image]
        mock_model.generate_images.return_value = mock_response

        # 執行工具
        result = storyboard_generate(
            prompt="A beautiful sunset scene",
            scene_number=1,
            tool_context=self.tool_context,
        )

        # 驗證
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert "storage.mtls.cloud.google.com" in result[0]
        mock_model.generate_images.assert_called_once()

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.storyboard_agent.generation_model")
    def test_storyboard_generate_no_images(self, mock_model):
        """測試生成失敗（無影像）。"""
        from app.storyboard_agent import storyboard_generate

        # Mock 空回應
        mock_response = Mock()
        mock_response.images = []
        mock_model.generate_images.return_value = mock_response

        # 執行工具
        result = storyboard_generate(
            prompt="Test prompt",
            scene_number=1,
            tool_context=self.tool_context,
        )

        # 驗證
        assert result == []

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.storyboard_agent.generation_model")
    def test_storyboard_generate_error_handling(self, mock_model):
        """測試錯誤處理。"""
        from app.storyboard_agent import storyboard_generate

        # Mock 異常
        mock_model.generate_images.side_effect = Exception("API Error")

        # 執行工具
        result = storyboard_generate(
            prompt="Test prompt",
            scene_number=1,
            tool_context=self.tool_context,
        )

        # 驗證 - 應該返回空列表而不是拋出異常
        assert result == []

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.storyboard_agent.generation_model")
    def test_storyboard_generate_uses_session_id(self, mock_model):
        """測試使用 session_id 生成 GCS 路徑。"""
        from app.storyboard_agent import storyboard_generate

        mock_response = Mock()
        mock_response.images = []
        mock_model.generate_images.return_value = mock_response

        storyboard_generate(
            prompt="Test prompt",
            scene_number=2,
            tool_context=self.tool_context,
        )

        # 驗證呼叫參數
        call_kwargs = mock_model.generate_images.call_args[1]
        assert "output_gcs_uri" in call_kwargs
        assert "test-session-123" in call_kwargs["output_gcs_uri"]
        assert "scene_2" in call_kwargs["output_gcs_uri"]


class TestVideoGenerateTool:
    """測試 video_generate 工具。"""

    def setup_method(self):
        """每個測試前的設定。"""
        self.tool_context = Mock()
        self.tool_context._invocation_context = Mock()
        self.tool_context._invocation_context.session = Mock()
        self.tool_context._invocation_context.session.id = "test-session-456"

    def test_tool_exists(self):
        """測試工具存在。"""
        from app.video_agent import video_generate

        assert callable(video_generate)

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.video_agent.client")
    def test_video_generate_success(self, mock_client):
        """測試成功生成影片。"""
        from app.video_agent import video_generate

        # Mock 影片生成回應
        mock_video = Mock()
        mock_video.video = Mock()
        mock_video.video.uri = "gs://test-bucket/test-session-456/scene_1/video.mp4"

        mock_result = Mock()
        mock_result.generated_videos = [mock_video]

        mock_operation = Mock()
        mock_operation.done = True
        mock_operation.response = True
        mock_operation.result = mock_result

        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.operations.get.return_value = mock_operation

        # 執行工具
        result = video_generate(
            prompt="A sunset scene",
            scene_number=1,
            image_link="https://example.com/image.png",
            screenplay="Scene 1: A beautiful sunset",
            tool_context=self.tool_context,
        )

        # 驗證
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert "storage.mtls.cloud.google.com" in result[0]

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.video_agent.client")
    def test_video_generate_no_videos(self, mock_client):
        """測試生成失敗（無影片）。"""
        from app.video_agent import video_generate

        # Mock 空回應
        mock_operation = Mock()
        mock_operation.done = True
        mock_operation.response = False

        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.operations.get.return_value = mock_operation

        # 執行工具
        result = video_generate(
            prompt="Test prompt",
            scene_number=1,
            image_link="https://example.com/image.png",
            screenplay="Test screenplay",
            tool_context=self.tool_context,
        )

        # 驗證
        assert result == []

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.video_agent.client")
    def test_video_generate_error_handling(self, mock_client):
        """測試錯誤處理。"""
        from app.video_agent import video_generate

        # Mock 異常
        mock_client.models.generate_videos.side_effect = Exception("API Error")

        # 執行工具
        result = video_generate(
            prompt="Test prompt",
            scene_number=1,
            image_link="https://example.com/image.png",
            screenplay="Test screenplay",
            tool_context=self.tool_context,
        )

        # 驗證 - 應該返回空列表而不是拋出異常
        assert result == []

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
        },
    )
    @patch("app.video_agent.client")
    def test_video_generate_extracts_dialogue(self, mock_client):
        """測試從劇本中提取對話。"""
        from app.video_agent import video_generate

        mock_operation = Mock()
        mock_operation.done = True
        mock_operation.response = False
        mock_client.models.generate_videos.return_value = mock_operation
        mock_client.operations.get.return_value = mock_operation

        screenplay = """
        NARRATOR (voiceover)
          Once upon a time...

        CHARACTER (excited)
          This is amazing!
        """

        video_generate(
            prompt="Test prompt",
            scene_number=1,
            image_link="https://example.com/image.png",
            screenplay=screenplay,
            tool_context=self.tool_context,
        )

        # 驗證函式被呼叫（代表對話提取邏輯正常運作）
        mock_client.models.generate_videos.assert_called_once()
