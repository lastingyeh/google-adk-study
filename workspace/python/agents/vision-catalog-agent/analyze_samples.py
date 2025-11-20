#!/usr/bin/env python3
"""
使用 Vision Catalog Agent 分析所有範例圖片。

此腳本透過分析三個範例產品圖片來展示多模態功能：
筆記型電腦、耳機和智慧手錶。
"""
import asyncio
import sys
from pathlib import Path

# 將父目錄新增至路徑以便匯入
sys.path.insert(0, str(Path(__file__).parent))

from vision_catalog_agent.agent import root_agent, load_image_from_file
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types


async def analyze_all_samples():
    """分析所有三個範例圖片。"""

    # 取得範例圖片目錄
    sample_dir = Path(__file__).parent / '_sample_images'

    # 檢查範例目錄是否存在
    if not sample_dir.exists():
        print("❌ 找不到範例圖片目錄！")
        print(f"預期路徑：{sample_dir}")
        print("\n請執行：make download-images")
        return

    # 定義包含產品 ID 的範例圖片
    samples = [
        {
            'product_id': 'LAPTOP-001',
            'filename': 'laptop.jpg',
            'name': '專業筆記型電腦'
        },
        {
            'product_id': 'AUDIO-001',
            'filename': 'headphones.jpg',
            'name': '高級耳機'
        },
        {
            'product_id': 'WATCH-001',
            'filename': 'smartwatch.jpg',
            'name': '智慧手錶'
        }
    ]

    print("=" * 80)
    print("視覺目錄代理 - 範例圖片分析")
    print("=" * 80)
    print()

    # 建立 session 服務和 runner
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="vision_catalog_demo",
        agent=root_agent,
        session_service=session_service
    )

    # 建立一個 session
    session_id = "analysis_session"
    user_id = "demo_user"
    await session_service.create_session(
        session_id=session_id,
        user_id=user_id,
        app_name="vision_catalog_demo"
    )

    # 逐一分析每個範例圖片
    for i, sample in enumerate(samples, 1):
        image_path = sample_dir / sample['filename']

        # 檢查圖片是否存在
        if not image_path.exists():
            print(f"⚠️  找不到圖片：{image_path}")
            continue

        print(f"\n{'=' * 80}")
        print(f"圖片 {i}/3：{sample['name']} ({sample['filename']})")
        print(f"產品 ID：{sample['product_id']}")
        print(f"路徑：{image_path}")
        print("=" * 80)
        print()

        # 載入圖片
        try:
            image_part = load_image_from_file(str(image_path))
        except Exception as e:
            print(f"❌ 載入圖片失敗：{e}")
            continue

        # 建立包含圖片的分析查詢
        query_text = f"""
        我正在上傳一張產品圖片供您分析。

        產品 ID：{sample['product_id']}
        產品名稱：{sample['name']}

        請分析此圖片並建立一個專業的產品目錄條目。
        內容應包含：
        1. 產品識別與類別
        2. 視覺特徵 (顏色、設計、材質)
        3. 品質指標
        4. 獨特功能
        5. 市場定位與目標客群

        請提供一份完整且可用於行銷的描述。
        """.strip()

        try:
            # 執行代理查詢
            print("🔍 正在分析圖片...")
            print()

            # 建立包含文字和圖片的訊息內容
            message = types.Content(
                parts=[
                    types.Part(text=query_text),
                    image_part
                ],
                role="user"
            )

            # 使用 ADK Runner 執行查詢
            response_text = []
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message
            ):
                # 從事件中收集文字
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text.append(part.text)

            # 顯示結果
            if response_text:
                print('\n'.join(response_text))
                print()
            else:
                print("❌ 未回傳分析結果")

        except Exception as e:
            print(f"❌ 分析 {sample['filename']} 時發生錯誤：{str(e)}")
            import traceback
            traceback.print_exc()

        print()

        # 在每次分析之間稍作延遲
        if i < len(samples):
            await asyncio.sleep(1)

    print("=" * 80)
    print("✅ 分析完成！")
    print("=" * 80)
    print()
    print("後續步驟：")
    print("- 嘗試網站介面：make dev")
    print("- 上傳您自己的圖片進行分析")
    print("- 比較多張圖片：compare_product_images()")
    print()


async def main():
    """主要進入點。"""
    try:
        await analyze_all_samples()
    except KeyboardInterrupt:
        print("\n\n⚠️  分析被使用者中斷")
    except Exception as e:
        print(f"\n❌ 錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
