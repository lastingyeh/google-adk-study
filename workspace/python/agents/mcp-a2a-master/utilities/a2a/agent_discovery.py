"""
重點摘要:
- **核心概念**: A2A 代理發現 (Discovery)。
- **關鍵技術**: JSON 設定檔, HTTP 請求, A2A Protocol (/.well-known/agent.json)。
- **重要結論**: 實作了一個簡單的基於檔案的發現機制，用於定位網路上的其他 Agent。
"""

import json
import os
import asyncio
import logging
from typing import Optional
from a2a.types import AgentCard

from a2a.client import A2ACardResolver

import httpx

# 設定日誌記錄器
logger = logging.getLogger(__name__)


class AgentDiscovery:
    """
    透過讀取 URL 的註冊檔並查詢每一個 URL 的 /.well-known/agent.json 端點來檢索 AgentCard，
    藉此發現 A2A 代理。

    Attributes:
        registry_file (str): 代理註冊檔案的路徑。 (Path to the agent registry file.)
        base_urls (List[str]): A2A 代理的基本 URL 列表。 (List of base URLs for A2A Agents.)
    """

    def __init__(self, registry_file: str = None):
        """
        初始化 AgentDiscovery。
        Initialise the AgentDiscovery

        Args:
            registry_file (str): 代理註冊檔案的路徑。 (Path to the agent registry file.)
                預設為 'utilities/a2a/agent_registry.json'。 (Defaults to 'utilities/a2a/agent_registry.json'.)
        """
        if registry_file:
            self.registry_file = registry_file
        else:
            self.registry_file = os.path.join(
                os.path.dirname(__file__), "agent_registry.json"
            )
        self.base_urls = self._load_registry()

    def _load_registry(self) -> list[str]:
        """
        載入並解析註冊 JSON 檔案為 URL 列表。
        Load and parse the registry JSON file into a list of URLs

        Returns:
            list[str]: A2A 代理的基本 URL 列表。 (List of base URLs for A2A Agents.)
        """
        try:
            with open(self.registry_file, "r") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(
                    "註冊檔必須包含 URL 列表。 (Registry file must contain a list of URLs.)"
                )
            return data
        except FileNotFoundError:
            print(f"找不到註冊檔 (Registry file) '{self.registry_file}'。")
            return []
        except (json.JSONDecodeError, ValueError) as e:
            print(f"解析註冊檔時發生錯誤 (Error parsing registry file): {e}")
            return []

    async def list_agent_cards(self) -> list[AgentCard]:
        """
        非同步地從註冊表中的每個基本 URL 獲取 AgentCard。
        Asynchronously fetches AgentCards from each
        base URL in the registry.

        Returns:
            list[AgentCard]: 從代理檢索到的 AgentCard 列表。 (List of AgentCards retrieved from the agents.)

        Note:
            - 使用並行請求提升效能 (Uses concurrent requests for better performance)
            - 單一 Agent 失敗不會影響其他 Agent (Individual agent failures won't affect others)
            - 自動記錄成功與失敗的結果 (Automatically logs success and failure results)
        """
        if not self.base_urls:
            logger.warning(
                "註冊表為空,沒有要查詢的 Agent URL。 (Registry is empty, no agent URLs to query.)"
            )
            return []

        cards: list[AgentCard] = []

        async with httpx.AsyncClient(timeout=300.0) as httpx_client:
            # 建立所有的非同步任務
            tasks = [
                self._fetch_agent_card(base_url, httpx_client)
                for base_url in self.base_urls
            ]

            # 並行執行所有任務
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 處理結果
            for base_url, result in zip(self.base_urls, results):
                if isinstance(result, Exception):
                    logger.error(
                        f"從 {base_url} 獲取 AgentCard 失敗: {result} "
                        f"(Failed to fetch AgentCard from {base_url}: {result})"
                    )
                elif result is not None:
                    cards.append(result)
                    logger.info(
                        f"成功從 {base_url} 獲取 AgentCard (Successfully fetched AgentCard from {base_url})"
                    )

        logger.info(
            f"共獲取 {len(cards)}/{len(self.base_urls)} 個 AgentCard (Fetched {len(cards)}/{len(self.base_urls)} AgentCards)"
        )
        return cards

    async def _fetch_agent_card(
        self, base_url: str, httpx_client: httpx.AsyncClient
    ) -> Optional[AgentCard]:
        """
        從單一 base URL 獲取 AgentCard (輔助方法)。
        Fetches an AgentCard from a single base URL (helper method).

        Args:
            base_url (str): Agent 的基本 URL。 (The base URL of the agent.)
            httpx_client (httpx.AsyncClient): 共用的 HTTP 客戶端。 (Shared HTTP client.)

        Returns:
            Optional[AgentCard]: 成功時返回 AgentCard,失敗時返回 None。
                                 (Returns AgentCard on success, None on failure.)

        Raises:
            Exception: 傳遞任何在獲取過程中發生的異常。 (Propagates any exceptions during fetching.)
        """
        try:
            resolver = A2ACardResolver(
                base_url=base_url.rstrip("/"), httpx_client=httpx_client
            )
            card = await resolver.get_agent_card()
            return card
        except httpx.TimeoutException as e:
            logger.error(f"請求 {base_url} 超時 (Timeout requesting {base_url}): {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP 錯誤來自 {base_url}: {e.response.status_code} (HTTP error from {base_url}: {e.response.status_code})"
            )
            raise
        except Exception as e:
            logger.error(
                f"從 {base_url} 獲取 AgentCard 時發生未預期的錯誤 (Unexpected error fetching AgentCard from {base_url}): {e}"
            )
            raise
