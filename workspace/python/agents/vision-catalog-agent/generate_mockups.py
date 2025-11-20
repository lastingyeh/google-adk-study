#!/usr/bin/env python3
"""
生成合成產品圖片 - 教學 21 增強功能

此腳本展示了使用 Gemini 2.5 Flash Image 模型的新合成圖片生成功能。
非常適合用於：
- 在攝影前進行產品目錄原型設計
- 測試現有產品的變化版本
- 為客戶簡報生成模型
- 快速建立多樣化的產品圖像
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


# 產品模型規格
PRODUCT_MOCKUPS = [
    {
        'name': '極簡風格桌燈',
        'description': '一款時尚的極簡風格桌燈，採用髮絲紋鋁製表面、LED 光源、可調式燈臂和現代幾何底座。線條簡潔，設計專業。',
        'style': '逼真的產品攝影',
        'aspect_ratio': '1:1'
    },
    {
        'name': '高級皮革錢包',
        'description': '豪華的棕色皮革雙摺錢包，帶有金色縫線，可見多個卡槽，RFID 保護標誌，工藝精湛，設計優雅。',
        'style': '逼真的產品攝影',
        'aspect_ratio': '4:3'
    },
    {
        'name': '無線電競滑鼠',
        'description': '未來感的電競滑鼠，帶有 RGB 燈光點綴，符合人體工學的設計，霧面黑色表面搭配亮面側板，可見高精度感應器。',
        'style': '帶有戲劇性燈光效果的逼真產品攝影',
        'aspect_ratio': '16:9'
    }
]


async def generate_mockups():
    """生成合成產品圖片並進行分析。"""

    print("=" * 80)
    print("合成產品圖片生成 - 教學 21 增強功能")
    print("=" * 80)
    print()
    print("此示範將：")
    print("1. 使用 Gemini 2.5 Flash Image 生成合成產品圖片")
    print("2. 使用視覺目錄代理分析每張生成的圖片")
    print("3. 建立專業的產品目錄條目")
    print()
    print("=" * 80)
    print()

    # 建立 session 服務和 runner
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="synthetic_generation_demo",
        agent=root_agent,
        session_service=session_service
    )

    # 建立一個 session
    session_id = "generation_session"
    user_id = "demo_user"
    await session_service.create_session(
        session_id=session_id,
        user_id=user_id,
        app_name="synthetic_generation_demo"
    )

    # 生成並分析每個產品
    for i, product in enumerate(PRODUCT_MOCKUPS, 1):
        print(f"\n{'=' * 80}")
        print(f"產品 {i}/{len(PRODUCT_MOCKUPS)}：{product['name']}")
        print("=" * 80)
        print()
        print(f"描述：{product['description']}")
        print(f"風格：{product['style']}")
        print(f"長寬比：{product['aspect_ratio']}")
        print()

        # 步驟 1：生成合成圖片
        print("🎨 步驟 1：正在生成合成產品圖片...")
        print()

        generation_query = f"""
        請使用 generate_product_mockup 工具生成一張合成產品圖片：

        產品名稱：{product['name']}
        描述：{product['description']}
        風格：{product['style']}
        長寬比：{product['aspect_ratio']}

        生成圖片後，請確認生成是否成功。
        """.strip()

        try:
            # 建立訊息內容
            message = types.Content(
                parts=[types.Part(text=generation_query)],
                role="user"
            )

            # 執行生成
            generation_response = []
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message
            ):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                generation_response.append(part.text)

            if generation_response:
                print('\n'.join(generation_response))
                print()
            else:
                print("❌ 未收到生成確認")
                continue

            # 在分析前稍作延遲
            await asyncio.sleep(2)

            # 步驟 2：載入並分析生成的圖片
            print()
            print("🔍 步驟 2：正在分析生成的合成圖片...")
            print()

            # 尋找生成的圖片
            sample_dir = Path(__file__).parent / '_sample_images'
            safe_name = product['name'].lower().replace(' ', '_').replace('-', '_')
            generated_image_path = sample_dir / f"{safe_name}_generated.jpg"

            if not generated_image_path.exists():
                print(f"⚠️  在以下路徑找不到生成的圖片：{generated_image_path}")
                continue

            # 載入生成的圖片
            image_part = load_image_from_file(str(generated_image_path))

            analysis_query = f"""
            我正在上傳剛為 {product['name']} 生成的合成圖片。

            請分析此合成產品圖片並建立一個專業的目錄條目。
            內容應包含：
            1. 對生成圖片品質的視覺評估
            2. 圖片中可見的產品功能
            3. 設計特點與美學吸引力
            4. 是否適合用於行銷/電子商務
            5. 專業的產品描述

            注意：這是一張合成生成的圖片，但請像分析真實產品照片一樣進行分析。
            """.strip()

            # 建立包含圖片的訊息
            analysis_message = types.Content(
                parts=[
                    types.Part(text=analysis_query),
                    image_part
                ],
                role="user"
            )

            # 執行分析
            analysis_response = []
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=analysis_message
            ):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                analysis_response.append(part.text)

            if analysis_response:
                print('\n'.join(analysis_response))
                print()
            else:
                print("❌ 未回傳分析結果")

        except Exception as e:
            print(f"❌ 處理 {product['name']} 時發生錯誤：{str(e)}")
            import traceback
            traceback.print_exc()

        print()

        # 在處理不同產品之間稍作延遲
        if i < len(PRODUCT_MOCKUPS):
            await asyncio.sleep(2)

    print("=" * 80)
    print("✅ 合成圖片生成與分析完成！")
    print("=" * 80)
    print()
    print("生成的圖片已儲存於：_sample_images/")
    print()
    print("主要優點：")
    print("- ✨ 無需攝影設備")
    print("- 🚀 快速原型設計與迭代")
    print("- 💰 具成本效益的產品模型")
    print("- 🎨 風格與品質一致")
    print("- 📸 專業的產品攝影美學")
    print()
    print("後續步驟：")
    print("- 檢查 _sample_images/ 中生成的圖片")
    print("- 嘗試網站介面：make dev")
    print("- 生成您自己的產品模型！")
    print()


async def main():
    """主要進入點。"""
    try:
        await generate_mockups()
    except KeyboardInterrupt:
        print("\n\n⚠️  生成被使用者中斷")
    except Exception as e:
        print(f"\n❌ 錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
