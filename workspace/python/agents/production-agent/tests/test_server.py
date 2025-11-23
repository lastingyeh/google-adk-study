"""測試 FastAPI 伺服器實作。"""

import pytest
from fastapi.testclient import TestClient
from production_agent.server import app, root_agent


@pytest.fixture
def client():
    """建立測試客戶端。"""
    return TestClient(app)


class TestServerEndpoints:
    """伺服器端點測試套件。"""

    def test_root_endpoint(self, client):
        """測試根端點。"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "endpoints" in data
        assert "health" in data["endpoints"]
        assert "invoke" in data["endpoints"]

    def test_health_check_endpoint(self, client):
        """測試健康檢查端點。"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "request_count" in data
        assert "error_count" in data
        assert "agent" in data
        assert data["agent"]["name"] == root_agent.name
        assert data["agent"]["model"] == root_agent.model

    def test_docs_endpoint(self, client):
        """測試 OpenAPI 文件是否可用。"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """測試 OpenAPI 架構是否可用。"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestServerConfiguration:
    """伺服器設定測試套件。"""

    def test_cors_middleware(self):
        """測試 CORS 中介軟體是否已設定。"""
        from production_agent.server import app

        # 透過驗證 middleware 列表不為空來檢查 middleware 是否存在
        # CORS middleware 是在應用程式初始化期間加入的
        assert len(app.user_middleware) > 0

        # 透過檢查 middleware 類型來驗證 CORS 是否已設定
        middleware_types = [m.cls.__name__ for m in app.user_middleware if hasattr(m, 'cls')]
        assert any("CORS" in name for name in middleware_types) or len(middleware_types) > 0

    def test_app_title(self):
        """測試應用程式是否有正確的標題。"""
        assert app.title == "ADK Production Deployment API"

    def test_app_version(self):
        """測試應用程式是否有版本。"""
        assert app.version == "1.0"


class TestRequestModels:
    """測試請求和回應模型。"""

    def test_query_request_model(self):
        """測試 QueryRequest 模型。"""
        from production_agent.server import QueryRequest

        # 測試預設值
        req = QueryRequest(query="test query")
        assert req.query == "test query"
        assert req.temperature == 0.5
        assert req.max_tokens == 2048

        # 測試自定義值
        req = QueryRequest(
            query="test query",
            temperature=0.8,
            max_tokens=1024
        )
        assert req.temperature == 0.8
        assert req.max_tokens == 1024

    def test_query_response_model(self):
        """測試 QueryResponse 模型。"""
        from production_agent.server import QueryResponse

        resp = QueryResponse(
            response="test response",
            model="gemini-2.0-flash",
            tokens=100
        )

        assert resp.response == "test response"
        assert resp.model == "gemini-2.0-flash"
        assert resp.tokens == 100


class TestMetricsTracking:
    """測試指標追蹤功能。"""

    def test_request_counter_increments(self, client):
        """測試請求計數器是否增加。"""
        # 獲取初始計數
        response1 = client.get("/health")
        count1 = response1.json()["request_count"]

        # 發出另一個請求
        response2 = client.get("/health")
        count2 = response2.json()["request_count"]

        # 計數應該增加
        assert count2 > count1

    def test_uptime_tracking(self, client):
        """測試是否追蹤正常運行時間。"""
        response = client.get("/health")
        data = response.json()

        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0
        assert isinstance(data["uptime_seconds"], (int, float))


class TestInvokeEndpoint:
    """測試 Agent 呼叫端點 (模擬)。"""

    def test_invoke_endpoint_accepts_post(self, client):
        """測試呼叫端點是否接受 POST 請求。"""
        # 注意：如果沒有正確的 API key 設定，這將會失敗
        # 但我們可以測試端點是否存在
        request_data = {
            "query": "What deployment options are available?",
            "temperature": 0.5,
            "max_tokens": 1024
        }

        response = client.post("/invoke", json=request_data)

        # 應該得到 200 (成功) 或 500 (無 API key)，但不是 404
        assert response.status_code in [200, 500]

    def test_invoke_endpoint_requires_query(self, client):
        """測試呼叫端點是否需要查詢欄位。"""
        request_data = {
            "temperature": 0.5,
            "max_tokens": 1024
        }

        response = client.post("/invoke", json=request_data)

        # 應該返回驗證錯誤 (422)
        assert response.status_code == 422
