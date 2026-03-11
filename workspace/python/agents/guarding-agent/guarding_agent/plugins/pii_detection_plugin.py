"""
PIIDetectionPlugin - 敏感資訊偵測與處理插件 (PII Detection & Handling Plugin)

功能：
1. 偵測多種個人識別資訊 (PII) 類型（電子郵件、電話、身分證字號、信用卡、API 金鑰）
2. 四種處理策略：完全遮蔽 (Redact)、部分掩碼 (Mask)、雜湊 (Hash)、直接攔截 (Block)
3. 可配置的場景策略
4. 偵測統計和審計日誌

設計決策：
- after_model_callback：在 LLM 回應後處理，防止敏感資料洩漏給使用者。
- before_model_callback（可選）：在輸入端也進行偵測，防止敏感資料進入模型訓練或日誌。
- 不記錄原始 PII 值：僅記錄類型、位置和雜湊值，確保符合資安合規。

### 翻譯內容
此插件實作了全方位的個人隱私資訊 (PII) 保護機制。它能自動識別對話中的敏感數據，並根據預設或設定的策略進行去識別化處理。

### 重點摘要
- **核心概念**：保護使用者隱私，防止 AI 模型在回應中無意間洩漏敏感資訊。
- **關鍵技術**：Regex 正則表達式、SHA-256 雜湊、Google ADK 插件生命週期回調。
- **重要結論**：支援「輸入攔截」與「輸出過濾」雙重保障，是企業級 AI 應用的必要組件。
- **行動項目**：根據業務需求調整 `PIIHandlingStrategy`（例如：內部日誌使用 HASH，外部回應與輸出過濾）使用 REDACT。

### 處理流程
```mermaid
graph TD
    Response[模型原始回應] --> Detect{偵測 PII?}
    Detect -- 是 --> Strategy{套用策略}
    Detect -- 否 --> Output[直接輸出]

    Strategy -- REDACT --> Redacted[完全遮蔽]
    Strategy -- MASK --> Masked[部分掩碼]
    Strategy -- HASH --> Hashed[雜湊化]

    Redacted --> Output
    Masked --> Output
    Hashed --> Output
```
"""

import hashlib
import logging
import os
import re
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse

# 匯入 Google ADK 元件
from google.adk.plugins import BasePlugin
from google.genai import types

# 初始化日誌
logger = logging.getLogger(__name__)


class PIIHandlingStrategy(Enum):
    """定義 PII 的處理策略"""

    REDACT = "redact"  # 完全遮蔽：john@email.com → [EMAIL_REDACTED]
    MASK = "mask"  # 部分掩碼：john@email.com → j***@email.com
    HASH = "hash"  # 雜湊：john@email.com → [EMAIL_8a3f2b1c]
    BLOCK = "block"  # 直接攔截：中斷流程並回傳錯誤訊息


class PIIDetectionPlugin(BasePlugin):
    """
    敏感資訊偵測與處理插件 (PII Detection & Handling Plugin)

    支援的 PII 類型：
    - Email 地址
    - 電話號碼（包含美國與國際格式）
    - 社會安全號碼 (SSN) / 身分證字號
    - 信用卡號
    - API 金鑰 / 存取權杖 (Access Tokens)

    處理策略可依據不同應用場景配置：
    - 客服系統：使用 MASK（保留部分上下文供專員參考）
    - 日誌系統：使用 REDACT（安全性優先，完全移除）
    - 內部開發工具：使用 HASH（保留唯一性以便追蹤）
    """

    # PII 偵測用的正則表達式定義
    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone_us": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "phone_intl": r"\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "api_key": r"\b[A-Za-z0-9_-]{32,}\b",  # 簡化版規則
    }

    def __init__(
        self,
        name: str = "pii_detection",
        config_path: str | None = None,
        default_strategy: PIIHandlingStrategy = PIIHandlingStrategy.REDACT,
        check_input: bool = True,
        check_output: bool = True,
    ):
        """
        初始化 PII 偵測器插件

        參數:
            name: 插件名稱
            config_path: YAML 設定檔路徑
            default_strategy: 當未指定特定類型時的預設處理策略
            check_input: 是否在模型處理前檢查輸入訊息
            check_output: 是否在模型回傳後檢查回應訊息
        """
        super().__init__(name)

        self.default_strategy = default_strategy
        self.check_input = check_input
        self.check_output = check_output

        # 從環境變數讀取預設配置路徑
        if config_path is None:
            config_path = os.getenv("CONTENT_FILTER_CONFIG_PATH")

        # 載入設定（每種 PII 類型可配置不同的處理方式）
        if config_path:
            self.pii_strategies = self._load_config(config_path)
        else:
            # 預設策略：所有偵測到的類型均使用 default_strategy
            self.pii_strategies = dict.fromkeys(
                self.PII_PATTERNS.keys(), default_strategy
            )

        # 預先編譯所有 PII 正則表達式
        self.compiled_patterns = {
            pii_type: re.compile(pattern)
            for pii_type, pattern in self.PII_PATTERNS.items()
        }

        # 初始化運作統計數據
        self.stats = {
            "total_checks": 0,
            "pii_detected": 0,
            "by_type": dict.fromkeys(self.PII_PATTERNS.keys(), 0),
            "by_strategy": {strategy.value: 0 for strategy in PIIHandlingStrategy},
        }

        logger.info(
            f"[PIIDetectionPlugin] 初始化完成 | "
            f"輸入檢查: {check_input} | 輸出檢查: {check_output} | "
            f"預設處理策略: {default_strategy.value}"
        )

    def _load_config(self, config_path: str) -> dict[str, PIIHandlingStrategy]:
        """從 YAML 設定檔載入各類別的 PII 處理策略"""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"設定檔不存在：{config_path}，使用系統預設策略")
            return {}

        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                pii_config = config.get("pii_detection", {}).get("strategies", {})

                # 將字串設定轉換為列舉 (Enum) 類型
                strategies = {}
                for pii_type, strategy_str in pii_config.items():
                    try:
                        strategies[pii_type] = PIIHandlingStrategy(strategy_str)
                    except ValueError:
                        logger.warning(
                            f"偵測到未知策略字串：{strategy_str}，將使用預設策略"
                        )
                        strategies[pii_type] = self.default_strategy

                logger.info(f"從設定檔成功載入 {len(strategies)} 個專屬 PII 處理策略")
                return strategies
        except Exception as e:
            logger.error(f"載入 PII 設定檔時發生錯誤：{e}")
            return {}

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request
    ) -> types.GenerateContentResponse | None:
        """攔截並檢查輸入文字中的 PII 資訊"""
        if not self.check_input:
            return None

        # 提取請求內容文字
        text = self._extract_text_from_request(llm_request)
        if not text:
            return None

        # 執行 PII 偵測邏輯
        detections = self._detect_pii(text)

        if detections:
            # 優先檢查是否有「阻斷 (BLOCK)」策略
            for detection in detections:
                strategy = self.pii_strategies.get(
                    detection["type"], self.default_strategy
                )
                if strategy == PIIHandlingStrategy.BLOCK:
                    logger.warning(
                        f"[PIIDetection] 🚫 輸入內容包含受保護的敏感資訊 (BLOCK) | "
                        f"類型: {detection['type']} | "
                        f"調用 ID: {callback_context.invocation_id}"
                    )
                    return self._create_blocked_response()

            # 記錄偵測結果到日誌中（不記錄敏感原始值）
            self._log_detections(callback_context, detections, location="input")

        return None

    async def after_model_callback(
        self,
        *,
        callback_context: CallbackContext,
        llm_response: LlmResponse | types.GenerateContentResponse,
    ) -> LlmResponse | types.GenerateContentResponse | None:
        """檢查模型回傳內容中的 PII 資訊並依策略進行處理"""
        if not self.check_output:
            return None

        self.stats["total_checks"] += 1

        # 提取回應內容文字
        response_text = self._extract_text_from_response(llm_response)
        if not response_text:
            return None

        # 執行偵測
        detections = self._detect_pii(response_text)

        if not detections:
            return None

        # 發現敏感資訊，開始處理
        self.stats["pii_detected"] += 1

        logger.warning(
            f"[PIIDetection] 🔍 模型回應包含 {len(detections)} 項敏感資訊 | "
            f"調用 ID: {callback_context.invocation_id}"
        )

        # 記錄偵測結果
        self._log_detections(callback_context, detections, location="output")

        # 執行去識別化處理
        filtered_text = self._handle_pii(response_text, detections)

        # 回傳過濾後的新回應對象
        return self._create_filtered_response(llm_response, filtered_text)

    def _detect_pii(self, text: str) -> list[dict[str, Any]]:
        """使用預定義的模式偵測文字中所有的 PII 項目"""
        detections = []

        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                detections.append(
                    {
                        "type": pii_type,
                        "value": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "hash": self._hash_value(match.group(0)),
                    }
                )

                # 更新類型統計
                self.stats["by_type"][pii_type] += 1

        return detections

    def _handle_pii(self, text: str, detections: list[dict[str, Any]]) -> str:
        """根據每種類型的策略對偵測到的內容進行處理"""
        # 按文字位置倒序排序，確保替換時不會影響前面項目的偏移量
        detections.sort(key=lambda x: x["start"], reverse=True)

        filtered_text = text
        for detection in detections:
            pii_type = detection["type"]
            value = detection["value"]
            start = detection["start"]
            end = detection["end"]

            # 確定適用的策略
            strategy = self.pii_strategies.get(pii_type, self.default_strategy)
            self.stats["by_strategy"][strategy.value] += 1

            # 套用處理邏輯
            if strategy == PIIHandlingStrategy.REDACT:
                replacement = f"[{pii_type.upper()}_REDACTED]"
            elif strategy == PIIHandlingStrategy.MASK:
                replacement = self._mask_value(value, pii_type)
            elif strategy == PIIHandlingStrategy.HASH:
                replacement = f"[{pii_type.upper()}_{detection['hash'][:8]}]"
            else:  # BLOCK 策略已在輸入階段處理，若出現在輸出則預設為 REMOVED
                replacement = f"[{pii_type.upper()}_REMOVED]"

            # 執行替換
            filtered_text = filtered_text[:start] + replacement + filtered_text[end:]

        return filtered_text

    def _mask_value(self, value: str, pii_type: str) -> str:
        """執行部分掩碼 (Masking) 邏輯"""
        if pii_type == "email":
            # 電子郵件範例：john@example.com → j***@example.com
            parts = value.split("@")
            if len(parts) == 2:
                return f"{parts[0][0]}***@{parts[1]}"
        elif pii_type in ["phone_us", "phone_intl"]:
            # 電話範例：保留末 4 碼
            return "***-***-" + value[-4:]
        elif pii_type == "credit_card":
            # 信用卡範例：保留末 4 碼
            clean_val = value.replace(" ", "").replace("-", "")
            return "****-****-****-" + clean_val[-4:]

        # 預設掩碼：保留首尾，中間隱藏
        if len(value) > 4:
            return value[0] + "*" * (len(value) - 2) + value[-1]
        return "*" * len(value)

    def _hash_value(self, value: str) -> str:
        """計算 PII 值的 SHA-256 雜湊 (Hash)"""
        return hashlib.sha256(value.encode()).hexdigest()

    def _log_detections(
        self, callback_context: CallbackContext, detections: list[dict], location: str
    ):
        """將偵測事件記錄到會話狀態中（安全性審計用）"""
        pii_log = callback_context.state.get("security:pii_detections", [])

        for detection in detections:
            pii_log.append(
                {
                    "type": detection["type"],
                    "hash": detection["hash"],
                    "location": location,
                    "timestamp": self._get_timestamp(),
                    "invocation_id": callback_context.invocation_id,
                }
            )

        # 限制日誌儲存量，保留最近 100 筆
        callback_context.state["security:pii_detections"] = pii_log[-100:]

    def _extract_text_from_request(self, llm_request) -> str:
        """從模型請求對象中合併提取所有文字"""
        text_parts = []
        for content in llm_request.contents:
            for part in content.parts:
                if part.text:
                    text_parts.append(part.text)
        return " ".join(text_parts)

    def _extract_text_from_response(
        self, llm_response: LlmResponse | types.GenerateContentResponse
    ) -> str:
        """從模型回應對象中合併提取文字"""
        # 情況 1：LlmResponse (ADK 封裝對象)
        if isinstance(llm_response, LlmResponse):
            if not llm_response.content or not llm_response.content.parts:
                return ""
            content = llm_response.content
        # 情況 2：GenerateContentResponse (Google GenAI SDK 原始對象)
        elif hasattr(llm_response, "candidates") and llm_response.candidates:
            content = llm_response.candidates[0].content
        else:
            return ""

        text_parts = []
        for part in content.parts:
            if part.text:
                text_parts.append(part.text)
        return " ".join(text_parts)

    def _create_blocked_response(self) -> types.GenerateContentResponse:
        """建立「請求包含敏感資訊」的阻斷回應內容"""
        message = (
            "⚠️ 您的請求包含敏感個人資訊，基於隱私保護政策，系統無法處理。\n\n"
            "Your request contains sensitive personal information. "
            "Please remove or anonymize the data before submitting.\n\n"
            "🔒 安全提示：對話中請勿提供真實的身分證字號、信用卡或密碼等資訊。"
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

    def _create_filtered_response(
        self,
        original_response: LlmResponse | types.GenerateContentResponse,
        filtered_text: str,
    ) -> LlmResponse | types.GenerateContentResponse:
        """將處理過的文字內容重新封裝成回應對象"""
        # 情況 1：LlmResponse
        if isinstance(original_response, LlmResponse):
            new_response = original_response.model_copy()
            new_response.content = types.Content(
                parts=[types.Part(text=filtered_text)],
                role="model",
            )
            return new_response

        # 情況 2：GenerateContentResponse
        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        parts=[types.Part(text=filtered_text)],
                        role="model",
                    )
                )
            ]
        )

    def _get_timestamp(self) -> str:
        """取得當前的 ISO 格式 UTC 時間戳"""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    def get_stats(self) -> dict[str, Any]:
        """獲取 PII 偵測器的運作指標統計"""
        stats = self.stats.copy()
        if stats["total_checks"] > 0:
            stats["detection_rate"] = stats["pii_detected"] / stats["total_checks"]
        else:
            stats["detection_rate"] = 0.0
        return stats

    def reset_stats(self):
        """重置所有內部運作統計指標"""
        self.stats = {
            "total_checks": 0,
            "pii_detected": 0,
            "by_type": dict.fromkeys(self.PII_PATTERNS.keys(), 0),
            "by_strategy": {strategy.value: 0 for strategy in PIIHandlingStrategy},
        }
        logger.info("[PIIDetectionPlugin] 安全指標統計已重置")
