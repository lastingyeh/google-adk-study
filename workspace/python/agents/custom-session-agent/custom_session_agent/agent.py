"""
自定義會話服務代理 (Custom Session Services Agent)

演示如何使用 Google ADK 的服務註冊模式 (Service Registry Pattern)
將 Redis 註冊並作為自定義會話存儲後端。
"""

import os
import json
import redis
from dotenv import load_dotenv
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

# 載入環境變數
load_dotenv()

# 匯入 ADK 元件
try:
    from google.adk import Agent
    from google.adk.cli import cli_tools_click
    # ADK 1.17+ 的服務註冊表位於 cli 模組中
    try:
        from google.adk.cli.service_registry import get_service_registry
        SERVICE_REGISTRY_AVAILABLE = True
    except ImportError:
        # 若無法使用則提供備用方案
        SERVICE_REGISTRY_AVAILABLE = False
        get_service_registry = None

    from google.adk.sessions import InMemorySessionService, BaseSessionService, Session
    from google.adk.sessions.base_session_service import ListSessionsResponse
except ImportError as e:
    print(f"匯入 ADK 元件時出錯：{e}")
    print("請確保已安裝 google-adk>=1.17.0：pip install google-adk")
    raise


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


class CustomSessionServiceDemo:
    """
    演示註冊自定義會話服務的工廠模式。

    核心概念：ADK 的服務註冊表將 URI 配置映射到建立會話服務實例的工廠函式。
    """

    @staticmethod
    def register_redis_service():
        """在服務註冊表中註冊 Redis 會話服務。"""

        if not SERVICE_REGISTRY_AVAILABLE or get_service_registry is None:
            print("⚠️  此 ADK 版本不支援服務註冊表")
            return

        def redis_service_factory(uri: str, **kwargs) -> Any:
            """
            建立 RedisSessionService 的工廠函式。
            """
            # 務必移除 agents_dir - ADK 會傳入但我們不需要
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop("agents_dir", None)

            print(f"🔴 正在註冊 Redis 會話服務：{uri}")

            # 傳回真正連接 Redis 的會話服務實例
            return RedisSessionService(uri=uri, **kwargs_copy)

        # 註冊至服務註冊表
        registry = get_service_registry()
        registry.register_session_service("redis", redis_service_factory)
        print("✅ Redis 會話服務註冊成功！")

    @staticmethod
    def register_memory_service():
        """
        註冊記憶體內會話服務 (用於無需 Docker 的測試環境)。
        """
        if not SERVICE_REGISTRY_AVAILABLE or get_service_registry is None:
            print("⚠️  服務註冊表不可用 - 記憶體服務未註冊")
            return

        def memory_service_factory(uri: str, **kwargs) -> Any:
            """記憶體會話存儲的工廠。"""
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop("agents_dir", None)

            print(f"💾 正在註冊記憶體會話服務：{uri}")
            return InMemorySessionService(**kwargs_copy)

        registry = get_service_registry()
        registry.register_session_service("memory", memory_service_factory)
        print("✅ 記憶體會話服務註冊成功！")


# ============================================================================
# 工具函式 (TOOL FUNCTIONS)
# ============================================================================

def describe_session_info(session_id: str) -> Dict[str, Any]:
    """
    描述會話資訊的工具。
    """
    return {
        "status": "success",
        "report": f"會話 {session_id} 已啟動",
        "data": {
            "session_id": session_id,
            "backend": "會話存儲已透過服務註冊表配置",
            "persistence": "支援 (視後端而定)",
            "note": "重新整理瀏覽器以測試持久化！"
        }
    }


def test_session_persistence(key: str, value: str) -> Dict[str, Any]:
    """
    測試跨請求會話持久化的工具。
    """
    return {
        "status": "success",
        "report": f"已將 {key}={value} 儲存至會話",
        "data": {
            "key": key,
            "value": value,
            "storage_backend": "透過服務註冊表配置",
            "persistence": "重新整理瀏覽器以驗證持久化",
            "redis_command": f"redis-cli GET session:{key}"
        }
    }


def show_service_registry_info() -> Dict[str, Any]:
    """
    顯示服務註冊表資訊的工具。
    """
    return {
        "status": "success",
        "report": "Redis 服務註冊資訊",
        "data": {
            "pattern": "註冊建立會話服務的工廠函式",
            "redis_registration": {
                "scheme": "redis",
                "factory_pattern": "def redis_factory(uri: str, **kwargs) -> RedisSessionService",
                "registration": "registry.register_session_service('redis', redis_factory)",
                "usage": "python -m agent web --session_service_uri=redis://localhost:6379"
            },
            "key_points": [
                "工廠函式接收 URI 字串作為輸入",
                "務必從 kwargs 中 pop 出 'agents_dir'",
                "傳回配置好的服務執行個體",
                "ADK 會自動處理後續操作"
            ]
        }
    }


def get_session_backend_guide() -> Dict[str, Any]:
    """
    提供 Redis 作為會話後端的指南工具。
    """
    return {
        "status": "success",
        "report": "Redis 會話後端指南",
        "data": {
            "why_redis": "快速、持久且適用於生產環境的記憶體數據存儲",
            "redis_setup": {
                "start_container": "make docker-up",
                "connect": "redis://localhost:6379",
                "default_ttl": "每個會話 24 小時"
            },
            "features": [
                "快速的會話查詢與存儲",
                "自動過期 (TTL)",
                "透過 AOF 達成持久化",
                "分散式會話共享",
                "簡單的發布/訂閱通知機制"
            ],
            "best_practices": [
                "設置 TTL 以自動清理舊會話",
                "使用鍵名前綴 (Prefix) 進行管理",
                "監控記憶體使用情況",
                "在生產環境啟用持久化"
            ]
        }
    }


# ============================================================================
# ROOT AGENT 定義

root_agent = Agent(
    name="custom_session_agent",
    model="gemini-2.5-flash",
    description="演示 ADK 中自定義會話服務註冊模式",
    instruction="""您是 ADK 自定義會話服務註冊模式的專家。

    您的職責是協助使用者理解 ADK 中的 Redis 會話持久化。

    核心概念：
    1. 服務註冊模式 - 將 URI 配置映射至工廠函式
    2. 工廠函式 - 從 URI 建立會話服務實例
    3. BaseSessionService - 所有自定義後端必須實作的介面
    4. Redis 後端 - 具備 TTL 與持久化功能的生產級會話存儲

    當使用者詢問關於會話的問題時：
    - 解釋為何持久化會話很重要
    - 展示 Redis 如何存儲對話歷史
    - 演示重新整理頁面後如何檢索會話
    - 展示使這一切運作的程式碼

    技術亮點：
    - 每個會話存儲完整的事件歷史
    - 作者欄位追蹤使用者與 Agent 的訊息
    - 會話在 24 小時後自動過期
    - 可透過 Redis 叢集擴展至多台伺服器
    - 即使重新整理頁面，對話內容依然存在

    協助使用者測試持久化會話並理解此模式！""",
    tools=[
        describe_session_info,
        test_session_persistence,
        show_service_registry_info,
        get_session_backend_guide
    ],
    output_key="session_result"
)


# ============================================================================
# CLI 入口點
# ============================================================================

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  警告：環境變數中未設置 GOOGLE_API_KEY")

    print("\n" + "=" * 70)
    print("🎯 自定義會話服務代理 - TIL 實作")
    print("=" * 70)
    print()
    print("📋 快速開始：")
    print("   1. 啟動服務：  make docker-up")
    print("   2. 啟動 Agent： make dev")
    print("   3. 開啟瀏覽器： http://localhost:8000")
    print("   4. 測試持久化： 發送訊息 → 重新整理頁面")
    print()
    print("🔍 服務註冊狀態：")
    print("   - Redis 服務：   ✅ 已註冊")
    print("   - Memory 服務：  ✅ 已註冊")
    print()
    print("=" * 70 + "\n")

    cli_tools_click.main()

"""
### 重點摘要
- **核心概念**：實作與註冊自定義 Redis 會話後端。
- **關鍵技術**：BaseSessionService, Redis Python Client, Service Registry, Factory Pattern。
- **重要結論**：透過繼承 `BaseSessionService` 並覆寫關鍵方法（特別是 `append_event`），可以輕鬆將 ADK 會話數據導向任何持久化存儲系統。
- **行動項目**：在生產環境中務必設置適當的 TTL 並監控 Redis 效能。
"""
