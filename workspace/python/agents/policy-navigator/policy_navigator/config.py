"""
Policy Navigator 的設定模組。

處理環境變數、API 設定以及應用程式設定。
"""

import os
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

# 從 .env 檔案載入環境變數
load_dotenv()


class Config:
    """Policy Navigator 的設定類別。"""

    # Google API 設定
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CLOUD_PROJECT: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    # File Search Store 名稱
    HR_STORE_NAME: str = os.getenv("HR_STORE_NAME", "policy-navigator-hr")
    IT_STORE_NAME: str = os.getenv("IT_STORE_NAME", "policy-navigator-it")
    LEGAL_STORE_NAME: str = os.getenv("LEGAL_STORE_NAME", "policy-navigator-legal")
    SAFETY_STORE_NAME: str = os.getenv("SAFETY_STORE_NAME", "policy-navigator-safety")

    # 模型設定
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

    # 日誌設定
    LOG_LEVEL: str = os.getenv("POLICY_NAVIGATOR_LOG_LEVEL", "INFO")

    # 除錯模式
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # File Search 設定
    MAX_TOKENS_PER_CHUNK: int = 500
    MAX_OVERLAP_TOKENS: int = 50
    MAX_STORE_SIZE_GB: int = 20
    RECOMMENDED_STORE_SIZE_GB: int = 10

    # 逾時設定
    INDEXING_TIMEOUT_SECONDS: int = 300  # 5 分鐘
    QUERY_TIMEOUT_SECONDS: int = 60  # 1 分鐘

    @classmethod
    def validate(cls) -> bool:
        """
        驗證設定是否正確設定。

        Returns:
            bool: 如果設定有效則回傳 True，否則回傳 False
        """
        if not cls.GOOGLE_API_KEY:
            logger.warning(
                "GOOGLE_API_KEY 未設定。請在 .env 檔案或環境變數中設定。"
            )
            return False

        logger.info(f"設定已載入。除錯模式: {cls.DEBUG}")
        logger.info(f"使用模型: {cls.DEFAULT_MODEL}")
        logger.info(f"日誌等級: {cls.LOG_LEVEL}")
        return True

    @classmethod
    def get_store_names(cls) -> dict[str, str]:
        """
        取得所有已設定的 store 名稱。

        Returns:
            dict: store 類型到 store 名稱的對應
        """
        return {
            "hr": cls.HR_STORE_NAME,
            "it": cls.IT_STORE_NAME,
            "legal": cls.LEGAL_STORE_NAME,
            "safety": cls.SAFETY_STORE_NAME,
        }


# 初始化 logger
logger.remove()  # 移除預設 handler
logger.add(
    lambda msg: print(msg, end=""),
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=Config.LOG_LEVEL,
)

# 在匯入時驗證設定
Config.validate()
