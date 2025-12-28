"""
Terminal Server - MCP Stdio Server 實作範例

重點摘要:
- **核心概念**: MCP Stdio Server 範例，提供終端機命令執行能力。
- **關鍵技術**: `FastMCP`, `subprocess` (執行系統指令), Stdio Transport。
- **重要結論**: 實作了一個可以在伺服器端執行 Shell 指令的工具，這是一個強大但也潛在危險的功能，需謹慎使用。

安全性警告:
⚠️ 此工具允許執行任意系統命令，存在以下安全風險:
  1. 命令注入攻擊 (Command Injection)
  2. 未授權的系統存取
  3. 潛在的資料洩露
  4. 系統資源濫用

設計模式:
- **工具模式 (Tool Pattern)**: 使用 @mcp.tool 裝飾器註冊工具
- **錯誤處理**: 基本的例外捕捉機制
- **標準輸出捕捉**: 使用 subprocess 的 capture_output

建議改善方向:
- 實作命令白名單機制
- 加入使用者權限驗證
- 增強日誌記錄功能
- 實作超時限制和資源控制
- 加入命令審計追蹤
"""

from mcp.server.fastmcp import FastMCP
import os
import subprocess
import logging
import shlex
from typing import Optional

# 設定日誌記錄器 (Configure logger for debugging and monitoring)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化 FastMCP 伺服器 (Initialize FastMCP server instance)
mcp = FastMCP("terminal_server")

# 預設工作目錄 (Default working directory for command execution)
# 使用者家目錄下的 mcp/workspace 作為安全的執行環境
DEFAULT_WORKSPACE = os.path.expanduser(
    "/Users/cfh00543956/Desktop/Labs/google-adk-study/workspace/python/agents/mcp-a2a-master/mcp/workspace"
)

# 確保工作目錄存在 (Ensure workspace directory exists)
os.makedirs(DEFAULT_WORKSPACE, exist_ok=True)
logger.info(f"Terminal Server initialized with workspace: {DEFAULT_WORKSPACE}")


@mcp.tool("terminal_server")
async def run_command(command: str) -> str:
    """
    在終端機中執行指令並回傳輸出。

    ⚠️ 安全性警告 (Security Warning):
    此函數使用 shell=True 執行命令,存在命令注入風險。
    建議僅在受信任的環境中使用,或實作命令白名單驗證。

    執行流程 (Execution Flow):
    1. 記錄命令執行請求
    2. 在指定的工作目錄中執行命令
    3. 捕捉標準輸出和標準錯誤
    4. 記錄執行結果並返回

    Args:
        command (str): 要在終端機中執行的指令。
                      The command to run in the terminal.
                      注意: 此命令將以 shell 模式執行,請避免使用不受信任的輸入。

    Returns:
        str: 指令的輸出 (stdout 或 stderr)。
             如果指令執行失敗,則回傳錯誤訊息。
             The output of the command (stdout or stderr).
             Returns error message if command execution fails.

    錯誤處理 (Error Handling):
        - subprocess.TimeoutExpired: 命令執行超時
        - subprocess.CalledProcessError: 命令返回非零狀態碼
        - Exception: 其他未預期的錯誤

    範例 (Examples):
        >>> await run_command("ls -la")
        >>> await run_command("pwd")
        >>> await run_command("echo 'Hello, World!'")
    """
    # 記錄命令執行請求 (Log command execution request)
    logger.info(f"收到命令執行請求 (Command execution requested): {command[:100]}...")

    # 驗證命令不為空 (Validate command is not empty)
    if not command or not command.strip():
        error_msg = "命令不能為空 (Command cannot be empty)"
        logger.warning(error_msg)
        return f"錯誤 (Error): {error_msg}"

    try:
        # 記錄執行環境 (Log execution environment)
        logger.debug(f"執行目錄 (Working directory): {DEFAULT_WORKSPACE}")

        # 執行命令 (Execute command)
        # 使用 shell=True 允許執行複雜的 shell 命令,但也帶來安全風險
        # timeout 設定為 30 秒以避免長時間運行的命令阻塞
        result = subprocess.run(
            command,
            shell=True,  # ⚠️ 安全風險: 啟用 shell 解析
            cwd=DEFAULT_WORKSPACE,  # 在指定目錄中執行
            text=True,  # 以文字模式處理輸出
            capture_output=True,  # 捕捉 stdout 和 stderr
            timeout=30,  # 30 秒超時限制
        )

        # 組合輸出結果 (Combine output results)
        output = result.stdout or result.stderr

        # 記錄執行結果 (Log execution result)
        if result.returncode == 0:
            logger.info(
                f"命令執行成功 (Command executed successfully), 返回碼: {result.returncode}"
            )
        else:
            logger.warning(
                f"命令執行完成但返回非零狀態碼 (Command completed with non-zero exit code): {result.returncode}"
            )

        # 記錄輸出長度 (Log output length)
        logger.debug(f"輸出長度 (Output length): {len(output)} 字元")

        return (
            output if output else f"命令執行完成,返回碼: {result.returncode},但無輸出"
        )

    except subprocess.TimeoutExpired as e:
        # 命令執行超時 (Command execution timeout)
        error_msg = f"命令執行超時 (Command timeout after 30s): {command[:50]}..."
        logger.error(error_msg)
        return f"錯誤 (Error): {error_msg}"

    except subprocess.CalledProcessError as e:
        # 命令返回錯誤狀態碼 (Command returned error status code)
        error_msg = f"命令執行失敗 (Command failed) [退出碼 {e.returncode}]: {str(e)}"
        logger.error(error_msg)
        return f"錯誤 (Error): {error_msg}"

    except PermissionError as e:
        # 權限不足 (Permission denied)
        error_msg = f"權限不足 (Permission denied): {str(e)}"
        logger.error(error_msg)
        return f"錯誤 (Error): {error_msg}"

    except FileNotFoundError as e:
        # 找不到命令或檔案 (Command or file not found)
        error_msg = f"找不到命令或檔案 (Command or file not found): {str(e)}"
        logger.error(error_msg)
        return f"錯誤 (Error): {error_msg}"

    except Exception as e:
        # 其他未預期的錯誤 (Other unexpected errors)
        error_msg = (
            f"執行指令時發生未預期的錯誤 (Unexpected error running command): {str(e)}"
        )
        logger.exception(error_msg)  # 記錄完整的堆疊追蹤
        return f"錯誤 (Error): {error_msg}"


if __name__ == "__main__":
    """
    主程式入口點 (Main entry point)

    啟動 MCP 伺服器並使用 stdio 傳輸協定進行通訊。

    傳輸模式 (Transport Mode):
    - stdio: 使用標準輸入/輸出進行通訊,適合作為子程序運行

    使用方式 (Usage):
        python terminal_server.py
    """
    try:
        logger.info("正在啟動 Terminal Server... (Starting Terminal Server...)")
        logger.info(f"工作目錄 (Workspace): {DEFAULT_WORKSPACE}")
        logger.warning("⚠️ 安全提醒: 此伺服器允許執行任意命令,請僅在受信任的環境中使用")

        # 啟動 MCP 伺服器 (Start MCP server)
        mcp.run(transport="stdio")

    except KeyboardInterrupt:
        logger.info(
            "收到中斷信號,正在關閉伺服器... (Received interrupt signal, shutting down...)"
        )
    except Exception as e:
        logger.exception(f"伺服器啟動失敗 (Server startup failed): {str(e)}")
        raise
