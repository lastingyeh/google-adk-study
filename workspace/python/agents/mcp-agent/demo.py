#!/usr/bin/env python3
"""
教程 16：MCP 整合 - 示範腳本
展示 MCP 檔案系統操作和文件組織功能。

執行方式：
  python demo.py
"""

import sys
from pathlib import Path

# 將父目錄加入路徑以供匯入模組使用
sys.path.insert(0, str(Path(__file__).parent))

from mcp_agent import root_agent


def print_header(title: str):
  """印出格式化的標題。"""
  print("\n" + "=" * 70)
  print(f"  {title}")
  print("=" * 70 + "\n")


def demo_filesystem_operations():
  """透過 MCP 示範基本檔案系統操作。"""
  print_header("MCP 檔案系統操作示範")

  print("🚀 MCP 代理程式配置：")
  print(f"   模型：{root_agent.model}")
  print(f"   名稱：{root_agent.name}")
  print(f"   工具：{len(root_agent.tools)} 個 MCP 工具集")
  print()

  print("📝 可用操作：")
  print("   - 列出目錄中的檔案")
  print("   - 讀取檔案內容")
  print("   - 建立新檔案")
  print("   - 搜尋檔案")
  print("   - 取得檔案資訊")
  print("   - 移動/重新命名檔案")
  print("   - 建立目錄")
  print()

  print("💡 在 ADK 網頁介面中嘗試這些查詢：")
  print()
  print("1. 列出檔案：")
  print("   '列出當前目錄中的所有檔案'")
  print()
  print("2. 讀取檔案：")
  print("   '讀取 README.md 的內容'")
  print()
  print("3. 建立檔案：")
  print("   '建立一個名為 demo.txt 的測試檔案，內容為：Hello MCP!'")
  print()
  print("4. 搜尋檔案：")
  print("   '找出此目錄中所有的 Python 檔案'")
  print()
  print("5. 檔案資訊：")
  print("   'requirements.txt 的檔案大小是多少？'")
  print()


def demo_connection_types():
  """示範不同的 MCP 連線類型。"""
  print_header("MCP 連線類型（ADK 1.16.0+）")

  print("📡 可用的連線方法：")
  print()

  print("1. Stdio（本地）：")
  print("   - 最適合：本地開發、檔案操作")
  print("   - 使用：Node.js npx 命令")
  print("   - 範例：檔案系統、本地資料庫")
  print()

  print("2. SSE（伺服器發送事件）：")
  print("   - 最適合：即時資料串流")
  print("   - 使用：HTTPS 端點")
  print("   - 支援：OAuth2 認證")
  print("   - 範例：即時儀表板、監控系統")
  print()

  print("3. HTTP 串流：")
  print("   - 最適合：雙向通訊")
  print("   - 使用：HTTPS 端點")
  print("   - 支援：OAuth2 認證")
  print("   - 範例：互動式 API、複雜工作流程")
  print()


def demo_authentication():
  """示範 MCP 認證選項。"""
  print_header("MCP 認證（生產環境）")

  print("🔐 支援的認證方法：")
  print()

  print("1. OAuth2（推薦）：")
  print("   - 生產環境最安全")
  print("   - 自動更新令牌")
  print("   - 支援範圍和權限控制")
  print()

  print("2. Bearer Token：")
  print("   - 簡單的 API 認證")
  print("   - 適合內部服務")
  print()

  print("3. HTTP Basic：")
  print("   - 使用者名稱/密碼認證")
  print("   - 僅用於舊版系統")
  print()

  print("4. API Key：")
  print("   - 基於標頭的認證")
  print("   - 常見於雲端服務")
  print()


def demo_best_practices():
  """示範 MCP 最佳實踐。"""
  print_header("MCP 最佳實踐")

  print("✅ 應該做的：")
  print("   - 連接前驗證目錄路徑")
  print("   - 生產環境使用 OAuth2")
  print("   - 啟用 retry_on_closed_resource")
  print("   - 為代理程式提供清楚的指示")
  print("   - 妥善處理連線錯誤")
  print("   - 安全地儲存憑證（環境變數）")
  print()

  print("❌ 不應該做的：")
  print("   - 硬編碼 API 金鑰或憑證")
  print("   - 忽略連線失敗")
  print("   - 在面向網際網路的服務中使用基本認證")
  print("   - 在不同環境間共用憑證")
  print()


def demo_quick_start():
  """顯示快速開始命令。"""
  print_header("快速開始指南")

  print("🚀 三步驟開始使用：")
  print()

  print("1. 設定：")
  print("   $ make setup")
  print()

  print("2. 配置：")
  print("   $ cp mcp_agent/.env.example mcp_agent/.env")
  print("   # 編輯 .env 並加入您的 GOOGLE_API_KEY")
  print()

  print("3. 執行：")
  print("   $ make dev")
  print("   # 開啟 http://localhost:8000")
  print()

  print("📚 參考資源：")
  print("   - 教程：docs/tutorial/16_mcp_integration.md")
  print("   - MCP 規範：https://spec.modelcontextprotocol.io/")
  print("   - 伺服器：https://github.com/modelcontextprotocol/servers")
  print()


def main():
  """執行所有示範。"""
  print("\n" + "🎓 " * 35)
  print("  教程 16：模型上下文協定 (MCP) 整合")
  print("🎓 " * 35)

  try:
    # 依序執行各個示範函數
    demo_quick_start()          # 快速開始指南
    demo_filesystem_operations() # 檔案系統操作示範
    demo_connection_types()     # 連線類型示範
    demo_authentication()       # 認證方法示範
    demo_best_practices()       # 最佳實踐示範

    print_header("下一步")
    print("✅ 準備嘗試 MCP 整合！")
    print()
    print("1. 執行 'make dev' 啟動 ADK 伺服器")
    print("2. 在瀏覽器中開啟 http://localhost:8000")
    print("3. 嘗試上述示範查詢")
    print("4. 探索社群中的其他 MCP 伺服器")
    print()
    print("📖 繼續到教程 17：代理程式間通訊")
    print()

  except Exception as e:
    # 錯誤處理：顯示錯誤訊息和故障排除建議
    print(f"\n❌ 錯誤：{e}")
    print("\n故障排除：")
    print("  - 確保已執行 'make setup'")
    print("  - 檢查 Node.js 和 npx 是否已安裝")
    print("  - 驗證您的 .env 配置")
    return 1

  return 0


if __name__ == "__main__":
  # 程式進入點：執行主函數並以其回傳值作為程式結束狀態
  sys.exit(main())
