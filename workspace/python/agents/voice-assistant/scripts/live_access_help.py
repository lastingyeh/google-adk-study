"""關於在 Vertex AI 上啟用 Gemini Live API 存取權限的指南。"""

from __future__ import annotations

import textwrap


# 定義啟用 Gemini Live API 的步驟列表
_STEPS = [
    "確認您的 Google Cloud 專案已啟用計費功能，且 Vertex AI API 已啟用 (gcloud services enable aiplatform.googleapis.com)。",
    "如果您仍在使用免費方案，請升級至付費的 Vertex AI 方案（標準或企業版）。",
    "開啟一個 Google Cloud 支援案例，或聯繫您的客戶團隊，為您的專案和地區（例如：us-central1）申請 Gemini Live API 發布者模型的存取權限。",
    "在您的請求中，請包含您計畫使用的確切模型 ID（例如，用於 Vertex Live API 的 gemini-2.0-flash-live-preview-04-09），並確認所需的地區。",
    "在 Google 啟用模型後，執行 'make live_models_list' 以確認模型可被搜尋到，並相應地更新 VOICE_ASSISTANT_LIVE_MODEL。",
]


def main() -> int:
    """主執行函數。"""
    print("📡 在 Vertex AI 上啟用 Gemini Live API 的步驟：")
    # 遍歷步驟列表並格式化輸出
    for idx, step in enumerate(_STEPS, start=1):
        # 將長文本自動換行，寬度為 88 個字元，後續行縮排 5 個空格
        wrapped = textwrap.fill(step, width=88, subsequent_indent="     ")
        print(f"  {idx}. {wrapped}")
    print("\nℹ️  提示：審核通常需要 1-2 個工作日；如果存取權限延遲，請與支援團隊聯繫。")
    return 0


if __name__ == "__main__":
    # 如果此腳本是主程式，則執行 main 函數並引發 SystemExit
    raise SystemExit(main())
