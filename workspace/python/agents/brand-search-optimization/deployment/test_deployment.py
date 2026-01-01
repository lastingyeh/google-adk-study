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

"""測試將 FOMC 研究代理程式部署到代理程式引擎。"""

import asyncio
import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from google.adk.sessions import VertexAiSessionService
from vertexai import agent_engines

FLAGS = flags.FLAGS

# 定義命令列旗標
flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 地區。")
flags.DEFINE_string("bucket", None, "GCP 儲存桶。")
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine 資源 ID (部署代理程式後返回)",
)
flags.DEFINE_string("user_id", None, "使用者 ID (可以是任何字串)。")
# 將 resource_id 和 user_id 標記為必要旗標
flags.mark_flag_as_required("resource_id")
flags.mark_flag_as_required("user_id")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument
    """主函式，用於執行代理程式測試。"""

    # 從 .env 檔案載入環境變數
    load_dotenv()

    # 優先從旗標獲取設定，若無則從環境變數獲取
    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    # 再次從環境變數獲取，確保值已設定
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    # 檢查必要的環境變數是否已設定
    if not project_id:
        print("缺少必要的環境變數：GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("缺少必要的環境變數：GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("缺少必要的環境變數：GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    # 初始化 Vertex AI
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    # 建立 Vertex AI 工作階段服務
    session_service = VertexAiSessionService(project_id, location)
    # 建立一個新的工作階段
    session = asyncio.run(
        session_service.create_session(
            app_name=FLAGS.resource_id, user_id=FLAGS.user_id
        )
    )

    # 取得已部署的代理程式
    agent = agent_engines.get(FLAGS.resource_id)
    print(f"找到資源 ID 為 {FLAGS.resource_id} 的代理程式")

    print(f"已為使用者 ID {FLAGS.user_id} 建立工作階段")
    print("輸入 'quit' 以離開。")
    # 進入與代理程式互動的迴圈
    while True:
        user_input = input("輸入: ")
        if user_input == "quit":
            break

        # 將使用者輸入串流查詢至代理程式並處理回應
        for event in agent.stream_query(
            user_id=FLAGS.user_id, session_id=session.id, message=user_input
        ):
            if "content" in event:
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    for part in parts:
                        if "text" in part:
                            text_part = part["text"]
                            print(f"回應: {text_part}")

    # 刪除工作階段
    asyncio.run(
        session_service.delete_session(
            app_name=FLAGS.resource_id, user_id=FLAGS.user_id, session_id=session.id
        )
    )
    print(f"已刪除使用者 ID {FLAGS.user_id} 的工作階段")


if __name__ == "__main__":
    app.run(main)
