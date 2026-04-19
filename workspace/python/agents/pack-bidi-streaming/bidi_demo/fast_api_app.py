
import asyncio
import base64
import json
import logging
import os
import socket
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import warnings

import google.auth
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import (
    DatabaseSessionService,
    InMemorySessionService,
    VertexAiSessionService,
)
from google.cloud import logging as google_cloud_logging
from google.genai import types
from vertexai import agent_engines

from bidi_demo.agent import root_agent as agent
from bidi_demo.app_utils.telemetry import setup_telemetry
from bidi_demo.app_utils.typing import Feedback

# 在導入 agent 之前，先從 .env 檔案載入環境變數
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 設定遙測功能
setup_telemetry()

# 抑制 Pydantic 序列化警告
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# 應用程式名稱常量
APP_NAME = "bidi-demo"

# ========================================
# 第一階段：應用程式初始化 (啟動時執行一次)
# ========================================

app = FastAPI()
app.title = "pack-bidi-streaming"
app.description = "與 pack-bidi-streaming 代理互動的 API"


# 掛載靜態檔案
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def _is_truthy(value: str | None) -> bool:
    return (value or "").lower() in ("true", "1", "yes")


def _get_session_backend() -> str:
    session_backend = os.environ.get("SESSION_BACKEND")
    if session_backend:
        return session_backend.lower()

    if _is_truthy(os.environ.get("USE_IN_MEMORY_SESSION")):
        return "in_memory"

    return "agent_engine"


def _get_project_id() -> str | None:
    configured_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if configured_project_id:
        return configured_project_id

    try:
        _, detected_project_id = google.auth.default()
        return detected_project_id
    except Exception:
        return None


@lru_cache(maxsize=1)
def _get_gcloud_logger():
    project_id = _get_project_id()
    if not project_id:
        logger.info("未設定 GOOGLE_CLOUD_PROJECT，feedback 將僅記錄到本地日誌")
        return None

    try:
        logging_client = google_cloud_logging.Client(project=project_id)
        return logging_client.logger(__name__)
    except Exception as exc:
        logger.warning("初始化 Google Cloud Logging 失敗，改用本地日誌: %s", exc)
        return None


def _get_database_session_kwargs() -> dict[str, int | bool]:
    kwargs: dict[str, int | bool] = {"pool_pre_ping": True}
    int_env_map = {
        "pool_size": "SESSION_DB_POOL_SIZE",
        "max_overflow": "SESSION_DB_MAX_OVERFLOW",
        "pool_timeout": "SESSION_DB_POOL_TIMEOUT",
        "pool_recycle": "SESSION_DB_POOL_RECYCLE",
    }

    for key, env_name in int_env_map.items():
        value = os.environ.get(env_name)
        if value:
            kwargs[key] = int(value)

    return kwargs


def _normalize_session_service_uri(session_service_uri: str) -> str:
    parsed_uri = urlsplit(session_service_uri)
    if parsed_uri.hostname != "postgres":
        return session_service_uri

    try:
        socket.getaddrinfo(parsed_uri.hostname, parsed_uri.port or 5432)
        return session_service_uri
    except socket.gaierror:
        auth = ""
        if parsed_uri.username:
            auth = parsed_uri.username
            if parsed_uri.password:
                auth = f"{auth}:{parsed_uri.password}"
            auth = f"{auth}@"

        port = f":{parsed_uri.port}" if parsed_uri.port else ""
        normalized_uri = urlunsplit(
            parsed_uri._replace(netloc=f"{auth}localhost{port}")
        )
        logger.info(
            "SESSION_SERVICE_URI 使用 Docker 主機名 postgres，但目前環境無法解析；改用 localhost: %s",
            normalized_uri,
        )
        return normalized_uri


def create_session_service():
    session_backend = _get_session_backend()
    logger.info("初始化 SessionService，backend=%s", session_backend)

    if session_backend == "in_memory":
        return InMemorySessionService()

    if session_backend == "postgres":
        session_service_uri = os.environ.get("SESSION_SERVICE_URI") or os.environ.get(
            "SESSION_DB_URL"
        )
        if not session_service_uri:
            raise ValueError(
                "SESSION_SERVICE_URI 未設定，postgres backend 需要資料庫連線字串"
            )
        session_service_uri = _normalize_session_service_uri(session_service_uri)
        return DatabaseSessionService(
            db_url=session_service_uri,
            **_get_database_session_kwargs(),
        )

    if session_backend == "agent_engine":
        project_id = _get_project_id()
        if not project_id:
            raise ValueError(
                "agent_engine backend 需要 GOOGLE_CLOUD_PROJECT 或有效的 ADC 憑證"
            )

        default_agent_name = "pack-bidi-streaming"
        agent_name = os.environ.get("AGENT_ENGINE_SESSION_NAME", default_agent_name)
        existing_agents = list(agent_engines.list(filter=f"display_name={agent_name}"))

        if existing_agents:
            agent_engine = existing_agents[0]
        else:
            agent_engine = agent_engines.create(display_name=agent_name)

        return VertexAiSessionService(
            project=project_id,
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
            agent_engine_id=agent_engine.resource_name.split("/")[-1],
        )

    raise ValueError("SESSION_BACKEND 僅支援 in_memory、postgres、agent_engine")


session_service = create_session_service()


# 定義執行器 (Runner)
runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)

# ========================================
# HTTP 端點
# ========================================


@app.get("/")
async def root():
    """提供 index.html 頁面。"""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄回饋。

    參數:
        feedback: 要記錄的回饋數據

    傳回值:
        成功訊息
    """
    gcloud_logger = _get_gcloud_logger()
    if gcloud_logger is not None:
        gcloud_logger.log_struct(feedback.model_dump(), severity="INFO")
    else:
        logger.info("feedback=%s", feedback.model_dump())
    return {"status": "success"}


# ========================================
# WebSocket 端點
# ========================================


@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
    proactivity: bool = False,
    affective_dialog: bool = False,
) -> None:
    """用於 ADK 雙向串流的 WebSocket 端點。

    參數:
        websocket: WebSocket 連線
        user_id: 用戶識別碼
        session_id: 會話識別碼
        proactivity: 啟用主動音訊 (僅限原生音訊模型)
        affective_dialog: 啟用情感對話 (僅限原生音訊模型)
    """
    logger.debug(
        f"WebSocket 連線請求: user_id={user_id}, session_id={session_id}, "
        f"proactivity={proactivity}, affective_dialog={affective_dialog}"
    )
    await websocket.accept()
    logger.debug("WebSocket 連線已接受")

    # ========================================
    # 第二階段：會話初始化 (每個串流會話執行一次)
    # ========================================

    # 根據模型架構自動決定回應模態 (Modality)
    # 原生音訊模型 (名稱中包含 "native-audio")
    # 僅支援 AUDIO 回應模態。
    # 半串聯 (Half-cascade) 模型支援 TEXT 和 AUDIO，
    # 我們預設使用 TEXT 以獲得更好的效能。
    model_name = agent.model
    is_native_audio = "native-audio" in model_name.lower()

    if is_native_audio:
        # 原生音訊模型需要 AUDIO 回應模態以及音訊轉錄
        response_modalities = ["AUDIO"]

        # 構建 RunConfig，包含選填的主動性和情感對話
        # 這些功能僅在原生音訊模型上支援
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(),
            proactivity=(
                types.ProactivityConfig(proactive_audio=True) if proactivity else None
            ),
            enable_affective_dialog=affective_dialog if affective_dialog else None,
        )
        logger.debug(
            f"檢測到原生音訊模型: {model_name}, "
            f"使用 AUDIO 回應模態, "
            f"proactivity={proactivity}, affective_dialog={affective_dialog}"
        )
    else:
        # 半串聯模型支援 TEXT 回應模態，效能較快
        response_modalities = ["TEXT"]
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            input_audio_transcription=None,
            output_audio_transcription=None,
            session_resumption=types.SessionResumptionConfig(),
        )
        logger.debug(f"檢測到半串聯模型: {model_name}, 使用 TEXT 回應模態")
        # 如果用戶嘗試啟用僅限原生音訊的功能，發出警告
        if proactivity or affective_dialog:
            logger.warning(
                f"主動性和情感對話僅在原生音訊模型上支援。當前模型: {model_name}。 "
                f"這些設定將被忽略。"
            )
    logger.debug(f"RunConfig 已建立: {run_config}")

    # 獲取或建立會話 (處理新會話和重新連線)
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

    live_request_queue = LiveRequestQueue()

    # ========================================
    # 第三階段：活躍會話 (並行雙向通訊)
    # ========================================

    async def upstream_task() -> None:
        """從 WebSocket 接收訊息並傳送到 LiveRequestQueue。"""
        logger.debug("upstream_task 已啟動")
        while True:
            # 從 WebSocket 接收訊息 (文字或二進位)
            message = await websocket.receive()

            # 處理二進位影格 (音訊數據)
            if "bytes" in message:
                audio_data = message["bytes"]
                logger.debug(f"收到二進位音訊區塊: {len(audio_data)} 位元組")

                audio_blob = types.Blob(
                    mime_type="audio/pcm;rate=16000", data=audio_data
                )
                live_request_queue.send_realtime(audio_blob)

            # 處理文字影格 (JSON 訊息)
            elif "text" in message:
                text_data = message["text"]
                logger.debug(f"收到文字訊息: {text_data[:100]}...")

                json_message = json.loads(text_data)

                # 從 JSON 提取文字並傳送到 LiveRequestQueue
                if json_message.get("type") == "text":
                    logger.debug(f"傳送文字內容: {json_message['text']}")
                    content = types.Content(
                        parts=[types.Part(text=json_message["text"])]
                    )
                    live_request_queue.send_content(content)

                # 處理圖像數據
                elif json_message.get("type") == "image":
                    logger.debug("收到圖像數據")

                    # 解碼 base64 圖像數據
                    image_data = base64.b64decode(json_message["data"])
                    mime_type = json_message.get("mimeType", "image/jpeg")

                    logger.debug(
                        f"傳送圖像: {len(image_data)} 位元組, 類型: {mime_type}"
                    )

                    # 將圖像作為 blob 傳送
                    image_blob = types.Blob(mime_type=mime_type, data=image_data)
                    live_request_queue.send_realtime(image_blob)

    async def downstream_task() -> None:
        """從 run_live() 接收事件並傳送到 WebSocket。"""
        logger.debug("downstream_task 已啟動，呼叫 runner.run_live()")
        logger.debug(f"開始 run_live，user_id={user_id}, session_id={session_id}")
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config,
        ):
            event_json = event.model_dump_json(exclude_none=True, by_alias=True)
            logger.debug(f"[SERVER] 事件: {event_json}")
            await websocket.send_text(event_json)
        logger.debug("run_live() 生成器已完成")

    # 並行執行兩個任務
    # 任何一個任務的異常都會傳播並取消另一個任務
    try:
        logger.debug("啟動 asyncio.gather 以執行上游和下游任務")
        await asyncio.gather(upstream_task(), downstream_task())
        logger.debug("asyncio.gather 正常完成")
    except WebSocketDisconnect:
        logger.debug("客戶端正常斷開連線")
    except Exception as e:
        logger.error(f"串流任務中發生非預期錯誤: {e}", exc_info=True)
    finally:
        # ========================================
        # 第四階段：會話終止
        # ========================================

        # 始終關閉隊列，即使發生異常
        logger.debug("正在關閉 live_request_queue")
        live_request_queue.close()


# 主程式執行
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
