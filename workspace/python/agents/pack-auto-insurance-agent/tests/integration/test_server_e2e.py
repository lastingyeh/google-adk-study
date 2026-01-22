# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

# 配置日誌紀錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000/"
STREAM_URL = BASE_URL + "run_sse"
FEEDBACK_URL = BASE_URL + "feedback"

HEADERS = {"Content-Type": "application/json"}


def log_output(pipe: Any, log_func: Any) -> None:
    """紀錄來自給定管道的輸出。"""
    for line in iter(pipe.readline, ""):
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    """使用子進程啟動 FastAPI 伺服器並紀錄其輸出。"""
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "auto_insurance_agent.fast_api_app:app",
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

    # 啟動線程以實時紀錄標準輸出和標準錯誤
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
                logger.info("伺服器已就緒")
                return True
        except RequestException:
            pass
        time.sleep(interval)
    logger.error(f"伺服器未在 {timeout} 秒內就緒")
    return False


@pytest.fixture(scope="session")
def server_fixture(request: Any) -> Iterator[subprocess.Popen[str]]:
    """Pytest fixture 用於啟動和停止測試伺服器。"""
    logger.info("正在啟動伺服器進程")
    server_process = start_server()
    if not wait_for_server():
        pytest.fail("伺服器啟動失敗")
    logger.info("伺服器進程已啟動")

    def stop_server() -> None:
        logger.info("正在停止伺服器進程")
        server_process.terminate()
        server_process.wait()
        logger.info("伺服器進程已停止")

    request.addfinalizer(stop_server)
    yield server_process


def test_chat_stream(server_fixture: subprocess.Popen[str]) -> None:
    """
    測試聊天串流功能。
    測試重點：驗證透過 API 調用代理時，是否能正確處理會話並返回串流回應。
    """
    logger.info("開始聊天串流測試")

    # 先建立會話
    user_id = "test_user_123"
    session_data = {"state": {"preferred_language": "English", "visit_count": 1}}

    session_url = f"{BASE_URL}/apps/auto_insurance_agent/users/{user_id}/sessions"
    session_response = requests.post(
        session_url,
        headers=HEADERS,
        json=session_data,
        timeout=60,
    )
    assert session_response.status_code == 200
    logger.info(f"會話建立回應: {session_response.json()}")
    session_id = session_response.json()["id"]

    # 然後發送聊天訊息
    data = {
        "app_name": "auto_insurance_agent",
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": "Hi!"}],
        },
        "streaming": True,
    }

    response = requests.post(
        STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=60
    )
    assert response.status_code == 200
    # 從回應中解析 SSE 事件
    events = []
    for line in response.iter_lines():
        if line:
            # SSE 格式為 "data: {json}"
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                event_json = line_str[6:]  # 移除 "data: " 前綴
                event = json.loads(event_json)
                events.append(event)

    assert events, "未從串流接收到任何事件"
    # 檢查回應中是否有有效的內容
    has_text_content = False
    for event in events:
        content = event.get("content")
        if (
            content is not None
            and content.get("parts")
            and any(part.get("text") for part in content["parts"])
        ):
            has_text_content = True
            break


def test_chat_stream_error_handling(server_fixture: subprocess.Popen[str]) -> None:
    """
    測試聊天串流錯誤處理。
    測試重點：驗證當傳入無效數據時，伺服器是否正確返回 422 錯誤。
    """
    logger.info("開始聊天串流錯誤處理測試")
    data = {
        "input": {"messages": [{"type": "invalid_type", "content": "Cause an error"}]}
    }
    response = requests.post(
        STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=10
    )

    assert response.status_code == 422, f"期望狀態碼 422，但得到 {response.status_code}"
    logger.info("錯誤處理測試成功完成")


def test_collect_feedback(server_fixture: subprocess.Popen[str]) -> None:
    """
    測試反饋收集端點 (/feedback)。
    測試重點：確保伺服器能正確接收並紀錄收到的用戶反饋。
    """
    # 建立範例反饋數據
    feedback_data = {
        "score": 4,
        "user_id": "test-user-456",
        "session_id": "test-session-456",
        "text": "Great response!",
    }

    response = requests.post(
        FEEDBACK_URL, json=feedback_data, headers=HEADERS, timeout=10
    )
    assert response.status_code == 200
