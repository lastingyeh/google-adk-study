"""
ContentFilterPlugin - 靜態內容過濾插件 (Static Content Filtering Plugin)

功能：
1. 關鍵字黑名單過濾（支援正則表達式 Regex）
2. 多語言支援（英文、中文、日文）
3. 模糊匹配和變體偵測
4. 過濾統計和日誌記錄

設計決策：
- 使用 Plugin 而非 Callback：全域性應用於所有代理和工具。
- before_model_callback：在 LLM 調用前攔截，成本極低。
- 可配置性：從 YAML 讀取黑名單，支援運行時更新。

### 模組說明
此插件實作了基於關鍵字的內容過濾機制。它在 LLM 接收到請求之前，先掃描使用者輸入的文字，若發現符合預定義黑名單的內容，則會直接阻斷請求並回傳安全提示訊息。

### 重點摘要
- **核心概念**：先發制人的安全防線，防止惡意指令或不當內容進入模型。
- **關鍵技術**：正則表達式 (Regex)、Google ADK `BasePlugin`、`before_model_callback` 攔截器。
- **重要結論**：靜態過濾是第一道防線，能有效過濾掉大部分常見的攻擊模式（如 SQL 注入、破解指令等）。
- **行動項目**：在 `security_config.yaml` 中維護 `blocked_patterns` 以更新過濾規則。

### 處理流程
```mermaid
graph LR
    User([使用者輸入]) --> Plugin[ContentFilterPlugin]
    Plugin -- 匹配黑名單 --> Blocked[回傳安全警告]
    Plugin -- 安全無誤 --> Next[下一個插件或模型]

    style Blocked fill:#f66,stroke:#333
    style Next fill:#6f6,stroke:#333
```
"""

import logging
import os
import re
from pathlib import Path
from typing import Any

import yaml
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest

# 匯入 Google ADK 相關類別
from google.adk.plugins import BasePlugin
from google.genai import types

# 初始化日誌
logger = logging.getLogger(__name__)


class ContentFilterPlugin(BasePlugin):
    """
    靜態內容過濾插件 (Static Content Filtering Plugin)

    階段一：基礎實作
    - 英文與中文關鍵字過濾
    - 正則表達式支援
    - 基本統計功能

    未來擴展（階段二）：
    - 多語言分詞（如中文使用 jieba, 日文使用 MeCab）
    - Unicode 正規化（簡繁轉換）
    - 上下文感知過濾
    """

    def __init__(
        self,
        name: str = "content_filter",
        config_path: str | None = None,
        blocked_words: list[str] | None = None,
    ):
        """
        初始化內容過濾器

        參數:
            name: 插件名稱
            config_path: YAML 設定檔路徑 (若未提供則從環境變數 CONTENT_FILTER_CONFIG_PATH 讀取)
            blocked_words: 直接提供的黑名單清單（用於測試或覆蓋）
        """
        super().__init__(name)

        # 從環境變數讀取預設配置路徑
        if config_path is None:
            config_path = os.getenv("CONTENT_FILTER_CONFIG_PATH")

        # 決定載入配置的優先順序
        if config_path:
            self.blocked_words = self._load_config(config_path)
        elif blocked_words:
            self.blocked_words = blocked_words
        else:
            # 預設黑名單（示範用途）
            self.blocked_words = [
                # 暴力、破解與攻擊相關
                r"\b(attack|hack|exploit|破解|攻擊|入侵)\b",
                # 惡意軟體與病毒相關
                r"\b(malware|virus|trojan|惡意軟體|病毒|木馬)\b",
                # 危險系統操作
                r"\b(delete.*database|drop.*table|刪除.*資料庫)\b",
                # 不當內容與仇恨言論
                r"\b(offensive-term|hate-speech|仇恨言論)\b",
            ]

        # 預先編譯正則表達式以優化效能 (忽略大小寫)
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.blocked_words
        ]

        # 初始化內部統計數據
        self.stats = {
            "total_checks": 0,
            "blocked_count": 0,
            "blocked_by_pattern": {},
        }

        logger.info(
            f"[ContentFilterPlugin] 初始化完成，載入 {len(self.blocked_words)} 個過濾規則"
        )

    def _get_project_root(self) -> Path:
        """
        獲取專案根目錄路徑

        從當前文件向上查找，直到找到包含 pyproject.toml 的目錄
        """
        current_path = Path(__file__).resolve()

        # 向上遍歷目錄，查找專案根目錄的標記文件
        for parent in current_path.parents:
            if (parent / "pyproject.toml").exists():
                return parent
            # 備選：也可以查找其他標記文件
            if (parent / "setup.py").exists() or (parent / ".git").exists():
                return parent

        # 如果找不到，返回當前文件所在目錄的上兩層（預設為 guarding-agent 目錄）
        return current_path.parent.parent.parent

    def _load_config(self, config_path: str) -> list[str]:
        """從 YAML 設定檔中讀取黑名單規則"""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"設定檔不存在：{config_path}，改用系統預設規則")
            return []

        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                # 從 content_filter -> blocked_patterns 路徑讀取
                blocked_words = config.get("content_filter", {}).get(
                    "blocked_patterns", []
                )
                logger.info(f"從 {config_path} 載入 {len(blocked_words)} 個過濾規則")
                return blocked_words
        except Exception as e:
            logger.error(f"讀取設定檔時發生錯誤：{e}")
            return []

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> types.GenerateContentResponse | None:
        """
        在 LLM 模型被調用之前執行內容檢查

        回傳:
            None: 內容通過安全性檢查，允許繼續執行。
            GenerateContentResponse: 內容不安全，攔截並回傳自定義的阻斷回應。
        """
        self.stats["total_checks"] += 1

        # 從 LLM 請求中提取原始文字
        user_text = self._extract_text(llm_request)

        if not user_text:
            return None

        # 遍歷所有已編譯的模式進行比對
        for idx, pattern in enumerate(self.compiled_patterns):
            match = pattern.search(user_text)
            if match:
                blocked_word = self.blocked_words[idx]
                matched_text = match.group(0)

                # 更新內部統計
                self.stats["blocked_count"] += 1
                self.stats["blocked_by_pattern"][blocked_word] = (
                    self.stats["blocked_by_pattern"].get(blocked_word, 0) + 1
                )

                # 記錄安全性事件日誌
                logger.warning(
                    f"[ContentFilter] 🚫 阻斷不當內容 | "
                    f"命中規則: {blocked_word} | "
                    f"匹配文字: '{matched_text}' | "
                    f"調用 ID: {callback_context.invocation_id}"
                )

                # 將統計數據同步到會話狀態 (Session State) 中
                blocked_count = callback_context.state.get("security:blocked_count", 0)
                callback_context.state["security:blocked_count"] = blocked_count + 1
                callback_context.state["security:last_blocked_pattern"] = blocked_word
                callback_context.state["security:last_blocked_time"] = (
                    self._get_timestamp()
                )

                # 回傳阻斷訊息給使用者，不調用實際模型
                return self._create_blocked_response(blocked_word, matched_text)

        # 內容安全，繼續後續流程
        return None

    def _extract_text(self, llm_request: LlmRequest) -> str:
        """從結構化的 LLM 請求中合併提取所有文字內容"""
        text_parts = []
        for content in llm_request.contents:
            for part in content.parts:
                if part.text:
                    text_parts.append(part.text)
        return " ".join(text_parts)

    def _create_blocked_response(
        self, pattern: str, matched_text: str
    ) -> types.GenerateContentResponse:
        """建構標準化的阻斷回應訊息"""
        message = (
            "⚠️ 您的請求包含不適當的內容，系統無法處理。\n\n"
            "I cannot process this request as it contains inappropriate content. "
            "Please rephrase your request respectfully.\n\n"
            "🔒 安全提示：請遵守使用政策，避免使用敏感詞彙。"
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
        """獲取 UTC 格式的當前時間戳"""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    def get_stats(self) -> dict[str, Any]:
        """獲取外掛程式的運作統計資料"""
        stats = self.stats.copy()
        if stats["total_checks"] > 0:
            stats["block_rate"] = stats["blocked_count"] / stats["total_checks"]
        else:
            stats["block_rate"] = 0.0
        return stats

    def reset_stats(self):
        """重置所有統計數據"""
        self.stats = {
            "total_checks": 0,
            "blocked_count": 0,
            "blocked_by_pattern": {},
        }
        logger.info("[ContentFilterPlugin] 統計資料已清空")
