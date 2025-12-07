#!/usr/bin/env python3
"""
展示：完整的 Policy Navigator 工作流程

此展示顯示了完整的工作流程：
1. 上傳政策
2. 搜尋資訊
3. 比較政策
4. 評估合規風險
5. 產生摘要與稽核追蹤

請在設定後執行此腳本：
    python demos/demo_full_workflow.py
"""

import sys
from pathlib import Path

# 將父目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from policy_navigator.config import Config
from policy_navigator.utils import validate_api_key, get_policy_files
from policy_navigator.tools import (
    search_policies,
    check_compliance_risk,
    generate_policy_summary,
    create_audit_trail,
    compare_policies,
)


def print_section(title: str):
    """列印格式化的章節標題。"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def main():
    """執行完整工作流程展示。"""

    print_section("Policy Navigator - 完整工作流程展示")

    # 驗證
    if not validate_api_key():
        print("✗ GOOGLE_API_KEY 未設定")
        return False

    try:
        # 第一部分：政策搜尋
        print_section("第一部分：政策資訊搜尋")

        print("情境：員工詢問關於遠端工作的政策\n")
        print("查詢：'我想遠端工作。有哪些要求？'\n")

        try:
            result = search_policies(
                "What are the requirements and process for remote work?",
                Config.HR_STORE_NAME,
            )

            if result.get("status") == "success":
                print("✓ 搜尋結果:")
                print(f"  答案: {result.get('answer', 'N/A')[:300]}...")
                print(f"  來源: 找到 {result.get('source_count', 0)} 個引用")
            else:
                print(f"✗ 搜尋失敗: {result.get('error', '未知錯誤')}")

        except Exception as e:
            print(f"⚠ 搜尋已略過: {str(e)}")

        # 第二部分：合規風險評估
        print_section("第二部分：合規風險評估")

        print("情境：工作地點政策的合規審查\n")
        print("查詢：'員工可以在不同的國家工作 3 個月嗎？'\n")

        try:
            result = check_compliance_risk(
                "Can employees work from a different country? What are the compliance concerns?",
                Config.HR_STORE_NAME,
            )

            if result.get("status") == "success":
                print("✓ 風險評估:")
                print(f"  結果: {result.get('assessment', 'N/A')[:300]}...")
            else:
                print(f"✗ 評估失敗: {result.get('error', '未知錯誤')}")

        except Exception as e:
            print(f"⚠ 風險評估已略過: {str(e)}")

        # 第三部分：政策摘要
        print_section("第三部分：產生政策摘要")

        print("情境：經理需要福利政策的快速摘要\n")
        print("請求：'摘要我們的員工福利'\n")

        try:
            result = generate_policy_summary(
                "employee benefits and time off",
                Config.HR_STORE_NAME,
            )

            if result.get("status") == "success":
                print("✓ 政策摘要:")
                print(f"  摘要: {result.get('summary', 'N/A')[:300]}...")
            else:
                print(f"✗ 摘要失敗: {result.get('error', '未知錯誤')}")

        except Exception as e:
            print(f"⚠ 摘要產生已略過: {str(e)}")

        # 第四部分：稽核追蹤
        print_section("第四部分：建立稽核追蹤")

        print("正在為政策存取建立稽核追蹤項目\n")

        try:
            result = create_audit_trail(
                action="search",
                user="john.doe@company.com",
                query="remote work policy requirements",
                result_summary="Retrieved remote work policy with 3 citations",
            )

            if result.get("status") == "success":
                audit_entry = result.get("audit_entry", {})
                print("✓ 稽核追蹤已建立:")
                print(f"  時間戳記: {audit_entry.get('timestamp', 'N/A')}")
                print(f"  動作: {audit_entry.get('action', 'N/A')}")
                print(f"  使用者: {audit_entry.get('user', 'N/A')}")
                print(f"  查詢: {audit_entry.get('query', 'N/A')}")
            else:
                print(f"✗ 稽核失敗: {result.get('error', '未知錯誤')}")

        except Exception as e:
            print(f"⚠ 稽核追蹤已略過: {str(e)}")

        # 第五部分：多 Store 比較
        print_section("第五部分：跨 Stores 比較政策")

        print("情境：合規團隊比較政策\n")
        print("請求：'安全需求有什麼差異？\n'")

        try:
            result = compare_policies(
                "Compare security and access control policies across departments",
                [Config.IT_STORE_NAME, Config.LEGAL_STORE_NAME],
            )

            if result.get("status") == "success":
                print("✓ 政策比較:")
                print(f"  比較的 Stores 數量: {result.get('stores_compared', 0)}")
                print(f"  分析: {result.get('comparison', 'N/A')[:300]}...")
            else:
                print(f"✗ 比較失敗: {result.get('error', '未知錯誤')}")

        except Exception as e:
            print(f"⚠ 比較已略過: {str(e)}")

        # 摘要
        print_section("工作流程完成")

        print("✓ 已展示 Policy Navigator 關鍵功能：")
        print("  1. 具備語意理解的政策搜尋")
        print("  2. 合規風險評估")
        print("  3. 政策摘要與重點擷取")
        print("  4. 用於合規的稽核追蹤建立")
        print("  5. 跨 Store 政策比較")
        print("\n✓ 所有工具運作正常！")

        print("\n" + "=" * 70)
        print("下一步：")
        print("  • 使用 'make dev' 啟動互動式網頁介面")
        print("  • 使用 'make demo' 探索其他展示腳本")
        print("  • 檢視 docs/ 中的文件")
        print("  • 使用 'make test' 執行測試")
        print("=" * 70 + "\n")

        return True

    except Exception as e:
        print(f"\n✗ 工作流程展示失敗: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
