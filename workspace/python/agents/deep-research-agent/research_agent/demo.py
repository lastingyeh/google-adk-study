"""
深度研究代理演示腳本 (Demo script for Deep Research Agent)

用法：
    python -m research_agent.demo          # 執行實際研究 (需要 API 金鑰)
    python -m research_agent.demo --mock   # 執行模擬演示 (無需 API 金鑰)
"""

import sys
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# 從套件目錄載入 .env
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path)


def mock_demo():
    """執行無需 API 呼叫的模擬演示 (Run a mock demonstration without API calls)。"""
    print("=" * 60)
    print("🔬 深度研究代理演示 (模擬模式)")
    print("=" * 60)
    print("")
    print("這展示了無需進行 API 呼叫的結構。")
    print("")

    # 模擬研究結構
    print("📝 查詢：'分析 2025 年 AI 程式碼助理的市場趨勢'")
    print("")
    print("🚀 開始研究...")
    print(f"   互動 ID: mock-interaction-12345")
    print("")

    # 模擬思考過程
    thoughts = [
        "規劃 AI 程式碼助理市場的研究策略",
        "搜尋最近的市場報告和分析",
        "閱讀主要供應商的文件：GitHub Copilot, Cursor, Codeium",
        "分析定價模型和功能比較",
        "將發現綜合成綜合報告",
    ]

    for i, thought in enumerate(thoughts, 1):
        time.sleep(0.5)  # 模擬處理
        print(f"💭 思考 {i}: {thought}")

    print("")
    print("📊 研究報告 (模擬):")
    print("-" * 40)
    print("""
    # 2025 年 AI 程式碼助理市場分析

    ## 執行摘要
    AI 程式碼助理市場顯著成長，自 2023 年以來採用率增加了 300%。
    主要參與者包括 GitHub Copilot、Cursor 和 Codeium。

    ## 主要參與者
    | 供應商 | 定價 | 關鍵功能 |
    |----------|---------|--------------|
    | GitHub Copilot | $10-19/月 | IDE 整合、聊天 |
    | Cursor | $20/月 | AI 原生編輯器 |
    | Codeium | 免費層級 | 多 IDE 支援 |

    ## 市場趨勢
    1. 代理能力的整合
    2. 專注於企業安全功能
    3. 轉向專業化的垂直解決方案

    ## 未來展望
    預計到 2028 年市場將達到 150 億美元，年複合成長率 (CAGR) 為 45%。
    """)
    print("-" * 40)
    print("")
    print("✅ 研究完成 (模擬)")
    print("   耗時：3.2 秒 (模擬)")
    print("")
    print("💡 若要執行實際研究，請使用：make research")
    print("   (需要設定 GOOGLE_API_KEY)")


def real_demo():
    """使用 API 執行實際研究 (Run actual research with the API)。"""
    import os

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ 未設定 GOOGLE_API_KEY！")
        print("")
        print("設定您的 API 金鑰：")
        print("  export GOOGLE_API_KEY='your-key-here'")
        print("")
        print("或執行模擬演示：")
        print("  python -m research_agent.demo --mock")
        sys.exit(1)

    from . import DeepResearchAgent, ResearchStatus
    import os

    print("=" * 60)
    print("🔬 深度研究代理 - 現場演示 (Live Demo)")
    print("=" * 60)
    print("")

    # 顯示正在使用的後端
    use_vertex_ai = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
    if use_vertex_ai:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("VERTEX_AI_PROJECT_ID")
        region = os.getenv("VERTEX_AI_REGION", "us-central1")
        print(f"📍 後端：Vertex AI (project={project_id}, region={region})")
    else:
        print("📍 後端：Google AI Studio")
    print("")
    print("⚠️  這將進行實際的 API 呼叫，可能需要數分鐘。")
    print("")

    query = "2025 年 12 月大型語言模型的前三大發展是什麼？請提供引用來源和 URL。"
    print(f"📝 查詢：'{query}'")
    print("")

    def status_callback(status: str, elapsed: float):
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        print(f"   [{mins:02d}:{secs:02d}] 狀態: {status}")

    print("🚀 開始研究...")
    print("")

    agent = DeepResearchAgent()

    try:
        result = agent.research(
            query,
            poll_interval=10,
            on_status=status_callback
        )

        print("")

        if result.status == ResearchStatus.COMPLETED:
            print("=" * 60)
            print("📊 研究報告")
            print("=" * 60)
            print("")
            print(result.report)
            print("")
            print("=" * 60)
            print(f"✅ 研究完成！")
            print(f"   互動 ID: {result.id}")
            print(f"   耗時: {result.elapsed_seconds:.1f} 秒")
            print(f"   發現引用: {len(result.citations)}")

            if result.citations:
                print("")
                print("📚 引用:")
                for i, citation in enumerate(result.citations[:10], 1):  # 顯示前 10 個
                    print(f"   {i}. {citation}")
                if len(result.citations) > 10:
                    print(f"   ... 以及其他 {len(result.citations) - 10} 個")
        else:
            print(f"❌ 研究失敗: {result.error}")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        sys.exit(1)


def main():
    """主要進入點 (Main entry point)。"""
    if "--mock" in sys.argv:
        mock_demo()
    else:
        real_demo()


if __name__ == "__main__":
    main()
