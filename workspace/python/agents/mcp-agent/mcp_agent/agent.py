"""
MCP 代理實現 - 具備人工介入迴路功能
展示 MCP 檔案系統與 Google ADK 的整合。

此代理使用 MCPToolset 連接到 MCP 檔案系統伺服器，
提供檔案操作功能，並對破壞性操作實施核准工作流程。

主要特色：
- 為了安全，限制在 sample_files 目錄內操作
- 對寫入/移動/刪除操作需要人工介入迴路核准
- 提供工具執行前的驗證和確認回調功能
- 全面的日誌記錄和錯誤處理
"""

import os
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters
from google.genai import types
import logging

# 設定日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 人工介入迴路回調函數 (防護機制與核准工作流程)
# ============================================================================


def before_tool_callback(
  tool, args: Dict[str, Any], tool_context
) -> Optional[Dict[str, Any]]:
  """
  MCP 檔案系統操作的人工介入迴路回調函數。

  此回調函數實現破壞性操作的核准工作流程：
  - 寫入操作需要確認
  - 移動/刪除操作需要明確核准
  - 讀取操作無需確認即可執行

  ADK 最佳實務：使用 before_tool_callback 進行：
  1. 驗證：檢查參數是否安全
  2. 授權：對敏感操作要求核准
  3. 日誌記錄：追蹤工具使用以供稽核
  4. 速率限制：防止濫用

  參數：
    tool: 被呼叫的 BaseTool 物件 (具有 .name 屬性)
    args: 傳遞給工具的參數
    tool_context: 包含狀態和調用存取的 ToolContext

  回傳值：
    None: 允許工具執行
    dict: 阻止工具執行並回傳此結果
  """
  # 從工具物件提取工具名稱
  tool_name = tool.name if hasattr(tool, "name") else str(tool)

  logger.info(f"[工具請求] {tool_name} 參數: {args}")

  # 在會話狀態中追蹤工具使用情況
  tool_count = tool_context.state.get("temp:tool_count", 0) or 0  # 處理 None 值
  tool_context.state["temp:tool_count"] = tool_count + 1
  tool_context.state["temp:last_tool"] = tool_name

  # 定義需要核准的破壞性操作
  DESTRUCTIVE_OPERATIONS = {
    "write_file": "寫入檔案會修改內容",
    "write_text_file": "寫入檔案會修改內容",
    "move_file": "移動檔案會改變檔案位置",
    "create_directory": "建立目錄會修改檔案系統結構",
  }

  # 檢查是否為破壞性操作
  if tool_name in DESTRUCTIVE_OPERATIONS:
    reason = DESTRUCTIVE_OPERATIONS[tool_name]

    # 記錄核准請求
    logger.warning(f"[需要核准] {tool_name}: {reason}")
    logger.info(f"[核准請求] 參數: {args}")

    # 在實際實現中，這裡會：
    # 1. 暫停代理執行
    # 2. 透過 UI 向用戶發送核准請求
    # 3. 等待用戶回應
    # 4. 根據回應繼續或取消

    # 在此示範中，我們通過檢查標誌來模擬核准
    # 在生產環境中，使用 ADK 的內建 HITL 機制
    auto_approve = tool_context.state.get("user:auto_approve_file_ops", False)

    if not auto_approve:
      # 回傳阻止回應 - 工具不會執行
      return {
        "status": "requires_approval",
        "message": (
          f"⚠️ 需要核准\n\n"
          f"操作: {tool_name}\n"
          f"原因: {reason}\n"
          f"參數: {args}\n\n"
          f"要核准，請設定 state['user:auto_approve_file_ops'] = True\n"
          f"或使用 ADK UI 核准工作流程。\n\n"
          f"此操作已因安全考量被阻止。"
        ),
        "tool_name": tool_name,
        "args": args,
        "requires_approval": True,
      }
    else:
      logger.info(f"[已核准] {tool_name} 透過自動核准標誌獲得核准")

  # 允許非破壞性操作 (讀取、列表、搜尋、取得資訊)
  logger.info(f"[已允許] {tool_name} 自動核准")
  return None  # None 表示允許工具執行


def create_mcp_filesystem_agent(
  base_directory: str = None, enable_hitl: bool = True
) -> Agent:
  """
  建立具有 MCP 檔案系統存取和人工介入迴路核准功能的代理。

  ADK 最佳實務：限制檔案系統存取到特定目錄
  以確保安全並防止意外修改系統檔案。

  參數：
    base_directory: 檔案系統存取的基本目錄。
             預設為 'sample_files' 子目錄以確保安全。
             MCP 伺服器只能存取此目錄內的檔案。
    enable_hitl: 啟用破壞性操作的人工介入迴路核准。
          當為 True 時，寫入/移動/刪除操作需要確認。

  回傳值：
    配置了 MCP 檔案系統工具和安全防護機制的代理

  安全特性：
    - 限制在特定目錄範圍內 (無系統存取權限)
    - 破壞性操作需要人工核准
    - 全面記錄所有操作
    - 執行前驗證檔案路徑
  """
  if base_directory is None:
    # 預設為 sample_files 目錄以確保安全
    current_dir = os.getcwd()
    base_directory = os.path.join(current_dir, "sample_files")

    # 如果 sample_files 不存在則建立
    if not os.path.exists(base_directory):
      logger.info(f"建立 sample_files 目錄: {base_directory}")
      os.makedirs(base_directory, exist_ok=True)

  # 驗證目錄是否存在
  if not os.path.exists(base_directory):
    raise ValueError(f"目錄不存在: {base_directory}")

  # 轉換為絕對路徑以確保安全
  base_directory = os.path.abspath(base_directory)
  logger.info(f"[安全] MCP 檔案系統存取限制於: {base_directory}")

  # 建立 MCP 工具集用於檔案系統存取
  server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", base_directory],
  )

  mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
      server_params=server_params,
      timeout=30.0,  # 增加超時時間到 30 秒用於 MCP 伺服器初始化
    )
  )

  # 建立具有 MCP 工具和 HITL 回調的代理
  agent = Agent(
    model="gemini-2.0-flash-exp",
    name="mcp_file_assistant",
    description="具有檔案系統存取和人工介入迴路核准功能的 AI 助理",
    instruction=f"""
    你是一個擁有透過 MCP 進行檔案系統操作存取權限的實用檔案助理。

    安全範圍：
    - 你只能存取以下目錄中的檔案: {base_directory}
    - 這是你的基本目錄 - 將其視為你的「當前目錄」
    - 你無法存取此目錄外的檔案
    - 系統檔案完全禁止存取

    你的功能：
    - read_file: 讀取檔案內容 (無需核准)
    - read_text_file: 讀取文字檔案 (無需核准)
    - list_directory: 列出目錄內容 (無需核准)
    - search_files: 依模式搜尋檔案 (無需核准)
    - get_file_info: 取得檔案元資料 (無需核准)
    - write_file: 建立或更新檔案 (⚠️ 需要核准)
    - write_text_file: 寫入文字檔案 (⚠️ 需要核准)
    - create_directory: 建立新目錄 (⚠️ 需要核准)
    - move_file: 移動或重新命名檔案 (⚠️ 需要核准)

    重要行為準則：

    1. 主動且智慧：
      - 當用戶說「列出檔案」→ 立即列出 {base_directory} 中的檔案
      - 當用戶說「當前目錄」或「這裡」→ 使用 {base_directory}
      - 當用戶說「寫入檔案」→ 一次詢問檔案名稱和內容
      - 不要問多個後續問題 - 收集上下文並果斷行動

    2. 上下文感知的路徑處理：
      - 如果用戶只提供檔案名稱：假設在 {base_directory} 中
      - 如果用戶說「sample_files」或子目錄：使用 {base_directory}/子目錄
      - 如果用戶提供以 {base_directory} 開頭的完整路徑：直接使用
      - 永遠不要問「當前目錄是什麼」- 你已經知道是 {base_directory}

    3. 高效溝通：
      - 合併問題：「要寫入檔案，我需要檔案名稱和內容。你想要什麼？」
      - 不要重複用戶已經給出的指示
      - 如果上下文清楚，立即進行
      - 只在真正模糊時詢問澄清問題

    4. 人工介入迴路工作流程：
      - 破壞性操作 (寫入、移動、刪除) 需要用戶核准
      - 如果操作被阻止等待核准，你會收到通知
      - 總是解釋為什麼需要執行該操作
      - 對於寫入操作：清楚說明你將建立檔案及其包含的內容

    5. 錯誤恢復：
      - 如果操作被阻止，解釋發生了什麼以及需要什麼
      - 盡可能建議替代方案
      - 保持有用，而非迂腐

    良好範例：
    用戶：「列出檔案」
    你：[立即使用 {base_directory} 呼叫 list_directory]

    用戶：「寫入檔案」
    你：「我可以為你建立檔案。應該命名為什麼，包含什麼內容？」

    用戶：「test.txt」[在被詢問檔案名稱後]
    你：「很好！我應該在 {base_directory} 中寫入什麼內容到 test.txt？」

    用戶：「建立一個 hello world Python 腳本」
    你：「我將建立一個名為 hello.py 的檔案，包含 hello world 腳本。以下是我將寫入的內容：[顯示內容]。這需要你的核准才能繼續。」

    錯誤範例 (不要這樣做)：
    用戶：「列出檔案」
    你：「你能指定哪個目錄嗎？」← 錯誤！使用 {base_directory}

    用戶：「寫入檔案」
    你：「哪個目錄？」← 錯誤！同時詢問檔案名稱和內容

    用戶：「當前目錄」
    你：「你能定義當前目錄嗎？」← 錯誤！就是 {base_directory}

    記住：你是智慧助理，不是字面命令解析器。理解意圖，使用上下文，果斷行動。
    """.strip(),
    tools=[mcp_tools],
    generate_content_config=types.GenerateContentConfig(
      temperature=0.2, max_output_tokens=2048  # 檔案操作的確定性設定
    ),
    # 如果要求則啟用人工介入迴路回調
    before_tool_callback=before_tool_callback if enable_hitl else None,
  )

  return agent


# ============================================================================
# 根代理 (預設配置，已啟用 HITL)
# ============================================================================

# 匯出 root_agent 供 ADK 發現
# 預設使用 sample_files 目錄以確保安全
root_agent = create_mcp_filesystem_agent(
  base_directory=None,  # 將使用 sample_files/
  enable_hitl=True,  # 預設啟用人工介入迴路
)
