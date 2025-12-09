"""
重點摘要:
- **核心概念**: MCP 伺服器發現 (Discovery)。
- **關鍵技術**: JSON 設定檔讀取。
- **重要結論**: 提供了一個統一的方式來管理和存取 MCP 伺服器的連接資訊。
"""

import json
import os
from typing import Any, Dict


class MCPDiscovery:
    """
    讀取定義 MCP 伺服器的 JSON 設定檔，並提供對 "mcpServers" 鍵下的伺服器定義的存取。
    Reads a JSON config file defining MCP servers and provides access
    to the server definitions under the "mcpServers" key

    Attributes:
        config_file (str): JSON 設定檔的路徑。 (Path to the JSON configuration file.)
        config (Dict[str, Any]): 解析後的 JSON 內容，預期包含 "mcpServers" 鍵。 (Parsed JSON content, expected to contain the "mcpServers" key.)
    """

    def __init__(self, config_file: str = None):
        """
        使用設定檔初始化 MCPDiscovery。
        Initializes the MCPDiscovery with a configuration file.

        Args:
            config_file (str, optional): JSON 設定檔的路徑。 (Path to the JSON configuration file.)
            如果為 None，預設為與此模組位於同一目錄下的 'mcp_config.json'。
            If None, defaults to 'mcp_config.json'
            located in the same directory as this module.
        """
        if config_file is None:
            self.config_file = os.path.join(
                os.path.dirname(__file__), "mcp_config.json"
            )
        else:
            self.config_file = config_file

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError(
                    f"設定檔格式無效 (Invalid configuration format in) {self.config_file}"
                )

            return data
        except FileNotFoundError:
            raise FileNotFoundError(
                f"找不到設定檔 (Configuration file not found) {self.config_file}"
            )
        except Exception as e:
            raise RuntimeError(
                f"讀取設定檔時發生錯誤 (Error reading configuration file) {self.config_file}: {e}"
            )

    def list_servers(self) -> Dict[str, Any]:
        """
        回傳設定檔中定義的 MCP 伺服器。
        Returns the MCP servers defined in the configuration file.

        Returns:
            Dict[str, Any]: 來自設定檔的 "mcpServers" 鍵的內容。 (The content of the "mcpServers" key from the config.)

        Raises:
            KeyError: 如果設定檔中找不到 "mcpServers" 鍵。 (If "mcpServers" key is not found in the configuration.)
        """
        if "mcpServers" not in self.config:
            raise KeyError(
                f"在 {self.config_file} 中找不到 'mcpServers' 鍵 ('mcpServers' key not found in {self.config_file})"
            )

        return self.config.get("mcpServers", {})
