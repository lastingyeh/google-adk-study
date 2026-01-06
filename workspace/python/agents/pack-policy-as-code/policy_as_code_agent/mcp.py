import logging
import subprocess
from typing import Any, List

import google.auth
import google.auth.transport.requests
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.oauth2 import id_token

from .config import DATAPLEX_MCP_SERVER_URL


class SafeMCPToolset(McpToolset):
    """SafeMCPToolset

    這個類別是對 :class:`McpToolset` 的安全封裝，用來在取得 MCP 工具時
    捕捉連線相關的例外狀況。

    目的：
    - 如果 MCP 伺服器掛掉、無法連線或回傳錯誤，代理程式仍然可以繼續執行。
    - 在發生錯誤時，不讓整個應用程式因為工具載入失敗而崩潰，只是單純
        不提供 MCP 工具（回傳空陣列）。
    """

    async def get_tools(self, *args: Any, **kwargs: Any) -> List[Any]:
        try:
            # 嘗試呼叫父類別的 get_tools，實際向 MCP 伺服器請求可用工具清單。
            return await super().get_tools(*args, **kwargs)
        except Exception as e:
            # 若發生任何例外（例如網路錯誤、伺服器錯誤、權限問題等），
            # 在日誌中記錄錯誤訊息，並改以空清單取代，以避免程式中斷。
            logging.error(f"Failed to connect to MCP server or retrieve tools: {e}")
            logging.warning("Continuing without MCP tools.")
            return []


def _get_dataplex_mcp_toolset():
    """建立 Dataplex MCP 伺服器的工具集合 (McpToolset)。

    此函式會使用 **ID Token 驗證** 方式連線到 Dataplex MCP 伺服器，
    並回傳一個包裝過的 :class:`SafeMCPToolset` 物件。

    驗證流程說明：
    1. 優先透過 ``gcloud auth print-identity-token`` 取得目前使用者的 ID Token，
       適用於本機開發、人類使用者情境。
    2. 若 gcloud 無法取得 Token，則改用 ``google-auth`` 函式庫（例如服務帳號、
       GCE/GKE metadata server）取得 ID Token。
    3. 若兩種方式皆失敗，回傳 ``None``，代表不註冊 MCP 工具集合。
    """
    if not DATAPLEX_MCP_SERVER_URL:
        # 若未設定 MCP 伺服器 URL，表示不啟用 MCP 整合，直接記錄資訊並返回 None。
        logging.info(
            "DATAPLEX_MCP_SERVER_URL not configured. Skipping MCP toolset registration."
        )
        return None

    # MCP SSE 端點 URL（伺服器會透過 Server-Sent Events 提供工具互動通道）。
    mcp_url = f"{DATAPLEX_MCP_SERVER_URL}/sse"
    token = None

    # 優先嘗試：使用 gcloud 取得 ID Token（適合本機使用者登入情境）。
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token"], text=True
        ).strip()
    except Exception as e:
        # 若 gcloud 不存在、尚未登入或其他錯誤，記錄警告但不結束流程，
        # 後續會改用 google-auth 嘗試取得 Token。
        logging.warning(f"Failed to get ID token via gcloud: {e}")

    # 後備方案：使用 google-auth 函式庫（服務帳號、metadata server 等情境）。
    if not token:
        try:
            auth_req = google.auth.transport.requests.Request()
            # 將 Dataplex MCP 伺服器的根 URL 作為 ID Token 的 audience。
            target_audience = DATAPLEX_MCP_SERVER_URL
            token = id_token.fetch_id_token(auth_req, target_audience)
        except Exception as e:
            # 若仍然無法取得 Token，代表無法對 MCP 伺服器進行授權存取，
            # 直接記錄錯誤並返回 None，表示不啟用 MCP 工具。
            logging.error(f"Failed to get ID token for MCP server via library: {e}")
            return None

    # 建立 SafeMCPToolset，並透過 SseConnectionParams 將 URL 與 Authorization 標頭
    # （包含 Bearer Token）一併傳入，以完成與 MCP 伺服器的安全連線設定。
    return SafeMCPToolset(
        connection_params=SseConnectionParams(
            url=mcp_url, headers={"Authorization": f"Bearer {token}"}
        )
    )
