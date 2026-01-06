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
import time
import uuid

import requests
from locust import HttpUser, between, task

ENDPOINT = "/run_sse"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ChatStreamUser(HttpUser):
    """模擬使用者與聊天串流 API 互動。"""

    wait_time = between(1, 3)  # 在任務之間等待 1-3 秒

    @task
    def chat_stream(self) -> None:
        """模擬聊天串流互動。"""
        headers = {"Content-Type": "application/json"}
        if os.environ.get("_ID_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['_ID_TOKEN']}"
        # 首先建立工作階段
        user_id = f"user_{uuid.uuid4()}"
        session_data = {"state": {"preferred_language": "English", "visit_count": 1}}

        session_url = f"{self.client.base_url}/apps/policy_as_code_agent/users/{user_id}/sessions"
        session_response = requests.post(
            session_url,
            headers=headers,
            json=session_data,
            timeout=10,
        )

        # 從回應中取得 session_id
        session_id = session_response.json()["id"]

        # 發送聊天訊息
        data = {
            "app_name": "policy_as_code_agent",
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": "Hello! Weather in New york?"}],
            },
            "streaming": True,
        }
        start_time = time.time()

        with self.client.post(
            ENDPOINT,
            name=f"{ENDPOINT} message",
            headers=headers,
            json=data,
            catch_response=True,
            stream=True,
            params={"alt": "sse"},
        ) as response:
            if response.status_code == 200:
                events = []
                has_error = False
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        events.append(line_str)

                        if "429 Too Many Requests" in line_str:
                            self.environment.events.request.fire(
                                request_type="POST",
                                name=f"{ENDPOINT} rate_limited 429s",
                                response_time=0,
                                response_length=len(line),
                                response=response,
                                context={},
                            )

                        # 檢查 JSON payload 中的錯誤回應
                        try:
                            event_data = json.loads(line_str)
                            if isinstance(event_data, dict) and "code" in event_data:
                                # 將任何非 2xx 代碼標記為錯誤
                                if event_data["code"] >= 400:
                                    has_error = True
                                    error_msg = event_data.get(
                                        "message", "Unknown error"
                                    )
                                    response.failure(f"Error in response: {error_msg}")
                                    logger.error(
                                        "Received error response: code=%s, message=%s",
                                        event_data["code"],
                                        error_msg,
                                    )
                        except json.JSONDecodeError:
                            # 如果不是有效的 JSON，繼續處理
                            pass

                end_time = time.time()
                total_time = end_time - start_time

                # 只有在沒有發現錯誤時才觸發成功事件
                if not has_error:
                    self.environment.events.request.fire(
                        request_type="POST",
                        name=f"{ENDPOINT} end",
                        response_time=total_time * 1000,  # 轉換為毫秒
                        response_length=len(events),
                        response=response,
                        context={},
                    )
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
