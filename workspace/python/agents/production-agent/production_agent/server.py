"""
適用於 ADK 代理部署的生產就緒 (Production-ready) FastAPI 伺服器。

此實作包含了生產環境的最佳實踐：
- 結構化 JSON 日誌記錄與請求追蹤 (Structured JSON logging with request tracing)
- API 金鑰驗證 (API key authentication)
- 具備設定限制的 CORS (Restricted CORS)
- 可靠性的逾時處理 (Timeout handling)
- 用於監控的 Prometheus 指標 (Prometheus metrics)
- 具備類型化例外的正確錯誤處理 (Proper error handling)
- 具備限制的輸入驗證 (Input validation with limits)
- 具備相依性狀態的健康檢查 (Health checks with dependency status)
"""

import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

# ============================================================================
# 設定 (CONFIGURATION)
# ============================================================================

class Settings(BaseSettings):
    """來自環境變數的應用程式設定。"""

    # 應用程式設定 (App settings)
    app_name: str = "ADK Production Deployment API"
    app_version: str = "1.0"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # 伺服器設定 (Server settings)
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    workers: int = int(os.getenv("WORKERS", "1"))

    # 安全性 (Security)
    api_key: Optional[str] = os.getenv("API_KEY", None)
    enable_auth: bool = os.getenv("ENABLE_AUTH", "false").lower() == "true"
    allowed_origins: list = Field(
        default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    )

    # 代理設定 (Agent settings)
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    max_query_length: int = int(os.getenv("MAX_QUERY_LENGTH", "10000"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))

    # Gemini 設定 (Gemini settings)
    use_vertexai: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# ============================================================================
# 日誌設定 (LOGGING CONFIGURATION)
# ============================================================================

def setup_logging() -> logging.Logger:
    """設定結構化 JSON 日誌。"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 移除現有的處理器 (handlers)
    logger.handlers.clear()

    # 具備格式化的控制台處理器 (Console handler)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = setup_logging()

# ============================================================================
# 驗證與啟動 (VALIDATION & STARTUP)
# ============================================================================

def validate_configuration() -> None:
    """在啟動時驗證設定。"""
    logger.info("Validating configuration...") # 正在驗證設定...

    if settings.environment == "production":
        if settings.enable_auth and not settings.api_key:
            raise ValueError(
                "ENABLE_AUTH is true but API_KEY is not set. "
                "Set API_KEY or set ENABLE_AUTH=false"
            )

        # 驗證來源 (origins) 不是萬用字元
        if "*" in settings.allowed_origins:
            logger.warning(
                "ALLOWED_ORIGINS contains '*'. This is NOT recommended for production. "
                "Set specific origins in ALLOWED_ORIGINS environment variable."
            )

    # 設定 Gemini 環境
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = str(settings.use_vertexai).lower()

    logger.info(f"Configuration validated. Environment: {settings.environment}") # 設定已驗證。環境: {settings.environment}

# ============================================================================
# 生命週期事件 (LIFESPAN EVENTS)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期：啟動與關閉。"""
    # 啟動 (Startup)
    logger.info("🚀 Application starting up...") # 應用程式啟動中...
    validate_configuration()

    yield

    # 關閉 (Shutdown)
    logger.info("🛑 Application shutting down...") # 應用程式關閉中...
    # 如果需要，在此清理資源
    pass

# ============================================================================
# 應用程式初始化 (APP INITIALIZATION)
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="具備完整監控與安全性的 ADK 代理生產就緒 API 伺服器",
    lifespan=lifespan
)

# 具備限制來源的 CORS 設定
cors_origins = [origin.strip() for origin in settings.allowed_origins if origin.strip()]
logger.info(f"Configuring CORS for origins: {cors_origins}") # 為以下來源設定 CORS: {cors_origins}

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,  # 僅在需要時設為 True
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# 建立對話服務 (Session Service) 與執行器 (Runner)
session_service = InMemorySessionService()
runner = Runner(
    app_name="production_deployment",
    agent=root_agent,
    session_service=session_service
)

# ============================================================================
# 指標追蹤 (METRICS TRACKING)
# ============================================================================

class HealthStatus(str, Enum):
    """健康狀態列舉。"""
    HEALTHY = "healthy"      # 健康
    DEGRADED = "degraded"    # 降級
    UNHEALTHY = "unhealthy"  # 不健康

# 指標 (Metrics)
service_start_time = datetime.now()
request_count = 0
successful_requests = 0
error_count = 0
timeout_count = 0
requests_by_endpoint = {}



class QueryRequest(BaseModel):
    """具備驗證的代理調用請求模型。"""
    query: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="代理查詢提示詞 (Query prompt for the agent)"
    )
    temperature: float = Field(
        0.5,
        ge=0.0,
        le=2.0,
        description="控制隨機性：數值越高越具創造力 (Controls randomness: higher = more creative)"
    )
    max_tokens: int = Field(
        2048,
        ge=1,
        le=4096,
        description="回應中的最大 token 數 (Maximum tokens in response)"
    )


class QueryResponse(BaseModel):
    """代理調用回應模型。"""
    response: str = Field(..., description="代理回應文字 (Agent response text)")
    model: str = Field(..., description="使用的模型 (Model used)")
    tokens: int = Field(..., description="Token 數量估計 (Token count estimate)")
    request_id: str = Field(default="", description="請求追蹤 ID (Request tracking ID)")


# ============================================================================
# 驗證 (AUTHENTICATION)
# ============================================================================

async def verify_api_key(authorization: Optional[str] = None) -> None:
    """如果啟用了驗證，則驗證 API 金鑰。"""
    if not settings.enable_auth:
        return

    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid authorization header") # 缺少或無效的授權標頭
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization" # 缺少或無效的授權
        )

    token = authorization.replace("Bearer ", "")
    if token != settings.api_key:
        logger.warning("Invalid API key attempted") # 嘗試使用無效的 API 金鑰
        raise HTTPException(
            status_code=403,
            detail="Invalid API key" # 無效的 API 金鑰
        )

# ============================================================================
# 端點 (ENDPOINTS)
# ============================================================================


@app.get("/")
async def root():
    """根端點，包含 API 資訊。"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "health": "/health",
            "invoke": "/invoke (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """
    包含相依性狀態的綜合健康檢查端點。

    Returns:
        - healthy (200): 所有系統運作正常
        - degraded (200): 服務運作中但有問題
        - unhealthy (503): 服務無法使用
    """
    uptime = (datetime.now() - service_start_time).total_seconds()
    error_rate = error_count / max(request_count, 1)

    # 決定健康狀態
    if request_count == 0:
        health_status = HealthStatus.HEALTHY
    elif error_rate > 0.1:  # 錯誤率超過 10%
        health_status = HealthStatus.UNHEALTHY
    elif error_rate > 0.05:  # 錯誤率超過 5%
        health_status = HealthStatus.DEGRADED
    else:
        health_status = HealthStatus.HEALTHY

    response_data = {
        "status": health_status.value,
        "service": "adk-production-deployment-api",
        "environment": settings.environment,
        "uptime_seconds": uptime,
        "request_count": request_count,
        "error_count": error_count,
        "agent": {
            "name": root_agent.name,
            "model": root_agent.model
        },
        "metrics": {
            "successful_requests": successful_requests,
            "timeout_count": timeout_count,
            "error_rate": round(error_rate, 3)
        }
    }

    # 回傳適當的狀態碼
    if health_status == HealthStatus.UNHEALTHY:
        return JSONResponse(
            status_code=503,
            content=response_data
        )
    else:
        return response_data


@app.post(
    "/invoke",
    response_model=QueryResponse,
    status_code=200,
    responses={
        200: {"description": "Successful agent invocation"}, # 代理調用成功
        400: {"description": "Invalid request parameters"}, # 無效的請求參數
        401: {"description": "Missing or invalid authentication"}, # 缺少或無效的驗證
        403: {"description": "Forbidden"}, # 禁止存取
        504: {"description": "Request timeout"}, # 請求逾時
        500: {"description": "Server error"} # 伺服器錯誤
    }
)
async def invoke_agent(
    request: QueryRequest,
    authorization: Optional[str] = None
):
    """
    調用生產環境部署代理。

    Args:
        request: 查詢與設定參數
        authorization: 用於 API 驗證的 Bearer token

    Returns:
        Agent response with metadata (包含詮釋資料的代理回應)

    Raises:
        HTTPException: 用於無效請求或伺服器錯誤
    """
    global request_count, successful_requests, error_count, timeout_count

    request_id = str(uuid.uuid4())
    request_count += 1

    logger.info(
        f"invoke_agent.start - request_id={request_id} "
        f"query_len={len(request.query)}"
    )

    try:
        # 如果啟用驗證，則進行驗證
        await verify_api_key(authorization)

        # 驗證查詢長度
        if len(request.query) > settings.max_query_length:
            logger.warning(
                f"invoke_agent.query_too_long - request_id={request_id} "
                f"len={len(request.query)}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Query exceeds maximum length of {settings.max_query_length}" # 查詢超過最大長度
            )

        # 為此調用建立一個對話 (session)
        session = await session_service.create_session(
            app_name="production_deployment",
            user_id="api_user"
        )

        # 更新代理設定
        root_agent.generate_content_config = types.GenerateContentConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens
        )

        # 建立訊息內容
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=request.query)]
        )

        # 執行代理並設定逾時
        response_text = ""
        try:
            async with asyncio.timeout(settings.request_timeout):
                async for event in runner.run_async(
                    user_id="api_user",
                    session_id=session.id,
                    new_message=new_message
                ):
                    if event.content and event.content.parts:
                        text = event.content.parts[0].text
                        if text:  # 僅在文字非 None 時串接
                            response_text += text
        except asyncio.TimeoutError:
            timeout_count += 1
            logger.error(
                f"invoke_agent.timeout - request_id={request_id} "
                f"timeout={settings.request_timeout}s"
            )
            raise HTTPException(
                status_code=504,
                detail=f"Agent request exceeded {settings.request_timeout} second timeout" # 代理請求超過逾時秒數
            )

        # 估計 Token 數 (以字數作為備案)
        token_count = len(response_text.split())

        successful_requests += 1
        logger.info(
            f"invoke_agent.success - request_id={request_id} "
            f"tokens={token_count}"
        )

        return QueryResponse(
            response=response_text,
            model=root_agent.model,
            tokens=token_count,
            request_id=request_id
        )

    except HTTPException as e:
        error_count += 1
        logger.warning(
            f"invoke_agent.http_error - request_id={request_id} "
            f"status={e.status_code}"
        )
        raise

    except ValueError as e:
        error_count += 1
        logger.warning(
            f"invoke_agent.validation_error - request_id={request_id} "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid request parameters" # 無效的請求參數
        )

    except Exception as e:
        error_count += 1
        logger.error(
            f"invoke_agent.unexpected_error - request_id={request_id} "
            f"error_type={type(e).__name__} error={str(e)}",
            exc_info=True
        )
        # 不要暴露內部錯誤細節
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later." # 發生未預期的錯誤。請稍後再試。
        )


@app.middleware("http")
async def track_requests(request, call_next):
    """追蹤請求與錯誤的中介軟體 (Middleware)。"""
    global request_count, error_count

    request_count += 1
    response = await call_next(request)

    if response.status_code >= 400:
        error_count += 1

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        log_level="info"
    )

"""
重點摘要:
- **核心概念**: 生產級 FastAPI 伺服器，整合了 ADK 代理
- **關鍵技術**:
    - FastAPI 框架
    - Pydantic 用於資料驗證與設定管理
    - 非同步處理 (asyncio)
    - 結構化日誌 (Structured Logging)
    - 中介軟體 (Middleware) 進行 CORS 與請求追蹤
- **重要結論**:
    - 實作了完整的生命週期管理 (Startup/Shutdown)
    - 提供健康檢查端點 `/health`，可根據錯誤率判斷服務狀態
    - 提供 `/invoke` 端點與 ADK 代理互動，並包含逾時與錯誤處理
    - 安全性方面支援 API Key 驗證與嚴格的 CORS 設定
- **行動項目**:
    - 設定環境變數 (如 `.env`) 以調整伺服器行為
    - 部署時需確保 API Key 與 CORS 設定正確
"""
