# main.py
"""
Not-Chat-GPT Agent 啟動入口點

此腳本確保 Redis 會話服務在 ADK CLI 啟動「之前」註冊到服務註冊表。
這是使用自定義會話服務的關鍵步驟，避免 ADK 降級到預設的 DatabaseSessionService。

使用方式：
    uv run python backend/main.py web agents --session_service_uri=redis://localhost:6379/0
"""

import sys
from pathlib import Path

from google.adk.cli import cli_tools_click
from google.adk.cli.service_registry import get_service_registry

# 將 service 目錄加入 Python 路徑，以便匯入 RedisSessionService
service_path = Path(__file__).parent.parent / "service"
sys.path.insert(0, str(service_path))

from redis_session_service import RedisSessionService

# ============================================================================
# 服務註冊 (在 ADK CLI 初始化之前執行)
# ============================================================================

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


# 取得 ADK 服務註冊表
registry = get_service_registry()

# 註冊 Redis 會話服務，將 "redis://" scheme 映射到 redis_factory
# 這樣當使用 --session_service_uri=redis://... 時，ADK 就會呼叫我們的工廠函式
registry.register_session_service("redis", redis_factory)

print("✅ Redis 會話服務已註冊到 ADK 服務註冊表")
print("💡 使用方式：--session_service_uri=redis://localhost:6379/0\n")


# ============================================================================
# 主程式入口
# ============================================================================

if __name__ == '__main__':
    # 啟動 ADK CLI (此時 Redis 服務已註冊完成)
    cli_tools_click.main()