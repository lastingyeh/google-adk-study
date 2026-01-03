"""客戶服務代理（Customer Service Agent）的配置模組。"""

import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

# 設定日誌記錄配置
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AgentModel(BaseModel):
    """代理模型設定。"""

    # 代理名稱，預設為 customer_service_agent
    name: str = Field(default="customer_service_agent")
    # 使用的模型名稱，預設為 gemini-2.5-flash
    model: str = Field(default="gemini-2.5-flash")

class Config(BaseSettings):
    """客戶服務代理的配置設定。"""

    # Pydantic Settings 配置
    model_config = SettingsConfigDict(
        # 指定環境變數檔案路徑 (.env)
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        # 環境變數前綴
        env_prefix="GOOGLE_",
        # 區分大小寫
        case_sensitive=True,
    )

    # 代理相關設定
    agent_settings: AgentModel = Field(default=AgentModel())
    # 應用程式名稱
    app_name: str = "customer_service_app"
    # Google Cloud 專案 ID
    CLOUD_PROJECT: str = Field(default="my_project")
    # Google Cloud 區域
    CLOUD_LOCATION: str = Field(default="us-central1")
    # 是否使用 Vertex AI
    GENAI_USE_VERTEXAI: str = Field(default="1")
    # API 金鑰（可選）
    API_KEY: str | None = Field(default="")
