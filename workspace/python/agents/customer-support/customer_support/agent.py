"""
客戶支援代理人 - ADK 網頁介面

此代理人從 root_agent.yaml 載入設定，並透過 ADK 網頁介面提供客戶支援功能。
"""

from google.adk.agents import config_agent_utils
import os

# 從 YAML 設定載入代理人
# 注意：此處的路徑假設 root_agent.yaml 位於專案根目錄
config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'root_agent.yaml')
root_agent = config_agent_utils.from_config(config_path)

# 重點摘要
# - **核心概念**：初始化客戶支援代理人。
# - **關鍵技術**：`google.adk.agents.config_agent_utils`, Python os module。
# - **重要結論**：此腳本負責從 `root_agent.yaml` 載入代理人配置，並將其公開為 `root_agent` 物件，供 ADK Web 介面或其他入口點使用。
# - **行動項目**：無。
