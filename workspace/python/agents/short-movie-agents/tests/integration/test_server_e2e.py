"""
FastAPI 伺服器端對端測試

測試 FastAPI 伺服器的完整功能，包括啟動、響應和回饋收集。
"""

import json
import logging
import os
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from typing import Any

import pytest
import requests
from requests.exceptions import RequestException

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000/"
STREAM_URL = BASE_URL + "run_sse"
FEEDBACK_URL = BASE_URL + "feedback"

HEADERS = {"Content-Type": "application/json"}


def log_output(pipe: Any, log_func: Any) -> None:
    """記錄給定管道的輸出。"""
    for line in iter(pipe.readline, ""):
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    """使用 subprocess 啟動 FastAPI 伺服器並記錄其輸出。"""
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.server:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    env = os.environ.copy()
    env["INTEGRATION_TEST"] = "TRUE"
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    # 啟動執行緒以即時記錄 stdout 和 stderr
    threading.Thread(
        target=log_output, args=(process.stdout, logger.info), daemon=True
    ).start()
    threading.Thread(
        target=log_output, args=(process.stderr, logger.error), daemon=True
    ).start()

    return process


def wait_for_server(timeout: int = 90, interval: int = 1) -> bool:
    """等待伺服器就緒。"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://127.0.0.1:8000/docs", timeout=10)
            if response.status_code == 200:
                logger.info("Server is ready")
                return True
        except RequestException:
            pass
        time.sleep(interval)
    logger.error(f"Server did not become ready within {timeout} seconds")
    return False


@pytest.fixture(scope="session")
def server_fixture(request: Any) -> Iterator[subprocess.Popen[str]]:
    """Pytest fixture 用於在測試期間啟動和停止伺服器。"""
    logger.info("Starting server process")
    server_process = start_server()

    # 等待伺服器就緒
    if not wait_for_server():
        server_process.terminate()
        server_process.wait()
        pytest.fail("Server failed to start in time")

    yield server_process

    # 測試結束後清理
    logger.info("Stopping server process")
    server_process.terminate()
    try:
        server_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        logger.warning("Server did not terminate gracefully, killing process")
        server_process.kill()
        server_process.wait()


@pytest.mark.integration
class TestServerEndpoints:
    """測試伺服器端點。"""

    def test_server_health(self, server_fixture: subprocess.Popen[str]) -> None:
        """測試伺服器健康檢查端點。"""
        response = requests.get(f"{BASE_URL}docs", timeout=10)
        assert response.status_code == 200
        logger.info("Health check passed")

    def test_feedback_endpoint(self, server_fixture: subprocess.Popen[str]) -> None:
        """測試回饋端點。"""
        feedback_data = {
            "score": 5,
            "text": "Great response!",
            "invocation_id": "test-invocation-123",
            "user_id": "test-user-456",
        }

        response = requests.post(
            FEEDBACK_URL,
            headers=HEADERS,
            json=feedback_data,
            timeout=10,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        logger.info("Feedback endpoint test passed")

    def test_feedback_endpoint_minimal_data(
        self, server_fixture: subprocess.Popen[str]
    ) -> None:
        """測試回饋端點（最小資料）。"""
        feedback_data = {
            "score": 3,
            "invocation_id": "test-invocation-789",
        }

        response = requests.post(
            FEEDBACK_URL,
            headers=HEADERS,
            json=feedback_data,
            timeout=10,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        logger.info("Feedback endpoint minimal data test passed")


@pytest.mark.integration
@pytest.mark.slow
class TestServerStreamingEndpoints:
    """測試伺服器串流端點（需要較長執行時間）。"""

    @pytest.mark.skip(reason="需要實際的 API 金鑰和足夠的配額")
    def test_streaming_endpoint(self, server_fixture: subprocess.Popen[str]) -> None:
        """測試串流端點（跳過 - 需要實際 API）。"""
        # 此測試需要真實的 Google Cloud 配置
        # 在實際環境中，取消註解並配置正確的請求資料

        request_data = {
            "message": {
                "role": "user",
                "parts": [{"text": "Create a very short story."}],
            },
            "events": [],
        }

        response = requests.post(
            STREAM_URL,
            headers=HEADERS,
            json=request_data,
            stream=True,
            timeout=60,
        )

        assert response.status_code == 200
        logger.info("Streaming endpoint test passed")


@pytest.mark.integration
class TestServerConfiguration:
    """測試伺服器配置。"""

    def test_server_title(self, server_fixture: subprocess.Popen[str]) -> None:
        """測試伺服器標題配置。"""
        response = requests.get(f"{BASE_URL}openapi.json", timeout=10)
        assert response.status_code == 200

        openapi_spec = response.json()
        assert "info" in openapi_spec
        assert "title" in openapi_spec["info"]
        assert "短片生成代理" in openapi_spec["info"]["title"]
        logger.info("Server title configuration test passed")

    def test_server_description(self, server_fixture: subprocess.Popen[str]) -> None:
        """測試伺服器描述配置。"""
        response = requests.get(f"{BASE_URL}openapi.json", timeout=10)
        assert response.status_code == 200

        openapi_spec = response.json()
        assert "info" in openapi_spec
        assert "description" in openapi_spec["info"]
        assert len(openapi_spec["info"]["description"]) > 0
        logger.info("Server description configuration test passed")
