#!/usr/bin/env python3
"""
清理所有 File Search stores 以重新開始。

此腳本會刪除所有與 policy navigator 相關的 File Search stores，
讓您可以從完全乾淨的狀態重新開始。

使用方法：
    python scripts/cleanup_stores.py
"""

import sys
from pathlib import Path

# 將父目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from policy_navigator.stores import StoreManager
from loguru import logger


def main():
    """刪除所有 File Search stores。"""
    try:
        store_manager = StoreManager()

        print("\n正在擷取所有 File Search stores...")
        stores = store_manager.list_stores()

        if not stores:
            print("✓ 沒有可刪除的 File Search stores")
            return True

        print(f"\n找到 {len(stores)} 個 stores:")
        for store in stores:
            display_name = store.get("display_name", "Unknown")
            store_id = store.get("name", "Unknown")
            print(f"  - {display_name} ({store_id})")

        print(f"\n正在刪除所有 {len(stores)} 個 stores...")
        print("-" * 70)

        deleted_count = 0
        for store in stores:
            store_id = store.get("name")
            display_name = store.get("display_name", "Unknown")

            try:
                if store_manager.delete_store(store_id, force=True):
                    print(f"✓ 已刪除: {display_name}")
                    deleted_count += 1
                else:
                    print(f"✗ 刪除失敗: {display_name}")
            except Exception as e:
                print(f"✗ 刪除 {display_name} 時發生錯誤: {str(e)}")

        print("-" * 70)
        print(f"\n✓ 成功刪除 {deleted_count}/{len(stores)} 個 stores")
        print("\n若要以新的 stores 重新開始，請執行：")
        print("  make demo-upload")

        return True

    except Exception as e:
        logger.error(f"清理 stores 失敗: {str(e)}")
        print(f"\n✗ 錯誤: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
