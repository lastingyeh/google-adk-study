"""
教學 21：多模態與影像處理的示範腳本
展示基於視覺的產品目錄分析

注意：對於上傳的圖片，請使用 ADK 網站介面：
1. 執行：adk web
2. 開啟 http://localhost:8000
3. 從下拉選單中選擇 'vision_catalog_agent'
4. 將圖片直接拖放或貼到聊天室中
5. 提問：「分析此產品並建立一個目錄條目」

此示範腳本展示了基於檔案的影像處理。
"""

import asyncio
import os
from pathlib import Path

from google.adk.runners import Runner
from vision_catalog_agent import root_agent
from vision_catalog_agent.agent import create_sample_image


async def setup_demo_images():
    """建立用於示範的範例圖片。"""
    print("正在設定示範圖片...")

    # 建立範例圖片目錄
    sample_dir = Path(__file__).parent / '_sample_images'
    sample_dir.mkdir(exist_ok=True)

    # 定義範例圖片資訊
    sample_images = [
        ('laptop.jpg', (100, 120, 140), '專業筆記型電腦'),
        ('headphones.jpg', (50, 50, 50), '無線耳機'),
        ('smartwatch.jpg', (80, 100, 120), '智慧手錶')
    ]

    created = []
    # 產生圖片
    for filename, color, description in sample_images:
        path = sample_dir / filename
        if not path.exists():
            create_sample_image(str(path), color)
            created.append(f"  ✓ {filename} ({description})")
        else:
            created.append(f"  • {filename} ({description}) [已存在]")

    print("\n示範圖片已就緒：")
    for item in created:
        print(item)

    return sample_dir


async def demo_basic_analysis():
    """示範 1：基本影像分析。"""
    print("\n" + "="*70)
    print("示範 1：基本影像分析")
    print("="*70)

    sample_dir = await setup_demo_images()
    laptop_path = sample_dir / 'laptop.jpg'

    runner = Runner()

    query = f"分析位於 {laptop_path} 的圖片並描述您看到了什麼。"

    print(f"\n查詢：{query}")
    print("\n正在處理...\n")

    result = await runner.run_async(query, agent=root_agent)

    print("結果：")
    print(result.content.parts[0].text)
    print("\n" + "="*70)


async def demo_catalog_entry():
    """示範 2：生成目錄條目。"""
    print("\n" + "="*70)
    print("示範 2：生成產品目錄條目")
    print("="*70)

    sample_dir = await setup_demo_images()
    headphones_path = sample_dir / 'headphones.jpg'

    runner = Runner()

    query = f"""
    分析位於 {headphones_path} 的圖片，並建立一個包含描述、
    功能與規格的專業產品目錄條目。
    """.strip()

    print(f"\n查詢：{query}")
    print("\n正在處理...\n")

    result = await runner.run_async(query, agent=root_agent)

    print("結果：")
    print(result.content.parts[0].text)
    print("\n" + "="*70)


async def demo_compare_images():
    """示範 3：比較多張圖片。"""
    print("\n" + "="*70)
    print("示範 3：比較多張產品圖片")
    print("="*70)

    sample_dir = await setup_demo_images()
    laptop_path = sample_dir / 'laptop.jpg'
    smartwatch_path = sample_dir / 'smartwatch.jpg'

    runner = Runner()

    query = f"""
    比較這兩張產品圖片：
    1. {laptop_path}
    2. {smartwatch_path}

    識別每張圖片的相似點、差異點與獨特功能。
    """.strip()

    print(f"\n查詢：{query}")
    print("\n正在處理...\n")

    result = await runner.run_async(query, agent=root_agent)

    print("結果：")
    print(result.content.parts[0].text)
    print("\n" + "="*70)


async def demo_batch_processing():
    """示範 4：批次處理多個產品。"""
    print("\n" + "="*70)
    print("示範 4：批次處理產品目錄")
    print("="*70)

    sample_dir = await setup_demo_images()

    runner = Runner()

    query = f"""
    分析 {sample_dir}/ 中的所有產品圖片，並為每個產品建立一個
    包含目錄條目的摘要。
    """.strip()

    print(f"\n查詢：{query}")
    print("\n正在處理...\n")

    result = await runner.run_async(query, agent=root_agent)

    print("結果：")
    print(result.content.parts[0].text)
    print("\n" + "="*70)


async def main():
    """主要示範執行器。"""
    print("\n" + "="*70)
    print("教學 21：多模態與影像處理 - 示範")
    print("="*70)

    # 顯示上傳圖片資訊
    print("\n💡 提示：為了獲得最佳的上傳圖片體驗：")
    print("   1. 執行：adk web")
    print("   2. 開啟：http://localhost:8000")
    print("   3. 從下拉選單中選擇：'vision_catalog_agent'")
    print("   4. 將圖片直接拖放或貼到聊天室")
    print("   5. 提問：'分析此產品並建立一個目錄條目'")
    print("\n   此示範展示了基於檔案的影像處理。")

    # 檢查環境變數
    if not os.getenv('GOOGLE_API_KEY') and not os.getenv('GOOGLE_GENAI_USE_VERTEXAI'):
        print("\n⚠️  警告：未設定 GOOGLE_API_KEY！")
        print("請設定您的 API 金鑰：export GOOGLE_API_KEY=your_key")
        print("\n將以模擬資料執行示範模式...\n")

    demos = [
        ("基本影像分析", demo_basic_analysis),
        ("生成目錄條目", demo_catalog_entry),
        ("比較圖片", demo_compare_images),
        ("批次處理", demo_batch_processing)
    ]

    print("\n可用的示範：")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")

    print("\n請選擇示範 (1-4，或輸入 'all' 執行所有示範)：", end='')

    try:
        choice = input().strip().lower()

        if choice == 'all':
            for name, demo_func in demos:
                try:
                    await demo_func()
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"\n❌ {name} 執行錯誤：{e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            name, demo_func = demos[int(choice) - 1]
            await demo_func()
        else:
            print("無效的選擇。正在執行所有示範...")
            for name, demo_func in demos:
                try:
                    await demo_func()
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"\n❌ {name} 執行錯誤：{e}")

    except KeyboardInterrupt:
        print("\n\n示範被使用者中斷。")
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")

    print("\n" + "="*70)
    print("示範完成！")
    print("="*70)
    print("\n後續步驟：")
    print("  • 執行 'make dev' 啟動 ADK 網站介面")
    print("  • 嘗試使用您自己的圖片與代理互動")
    print("  • 查看 README.md 以獲得更多範例")
    print("  • 執行 'make test' 驗證功能")
    print()


if __name__ == '__main__':
    asyncio.run(main())
