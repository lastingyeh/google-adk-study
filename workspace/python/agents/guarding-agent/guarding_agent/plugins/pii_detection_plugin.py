"""
PIIDetectionPlugin - 敏感資訊偵測和處理外掛程式

功能：
1. 偵測多種 PII 類型（email, phone, SSN, credit card, API keys）
2. 四種處理策略：完全遮蔽、部分掩碼、雜湊、直接攔截
3. 可配置的場景策略
4. 偵測統計和審計日誌

設計決策：
- after_model_callback：在 LLM 回應後處理，避免洩漏
- before_model_callback（可選）：在輸入端也進行偵測
- 不記錄原始 PII 值：僅記錄類型、位置和雜湊
"""

import logging
import re
import hashlib
from typing import Optional, Dict, Any, List
from enum import Enum
import yaml
from pathlib import Path

from google.adk.plugins import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types

logger = logging.getLogger(__name__)


class PIIHandlingStrategy(Enum):
    """PII 處理策略"""
    REDACT = "redact"          # 完全遮蔽：john@email.com → [EMAIL_REDACTED]
    MASK = "mask"              # 部分掩碼：john@email.com → j***@email.com
    HASH = "hash"              # 雜湊：john@email.com → [EMAIL_8a3f2b1c]
    BLOCK = "block"            # 直接攔截：返回錯誤訊息


class PIIDetectionPlugin(BasePlugin):
    """
    敏感資訊偵測和處理外掛程式

    支援的 PII 類型：
    - Email 地址
    - 電話號碼（多種格式）
    - 社會安全號碼（SSN）
    - 信用卡號
    - API Keys / Access Tokens

    處理策略可按場景配置：
    - 客服系統：MASK（保留上下文）
    - 日誌系統：REDACT（安全優先）
    - 內部工具：HASH（保留唯一性）
    """

    # PII 偵測正則表達式
    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone_us": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "phone_intl": r"\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "api_key": r"\b[A-Za-z0-9_-]{32,}\b",  # 簡化版，實際可更精確
    }

    def __init__(
        self,
        name: str = "pii_detection",
        config_path: Optional[str] = None,
        default_strategy: PIIHandlingStrategy = PIIHandlingStrategy.REDACT,
        check_input: bool = True,
        check_output: bool = True,
    ):
        """
        初始化 PII 偵測器

        Args:
            name: 外掛程式名稱
            config_path: 配置檔案路徑
            default_strategy: 預設處理策略
            check_input: 是否檢查輸入
            check_output: 是否檢查輸出
        """
        super().__init__(name)

        self.default_strategy = default_strategy
        self.check_input = check_input
        self.check_output = check_output

        # 載入配置（每種 PII 類型可有不同策略）
        if config_path:
            self.pii_strategies = self._load_config(config_path)
        else:
            # 預設策略：所有類型都使用 default_strategy
            self.pii_strategies = {
                pii_type: default_strategy for pii_type in self.PII_PATTERNS.keys()
            }

        # 編譯正則表達式
        self.compiled_patterns = {
            pii_type: re.compile(pattern)
            for pii_type, pattern in self.PII_PATTERNS.items()
        }

        # 統計資料
        self.stats = {
            "total_checks": 0,
            "pii_detected": 0,
            "by_type": {pii_type: 0 for pii_type in self.PII_PATTERNS.keys()},
            "by_strategy": {strategy.value: 0 for strategy in PIIHandlingStrategy},
        }

        logger.info(
            f"[PIIDetectionPlugin] 初始化完成 | "
            f"檢查輸入: {check_input} | 檢查輸出: {check_output} | "
            f"預設策略: {default_strategy.value}"
        )

    def _load_config(self, config_path: str) -> Dict[str, PIIHandlingStrategy]:
        """從配置檔載入 PII 策略"""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"配置檔不存在：{config_path}，使用預設策略")
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                pii_config = config.get("pii_detection", {}).get("strategies", {})

                # 轉換字串為 Enum
                strategies = {}
                for pii_type, strategy_str in pii_config.items():
                    try:
                        strategies[pii_type] = PIIHandlingStrategy(strategy_str)
                    except ValueError:
                        logger.warning(f"未知策略：{strategy_str}，使用預設策略")
                        strategies[pii_type] = self.default_strategy

                logger.info(f"從配置載入 {len(strategies)} 個 PII 策略")
                return strategies
        except Exception as e:
            logger.error(f"載入配置失敗：{e}")
            return {}

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request
    ) -> Optional[types.GenerateContentResponse]:
        """檢查輸入文字中的 PII（可選）"""
        if not self.check_input:
            return None

        # 提取文字
        text = self._extract_text_from_request(llm_request)
        if not text:
            return None

        # 偵測 PII
        detections = self._detect_pii(text)

        if detections:
            # 檢查是否有 BLOCK 策略
            for detection in detections:
                strategy = self.pii_strategies.get(
                    detection["type"], self.default_strategy
                )
                if strategy == PIIHandlingStrategy.BLOCK:
                    logger.warning(
                        f"[PIIDetection] 🚫 輸入包含受保護的 PII | "
                        f"類型: {detection['type']} | "
                        f"invocation: {callback_context.invocation_id}"
                    )
                    return self._create_blocked_response()

            # 記錄偵測（不記錄原始值）
            self._log_detections(callback_context, detections, location="input")

        return None

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """檢查輸出文字中的 PII 並處理"""
        if not self.check_output:
            return None

        self.stats["total_checks"] += 1

        # 提取回應文字
        response_text = self._extract_text_from_response(llm_response)
        if not response_text:
            return None

        # 偵測 PII
        detections = self._detect_pii(response_text)

        if not detections:
            return None

        # 有 PII 偵測到，進行處理
        self.stats["pii_detected"] += 1

        logger.warning(
            f"[PIIDetection] 🔍 輸出包含 {len(detections)} 個 PII | "
            f"invocation: {callback_context.invocation_id}"
        )

        # 記錄偵測
        self._log_detections(callback_context, detections, location="output")

        # 處理 PII
        filtered_text = self._handle_pii(response_text, detections)

        # 建立新的回應
        return self._create_filtered_response(llm_response, filtered_text)

    def _detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """偵測文字中的所有 PII"""
        detections = []

        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                detections.append({
                    "type": pii_type,
                    "value": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "hash": self._hash_value(match.group(0)),
                })

                # 更新統計
                self.stats["by_type"][pii_type] += 1

        return detections

    def _handle_pii(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """根據策略處理 PII"""
        # 按位置倒序排序，從後往前替換（避免位置偏移）
        detections.sort(key=lambda x: x["start"], reverse=True)

        filtered_text = text
        for detection in detections:
            pii_type = detection["type"]
            value = detection["value"]
            start = detection["start"]
            end = detection["end"]

            # 獲取策略
            strategy = self.pii_strategies.get(pii_type, self.default_strategy)
            self.stats["by_strategy"][strategy.value] += 1

            # 根據策略處理
            if strategy == PIIHandlingStrategy.REDACT:
                replacement = f"[{pii_type.upper()}_REDACTED]"
            elif strategy == PIIHandlingStrategy.MASK:
                replacement = self._mask_value(value, pii_type)
            elif strategy == PIIHandlingStrategy.HASH:
                replacement = f"[{pii_type.upper()}_{detection['hash'][:8]}]"
            else:  # BLOCK 在 before_model_callback 已處理
                replacement = f"[{pii_type.upper()}_REMOVED]"

            # 替換
            filtered_text = filtered_text[:start] + replacement + filtered_text[end:]

        return filtered_text

    def _mask_value(self, value: str, pii_type: str) -> str:
        """部分掩碼處理"""
        if pii_type == "email":
            # john@example.com → j***@example.com
            parts = value.split("@")
            if len(parts) == 2:
                return f"{parts[0][0]}***@{parts[1]}"
        elif pii_type in ["phone_us", "phone_intl"]:
            # 保留後四碼
            return "***-***-" + value[-4:]
        elif pii_type == "credit_card":
            # 保留後四碼
            return "****-****-****-" + value.replace(" ", "").replace("-", "")[-4:]

        # 預設：顯示前後各一個字符
        if len(value) > 4:
            return value[0] + "*" * (len(value) - 2) + value[-1]
        return "*" * len(value)

    def _hash_value(self, value: str) -> str:
        """計算 PII 值的雜湊"""
        return hashlib.sha256(value.encode()).hexdigest()

    def _log_detections(
        self, callback_context: CallbackContext, detections: List[Dict], location: str
    ):
        """記錄 PII 偵測（不含原始值）"""
        # 更新 session state
        pii_log = callback_context.state.get("security:pii_detections", [])

        for detection in detections:
            pii_log.append({
                "type": detection["type"],
                "hash": detection["hash"],
                "location": location,
                "timestamp": self._get_timestamp(),
                "invocation_id": callback_context.invocation_id,
            })

        callback_context.state["security:pii_detections"] = pii_log[-100:]  # 保留最近100條

    def _extract_text_from_request(self, llm_request) -> str:
        """從請求提取文字"""
        text_parts = []
        for content in llm_request.contents:
            for part in content.parts:
                if part.text:
                    text_parts.append(part.text)
        return " ".join(text_parts)

    def _extract_text_from_response(self, llm_response: LlmResponse) -> str:
        """從回應提取文字"""
        if not llm_response.candidates:
            return ""

        text_parts = []
        for part in llm_response.candidates[0].content.parts:
            if part.text:
                text_parts.append(part.text)
        return " ".join(text_parts)

    def _create_blocked_response(self) -> types.GenerateContentResponse:
        """建立阻擋回應（輸入包含敏感資訊）"""
        message = (
            "⚠️ 您的請求包含敏感個人資訊，為保護隱私無法處理。\n\n"
            "Your request contains sensitive personal information. "
            "Please remove or anonymize the data before submitting.\n\n"
            "🔒 安全提示：請勿在對話中提供真實的個人資訊。"
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
        self, original_response: LlmResponse, filtered_text: str
    ) -> LlmResponse:
        """建立過濾後的回應"""
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
        """獲取當前時間戳"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計資料"""
        stats = self.stats.copy()
        if stats["total_checks"] > 0:
            stats["detection_rate"] = stats["pii_detected"] / stats["total_checks"]
        else:
            stats["detection_rate"] = 0.0
        return stats

    def reset_stats(self):
        """重置統計資料"""
        self.stats = {
            "total_checks": 0,
            "pii_detected": 0,
            "by_type": {pii_type: 0 for pii_type in self.PII_PATTERNS.keys()},
            "by_strategy": {strategy.value: 0 for strategy in PIIHandlingStrategy},
        }
        logger.info("[PIIDetectionPlugin] 統計資料已重置")
