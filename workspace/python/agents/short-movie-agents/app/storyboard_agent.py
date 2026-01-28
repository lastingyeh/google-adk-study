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

import vertexai
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from vertexai.preview.vision_models import ImageGenerationModel

from .utils.utils import load_prompt_from_file

# 設定日誌記錄 (Logging)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 配置常數
MODEL = "gemini-2.5-flash"
DESCRIPTION = (
    "負責根據劇本和故事建立分鏡腳本的代理"
)

# 初始化 Vertex AI 和影像生成模型
IMAGEN_MODEL = "imagen-4.0-ultra-generate-001"

logger.debug(f"專案 ID: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
logger.debug(f"區域位置: {os.getenv('GOOGLE_CLOUD_LOCATION')}")

# 初始化 Vertex AI 環境
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)
# 載入預訓練的影像生成模型
generation_model = ImageGenerationModel.from_pretrained(IMAGEN_MODEL)


# 分鏡腳本生成工具 (Storyboard generate tool)
def storyboard_generate(
    prompt: str, scene_number: int, tool_context: ToolContext
) -> list[str]:
    """
    生成代表傳遞的提示詞的分鏡圖。

    參數：
        prompt (str): 描述應生成並由工具返回的分鏡圖的文字提示詞。
        scene_number (int): 場景編號。
        tool_context (): 工具所需的 ToolContext 上下文物件。

    返回：
        list[str]: 存儲在 GCS 儲存桶中的影像連結列表。
    """
    try:
        # 獲取工作階段 ID 以定義 GCS 存儲路徑
        session_id = tool_context._invocation_context.session.id
        bucket_name = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")
        GCS_PATH = f"gs://{bucket_name}/{session_id}"
        AUTHORIZED_URI = "https://storage.mtls.cloud.google.com/"

        # 執行實際的影像生成
        logger.info(
            f"正在為場景 {scene_number} 生成影像，提示詞為：{prompt}"
        )
        response = generation_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            output_gcs_uri=f"{GCS_PATH}/scene_{scene_number}",
            aspect_ratio="1:1",
            negative_prompt="",
            person_generation="allow_adult",
            safety_filter_level="block_few",
            add_watermark=True,
        )

        # 處理生成結果
        if response.images:
            logger.info(
                f"已為提示詞生成 {len(response.images)} 張影像：{prompt}"
            )
            # 將 GCS 路徑轉換為可授權存取的網址
            return [
                image._gcs_uri.replace("gs://", AUTHORIZED_URI)
                for image in response.images
            ]
        else:
            logger.info(f"提示詞未生成任何 (0) 影像：{prompt}")
            return []  # 若無影像則返回空列表
    except Exception as e:
        logger.error(f"為 {prompt} 生成影像時發生錯誤：{e}")
        return []


# --- 分鏡腳本代理 (Storyboard Agent) ---
storyboard_agent = None
try:
    # 建立分鏡腳本代理實例
    storyboard_agent = Agent(
        # 對於簡單任務使用潛在的較便宜/快速模型
        model=MODEL,
        name="storyboard_agent",
        description=(DESCRIPTION),
        # 從外部檔案載入分鏡製作指令
        instruction=load_prompt_from_file("storyboard_agent.txt"),
        # 將結果存儲在 "storyboard" 鍵下
        output_key="storyboard",
        # 註冊影像生成工具
        tools=[storyboard_generate],
    )
    logger.info(
        f"✅ 代理 '{storyboard_agent.name}' 已使用模型 '{MODEL}' 建立。"
    )
except Exception as e:
    # 發生錯誤時記錄詳細資訊
    logger.error(
        f"❌ 無法建立分鏡腳本代理。請檢查 API 金鑰 ({MODEL})。錯誤：{e}"
    )
