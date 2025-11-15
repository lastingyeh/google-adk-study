"""用於列出已設定的 Vertex 專案中可用的 Live API 模型的工具腳本。"""

import os
import sys
from typing import List

try:
    # 嘗試匯入 google.genai 的 Client
    from google.genai import Client
except ImportError:  # pragma: no cover
    # 如果匯入失敗，表示尚未安裝 google-genai 套件
    print("查詢模型需要安裝 google-genai 套件。")
    raise


def _load_client() -> Client:
    """使用環境變數設定來建立一個啟用 Vertex 的客戶端。"""
    # 從環境變數中獲取 GOOGLE_CLOUD_PROJECT
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        # 如果未設定，則引發執行期錯誤
        raise RuntimeError("環境變數 GOOGLE_CLOUD_PROJECT 尚未設定")

    # 從環境變數中獲取 GOOGLE_CLOUD_LOCATION，預設為 'us-central1'
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    # 建立並返回一個啟用 Vertex AI 的 Client
    return Client(vertexai=True, project=project, location=location)


def list_live_models(client: Client) -> List[str]:
    """返回支援 Vertex Live API 的模型識別碼列表。"""
    live_models: List[str] = []
    # 遍歷客戶端中所有可用的模型
    for model in client.models.list():
        # 獲取模型名稱
        name = getattr(model, "name", "") or ""
        # 如果模型名稱中包含 'live'（不區分大小寫）
        if "live" in name.lower():
            # 將模型的最後一部分（即模型 ID）加入列表
            live_models.append(name.split("/")[-1])
    return live_models


def _print_banner(message: str) -> None:
    """以特定格式輸出橫幅訊息。"""
    print(f"   {message}")


def main() -> int:
    """主執行函數。"""
    try:
        # 載入 Vertex AI 客戶端
        client = _load_client()
    except Exception as exc:  # pragma: no cover
        # 如果初始化失敗，輸出錯誤訊息並返回 1
        _print_banner(f"❌ 無法初始化 Vertex 客戶端：{exc}")
        return 1

    # 列出所有 Live API 模型
    live_models = list_live_models(client)
    if not live_models:
        # 如果找不到任何 Live API 模型，輸出提示訊息
        _print_banner("❌ 在此專案/地區目前看不到任何 Live API 模型。")
        _print_banner("👉 請申請 Vertex Live 存取權限或切換到支援的地區。")
        _print_banner("👉 如有需要，請聯繫 Google Cloud 支援團隊以啟用 Live API 發布者模型。")
        return 1

    # 如果找到 Live API 模型，則輸出成功訊息及模型列表
    _print_banner("✅ 偵測到支援 Live API 的模型：")
    for model_name in live_models:
        print(f"      • {model_name}")
    _print_banner("ℹ️  如果缺少必要的模型，請確認您的授權與地區可用性。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    # 如果此腳本是主程式，則執行 main 函數並退出
    sys.exit(main())
