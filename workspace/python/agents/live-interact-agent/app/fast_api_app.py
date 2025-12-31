import asyncio
import json
import logging
import os
from collections.abc import Callable
from pathlib import Path

import backoff
import google.auth
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.live_request_queue import LiveRequest, LiveRequestQueue
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.cloud import logging as google_cloud_logging
from vertexai.agent_engines import _utils
from websockets.exceptions import ConnectionClosedError

from .agent import app as adk_app
from .app_utils.telemetry import setup_telemetry
from .app_utils.typing import Feedback

# 初始化 FastAPI 應用程式
app = FastAPI()

# 設定 CORS 中介軟體，允許所有來源、方法和標頭
# 這是為了方便開發和跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 獲取前端建置目錄的路徑
current_dir = Path(__file__).parent
frontend_build_dir = current_dir.parent / "frontend" / "build"

# 如果建置目錄存在，則掛載靜態檔案
if frontend_build_dir.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(frontend_build_dir / "static")),
        name="static",
    )

# 初始化 Google Cloud Logging 客戶端
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
logging.basicConfig(level=logging.INFO)

# 設定遙測功能
setup_telemetry()
# 獲取專案 ID
_, project_id = google.auth.default()


# 初始化 ADK 服務
# Session Service: 管理使用者會話，這裡使用記憶體儲存
session_service = InMemorySessionService()

# Artifact Service: 管理檔案等產出物
# 如果設定了 LOGS_BUCKET_NAME 環境變數，則使用 GCS 儲存，否則使用記憶體儲存
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
artifact_service = (
    GcsArtifactService(bucket_name=logs_bucket_name)
    if logs_bucket_name
    else InMemoryArtifactService()
)
# Memory Service: 管理對話記憶，這裡使用記憶體儲存
memory_service = InMemoryMemoryService()

# 初始化 ADK 執行器 (Runner)
# 將應用程式邏輯與各種服務結合
runner = Runner(
    app=adk_app,
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service,
)


class AgentSession:
    """管理客戶端與代理程式之間的雙向通訊會話。"""

    def __init__(self, websocket: WebSocket) -> None:
        """初始化代理程式會話。

        Args:
            websocket: 客戶端 WebSocket 連線
        """
        self.websocket = websocket
        # 用於緩衝從客戶端接收到的訊息
        self.input_queue: asyncio.Queue[dict] = asyncio.Queue()
        self.user_id: str | None = None
        self.session_id: str | None = None

    async def receive_from_client(self) -> None:
        """監聽來自客戶端的訊息並將其放入佇列。"""
        while True:
            try:
                message = await self.websocket.receive()

                if "text" in message:
                    data = json.loads(message["text"])

                    if isinstance(data, dict):
                        # 跳過設定訊息 (setup messages) - 僅用於後端日誌記錄
                        if "setup" in data:
                            logger.log_struct(
                                {**data["setup"], "type": "setup"}, severity="INFO"
                            )
                            logging.info("收到設定訊息 (不轉發給代理程式)")
                            continue

                        # 將訊息轉發給代理引擎
                        await self.input_queue.put(data)
                    else:
                        logging.warning(f"收到來自客戶端的意外 JSON 結構: {data}")

                elif "bytes" in message:
                    # 處理二進位數據 (如音訊流)
                    await self.input_queue.put({"binary_data": message["bytes"]})

                else:
                    logging.warning(f"收到來自客戶端的意外訊息類型: {message}")

            except ConnectionClosedError as e:
                logging.warning(f"客戶端關閉了連線: {e}")
                break
            except json.JSONDecodeError as e:
                logging.error(f"解析來自客戶端的 JSON 時發生錯誤: {e}")
                break
            except Exception as e:
                logging.error(f"接收來自客戶端的訊息時發生錯誤: {e!s}")
                break

    async def run_agent(self) -> None:
        """使用雙向串流協定 (bidi_stream_query) 執行代理程式。"""
        try:
            # 立即發送 setupComplete 回應
            setup_complete_response: dict = {"setupComplete": {}}
            await self.websocket.send_json(setup_complete_response)

            # 等待第一個帶有 user_id 的請求
            first_request = await self.input_queue.get()
            self.user_id = first_request.get("user_id")
            if not self.user_id:
                raise ValueError("第一個請求必須包含 user_id。")

            self.session_id = first_request.get("session_id")
            first_live_request = first_request.get("live_request")

            # 如果需要，建立新會話
            if not self.session_id:
                session = await session_service.create_session(
                    app_name=adk_app.name,
                    user_id=self.user_id,
                )
                self.session_id = session.id

            # 建立 LiveRequestQueue 用於與代理程式通訊
            live_request_queue = LiveRequestQueue()

            # 如果存在第一個即時請求，將其加入佇列
            if first_live_request and isinstance(first_live_request, dict):
                live_request_queue.send(LiveRequest.model_validate(first_live_request))

            # 將請求從 input_queue 轉發到 live_request_queue
            async def _forward_requests() -> None:
                while True:
                    request = await self.input_queue.get()
                    live_request = LiveRequest.model_validate(request)
                    live_request_queue.send(live_request)

            # 將事件從代理程式轉發到 WebSocket
            async def _forward_events() -> None:
                # 執行即時代理程式
                events_async = runner.run_live(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    live_request_queue=live_request_queue,
                )
                # 迭代處理代理程式產生的事件
                async for event in events_async:
                    event_dict = _utils.dump_event_for_json(event)
                    await self.websocket.send_json(event_dict)

                    # 檢查錯誤回應
                    if isinstance(event_dict, dict) and "error" in event_dict:
                        logging.error(f"代理程式錯誤: {event_dict['error']}")
                        break

            # 同時執行兩個任務 (轉發請求和轉發事件)
            requests_task = asyncio.create_task(_forward_requests())

            try:
                await _forward_events()
            finally:
                # 確保請求轉發任務被取消
                requests_task.cancel()
                try:
                    await requests_task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            logging.error(f"代理程式執行錯誤: {e}")
            await self.websocket.send_json({"error": str(e)})


def get_connect_and_run_callable(websocket: WebSocket) -> Callable:
    """建立一個可呼叫物件，處理具有重試邏輯的代理程式連線。

    Args:
        websocket: 客戶端 WebSocket 連線

    Returns:
        Callable: 一個非同步函式，用於建立和管理代理程式連線
    """

    async def on_backoff(details: backoff._typing.Details) -> None:
        await websocket.send_json(
            {"status": f"模型連線錯誤，將於 {details['wait']} 秒後重試..."}
        )

    @backoff.on_exception(
        backoff.expo, ConnectionClosedError, max_tries=10, on_backoff=on_backoff
    )
    async def connect_and_run() -> None:
        logging.info("啟動 ADK 代理程式")
        session = AgentSession(websocket)

        logging.info("開始與代理程式進行雙向通訊")
        await asyncio.gather(
            session.receive_from_client(),
            session.run_agent(),
        )

    return connect_and_run


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """處理新的 WebSocket 連線。"""
    await websocket.accept()
    connect_and_run = get_connect_and_run_callable(websocket)
    await connect_and_run()


@app.get("/")
async def serve_frontend_root() -> FileResponse:
    """在根路徑提供前端 index.html。"""
    index_file = frontend_build_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(
        status_code=404,
        detail="前端尚未建置。請在 frontend 目錄中執行 'npm run build'。",
    )


@app.get("/{full_path:path}")
async def serve_frontend_spa(full_path: str) -> FileResponse:
    """處理所有其他路徑的前端 SPA 路由。

    這確保了客戶端路由由 React 應用程式處理。
    排除 API 路由 (ws, feedback) 和靜態資源。
    """
    # 不攔截 API 路由
    if full_path.startswith(("ws", "feedback", "static", "api")):
        raise HTTPException(status_code=404, detail="找不到路徑")

    # 為所有其他路由提供 index.html (SPA 路由)
    index_file = frontend_build_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(
        status_code=404,
        detail="前端尚未建置。請在 frontend 目錄中執行 'npm run build'。",
    )


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """收集並記錄回饋。

    Args:
        feedback: 要記錄的回饋資料

    Returns:
        成功訊息
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# 主要執行區塊
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
