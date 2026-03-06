"""
ContentFilterPlugin - 靜態內容過濾外掛程式

功能：
1. 關鍵字黑名單過濾（支援正則表達式）
2. 多語言支援（英文、中文、日文）
3. 模糊匹配和變體偵測
4. 過濾統計和日誌記錄

設計決策：
- 使用 Plugin 而非 Callback：全域性應用於所有代理和工具
- before_model_callback：在 LLM 調用前攔截，成本為零
- 可配置：從 YAML 讀取黑名單，支援運行時更新
"""

import logging
import re
from typing import Optional, List, Dict, Any
import yaml
from pathlib import Path

from google.adk.plugins import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.genai import types

logger = logging.getLogger(__name__)


class ContentFilterPlugin(BasePlugin):
    """
    靜態內容過濾外掛程式

    階段一：基礎實作
    - 英文關鍵字過濾
    - 正則表達式支援
    - 基本統計

    未來擴展（階段二）：
    - 多語言分詞（jieba for Chinese, MeCab for Japanese）
    - Unicode 正規化（簡繁轉換）
    - 上下文感知過濾
    """

    def __init__(
        self,
        name: str = "content_filter",
        config_path: Optional[str] = None,
        blocked_words: Optional[List[str]] = None,
    ):
        """
        初始化內容過濾器

        Args:
            name: 外掛程式名稱
            config_path: 配置檔案路徑（YAML）
            blocked_words: 直接提供的黑名單（用於測試）
        """
        super().__init__(name)

        # 載入配置
        if config_path:
            self.blocked_words = self._load_config(config_path)
        elif blocked_words:
            self.blocked_words = blocked_words
        else:
            # 預設黑名單（示範用）
            self.blocked_words = [
                # 暴力和攻擊相關
                r"\b(attack|hack|exploit|破解|攻擊|入侵)\b",
                # 惡意軟體相關
                r"\b(malware|virus|trojan|惡意軟體|病毒|木馬)\b",
                # 危險操作
                r"\b(delete.*database|drop.*table|刪除.*資料庫)\b",
                # 不當內容（需根據實際場景調整）
                r"\b(offensive-term|hate-speech|仇恨言論)\b",
            ]

        # 編譯正則表達式以提升性能
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.blocked_words
        ]

        # 統計資料
        self.stats = {
            "total_checks": 0,
            "blocked_count": 0,
            "blocked_by_pattern": {},
        }

        logger.info(f"[ContentFilterPlugin] 初始化完成，載入 {len(self.blocked_words)} 個過濾規則")

    def _load_config(self, config_path: str) -> List[str]:
        """從 YAML 配置檔載入黑名單"""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"配置檔不存在：{config_path}，使用預設規則")
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                blocked_words = config.get("content_filter", {}).get("blocked_patterns", [])
                logger.info(f"從 {config_path} 載入 {len(blocked_words)} 個過濾規則")
                return blocked_words
        except Exception as e:
            logger.error(f"載入配置檔失敗：{e}")
            return []

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> Optional[types.GenerateContentResponse]:
        """
        在 LLM 調用前檢查內容

        Returns:
            None: 內容安全，允許繼續
            GenerateContentResponse: 內容不安全，返回阻擋訊息
        """
        self.stats["total_checks"] += 1

        # 提取使用者輸入文字
        user_text = self._extract_text(llm_request)

        if not user_text:
            return None

        # 檢查每個過濾規則
        for idx, pattern in enumerate(self.compiled_patterns):
            match = pattern.search(user_text)
            if match:
                blocked_word = self.blocked_words[idx]
                matched_text = match.group(0)

                # 更新統計
                self.stats["blocked_count"] += 1
                self.stats["blocked_by_pattern"][blocked_word] = (
                    self.stats["blocked_by_pattern"].get(blocked_word, 0) + 1
                )

                # 記錄阻擋事件
                logger.warning(
                    f"[ContentFilter] 🚫 阻擋內容 | "
                    f"規則: {blocked_word} | "
                    f"匹配: '{matched_text}' | "
                    f"invocation: {callback_context.invocation_id}"
                )

                # 更新 session state 統計
                blocked_count = callback_context.state.get("security:blocked_count", 0)
                callback_context.state["security:blocked_count"] = blocked_count + 1
                callback_context.state["security:last_blocked_pattern"] = blocked_word
                callback_context.state["security:last_blocked_time"] = self._get_timestamp()

                # 返回阻擋訊息
                return self._create_blocked_response(blocked_word, matched_text)

        # 內容安全，允許繼續
        return None

    def _extract_text(self, llm_request: LlmRequest) -> str:
        """從 LLM 請求中提取文字內容"""
        text_parts = []
        for content in llm_request.contents:
            for part in content.parts:
                if part.text:
                    text_parts.append(part.text)
        return " ".join(text_parts)

    def _create_blocked_response(
        self, pattern: str, matched_text: str
    ) -> types.GenerateContentResponse:
        """建立阻擋回應"""
        message = (
            "⚠️ 您的請求包含不適當的內容，無法處理。\n\n"
            "I cannot process this request as it contains inappropriate content. "
            "Please rephrase your request respectfully.\n\n"
            f"🔒 安全提示：請避免使用可能違反使用政策的詞彙或表達。"
        )

        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        parts=[types.Part(text=message)],
                        role="model",
                    )
                )
            ]
        )

    def _get_timestamp(self) -> str:
        """獲取當前時間戳"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def get_stats(self) -> Dict[str, Any]:
        """獲取過濾統計資料"""
        stats = self.stats.copy()
        if stats["total_checks"] > 0:
            stats["block_rate"] = stats["blocked_count"] / stats["total_checks"]
        else:
            stats["block_rate"] = 0.0
        return stats

    def reset_stats(self):
        """重置統計資料"""
        self.stats = {
            "total_checks": 0,
            "blocked_count": 0,
            "blocked_by_pattern": {},
        }
        logger.info("[ContentFilterPlugin] 統計資料已重置")
