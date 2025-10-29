"""
文件整理器，使用 MCP 檔案系統伺服器
根據類型、日期和內容自動整理文件。

這演示了如何使用 MCP 檔案系統工具創建專門的代理程式。
"""

import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters
from google.genai import types

def create_document_organizer_agent(base_directory: str) -> Agent:
  """
  創建專門用於文件整理的代理程式。

  Args:
    base_directory: 要整理的根目錄

  Returns:
    配置了 MCP 檔案系統工具的文件整理代理程式
  """
  # 驗證目錄是否存在
  if not os.path.exists(base_directory):
    raise ValueError(f"目錄不存在: {base_directory}")

  # 為檔案系統存取創建 MCP 工具集
  # 使用 stdio 連接參數來啟動 MCP 檔案系統伺服器
  server_params = StdioServerParameters(
    command='npx',  # 使用 npx 來執行 npm 套件
    args=[
      '-y',  # 自動確認安裝
      '@modelcontextprotocol/server-filesystem',  # MCP 檔案系統伺服器套件
      base_directory  # 指定要操作的基礎目錄
    ]
  )

  # 創建 MCP 工具集，提供檔案系統操作能力
  mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
      server_params=server_params
    )
  )

  # 創建文件整理代理程式
  agent = Agent(
    model='gemini-2.0-flash-exp',  # 使用 Gemini 2.0 Flash 模型
    name='document_organizer',     # 代理程式名稱
    description='具有檔案系統存取能力的智能文件整理代理程式',  # 代理程式描述
    instruction="""
    你是一個具有透過 MCP 存取檔案系統能力的文件整理專家。

    你的職責：
    1. 根據檔案名稱、類型和內容分析檔案
    2. 創建邏輯性的資料夾結構
    3. 將檔案移動到適當的位置
    4. 重新命名檔案以提高清晰度
    5. 生成整理報告

    指導原則：
    - 按類別創建資料夾（例如：Documents、Images、Code、Archives）
    - 在有幫助時使用子類別（例如：Documents/2024/、Documents/Work/）
    - 除非不清楚，否則保留原始檔案名稱
    - 絕不刪除檔案
    - 報告所有更改
    - 總是說明你在做什麼

    你可以使用的檔案系統工具：
    - read_file: 讀取檔案內容
    - write_file: 創建檔案
    - list_directory: 列出目錄內容
    - create_directory: 創建資料夾
    - move_file: 移動/重新命名檔案
    - search_files: 按模式搜尋
    - get_file_info: 獲取檔案元資料

    提供清晰、結構化的所有更改報告。
    """.strip(),
    tools=[mcp_tools],  # 提供 MCP 工具集給代理程式
    generate_content_config=types.GenerateContentConfig(
      temperature=0.2,  # 低溫度設定，讓檔案操作更加確定性
      max_output_tokens=2048  # 最大輸出 token 數
    )
  )

  return agent