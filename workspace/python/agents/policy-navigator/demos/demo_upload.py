#!/usr/bin/env python3
"""
展示：上傳政策文件到 File Search Store

此展示說明如何：
1. 為不同的政策部門建立 File Search Stores
2. 上傳範例政策文件
3. 為文件加入 metadata
4. 驗證上傳成功

在 .env 檔案中設定 GOOGLE_API_KEY 後執行此展示：
    python demos/demo_upload.py
"""

import sys
from pathlib import Path

# 將父目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from policy_navigator.config import Config
from policy_navigator.utils import (
    validate_api_key,
    get_policy_files,
    get_store_name_for_policy,
)
from policy_navigator.stores import StoreManager
from policy_navigator.metadata import MetadataSchema


def main():
    """執行上傳展示。"""

    print("\n" + "=" * 70)
    print("Policy Navigator - 展示：上傳政策文件")
    print("=" * 70 + "\n")

    # 驗證 API 金鑰
    if not validate_api_key():
        print("\n✗ GOOGLE_API_KEY 未設定。請設定您的 API 金鑰。")
        print("  請參閱 .env.example 取得說明。")
        return False

    try:
        store_manager = StoreManager()

        # 步驟 1：建立或重複使用 File Search Stores
        print("步驟 1：建立或重複使用 File Search Stores")
        print("-" * 70)

        stores = {}
        for store_type, store_name in Config.get_store_names().items():
            print(f"  {store_type.upper()} store: {store_name}")
            try:
                # 檢查 store 是否已存在 (重複使用模式)
                existing_store = store_manager.get_store_by_display_name(store_name)
                if existing_store:
                    stores[store_type] = existing_store
                    print(f"    → 使用現有 store: {existing_store}\n")
                else:
                    # 只有在不存在時才建立新 store
                    store_id = store_manager.create_policy_store(store_name)
                    stores[store_type] = store_id
                    print(f"    → 建立新 store: {store_id}\n")
            except Exception as e:
                print(f"    ✗ 失敗: {str(e)}\n")

        # 步驟 2：取得政策檔案
        print("\n步驟 2：尋找政策檔案")
        print("-" * 70)

        policy_files = get_policy_files()

        if not policy_files:
            print("  ✗ 在 sample_policies/ 中找不到政策檔案")
            return False

        print(f"  找到 {len(policy_files)} 個政策檔案:")
        for pf in policy_files:
            print(f"    - {Path(pf).name}")

        # 步驟 3：上傳文件
        print("\n\n步驟 3：上傳政策文件")
        print("-" * 70)

        uploaded_count = 0
        for policy_file in policy_files:
            policy_name = Path(policy_file).name
            store_type = get_store_name_for_policy(policy_name)
            store_id = stores.get(store_type)

            if not store_id:
                print(f"\n  ✗ 無法為 {policy_name} 設定 store")
                continue

            print(f"\n  正在上傳: {policy_name}")
            print(f"    Store: {store_type}")

            # 取得適當的 metadata
            if "hr" in policy_name.lower() or "handbook" in policy_name.lower():
                metadata = MetadataSchema.hr_metadata()
            elif "it" in policy_name.lower() or "security" in policy_name.lower():
                metadata = MetadataSchema.it_metadata()
            elif "remote" in policy_name.lower():
                metadata = MetadataSchema.remote_work_metadata()
            else:
                metadata = MetadataSchema.code_of_conduct_metadata()

            try:
                result = store_manager.upsert_file_to_store(
                    policy_file,
                    store_id,
                    display_name=policy_name,
                    metadata=metadata,
                )

                if result:
                    print("    ✓ Upsert (更新插入) 成功")
                    uploaded_count += 1
                else:
                    print("    ✗ Upsert (更新插入) 失敗")

            except Exception as e:
                print(f"    ✗ 錯誤: {str(e)}")

        # 步驟 4：列出 stores
        print("\n\n步驟 4：驗證 Stores")
        print("-" * 70)

        try:
            all_stores = store_manager.list_stores()
            print(f"\n  File Search Stores 總數: {len(all_stores)}")

            for store in all_stores:
                store_name = store.get("name", "Unknown")
                display_name = store.get("display_name", "Unknown")
                print(f"    - {display_name}")
                print(f"      ID: {store_name}")

        except Exception as e:
            print(f"  ✗ 列出 stores 失敗: {str(e)}")

        # 摘要
        print("\n\n" + "=" * 70)
        print("展示完成")
        print("=" * 70)
        print(f"\n✓ 成功上傳 {uploaded_count}/{len(policy_files)} 個政策")
        print("\n下一步：")
        print("  1. 執行 demo_search.py 測試搜尋政策")
        print("  2. 執行 demo_full_workflow.py 進行完整工作流程")
        print("  3. 使用 'make dev' 啟動互動式網頁介面")
        print()

        return True

    except Exception as e:
        print(f"\n✗ 展示失敗，錯誤: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
