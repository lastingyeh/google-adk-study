# 匯入必要的標準函式庫與第三方函式庫
import asyncio  # 用於非同步 I/O 操作，特別是 WebSocket 通訊
import json  # 用於處理 JSON 格式的資料
import logging  # 用於記錄應用程式事件
import subprocess  # 用於建立和管理子程序，如此處的伺服器
import sys  # 用於存取系統相關參數，如此處的 Python 解譯器路徑
import threading  # 用於並行執行任務，如此處的日誌輸出
import time  # 用於時間相關操作，如等待和超時
from collections.abc import Iterator  # 用於類型提示，表示一個迭代器
from typing import Any  # 用於類型提示，表示任何類型

import pytest  # 用於撰寫和執行測試的框架
import requests  # 用於發送 HTTP 請求，以檢查伺服器狀態
from websockets.asyncio.client import connect  # 用於非同步地連接 WebSocket 伺服器

# --- 全域設定 ---

# 設定日誌記錄
# 設定日誌的基本組態，將日誌級別設為 DEBUG，這樣所有級別的日誌都會被顯示
logging.basicConfig(level=logging.DEBUG)
# 獲取一個名為 __name__ (即目前模組名稱) 的 logger 實例
logger = logging.getLogger(__name__)

# 定義 WebSocket 和 HTTP 端點的 URL
WS_URL = "ws://127.0.0.1:8000/ws"  # WebSocket 連接的 URL
FEEDBACK_URL = "http://127.0.0.1:8000/feedback"  # 提交回饋的 HTTP POST 端點 URL


# --- 輔助函式 ---


def log_output(pipe: Any, log_func: Any) -> None:
    """從給定的管道 (pipe) 讀取輸出並記錄下來。

    Args:
        pipe: 子程序的標準輸出 (stdout) 或標準錯誤 (stderr) 管道。
        log_func: 用於記錄訊息的函式 (例如 logger.info 或 logger.error)。
    """
    # 使用 iter 函式持續從管道讀取每一行，直到讀到空字串 (表示管道已關閉)
    for line in iter(pipe.readline, ""):
        # 去除行尾的空白字元並使用指定的日誌函式記錄下來
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    """以本地模式啟動 uvicorn 伺服器。

    Returns:
        一個 subprocess.Popen 物件，代表正在執行的伺服器子程序。
    """
    # 定義啟動伺服器的命令
    # 使用 'sys.executable' 確保用的是目前 Python 環境的解譯器
    # '-m uvicorn' 表示以模組方式執行 uvicorn
    # 'app.fast_api_app:app' 是 uvicorn 要運行的 FastAPI 應用實例
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.fast_api_app:app",
        "--host",
        "0.0.0.0",  # 監聽所有網路介面
        "--port",
        "8000",  # 監聽 8000 埠
    ]
    # 使用 subprocess.Popen 啟動伺服器子程序
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,  # 捕獲標準輸出
        stderr=subprocess.PIPE,  # 捕獲標準錯誤
        text=True,  # 以文字模式處理輸出 (解碼為字串)
        bufsize=1,  # 設定行緩衝，確保即時讀取輸出
        encoding="utf-8",  # 指定編碼
    )

    # 建立並啟動執行緒以即時記錄伺服器的 stdout 和 stderr
    # 這可以避免主執行緒被 I/O 操作阻塞
    # daemon=True 確保主執行緒結束時，這些日誌執行緒也會被終止
    threading.Thread(
        target=log_output, args=(process.stdout, logger.info), daemon=True
    ).start()
    threading.Thread(
        target=log_output, args=(process.stderr, logger.error), daemon=True
    ).start()

    return process


def wait_for_server(timeout: int = 60, interval: int = 1) -> bool:
    """等待伺服器準備就緒。

    此函式會定期向伺服器的 /docs 端點發送 GET 請求，直到成功或超時。

    Args:
        timeout: 等待的總秒數。
        interval: 每次嘗試之間的間隔秒數。

    Returns:
        如果伺服器在超時前準備就緒，則返回 True，否則返回 False。
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 嘗試向 FastAPI 自動產生的文件頁面發送請求
            response = requests.get("http://127.0.0.1:8000/docs", timeout=10)
            # 如果狀態碼為 200 OK，表示伺服器已成功啟動並可接受請求
            if response.status_code == 200:
                logger.info("伺服器已準備就緒")
                return True
        except Exception:
            # 如果發生任何異常 (如連接錯誤)，則忽略並在稍後重試
            pass
        # 等待指定的間隔時間
        time.sleep(interval)
    logger.error(f"伺服器在 {timeout} 秒內未能準備就緒")
    return False


# --- Pytest Fixtures ---


@pytest.fixture(scope="module")
def server_fixture(request: Any) -> Iterator[subprocess.Popen[str]]:
    """Pytest fixture，用於在測試模組執行期間啟動和停止伺服器。

    'scope="module"' 表示此 fixture 在整個測試模組中只會執行一次，
    所有測試共享同一個伺服器實例，以提高效率。

    Args:
        request: Pytest 的內建 fixture，用於存取請求測試的上下文。

    Yields:
        一個 subprocess.Popen 物件，代表正在執行的伺服器子程序。
    """
    logger.info("正在啟動伺服器程序")
    server_process = start_server()
    # 等待伺服器完全啟動
    if not wait_for_server():
        # 如果伺服器啟動失敗，則標記測試失敗
        pytest.fail("伺服器啟動失敗")
    logger.info("伺服器程序已啟動")

    def stop_server() -> None:
        """定義一個在測試結束後執行的清理函式。"""
        logger.info("正在停止伺服器程序")
        # 嘗試正常終止伺服器程序
        server_process.terminate()
        try:
            # 等待最多 5 秒讓程序自行關閉
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # 如果程序在 5 秒內沒有終止，則強制結束
            logger.warning("伺服器程序未終止，將強制結束")
            server_process.kill()
            server_process.wait()
        logger.info("伺服器程序已停止")

    # 使用 request.addfinalizer 註冊清理函式，確保在測試模組結束時執行
    request.addfinalizer(stop_server)
    # 使用 yield 將伺服器程序物件提供給測試函式
    yield server_process


# --- 測試案例 ---


@pytest.mark.asyncio
async def test_websocket_audio_input(server_fixture: subprocess.Popen[str]) -> None:
    """測試 WebSocket 的音訊輸入功能 (本地模式)。

    這個測試模擬客戶端透過 WebSocket 發送音訊和文字訊息的流程。
    '@pytest.mark.asyncio' 標記此測試為非同步函式，由 pytest-asyncio 插件處理。

    Args:
        server_fixture: 從 fixture 注入的正在執行的伺服器程序。
    """

    # 定義非同步輔助函式
    async def send_message(websocket: Any, message: dict[str, Any]) -> None:
        """將字典轉換為 JSON 字串並透過 WebSocket 發送。"""
        await websocket.send(json.dumps(message))

    async def receive_message(websocket: Any, timeout: float = 5.0) -> dict[str, Any]:
        """從 WebSocket 接收訊息，並設定超時。"""
        try:
            # 等待接收訊息，如果超過指定時間則會引發 asyncio.TimeoutError
            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            # 伺服器可能返回 bytes 或 str，都需要解碼並解析為 JSON
            if isinstance(response, bytes):
                return json.loads(response.decode())
            if isinstance(response, str):
                return json.loads(response)
            return response
        except asyncio.TimeoutError as exc:
            raise TimeoutError(f"在 {timeout} 秒內未收到回應") from exc

    try:
        # 等待一段時間，確保伺服器內部狀態完全就緒
        await asyncio.sleep(2)

        # 建立 WebSocket 連接
        async with connect(WS_URL, ping_timeout=10, close_timeout=10) as websocket:
            try:
                # 1. 等待伺服器發送 'setupComplete' 訊息
                # 這表示伺服器端的 WebSocket 連接已準備好接收資料
                setup_response = await receive_message(websocket, timeout=10.0)
                assert "setupComplete" in setup_response
                logger.info("已收到 setupComplete")

                # 2. 發送一個包含使用者 ID 的虛擬音訊區塊
                dummy_audio = bytes([0] * 1024)  # 建立一個 1024 位元組的零值音訊資料
                audio_msg = {
                    "user_id": "test-user",
                    "realtimeInput": {
                        "mediaChunks": [
                            {
                                "mimeType": "audio/pcm;rate=16000",
                                "data": dummy_audio.hex(),  # 將位元組轉換為十六進位字串
                            }
                        ]
                    },
                }
                await send_message(websocket, audio_msg)
                logger.info("已發送音訊區塊")

                # 3. 發送文字訊息以完成這一輪對話 (模擬前端行為)
                text_msg = {
                    "content": {
                        "role": "user",
                        "parts": [{"text": "Test audio"}],
                    }
                }
                await send_message(websocket, text_msg)
                logger.info("已發送文字完成訊息")

                # 4. 收集伺服器的回應
                responses = []
                # 設置一個循環來接收多個可能的回應
                for _ in range(10):  # 最多接收 10 個回應
                    try:
                        response = await receive_message(websocket, timeout=5.0)
                        responses.append(response)
                        logger.info(f"已收到: {response}")

                        # 如果收到 'turn_complete' 訊息，表示此輪對話結束，可以跳出循環
                        if isinstance(response, dict) and response.get("turn_complete"):
                            break
                    except TimeoutError:
                        # 如果在等待時間內沒有收到更多訊息，也跳出循環
                        break

                # 5. 驗證測試結果
                # 斷言至少收到了一個回應
                assert len(responses) > 0, "未收到任何回應"

                # 斷言所有回應中都不包含錯誤訊息
                for idx, response in enumerate(responses):
                    assert (
                        "error" not in response
                    ), f"回應 {idx} 包含錯誤: {response.get('error')}"

                logger.info(f"音訊測試通過。共收到 {len(responses)} 個回應")

            finally:
                # 確保 WebSocket 連接被關閉
                await websocket.close()

    except Exception as e:
        # 如果測試過程中發生任何未預期的錯誤，記錄下來並重新引發，讓 pytest 標記測試失敗
        logger.error(f"音訊測試失敗: {e}")
        raise


def test_feedback_endpoint(server_fixture: subprocess.Popen[str]) -> None:
    """測試 /feedback 端點。

    這個測試模擬客戶端向伺服器提交使用者回饋。

    Args:
        server_fixture: 從 fixture 注入的正在執行的伺服器程序。
    """
    # 準備要發送的回饋資料
    feedback_data = {
        "score": 5,
        "text": "Great response!",
        "user_id": "test-user-123",
        "session_id": "test-session-123",
        "log_type": "feedback",
    }

    # 使用 requests.post 向 FEEDBACK_URL 發送 POST 請求
    response = requests.post(FEEDBACK_URL, json=feedback_data, timeout=10)

    # 斷言 HTTP 狀態碼應為 200 (OK)
    assert response.status_code == 200
    # 斷言回應的 JSON 內容符合預期
    assert response.json() == {"status": "success"}
    logger.info("回饋端點測試通過")
