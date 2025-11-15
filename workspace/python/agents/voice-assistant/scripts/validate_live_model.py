"""驗證已設定的 Live 模型在 Vertex 專案中是否可用。"""

import os
import sys

from google.genai import Client, errors


def _load_environment() -> tuple[str, str, str]:
    """載入環境變數。"""
    # 從環境變數中獲取 GOOGLE_CLOUD_PROJECT
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        # 如果未設定，則引發執行期錯誤
        raise RuntimeError("環境變數 GOOGLE_CLOUD_PROJECT 尚未設定")

    # 從環境變數中獲取 GOOGLE_CLOUD_LOCATION，預設為 'us-central1'
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    # 從環境變數中獲取 VOICE_ASSISTANT_LIVE_MODEL
    model = os.environ.get("VOICE_ASSISTANT_LIVE_MODEL")
    if not model:
        # 如果未設定，則引發執行期錯誤
        raise RuntimeError("環境變數 VOICE_ASSISTANT_LIVE_MODEL 尚未設定")

    return project, location, model


def main() -> int:
    """主執行函數。"""
    try:
        # 載入環境變數
        project, location, model = _load_environment()
    except RuntimeError as exc:  # pragma: no cover
        # 如果載入失敗，輸出錯誤訊息並返回 1
        print(f"   ❌ {exc}")
        return 1

    try:
        # 初始化 Vertex AI 客戶端
        client = Client(vertexai=True, project=project, location=location)
        # 嘗試獲取模型資訊以進行驗證
        client.models.get(model=model)
    except errors.ClientError as exc:
        # 如果模型查找失敗
        message = str(exc)
        print(f"   ❌ Live 模型查找失敗：{message}")
        # 如果錯誤訊息包含 "Publisher Model" 或 "NOT_FOUND"，提供具體指引
        if "Publisher Model" in message or "NOT_FOUND" in message:
            print("   👉 所選模型未在此專案/地區啟用。")
            print("   👉 請執行 `make live_models_doc` 以獲取支援的模型 ID，或申請 Vertex Live 存取權限。")
            print("   👉 存取權限授予後，請重新執行 `make live_models_list` 以確認可用性。")
        return 1
    except Exception as exc:  # pragma: no cover
        # 處理其他非預期的錯誤
        print(f"   ❌ 驗證 Live 模型時發生非預期錯誤：{exc}")
        return 1

    # 如果模型可被搜尋到，輸出成功訊息
    print("   ✅ Live 模型在此專案/地區可被搜尋到。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    # 如果此腳本是主程式，則執行 main 函數並退出
    sys.exit(main())
