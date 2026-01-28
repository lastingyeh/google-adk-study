# 版權所有 2025 Google LLC
#
# 根據 Apache 許可證 2.0 版（「許可證」）授權；
# 除非遵守許可證，否則您不得使用此檔案。
# 您可以在以下網址獲得許可證副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據許可證分發的軟體
# 是按「原樣」分發的，不附帶任何形式的明示或暗示的保證或條件。
# 請參閱許可證以瞭解管理權限和限制的特定語言。

import logging
import os
import re
import time

from google import genai
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types

from .utils.utils import load_prompt_from_file

# 設定日誌記錄 (Logging)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 配置常數
MODEL = "gemini-2.5-flash"
VIDEO_MODEL = "veo-3.0-generate-preview"
VIDEO_MODEL_LOCATION = "us-central1"
DESCRIPTION = "負責根據劇本和分鏡圖建立影片的代理"
ASPECT_RATIO = "16:9"

# 初始化生成式 AI 客戶端
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=VIDEO_MODEL_LOCATION,
)


# 影片生成工具 (Video generate tool)
def video_generate(
    prompt: str,
    scene_number: int,
    image_link: str,
    screenplay: str,
    tool_context: ToolContext,
) -> list[str]:
    """
    根據傳遞的提示詞和分鏡影像生成影片。

    參數：
        prompt (str): 描述應生成並由工具返回的影片的文字提示詞。
        scene_number (int): 場景編號。
        image_link (str): 存儲在 GCS 儲存桶中的影像連結。
        screenplay (str): 該場景的劇本內容。
        tool_context (): 工具所需的 ToolContext 上下文物件。

    返回：
        list[str]: 存儲在 GCS 儲存桶中的影片連結列表。
    """
    try:
        # 獲取工作階段 ID 以定義 GCS 存儲路徑
        session_id = tool_context._invocation_context.session.id
        bucket_name = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")
        GCS_PATH = f"gs://{bucket_name}/{session_id}"
        AUTHORIZED_URI = "https://storage.mtls.cloud.google.com/"

        # 從劇本中提取對話內容
        dialogue = "\n".join(
            re.findall(r"^\w+\s*\(.+\)\s*$", screenplay, re.MULTILINE)
        )
        dialogue += "\n".join(
            re.findall(r"^\s{2,}.+$", screenplay, re.MULTILINE)
        )

        # 若有對話，將其添加到提示詞中作為音訊參考
        if dialogue:
            prompt += f"\n\n音訊 (Audio)：\n{dialogue}"

        # 執行實際的影片生成
        logger.info(
            f"正在為提示詞 '{prompt}' 和影像 '{image_link}' 生成影片"
        )

        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=ASPECT_RATIO,
                output_gcs_uri=f"{GCS_PATH}/scene_{scene_number}",
                number_of_videos=1,
                duration_seconds=8,
                person_generation="allow_adult",
            ),
        )

        # 輪詢異步操作直到完成
        while not operation.done:
            time.sleep(15)
            operation = client.operations.get(operation)
            logger.info(f"影片生成操作狀態：{operation}")

        # 處理生成結果
        if operation.response:
            logger.info(
                f"已為提示詞生成 {len(operation.result.generated_videos)} 個影片：{prompt}"
            )
            return [
                video.video.uri.replace("gs://", AUTHORIZED_URI)
                for video in operation.result.generated_videos
            ]
        else:
            logger.info(f"提示詞未生成任何 (0) 影片：{prompt}")
            return []  # 若無影片則返回空列表
    except Exception as e:
        logger.error(f"為 {prompt} 生成影片時發生錯誤：{e}")
        return []


# --- 影片代理 (Video Agent) ---
video_agent = None
try:
    # 建立影片代理實例
    video_agent = Agent(
        # 對於簡單任務使用潛在的較便宜/快速模型
        model=MODEL,
        name="video_agent",
        description=(DESCRIPTION),
        # 從外部檔案載入影片製作指令
        instruction=load_prompt_from_file("video_agent.txt"),
        # 將結果存儲在 "video" 鍵下
        output_key="video",
        # 註冊影片生成工具
        tools=[video_generate],
    )
    logger.info(f"✅ 代理 '{video_agent.name}' 已使用模型 '{MODEL}' 建立。")
except Exception as e:
    # 發生錯誤時記錄詳細資訊
    logger.error(
        f"❌ 無法建立影片代理。請檢查 API 金鑰 ({MODEL})。錯誤：{e}"
    )
