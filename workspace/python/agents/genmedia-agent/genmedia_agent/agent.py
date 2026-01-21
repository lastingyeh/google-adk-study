import os

# 從 google-adk==1.3.0 開始，使用 StdioConnectionParams
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

# 載入環境變數
load_dotenv()

# 取得 Google Cloud 專案 ID
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

# MCP 客戶端 (STDIO 方式)
# 假設你已經在系統路徑中安裝了 MCP 伺服器

# Veo 影片生成工具集
veo = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="mcp-veo-go",  # 執行 Veo 伺服器指令
            env=dict(os.environ, PROJECT_ID=project_id),  # 傳遞環境變數
        ),
        timeout=60,  # 連線逾時設定（秒）
    ),
)

# Chirp3 音訊生成工具集
chirp3 = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="mcp-chirp3-go",  # 執行 Chirp3 伺服器指令
            env=dict(os.environ, PROJECT_ID=project_id),
        ),
        timeout=60,
    ),
)

# Imagen 圖片生成工具集
imagen = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="mcp-imagen-go",  # 執行 Imagen 伺服器指令
            env=dict(os.environ, PROJECT_ID=project_id),
        ),
        timeout=60,
    ),
)

# MCP 客戶端 (SSE 方式) - 範例註解
# 假設你已經另外啟動 MCP 伺服器
# 例如：mcp-imagen-go --transport sse
# from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
# imagen = MCPToolset(
#     connection_params=StreamableHTTPConnectionParams(
#         url="http://localhost:8081/sse",
#         timeout=60,
#         sse_read_timeout=300,

#     )
# )

# AVTool 音視訊合成工具集
avtool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="mcp-avtool-go",  # 執行 AVTool 伺服器指令
            env=dict(os.environ, PROJECT_ID=project_id),
        ),
        timeout=240,  # 較長的逾時設定，因為音視訊處理需要更多時間
    ),
)

# 建立主要代理程式
root_agent = LlmAgent(
    model="gemini-2.0-flash",  # 使用 Gemini 2.0 Flash 模型
    name="genmedia_agent",  # 代理程式名稱
    instruction="""你是一個創意助理，可以透過生成式媒體工具協助使用者創建音訊、圖片和影片。你也有能力使用可用的工具來合成這些媒體。
    請根據你所知道的資訊或能從工具中檢索的資訊，積極提供有用的建議。
    如果被要求翻譯成其他語言，請執行翻譯。
    """,
    tools=[
        imagen,  # 圖片生成工具
        chirp3,  # 音訊生成工具
        veo,  # 影片生成工具
        avtool,  # 音視訊合成工具
    ],
)
