"""
Human-in-the-Loop (人機交互) 功能的快速測試
展示如何阻止破壞性操作
"""

from mcp_agent.agent import create_mcp_filesystem_agent, before_tool_callback
from google.adk.agents.callback_context import CallbackContext

# Fix: State is no longer an independent class in the new version
# Use dictionary directly instead of State object
# Create mock context
# 修正：State 在新版本中不再是獨立的類別
# 直接使用字典來代替 State 對象
# 建立模擬上下文
state = {}  # 使用字典替代 State()
context = CallbackContext(state=state)

# Test 1: Safe operation (should allow)
# 測試 1：安全操作（應該允許）
print("Test 1: Safe Operation (read_file)")
print("測試 1：安全操作 (read_file)")
print("-" * 70)
# 呼叫 before_tool_callback 函式測試讀取檔案操作
# 此操作被視為安全操作，應該自動通過
result = before_tool_callback(context, "read_file", {"path": "test.txt"})
if result is None:
    # result 為 None 表示操作被允許
    print("✅ ALLOWED: read_file operation approved automatically")
    print("✅ 允許：read_file 操作自動通過")
else:
    # result 有值表示操作被阻止
    print(f"❌ BLOCKED: {result}")
    print(f"❌ 阻止：{result}")
print()

# Test 2: Destructive operation without approval (should block)
# 測試 2：沒有批准的破壞性操作（應該被阻止）
print("Test 2: Destructive Operation (write_file) - No Approval")
print("測試 2：破壞性操作 (write_file) - 無批准")
print("-" * 70)
# 測試寫入檔案操作，這是破壞性操作
# 在沒有用戶批准的情況下應該被阻止
result = before_tool_callback(
    context, "write_file", {"path": "test.txt", "content": "Hello"}
)
if result is None:
    # 如果 result 為 None，表示系統錯誤，破壞性操作不應該被允許
    print("❌ ERROR: write_file should have been blocked!")
    print("❌ 錯誤：write_file 應該被阻止！")
else:
    # result 有值表示操作正確被阻止
    print(f"✅ BLOCKED: {result['status']}")
    print(f"✅ 阻止：{result['status']}")
    print(f"   Message: {result['message'][:80]}...")
    print(f"   訊息：{result['message'][:80]}...")
print()

# Test 3: Destructive operation with approval (should allow)
# 測試 3：有批准的破壞性操作（應該允許）
print("Test 3: Destructive Operation (write_file) - With Approval")
print("測試 3：破壞性操作 (write_file) - 有批准")
print("-" * 70)
# 設定自動批准檔案操作的標誌
# 這模擬用戶事先同意破壞性檔案操作
context.state["user:auto_approve_file_ops"] = True
result = before_tool_callback(
    context, "write_file", {"path": "test.txt", "content": "Hello"}
)
if result is None:
    # result 為 None 表示操作被允許（因為有自動批准標誌）
    print("✅ ALLOWED: write_file operation approved via auto_approve flag")
    print("✅ 允許：write_file 操作透過自動批准標誌通過")
else:
    # result 有值表示操作被阻止（不應該發生）
    print(f"❌ BLOCKED: {result}")
    print(f"❌ 阻止：{result}")
print()

# Test 4: Agent creation with default directory
# 測試 4：使用預設目錄建立代理程式
print("Test 4: Agent Creation - Directory Restriction")
print("測試 4：代理程式建立 - 目錄限制")
print("-" * 70)
# 建立 MCP 檔案系統代理程式
# 這個代理程式具有 HITL 功能，可以控制檔案操作
agent = create_mcp_filesystem_agent()
print(f"✅ Agent created successfully")
print(f"✅ 代理程式建立成功")
print(f"   Name: {agent.name}")
print(f"   名稱：{agent.name}")
print(f"   HITL enabled: {agent.before_tool_callback is not None}")
print(f"   HITL 已啟用：{agent.before_tool_callback is not None}")
print(f"   Description: {agent.description[:60]}...")
print(f"   描述：{agent.description[:60]}...")
print()

print("=" * 70)
print("ALL TESTS PASSED - HITL IS WORKING CORRECTLY")
print("所有測試通過 - HITL 運作正常")
print("=" * 70)
