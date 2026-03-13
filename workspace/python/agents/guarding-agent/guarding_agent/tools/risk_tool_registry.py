"""
風險工具註冊表模組

管理工具的風險等級配置，並提供工具包裝和確認邏輯。
"""

from typing import Dict, Callable, Any, Optional
import logging
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

from .risk_level import (
    RiskLevel,
    RiskMetadata,
    DEFAULT_RISK_CONFIGS,
)

logger = logging.getLogger(__name__)


class RiskToolRegistry:
    """工具風險註冊表

    管理工具的風險等級配置，並提供基於風險等級的確認策略。

    主要功能：
    1. 註冊工具的風險等級
    2. 根據風險等級和參數決定是否需要確認
    3. 提供工具包裝功能（自動添加確認邏輯）

    使用範例：
    ```python
    registry = RiskToolRegistry()

    # 註冊工具風險等級
    registry.register('delete_user', RiskMetadata(
        level=RiskLevel.HIGH,
        description='刪除用戶',
        require_confirmation=True,
    ))

    # 包裝工具（自動添加確認邏輯）
    wrapped_tool = registry.wrap_tool(delete_user_func)

    # 在 Agent 中使用
    agent = Agent(tools=[wrapped_tool, ...])
    ```
    """

    def __init__(self, default_configs: Optional[Dict[str, RiskMetadata]] = None):
        """初始化註冊表

        Args:
            default_configs: 預設的風險配置字典，若為 None 則使用內建配置
        """
        self._risk_configs: Dict[str, RiskMetadata] = {}

        # 載入預設配置
        if default_configs is None:
            default_configs = DEFAULT_RISK_CONFIGS

        for tool_name, config in default_configs.items():
            self.register(tool_name, config)

        logger.info(f"RiskToolRegistry 初始化完成，已註冊 {len(self._risk_configs)} 個工具配置")

    def register(self, tool_name: str, risk_metadata: RiskMetadata) -> None:
        """註冊工具的風險配置

        Args:
            tool_name: 工具名稱
            risk_metadata: 風險元數據
        """
        self._risk_configs[tool_name] = risk_metadata
        logger.info(f"已註冊工具 '{tool_name}' 的風險等級：{risk_metadata.level.value}")

    def get_risk_metadata(self, tool_name: str) -> Optional[RiskMetadata]:
        """獲取工具的風險元數據

        Args:
            tool_name: 工具名稱

        Returns:
            風險元數據，若未註冊則返回 None
        """
        return self._risk_configs.get(tool_name)

    def get_risk_level(self, tool_name: str) -> RiskLevel:
        """獲取工具的風險等級

        Args:
            tool_name: 工具名稱

        Returns:
            風險等級，若未註冊則返回 LOW
        """
        metadata = self.get_risk_metadata(tool_name)
        return metadata.level if metadata else RiskLevel.LOW

    def requires_confirmation(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
    ) -> bool:
        """判斷工具調用是否需要確認

        根據風險配置和工具參數判斷是否需要人工確認。

        Args:
            tool_name: 工具名稱
            tool_args: 工具參數

        Returns:
            是否需要確認
        """
        metadata = self.get_risk_metadata(tool_name)

        # 未註冊的工具，預設不需要確認
        if not metadata:
            return False

        # CRITICAL 等級始終需要確認
        if metadata.level == RiskLevel.CRITICAL:
            return True

        # HIGH 等級始終需要確認（根據配置）
        if metadata.level == RiskLevel.HIGH:
            return metadata.require_confirmation

        # MEDIUM 等級根據閾值判斷
        if metadata.level == RiskLevel.MEDIUM:
            return self._check_threshold_exceeded(
                tool_args,
                metadata.max_auto_approve_threshold
            )

        # LOW 等級不需要確認
        return False

    def _check_threshold_exceeded(
        self,
        tool_args: Dict[str, Any],
        threshold: Optional[Dict[str, Any]],
    ) -> bool:
        """檢查參數是否超過自動核准閾值

        Args:
            tool_args: 工具參數
            threshold: 閾值配置

        Returns:
            是否超過閾值（需要確認）
        """
        if not threshold:
            return False

        for key, max_value in threshold.items():
            if key in tool_args:
                arg_value = tool_args[key]

                # 比較數值
                if isinstance(arg_value, (int, float)):
                    if arg_value > max_value:
                        logger.warning(
                            f"參數 '{key}' 的值 {arg_value} 超過閾值 {max_value}"
                        )
                        return True

                # 比較列表長度
                elif isinstance(arg_value, list):
                    if len(arg_value) > max_value:
                        logger.warning(
                            f"參數 '{key}' 的列表長度 {len(arg_value)} 超過閾值 {max_value}"
                        )
                        return True

        return False

    def wrap_tool(
        self,
        func: Callable,
        tool_name: Optional[str] = None,
    ) -> FunctionTool:
        """包裝工具，自動添加確認邏輯

        Args:
            func: 工具函數
            tool_name: 工具名稱（若為 None 則使用函數名）

        Returns:
            包裝後的 FunctionTool
        """
        if tool_name is None:
            tool_name = func.__name__

        metadata = self.get_risk_metadata(tool_name)

        # 未註冊的工具，直接返回基本包裝
        if not metadata:
            logger.warning(f"工具 '{tool_name}' 未註冊，使用預設配置")
            return FunctionTool(func)

        # 根據風險等級決定確認策略
        if metadata.level == RiskLevel.CRITICAL or metadata.level == RiskLevel.HIGH:
            # 高風險和關鍵操作：始終需要確認
            if metadata.require_confirmation:
                logger.info(f"工具 '{tool_name}' ({metadata.level.value}) 配置為需要確認")
                return FunctionTool(
                    func,
                    require_confirmation=True,
                )

        elif metadata.level == RiskLevel.MEDIUM:
            # 中等風險：使用條件確認函數
            logger.info(f"工具 '{tool_name}' ({metadata.level.value}) 配置為條件確認")

            def conditional_confirmation(**kwargs) -> bool:
                """條件確認函數"""
                # 從 kwargs 中提取工具參數（排除 tool_context）
                tool_args = {
                    k: v for k, v in kwargs.items()
                    if k != 'tool_context' and not k.startswith('_')
                }
                return self.requires_confirmation(tool_name, tool_args)

            return FunctionTool(
                func,
                require_confirmation=conditional_confirmation,
            )

        # 低風險：不需要確認
        logger.info(f"工具 '{tool_name}' ({metadata.level.value}) 不需要確認")
        return FunctionTool(func)

    def get_all_configs(self) -> Dict[str, RiskMetadata]:
        """獲取所有註冊的風險配置

        Returns:
            風險配置字典
        """
        return self._risk_configs.copy()

    def export_config(self) -> Dict[str, Any]:
        """匯出配置為字典格式（可序列化）

        Returns:
            可序列化的配置字典
        """
        return {
            tool_name: metadata.to_dict()
            for tool_name, metadata in self._risk_configs.items()
        }


# 全局單例實例
_global_registry: Optional[RiskToolRegistry] = None


def get_global_registry() -> RiskToolRegistry:
    """獲取全局風險工具註冊表實例

    Returns:
        全局 RiskToolRegistry 實例
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = RiskToolRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """重置全局註冊表（主要用於測試）"""
    global _global_registry
    _global_registry = None
