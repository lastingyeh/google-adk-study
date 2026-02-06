"""
FastAPI 應用程式測試
"""


class TestFastAPIApp:
    """
    測試 FastAPI 應用基本配置。

    重點說明:
    1. 驗證 FastAPI 實例化
    2. 驗證應用元數據 (Title, Description)
    """

    def test_fastapi_app_exists(self):
        """
        測試 FastAPI app 是否存在。

        驗證點:
        1. app 物件不為 None
        """
        from rag.fast_api_app import app

        assert app is not None

    def test_app_is_fastapi_instance(self):
        """
        測試 app 是 FastAPI 實例。

        驗證點:
        1. app 是 FastAPI 類別的實例
        """
        from fastapi import FastAPI

        from rag.fast_api_app import app

        assert isinstance(app, FastAPI)

    def test_app_has_title(self):
        """測試 app 有標題。"""
        from rag.fast_api_app import app

        assert hasattr(app, "title")
        assert app.title == "pack-rag"

    def test_app_has_description(self):
        """測試 app 有描述。"""
        from rag.fast_api_app import app

        assert hasattr(app, "description")
        assert app.description is not None
        assert len(app.description) > 0


class TestFeedbackEndpoint:
    """測試回饋收集端點。"""

    def test_feedback_endpoint_exists(self):
        """測試回饋端點是否存在。"""
        from rag.fast_api_app import collect_feedback

        assert collect_feedback is not None
        assert callable(collect_feedback)

    def test_feedback_function_signature(self):
        """測試回饋函式簽名。"""
        from inspect import signature

        from rag.fast_api_app import collect_feedback

        sig = signature(collect_feedback)
        params = list(sig.parameters.keys())

        # 應該有 feedback 參數
        assert "feedback" in params

    def test_feedback_endpoint_in_routes(self):
        """測試回饋端點是否在路由中。"""
        from rag.fast_api_app import app

        # 檢查路由中是否包含 /feedback
        routes = [getattr(route, "path", "") for route in app.routes]
        assert "/feedback" in routes

    def test_feedback_endpoint_method(self):
        """測試回饋端點使用 POST 方法。"""
        from rag.fast_api_app import app

        # 找到 /feedback 路由
        feedback_route = None
        for route in app.routes:
            if getattr(route, "path", "") == "/feedback":
                feedback_route = route
                break

        assert feedback_route is not None
        # 檢查方法
        assert "POST" in getattr(feedback_route, "methods", [])


class TestAppConfiguration:
    """測試應用配置。"""

    def test_agent_directory_configuration(self):
        """測試 agent 目錄配置。"""
        from rag.fast_api_app import AGENT_DIR

        assert AGENT_DIR is not None
        assert isinstance(AGENT_DIR, str)
        assert len(AGENT_DIR) > 0

    def test_google_cloud_logging_initialized(self):
        """測試 Google Cloud Logging 已初始化。"""
        from rag.fast_api_app import logger, logging_client

        assert logging_client is not None
        assert logger is not None

    def test_telemetry_setup_called(self):
        """測試遙測設定已被呼叫。"""
        # 透過匯入 fast_api_app，setup_telemetry() 應已被執行
        import rag.fast_api_app

        # 如果沒有拋出異常，表示設定成功
        assert rag.fast_api_app is not None


class TestSessionConfiguration:
    """測試會話服務配置。"""

    def test_session_uri_configuration(self):
        """測試會話 URI 配置邏輯。"""
        import os

        # 測試環境變數的存在性
        db_pass = os.environ.get("DB_PASS")
        instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

        # 如果有完整的資料庫配置，應該建立 session_service_uri
        if instance_connection_name and db_pass:
            from rag.fast_api_app import session_service_uri

            assert session_service_uri is not None
            assert "postgresql+asyncpg://" in session_service_uri


class TestArtifactConfiguration:
    """測試構件服務配置。"""

    def test_artifact_uri_configuration(self):
        """測試構件 URI 配置邏輯。"""
        import os

        logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

        if logs_bucket_name:
            from rag.fast_api_app import artifact_service_uri

            assert artifact_service_uri is not None
            assert artifact_service_uri.startswith("gs://")
            assert logs_bucket_name in artifact_service_uri
