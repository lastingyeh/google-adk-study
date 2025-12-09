"""
重點摘要:
- **核心概念**: A2A 代理連接器 (Connector)。
- **關鍵技術**: A2A Client SDK, HTTPX。
- **重要結論**: 封裝了與遠端 A2A 代理通訊的細節，包括建構請求 payload 和處理回應。

設計模式:
- **單一職責原則 (SRP)**: 專注於處理與單一遠端 Agent 的通訊
- **依賴注入**: 透過 AgentCard 注入 Agent 的連接資訊
- **錯誤處理**: 優雅處理回應解析失敗的情況
"""

from typing import Any, Optional
from uuid import uuid4
from a2a.types import AgentCard, Task, SendMessageRequest, MessageSendParams
import httpx
from a2a.client import A2AClient
import logging

# 設定日誌記錄器
logger = logging.getLogger(__name__)


class AgentConnector:
    """
    A2A 代理連接器 - 封裝與遠端 A2A 代理的通訊邏輯
    Connects to a remote A2A agent and provides a uniform method to delegate tasks

    職責 (Responsibilities):
    1. 管理與單一遠端 Agent 的連接配置
    2. 建構符合 A2A 協議的訊息請求
    3. 處理非同步 HTTP 通訊
    4. 解析並驗證 Agent 回應

    使用範例 (Usage Example):
        connector = AgentConnector(agent_card)
        response = await connector.send_task("請幫我分析這段代碼", session_id="123")
    """

    def __init__(self, agent_card: AgentCard):
        """
        初始化 Agent 連接器

        Args:
            agent_card (AgentCard): A2A Agent 的識別卡片,包含連接所需的元資料
                - 包含 Agent 的 URL、能力描述、版本等資訊
                - 通常由 AgentDiscovery 服務提供
        """
        self.agent_card = agent_card
        logger.info(f"初始化 AgentConnector,目標 Agent: {agent_card.url}")

    async def send_task(self, message: str, session_id: str) -> str:
        """
        傳送任務給遠端 Agent 並等待回應
        Send a task to the agent and return the response text

        執行流程 (Execution Flow):
        1. 建立非同步 HTTP 客戶端 (支援長時間等待,最多 5 分鐘)
        2. 初始化 A2A 客戶端並綁定 AgentCard
        3. 建構符合 A2A 協議的訊息 payload
        4. 發送請求並等待 Agent 處理
        5. 解析回應並提取文字內容

        Args:
            message (str): 要傳送給代理的訊息內容 (The message to send to the agent)
                - 可以是問題、指令或任何文字輸入
                - 應該清楚表達使用者意圖
            session_id (str): 工作階段 ID,用於追蹤對話上下文 (The session ID for tracking the conversation)
                - 同一 session_id 可串聯多輪對話
                - 建議使用 UUID 或其他唯一識別碼

        Returns:
            str: Agent 的回應文字 (The response text from the agent)
                - 成功時返回 Agent 處理後的回應
                - 失敗時返回錯誤訊息

        Raises:
            httpx.TimeoutException: 當請求超過 300 秒時
            httpx.HTTPError: 當 HTTP 請求失敗時

        技術細節 (Technical Details):
        - 使用非同步上下文管理器確保資源正確釋放
        - Timeout 設定為 300 秒,適合處理複雜任務
        - 訊息格式遵循 A2A Protocol 規範
        """

        logger.info(f"發送任務到 Agent (session: {session_id}): {message[:50]}...")

        try:
            # 步驟 1: 建立非同步 HTTP 客戶端
            # 使用 context manager 確保連接正確關閉
            async with httpx.AsyncClient(timeout=300.0) as httpx_client:

                # 步驟 2: 初始化 A2A 客戶端
                # 綁定特定的 AgentCard,確保請求發送到正確的 Agent
                a2a_client = A2AClient(
                    httpx_client=httpx_client,
                    agent_card=self.agent_card,
                )

                # 步驟 3: 建構訊息 payload
                # 遵循 A2A Protocol 的訊息格式規範
                send_message_payload: dict[str, Any] = {
                    "message": {
                        "role": "user",  # 訊息來源角色
                        "messageId": str(uuid4()),  # 唯一訊息 ID,用於追蹤和去重
                        "parts": [  # 訊息可包含多個部分 (文字、圖片等)
                            {
                                "text": message,  # 實際訊息內容
                                "kind": "text",  # 內容類型
                            }
                        ],
                    }
                }

                # 步驟 4: 建立發送請求物件
                # 包裝 payload 為標準的 SendMessageRequest
                request = SendMessageRequest(
                    id=str(uuid4()),  # 請求 ID
                    params=MessageSendParams(**send_message_payload),
                )

                # 步驟 5: 發送訊息並等待回應
                logger.debug(f"正在等待 Agent 回應...")
                response = await a2a_client.send_message(request=request)

                # 步驟 6: 轉換回應為字典格式便於處理
                response_data = response.model_dump(mode="json", exclude_none=True)

                # 步驟 7: 安全地提取回應文字
                # 使用 try-except 處理可能的結構變化或缺失欄位
                try:
                    agent_response = response_data["result"]["status"]["message"]["parts"][0]["text"]
                    logger.info(
                        f"成功接收 Agent 回應 (長度: {len(agent_response)} 字元)"
                    )
                except (KeyError, IndexError) as e:
                    # 當回應結構不符合預期時的錯誤處理
                    logger.error(f"無法解析 Agent 回應: {e}")
                    logger.debug(f"回應資料結構: {response_data}")
                    agent_response = "沒有來自代理的回應 (No response from agent)"

                return agent_response

        except httpx.TimeoutException as e:
            # 處理超時錯誤
            error_msg = f"請求超時 (Timeout after 300s): {str(e)}"
            logger.error(error_msg)
            return f"錯誤: {error_msg}"
        except httpx.HTTPError as e:
            # 處理 HTTP 相關錯誤
            error_msg = f"HTTP 請求失敗: {str(e)}"
            logger.error(error_msg)
            return f"錯誤: {error_msg}"
        except Exception as e:
            # 處理其他未預期的錯誤
            error_msg = f"未預期的錯誤: {str(e)}"
            logger.exception(error_msg)
            return f"錯誤: {error_msg}"
