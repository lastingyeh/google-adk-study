#!/usr/bin/env python3
"""
輔助腳本，用於以可讀格式檢視存儲在 Redis 中的會話數據。

用法：
    python view_sessions.py              # 顯示所有會話
    python view_sessions.py <session_id> # 顯示特定會話
"""

import redis
import json
import sys
from typing import Optional

def connect_to_redis(uri: str = "redis://localhost:6379/0") -> redis.Redis:
    """連接至 Redis。"""
    try:
        # 建立 Redis 連線，decode_responses=True 會自動將 bytes 轉為字串
        client = redis.from_url(uri, decode_responses=True)
        client.ping()
        return client
    except Exception as e:
        print(f"❌ 無法連接至 Redis：{e}")
        sys.exit(1)

def print_session(key: str, data: dict) -> None:
    """美化輸出單一會話資訊。"""
    print(f"\n{'=' * 80}")
    print(f"📋 會話鍵名 (SESSION KEY): {key}")
    print('=' * 80)

    print(f"\n🔑 會話 ID:        {data.get('session_id', 'N/A')}")
    print(f"📱 應用程式名稱:    {data.get('app_name', 'N/A')}")
    print(f"👤 使用者 ID:       {data.get('user_id', 'N/A')}")
    print(f"📅 建立時間:        {data.get('created_at', 'N/A')}")
    print(f"🔄 更新時間:        {data.get('updated_at', 'N/A')}")

    state = data.get('state', {})
    if state:
        print(f"\n📦 會話狀態 (SESSION STATE) ({len(state)} 個項目):")
        for key, value in state.items():
            print(f"   • {key}: {json.dumps(value) if not isinstance(value, (str, int, float, bool)) else value}")
    else:
        print(f"\n📦 會話狀態 (SESSION STATE): (空)")

    events = data.get('events', [])
    if events:
        print(f"\n📝 事件紀錄 (EVENTS) (共 {len(events)} 筆):")
        for i, event in enumerate(events, 1):
            # 輸出每個事件的 JSON 內容
            print(f"   {i}. {json.dumps(event, indent=6)}")
    else:
        print(f"\n📝 事件紀錄 (EVENTS): (無)")

    print()

def view_all_sessions() -> None:
    """顯示存儲在 Redis 中的所有會話。"""
    client = connect_to_redis()

    print("\n" + "=" * 80)
    print("🔍 Redis 會話查詢 - 全部")
    print("=" * 80)

    # 查找所有以 'session:' 開頭的鍵名
    keys = client.keys("session:*")

    if not keys:
        print("\n❌ 在 Redis 中找不到任何會話")
        return

    print(f"\n✅ 在 Redis 中找到 {len(keys)} 個會話\n")

    for i, key in enumerate(sorted(keys), 1):
        session_json = client.get(key)
        if session_json:
            try:
                session_data = json.loads(session_json)
                print(f"\n{i}. {key}")
                print(f"   📝 狀態鍵名: {list(session_data.get('state', {}).keys())}")
                print(f"   ⏱️  建立時間: {session_data.get('created_at', 'N/A')}")
                print(f"   📊 事件數量: {len(session_data.get('events', []))}")
            except json.JSONDecodeError:
                print(f"❌ 無法解析鍵名為 {key} 的會話數據")

def view_session(session_id: str) -> None:
    """顯示特定的會話詳細資訊。"""
    client = connect_to_redis()

    # 嘗試匹配包含 session_id 的鍵名
    pattern = f"session:*{session_id}*"
    keys = client.keys(pattern)

    if not keys:
        print(f"\n❌ 找不到匹配 '{session_id}' 的會話")
        return

    if len(keys) > 1:
        print(f"\n⚠️  有多個會話匹配 '{session_id}':")
        for key in keys:
            print(f"   • {key}")
        print("\n正在顯示第一個匹配項...\n")

    key = keys[0]
    session_json = client.get(key)

    if not session_json:
        print(f"❌ 找不到會話：{key}")
        return

    try:
        session_data = json.loads(session_json)
        print_session(key, session_data)
    except json.JSONDecodeError as e:
        print(f"❌ 解析會話數據失敗：{e}")

def main():
    """主要入口點。"""
    if len(sys.argv) > 1:
        # 檢視特定會話
        session_id = sys.argv[1]
        view_session(session_id)
    else:
        # 檢視所有會話
        view_all_sessions()

    print("\n" + "=" * 80)
    print("💡 提示：若要檢視特定會話，請執行：")
    print("   python view_sessions.py <session_id>")
    print("\n🔗 常用 Redis 指令：")
    print("   redis-cli KEYS 'session:*'")
    print("   redis-cli GET 'session:app:user:id'")
    print("   redis-cli TTL 'session:app:user:id'  # 檢查過期時間")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

"""
### 重點摘要
- **核心概念**：Redis 會話數據可視化工具。
- **關鍵技術**：Redis Python Client, JSON Parsing, CLI Argument Handling。
- **重要結論**：此工具提供了一個直觀的方式來檢視存儲在 Redis 中的會話狀態與事件歷史。
- **行動項目**：在 Agent 運作期間使用此腳本來除錯或監控對話狀態。
"""
