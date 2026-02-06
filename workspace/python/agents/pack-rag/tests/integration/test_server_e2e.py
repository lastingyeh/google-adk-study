# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# 檔案：test_server_e2e.py
# 說明：此檔案包含 RAG (Retrieval-Augmented Generation) 應用程式 FastAPI 伺服器的端對端整合測試。
#      這些測試會啟動一個真實的伺服器實例，並透過 HTTP 請求與其 API 端點進行互動，
#      以驗證聊天串流、錯誤處理和回饋收集等核心功能的正確性。

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

# --- 日誌設定 (Logging Configuration) ---
# 設定日誌記錄器，以便在測試執行期間輸出詳細資訊。
# 這有助於調試和追蹤測試流程。
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- API 端點與標頭 (API Endpoints and Headers) ---
# 定義測試中將使用的 API 端點 URL 和 HTTP 標頭。
BASE_URL = "http://127.0.0.1:8000/"  # 伺服器基礎 URL
STREAM_URL = BASE_URL + "run_sse"  # Server-Sent Events (SSE) 串流端點
FEEDBACK_URL = BASE_URL + "feedback"  # 回饋收集端點

HEADERS = {"Content-Type": "application/json"}  # 設定請求內容類型為 JSON


def log_output(pipe: Any, log_func: Any) -> None:
    """
    從給定的管道 (pipe) 讀取輸出並使用指定的日誌函式記錄下來。
    此函式用於即時捕獲子程序的標準輸出 (stdout) 和標準錯誤 (stderr)。

    Args:
        pipe: 子程序的輸出管道 (例如 process.stdout)。
        log_func: 用於記錄的函式 (例如 logger.info 或 logger.error)。
    """
    # 使用 iter 迭代管道的每一行，直到管道關閉
    for line in iter(pipe.readline, ""):
        # 去除行尾的空白字元並記錄
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    """
    使用 subprocess 啟動 FastAPI 伺服器，並記錄其輸出。
    這會模擬應用程式在真實環境中的啟動過程。

    Returns:
        一個 subprocess.Popen 物件，代表正在運行的伺服器子程序。
    """
    # 定義啟動 uvicorn 伺服器的命令
    # sys.executable確保我們使用與執行 pytest 相同的 Python 解譯器
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "rag.fast_api_app:app",  # 指向 FastAPI 應用程式實例
        "--host",
        "0.0.0.0",  # 監聽所有網路介面
        "--port",
        "8000",  # 使用 8000 連接埠
    ]
    # 複製當前環境變數，並添加一個用於整合測試的標誌
    env = os.environ.copy()
    env["INTEGRATION_TEST"] = "TRUE"  # 讓應用程式知道它在測試模式下運行

    # 啟動子程序
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,  # 捕獲標準輸出
        stderr=subprocess.PIPE,  # 捕獲標準錯誤
        text=True,  # 以文字模式處理輸出
        bufsize=1,  # 設定行緩衝，以便即時讀取輸出
        env=env,
    )

    # 建立並啟動執行緒來即時記錄伺服器的 stdout 和 stderr
    # 這對於調試伺服器啟動問題非常有用
    # 使用 daemon=True 確保主執行緒結束時，這些日誌執行緒也會被終止
    threading.Thread(
        target=log_output, args=(process.stdout, logger.info), daemon=True
    ).start()
    threading.Thread(
        target=log_output, args=(process.stderr, logger.error), daemon=True
    ).start()

    return process


def wait_for_server(timeout: int = 90, interval: int = 1) -> bool:
    """
    等待伺服器準備就緒，直到可以接受請求。
    此函式會定期向伺服器的 /docs 端點發送請求，直到成功或超時。

    Args:
        timeout: 等待的總秒數 (預設 90 秒)。
        interval: 每次重試之間的間隔秒數 (預設 1 秒)。

    Returns:
        如果伺服器在超時時間內準備就緒，則返回 True，否則返回 False。
    """
    logger.info(f"等待伺服器啟動... (超時: {timeout} 秒)")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 嘗試向 FastAPI 自動生成的 /docs 端點發送 GET 請求
            # 這是檢查伺服器是否已啟動並能回應的可靠方法
            response = requests.get("http://127.0.0.1:8000/docs", timeout=10)
            if response.status_code == 200:
                logger.info("伺服器已準備就緒！")
                return True
        except RequestException:
            # 如果請求失敗 (例如，連線被拒絕)，則忽略並在短暫延遲後重試
            pass
        time.sleep(interval)

    logger.error(f"伺服器在 {timeout} 秒內未能準備就緒。")
    return False


@pytest.fixture(scope="session")
def server_fixture(request: Any) -> Iterator[subprocess.Popen[str]]:
    """
    一個 Pytest fixture，用於在整個測試會話 (session) 期間啟動和停止伺服器。
    `scope="session"` 表示此 fixture 只會執行一次，所有測試共享同一個伺服器實例，
    這樣可以節省啟動和關閉伺服器的時間。

    Args:
        request: Pytest 的內建 fixture，用於註冊清理函式。

    Yields:
        代表伺服器子程序的 Popen 物件。
    """
    logger.info("正在啟動伺服器程序...")
    server_process = start_server()

    # 等待伺服器完全啟動
    if not wait_for_server():
        # 如果伺服器啟動失敗，則終止測試會話
        pytest.fail("伺服器啟動失敗。")
    logger.info("伺服器程序已成功啟動。")

    # 定義一個在測試會話結束時執行的清理函式
    def stop_server() -> None:
        logger.info("正在停止伺服器程序...")
        server_process.terminate()  # 發送終止信號
        server_process.wait()  # 等待程序完全關閉
        logger.info("伺服器程序已停止。")

    # 使用 request.addfinalizer 註冊清理函式
    request.addfinalizer(stop_server)

    # 使用 yield 將伺服器程序物件提供給測試函式
    yield server_process


def test_chat_stream(server_fixture: subprocess.Popen[str]) -> None:
    """
    測試聊天串流功能 (/run_sse)。

    此測試驗證以下流程：
    1. 建立一個新的使用者會話 (session)。
    2. 使用該會話 ID 發送一條聊天訊息。
    3. 接收並解析來自伺服器的 Server-Sent Events (SSE) 串流。
    4. 驗證串流中是否包含有效的事件和文字內容。
    """
    logger.info("--- 開始聊天串流功能測試 ---")

    # 步驟 1: 建立會話
    user_id = "test_user_123"
    session_data = {"state": {"preferred_language": "English", "visit_count": 1}}

    session_url = f"{BASE_URL}/apps/rag/users/{user_id}/sessions"
    logger.info(f"向 {session_url} 發送 POST 請求以建立會話...")
    session_response = requests.post(
        session_url,
        headers=HEADERS,
        json=session_data,
        timeout=60,
    )
    assert session_response.status_code == 200, "建立會話失敗"
    session_info = session_response.json()
    logger.info(f"會話建立成功，回應: {session_info}")
    session_id = session_info["id"]

    # 步驟 2: 發送聊天訊息並請求串流回覆
    data = {
        "app_name": "rag",
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": "Hi!"}],
        },
        "streaming": True,  # 關鍵：啟用串流模式
    }

    logger.info(f"向 {STREAM_URL} 發送 POST 請求以開始聊天串流...")
    response = requests.post(
        STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=60
    )
    assert response.status_code == 200, "請求聊天串流失敗"

    # 步驟 3: 解析 SSE 事件
    events = []
    logger.info("正在從回應中解析 SSE 事件...")
    for line in response.iter_lines():
        if line:
            # SSE 事件的格式為 "data: {json}"
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                # 移除 "data: " 前綴並解析 JSON
                event_json = line_str[6:]
                try:
                    event = json.loads(event_json)
                    events.append(event)
                    logger.debug(f"收到事件: {event}")
                except json.JSONDecodeError:
                    logger.warning(f"無法解析的 JSON 事件: {event_json}")

    # 步驟 4: 驗證結果
    assert events, "從串流中未收到任何事件"
    logger.info(f"共收到 {len(events)} 個事件。")

    # 檢查回應中是否至少有一個事件包含文字內容
    has_text_content = False
    for event in events:
        content = event.get("content")
        if (
            content is not None
            and content.get("parts")
            and any(part.get("text") for part in content["parts"])
        ):
            has_text_content = True
            logger.info(f"在事件中找到文字內容: {content['parts']}")
            break

    assert has_text_content, "串流回應中未找到任何有效的文字內容"
    logger.info("--- 聊天串流功能測試成功 ---")


def test_chat_stream_error_handling(server_fixture: subprocess.Popen[str]) -> None:
    """
    測試聊天串流的錯誤處理能力。

    此測試驗證當向 /run_sse 端點發送無效的輸入資料時，
    伺服器是否能正確回傳 HTTP 422 Unprocessable Entity 錯誤。
    """
    logger.info("--- 開始聊天串流錯誤處理測試 ---")
    # 準備一個無效的請求資料結構
    data = {
        "input": {"messages": [{"type": "invalid_type", "content": "Cause an error"}]}
    }
    logger.info(f"向 {STREAM_URL} 發送無效資料以觸發錯誤...")
    response = requests.post(
        STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=10
    )

    # 驗證狀態碼是否為 422
    assert response.status_code == 422, (
        f"預期狀態碼為 422，但收到 {response.status_code}"
    )
    logger.info("伺服器已正確回傳 422 錯誤碼。")
    logger.info("--- 聊天串流錯誤處理測試成功 ---")


def test_collect_feedback(server_fixture: subprocess.Popen[str]) -> None:
    """
    測試回饋收集端點 (/feedback) 以確保其能正確接收並處理回饋資料。

    此測試驗證以下流程：
    1. 準備一筆範例回饋資料。
    2. 向 /feedback 端點發送 POST 請求。
    3. 驗證伺服器是否回傳 HTTP 200 OK 狀態碼，表示已成功接收。
    """
    logger.info("--- 開始回饋收集功能測試 ---")
    # 準備範例回饋資料
    feedback_data = {
        "score": 4,
        "user_id": "test-user-456",
        "session_id": "test-session-456",
        "text": "Great response!",
    }
    logger.info(f"向 {FEEDBACK_URL} 發送 POST 請求以提交回饋: {feedback_data}")

    response = requests.post(
        FEEDBACK_URL, json=feedback_data, headers=HEADERS, timeout=10
    )

    # 驗證回應狀態碼是否為 200
    assert response.status_code == 200, (
        f"預期狀態碼為 200，但收到 {response.status_code}"
    )
    logger.info("伺服器已成功接收回饋。")
    logger.info("--- 回饋收集功能測試成功 ---")
