import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from google.adk.sessions import BaseSessionService, Session
from google.adk.sessions.base_session_service import ListSessionsResponse

# ============================================================================
# 自定義會話服務實作 (CUSTOM SESSION SERVICE IMPLEMENTATIONS)
# ============================================================================

class RedisSessionService(BaseSessionService):
    """
    可用於生產環境的 Redis 會話存儲後端。

    實作 BaseSessionService 介面以將會話存儲於 Redis。
    演示如何使用真實運作的後端來實踐服務註冊模式。
    """

    def __init__(self, uri: str = "redis://localhost:6379/0", **kwargs):
        """
        初始化 Redis 會話服務。

        參數：
            uri: Redis 連線 URI (例如：redis://localhost:6379/0)
            **kwargs: 其他選項 (ADK 會傳遞 agents_dir 但此處不需要)
        """
        self.redis_uri = uri
        self.redis_client = None
        self._connect_to_redis()

    def _connect_to_redis(self):
        """使用提供的 URI 連接至 Redis。"""
        try:
            import redis
            # 解析 URI 並建立連線
            self.redis_client = redis.from_url(
                self.redis_uri,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # 測試連線
            self.redis_client.ping()
            print(f"✅ 已連接至 Redis：{self.redis_uri}")
        except Exception as e:
            print(f"❌ 無法連接至 Redis：{e}")
            print("   正在切換回記憶體內存儲 (In-memory storage)")
            self.redis_client = None

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ):
        """建立新會話並將其存儲於 Redis。"""
        if not session_id:
            session_id = str(uuid.uuid4())

        # 建立會話數據結構
        session_data = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "state": state or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "events": []
        }

        if self.redis_client:
            try:
                # 以 JSON 格式存儲於 Redis
                key = f"session:{app_name}:{user_id}:{session_id}"
                self.redis_client.set(key, json.dumps(session_data), ex=86400)  # 24小時過期
                print(f"   📝 會話已存儲於 Redis：{key}")
            except Exception as e:
                print(f"   ⚠️  無法將會話存儲於 Redis：{e}")

        # 建立並傳回 Session 物件
        from google.adk.sessions import Session
        return Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=session_data.get("state", {}),
            events=[]
        )

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[Any] = None,
    ):
        """從 Redis 檢索會話。"""
        if not self.redis_client:
            return None

        try:
            key = f"session:{app_name}:{user_id}:{session_id}"
            session_json = self.redis_client.get(key)

            if not session_json:
                return None

            session_data = json.loads(session_json)

            return Session(
                id=session_id,
                app_name=app_name,
                user_id=user_id,
                state=session_data.get("state", {}),
                events=session_data.get("events", []),
                last_update_time=0
            )
        except Exception as e:
            print(f"   ⚠️  從 Redis 檢索會話時失敗：{e}")
            return None

    async def list_sessions(
        self, *, app_name: str, user_id: Optional[str] = None
    ) -> ListSessionsResponse:
        """列出 Redis 中的所有會話。"""
        if not self.redis_client:
            return ListSessionsResponse(sessions=[])

        try:
            pattern = f"session:{app_name}:{user_id or '*'}:*" if user_id else f"session:{app_name}:*"
            keys = self.redis_client.keys(pattern)

            sessions = []
            for key in keys:
                session_json = self.redis_client.get(key)
                if session_json:
                    session_data = json.loads(session_json)

                    # 重建 Session 物件並進行欄位映射
                    # Redis 存儲為 session_id，但 Session 模型預期為 id
                    session = Session(
                        id=session_data.get("session_id"),
                        app_name=session_data.get("app_name"),
                        user_id=session_data.get("user_id"),
                        state=session_data.get("state", {}),
                        events=[],  # 將從事件數據重建
                        last_update_time=0
                    )
                    sessions.append(session)

            return ListSessionsResponse(sessions=sessions)
        except Exception as e:
            print(f"   ⚠️  從 Redis 列出會話時失敗：{e}")
            return ListSessionsResponse(sessions=[])

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        """從 Redis 刪除會話。"""
        if not self.redis_client:
            return

        try:
            key = f"session:{app_name}:{user_id}:{session_id}"
            self.redis_client.delete(key)
            print(f"   🗑️  已從 Redis 刪除會話：{key}")
        except Exception as e:
            print(f"   ⚠️  從 Redis 刪除會話時失敗：{e}")

    async def append_event(self, session: Session, event) -> Any:
        """
        將事件附加至會話並儲存到 Redis。

        這是關鍵方法，負責將對話數據（如詩詞、使用者訊息等）存儲到 Redis。
        若不覆寫此方法，事件將僅存儲於記憶體中。
        """
        # 調用基礎實作以處理事件（更新記憶體中的會話狀態）
        event = await super().append_event(session=session, event=event)

        # 接著將更新後的會話存儲到 Redis
        try:
            app_name = session.app_name
            user_id = session.user_id
            session_id = session.id

            key = f"session:{app_name}:{user_id}:{session_id}"

            # 轉換會話為 JSON 格式
            session_data = {
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
                "state": dict(session.state),
                "created_at": session.created_at.isoformat() if hasattr(session, 'created_at') else datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "id": e.id,
                        "timestamp": e.timestamp,
                        "partial": e.partial,
                        "author": e.author if hasattr(e, 'author') else "unknown",
                        "actions": {
                            "state_delta": e.actions.state_delta if e.actions else {}
                        } if e.actions else {}
                    }
                    for e in session.events
                ]
            }

            # 存儲至 Redis 並設置 24 小時過期時間
            if self.redis_client:
                self.redis_client.set(key, json.dumps(session_data), ex=86400)

        except Exception as e:
            print(f"   ⚠️  將事件儲存至 Redis 時失敗：{e}")

        return event
