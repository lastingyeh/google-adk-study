import os
import sys

from dotenv import load_dotenv
from google.adk.cli.service_registry import get_service_registry
from google.adk.memory import VertexAiMemoryBankService, InMemoryMemoryService, BaseMemoryService
from google.adk.artifacts import InMemoryArtifactService, GcsArtifactService, BaseArtifactService


# 添加 backend 目錄到 Python 路徑
sys.path.append(os.path.dirname(__file__))

from service.redis_session_service import RedisSessionService

# 在所有其他匯入之前，從 .env 檔案載入環境變數
load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

"""
此模組提供用於創建服務 URI 的工廠函式。

它集中了根據環境變數決定使用哪種服務實現的邏輯。
這允許靈活的配置，並能在不更改應用程式碼的情況下，輕鬆切換不同的服務提供者（例如：雲端、資料庫、Redis）。
"""

# session service uri factory
# priority: cloud > db > redis > default
def session_service_uri_factory():
    """
    Determines the session service URI based on environment variables.
    It checks for SESSION_SERVICE_URI, DATABASE_URI, and REDIS_URI in order,
    and returns the first one found. It also prints a message indicating which URI is being used.
    """
    # 取得 ADK 服務註冊表
    registry = get_service_registry()
    session_uri = os.getenv("SESSION_SERVICE_URI")
    if session_uri:
        print("✅ Using SESSION_SERVICE_URI for session service.")
        return session_uri

    db_uri = os.getenv("DATABASE_URI")
    if db_uri:
        print("✅ Using DATABASE_URI for session service.")
        return db_uri

    redis_uri = os.getenv("REDIS_URI")
    if redis_uri:
        print("✅ Using REDIS_URI for session service.")
        # 註冊 Redis 會話服務，將 "redis://" scheme 映射到 redis_factory
        registry.register_session_service("redis", redis_factory)
        return redis_uri

    print("⚠️ No session service URI configured, defaulting to None.")
    return None


# memory service uri factory
def memory_service_uri_factory():
    MEMORY_SERVICE_URI = os.getenv("MEMORY_SERVICE_URI")
    if MEMORY_SERVICE_URI:
        print("✅ Using MEMORY_SERVICE_URI for memory service.")
        return MEMORY_SERVICE_URI
    print("⚠️ No memory service URI configured, defaulting to None.")
    return None

def redis_factory(uri: str, **kwargs):
    """
    Redis 會話服務工廠函式。
    
    ADK 服務註冊表會呼叫此函式來建立 RedisSessionService 實例。
    
    參數：
        uri: Redis 連線 URI (例如：redis://localhost:6379/0)
        **kwargs: ADK 傳遞的其他參數，包含 agents_dir 等
    
    回傳：
        RedisSessionService 實例
    """
    # 移除 ADK 傳入但 RedisSessionService 不需要的參數
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("agents_dir", None)
    
    # 建立並回傳 Redis 會話服務實例
    return RedisSessionService(uri=uri, **kwargs_copy)

def memory_service_factory() -> BaseMemoryService:
    MEMORY_SERVICE_URI = os.getenv("MEMORY_SERVICE_URI")
    if MEMORY_SERVICE_URI:
        agent_engine_id = MEMORY_SERVICE_URI.split("://")[-1]
        print("✅ Using MEMORY_SERVICE_URI for memory service.")
        return VertexAiMemoryBankService(agent_engine_id=agent_engine_id)
    print("⚠️ No memory service URI configured, defaulting to InMemoryMemoryService.")
    return InMemoryMemoryService()

# artifact service uri factory
def artifact_service_uri_factory():
    ARTIFACT_SERVICE_URI = os.getenv("ARTIFACT_SERVICE_URI")
    if ARTIFACT_SERVICE_URI:
        print("✅ Using ARTIFACT_SERVICE_URI for artifact service.")
        return ARTIFACT_SERVICE_URI
    print("⚠️ No artifact service URI configured, defaulting to None.")
    return None

# artifact service factory
def artifact_service_factory() -> BaseArtifactService:
    ARTIFACT_SERVICE_URI = os.getenv("ARTIFACT_SERVICE_URI")
    if ARTIFACT_SERVICE_URI:
        bucket_name = ARTIFACT_SERVICE_URI.split("://")[-1]
        print("✅ Using ARTIFACT_SERVICE_URI for artifact service.")
        return GcsArtifactService(bucket_name=bucket_name)
    print("⚠️ No artifact service URI configured, defaulting to InMemoryArtifactService.")
    return InMemoryArtifactService()
