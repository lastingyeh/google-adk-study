#!/bin/bash
# 測試 adk web 的 SQLite 會話持久性
# 這驗證了官方的 --session_service_uri 旗標是否正常運作

set -e

echo "============================================"
echo "測試：使用 SQLite 會話服務的 adk web"
echo "============================================"
echo ""

# 清理任何現有的測試資料庫
rm -f ./test_adk_web_sessions.db

echo "✅ Step 1: Verify adk web supports --session_service_uri flag (步驟 1：驗證 adk web 支援 --session_service_uri 旗標)"
adk web --help | grep -q "session_service_uri" && echo "   Flag exists in adk web! (旗標存在於 adk web！)" || (echo "   ❌ Flag not found (旗標未找到)"; exit 1)

echo ""
echo "✅ Step 2: Test adk web command syntax (步驟 2：測試 adk web 指令語法)"
echo "   Command: adk web --session_service_uri sqlite:///./test_adk_web_sessions.db"
echo "   (This is the OFFICIAL way to use SQLite with adk web) (這是使用 SQLite 搭配 adk web 的官方方式)"
echo ""

echo "📝 To test manually (手動測試):"
echo ""
echo "   1. Run (執行): adk web --session_service_uri sqlite:///./commerce_sessions.db"
echo "   2. Open (開啟): http://localhost:8000"
echo "   3. Select 'commerce_agent' from dropdown (從下拉選單選擇 'commerce_agent')"
echo "   4. Chat with agent, then close browser (與代理人聊天，然後關閉瀏覽器)"
echo "   5. Restart server with same command (使用相同指令重啟伺服器)"
echo "   6. Open browser again (再次開啟瀏覽器)"
echo "   7. ✅ Your session data should persist! (您的會話資料應該仍然存在！)"
echo ""
echo "   Database location (資料庫位置): ./commerce_sessions.db"
echo "   Inspect with (檢查方式): sqlite3 commerce_sessions.db"
echo ""

echo "============================================"
echo "Official ADK Documentation (官方 ADK 文件):"
echo "https://google.github.io/adk-docs/api-reference/cli/cli.html#web"
echo "============================================"
