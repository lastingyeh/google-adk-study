# 匯入必要的函式庫
import json  # 用於處理 JSON 格式的資料
import logging  # 用於記錄日誌訊息
import time  # 用於計時
from typing import Any  # 用於型別提示

from locust import User, between, task  # 從 locust 匯入負載測試相關的類別與函式
from websockets.exceptions import (
    WebSocketException,
)  # 從 websockets 匯入 WebSocket 相關的例外
from websockets.sync.client import connect  # 從 websockets 匯入同步的客戶端連線函式

# 設定日誌記錄的基本組態，級別為 INFO，表示只顯示 INFO 等級以上的訊息
logging.basicConfig(level=logging.INFO)
# 獲取一個以目前模組名稱命名的日誌記錄器
logger = logging.getLogger(__name__)


class WebSocketUser(User):
    """模擬一個向遠端代理引擎發送 websocket 請求的使用者。"""

    # 設定每個任務執行後等待的時間，介於 1 到 3 秒之間
    wait_time = between(1, 3)
    # 將此類別標記為抽象類別，Locust 不會直接將其實例化為模擬使用者
    abstract = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # 呼叫父類別 (User) 的初始化方法
        super().__init__(*args, **kwargs)
        # 將 host 的 URL 從 http:// 或 https:// 轉換為 ws:// 或 wss://，並在結尾加上 /ws 路徑
        self.ws_url = (
            self.host.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
        )

    @task
    def websocket_audio_conversation(self) -> None:
        """測試一個帶有音訊輸入的完整 websocket 對話。"""
        # 記錄任務開始時間
        start_time = time.time()
        # 初始化回應計數器與例外變數
        response_count = 0
        exception = None

        try:
            # 執行核心的 websocket 互動邏輯，並獲取回應數量
            response_count = self._websocket_interaction()

            # 如果沒有收到任何有效回應，則將其標記為失敗
            if response_count == 0:
                exception = Exception(
                    "未從代理收到任何回應 (No responses received from agent)"
                )

        except WebSocketException as e:
            # 捕捉 WebSocket 相關的錯誤
            exception = e
            logger.error(f"WebSocket 錯誤: {e}")
        except Exception as e:
            # 捕捉其他未預期的錯誤
            exception = e
            logger.error(f"未預期的錯誤: {e}")
        finally:
            # 計算總共花費的時間（以毫秒為單位）
            total_time = int((time.time() - start_time) * 1000)

            # 向 Locust 回報這次請求的指標數據
            self.environment.events.request.fire(
                request_type="WS",  # 請求類型
                name="websocket_conversation",  # 請求名稱，會顯示在 Locust 報告中
                response_time=total_time,  # 回應時間（毫秒）
                response_length=response_count * 100,  # 估算的回應大小
                response=None,  # 回應內容（此處不記錄）
                context={},  # 上下文資訊
                exception=exception,  # 如果有錯誤，則記錄下來
            )

    def _websocket_interaction(self) -> int:
        """處理 websocket 互動並返回回應計數。"""
        response_count = 0

        # 建立一個 websocket 連線，設定連線逾時為 10 秒，關閉連線逾時為 20 秒
        with connect(self.ws_url, open_timeout=10, close_timeout=20) as websocket:
            # 等待伺服器傳來 setupComplete 訊息，逾時時間為 10 秒
            setup_response = websocket.recv(timeout=10.0)
            setup_data = json.loads(setup_response)
            # 斷言收到的訊息中包含 "setupComplete" 鍵，否則拋出錯誤
            assert (
                "setupComplete" in setup_data
            ), f"預期收到 setupComplete，但收到了 {setup_data}"
            logger.info("已收到 setupComplete")

            # 準備一個假的音訊區塊，並帶上 user_id
            dummy_audio = bytes([0] * 1024)  # 1024 位元組的零
            audio_msg = {
                "user_id": "load-test-user",
                "realtimeInput": {
                    "mediaChunks": [
                        {
                            "mimeType": "audio/pcm;rate=16000",  # 音訊格式
                            "data": dummy_audio.hex(),  # 將位元組轉換為十六進位字串
                        }
                    ]
                },
            }
            # 發送音訊訊息
            websocket.send(json.dumps(audio_msg))
            logger.info("已發送音訊區塊")

            # 發送文字訊息以完成這一輪的對話
            text_msg = {
                "content": {
                    "role": "user",
                    "parts": [{"text": "Hello!"}],
                }
            }
            # 發送文字訊息
            websocket.send(json.dumps(text_msg))
            logger.info("已發送文字補完訊息")

            # 收集回應，直到收到 turn_complete 或逾時
            for _ in range(20):  # 最多接收 20 個回應
                try:
                    # 等待接收伺服器的回應，逾時時間為 10 秒
                    response = websocket.recv(timeout=10.0)
                    response_data = json.loads(response)
                    response_count += 1
                    logger.debug(f"收到的回應: {response_data}")

                    # 檢查回應是否為字典且包含 "turn_complete" 鍵
                    if isinstance(response_data, dict) and response_data.get(
                        "turn_complete"
                    ):
                        logger.info(f"在 {response_count} 個回應後，對話輪次完成")
                        break  # 結束迴圈
                except TimeoutError:
                    # 如果在指定時間內沒有收到回應，則視為逾時
                    logger.info(f"在 {response_count} 個回應後逾時")
                    break  # 結束迴圈

        # 返回總共收到的回應數量
        return response_count


class RemoteAgentUser(WebSocketUser):
    """用於測試遠端代理引擎部署的使用者。"""

    # 可以透過命令列設定 host，例如: locust -f load_test.py --host=https://your-deployed-service.run.app
    host = "http://localhost:8000"  # 本地測試時的預設 host
