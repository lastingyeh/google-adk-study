"""品牌搜尋優化代理程式的部署腳本。"""


import vertexai
from absl import app, flags
from brand_search_optimization.agent import root_agent
from brand_search_optimization.shared_libraries import constants
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# 定義命令列參數
FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 地區。")
flags.DEFINE_string("bucket", None, "GCP 儲存桶。")
flags.DEFINE_string("resource_id", None, "ReasoningEngine 資源 ID。")
flags.DEFINE_bool("create", False, "建立一個新的代理程式。")
flags.DEFINE_bool("delete", False, "刪除一個現有的代理程式。")
# 確保 'create' 和 'delete' 參數不會同時被設定
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])


def create(env_vars: dict) -> None:
    """建立並部署一個新的遠端代理程式。"""
    # 使用 AdkApp 初始化代理程式，並啟用追蹤功能
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # 定義需要額外打包的本地 Python 套件路徑
    extra_packages = ["./brand_search_optimization"]

    # 使用 agent_engines.create 建立遠端代理程式
    remote_agent = agent_engines.create(
        adk_app,
        # 定義代理程式執行所需的 Python 依賴套件
        requirements=[
            "google-adk>=1.0.0,<2.0.0",
            "google-cloud-aiplatform[agent_engines]>=1.93.0",
            "pydantic",
            "requests",
            "python-dotenv",
            "google-genai",
            "selenium",
            "webdriver-manager",
            "google-cloud-bigquery",
            "absl-py",
            "pillow",
        ],
        extra_packages=extra_packages,
        env_vars=env_vars,
    )
    print(f"已建立遠端代理程式: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """刪除一個現有的遠端代理程式。"""
    # 根據 resource_id 取得遠端代理程式物件
    remote_agent = agent_engines.get(resource_id)
    # 強制刪除代理程式
    remote_agent.delete(force=True)
    print(f"已刪除遠端代理程式: {resource_id}")


def main(argv: list[str]) -> None:
    """腳本主函式，處理參數並執行對應操作。"""
    # 優先使用旗標設定，若無則從常數模組讀取
    project_id = FLAGS.project_id if FLAGS.project_id else constants.PROJECT
    location = FLAGS.location if FLAGS.location else constants.LOCATION
    bucket = FLAGS.bucket if FLAGS.bucket else constants.STAGING_BUCKET
    env_vars = {}

    print(f"專案: {project_id}")
    print(f"地區: {location}")
    print(f"儲存桶: {bucket}")

    # 檢查必要的 GCP 設定是否存在
    if not project_id:
        print("缺少必要的環境變數: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("缺少必要的環境變數: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("缺少必要的環境變數: GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    # 設定環境變數以在部署環境中禁用 WebDriver
    env_vars["DISABLE_WEB_DRIVER"] = "1"

    # 初始化 Vertex AI SDK
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    # 根據命令列參數執行建立或刪除操作
    if FLAGS.create:
        create(env_vars)
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("刪除操作需要 resource_id")
            return
        delete(FLAGS.resource_id)
    else:
        print("未知的指令")


if __name__ == "__main__":
    # 透過 absl.app 執行 main 函式
    app.run(main)
