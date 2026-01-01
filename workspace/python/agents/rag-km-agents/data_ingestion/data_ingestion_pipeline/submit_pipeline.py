# 匯入必要的函式庫
import argparse  # 用於解析命令列參數
import logging  # 用於記錄日誌訊息
import os  # 用於與作業系統互動，例如讀取環境變數
import sys  # 用於與 Python 解譯器互動，例如退出程式

import backoff  # 用於實現指數退避重試機制
from data_ingestion_pipeline.pipeline import pipeline  # 從本地模組匯入 pipeline 定義
from google.cloud import aiplatform  # Google Cloud Vertex AI SDK
from kfp import (
    compiler,
)  # Kubeflow Pipelines (KFP) 編譯器，用於將 Python 程式碼編譯成 pipeline 規格

# 定義編譯後的 pipeline JSON 檔案名稱
PIPELINE_FILE_NAME = "data_processing_pipeline.json"

# 設定日誌記錄器
# 設定日誌級別為 INFO，並定義日誌訊息的格式
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# 獲取一個名為 __name__ (當前模組名稱) 的日誌記錄器實例
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """解析用於 pipeline 設定的命令列參數。"""

    # 建立一個 ArgumentParser 物件，用於處理命令列參數
    parser = argparse.ArgumentParser(description="Pipeline 設定")

    # 新增各項命令列參數的定義
    # 優先使用命令列傳入的值，若未傳入，則嘗試從環境變數讀取
    parser.add_argument(
        "--project-id", default=os.getenv("PROJECT_ID"), help="GCP 專案 ID"
    )
    parser.add_argument(
        "--region", default=os.getenv("REGION"), help="Vertex AI Pipelines 所在的區域"
    )
    parser.add_argument(
        "--data-store-region",
        default=os.getenv("DATA_STORE_REGION"),
        help="Data Store 所在的區域",
    )
    parser.add_argument(
        "--data-store-id", default=os.getenv("DATA_STORE_ID"), help="Data Store 的 ID"
    )
    parser.add_argument(
        "--service-account",
        default=os.getenv("SERVICE_ACCOUNT"),
        help="執行 pipeline 所使用的服務帳號",
    )
    parser.add_argument(
        "--pipeline-root",
        default=os.getenv("PIPELINE_ROOT"),
        help="Pipeline 的根目錄，用於存放中繼產物",
    )
    parser.add_argument(
        "--pipeline-name", default=os.getenv("PIPELINE_NAME"), help="Pipeline 的名稱"
    )
    parser.add_argument(
        "--disable-caching",
        type=bool,
        # 將環境變數字串轉為布林值，預設為 'false'
        default=os.getenv("DISABLE_CACHING", "false").lower() == "true",
        help="是否停用 pipeline 快取 (預設為啟用)",
    )
    parser.add_argument(
        "--cron-schedule",
        default=os.getenv("CRON_SCHEDULE", None),
        help="Cron 排程表達式 (例如 '0 0 * * 0' 表示每週日午夜)",
    )
    parser.add_argument(
        "--schedule-only",
        type=bool,
        # 將環境變數字串轉為布林值，預設為 'false'
        default=os.getenv("SCHEDULE_ONLY", "false").lower() == "true",
        help="僅建立或更新排程，而不立即執行 pipeline",
    )
    # 解析傳入的命令列參數
    parsed_args = parser.parse_args()

    # 驗證必要的參數是否都已提供
    missing_params = []
    required_params = {
        "project_id": parsed_args.project_id,
        "region": parsed_args.region,
        "service_account": parsed_args.service_account,
        "pipeline_root": parsed_args.pipeline_root,
        "pipeline_name": parsed_args.pipeline_name,
        "data_store_region": parsed_args.data_store_region,
        "data_store_id": parsed_args.data_store_id,
    }

    # 檢查每個必要參數是否有值
    for param_name, param_value in required_params.items():
        if param_value is None:
            missing_params.append(param_name)

    # 如果有任何必要參數缺失，則記錄錯誤並終止程式
    if missing_params:
        logging.error("錯誤：缺少以下必要的參數：")
        for param in missing_params:
            logging.error(f"  - {param}")
        logging.error("\n請透過環境變數或命令列參數提供這些值。")
        sys.exit(1)

    # 返回解析後的參數物件
    return parsed_args


# 使用 backoff 裝飾器為函數加上自動重試機制
@backoff.on_exception(
    backoff.expo,  # 使用指數退避策略 (等待時間會指數增長)
    Exception,  # 捕捉所有 Exception 類型的錯誤
    max_tries=3,  # 最多重試 3 次
    max_time=3600,  # 總重試時間不超過 3600 秒 (1 小時)
    # 當重試發生時，呼叫此 lambda 函數記錄日誌
    on_backoff=lambda details: logging.warning(
        f"Pipeline 第 {details['tries']} 次嘗試失敗，將在 {details['wait']:.1f} 秒後重試..."
    ),
)
def submit_and_wait_pipeline(pipeline_job_params: dict, service_account: str) -> None:
    """提交 pipeline 作業並等待其完成，具備重試邏輯。"""
    # 使用傳入的參數建立一個 PipelineJob 物件
    job = aiplatform.PipelineJob(**pipeline_job_params)
    # 提交 pipeline 作業，並指定服務帳號
    job.submit(service_account=service_account)
    # 等待作業執行完成
    job.wait()


# Python 程式的進入點
if __name__ == "__main__":
    # 解析命令列參數
    args = parse_args()

    # 檢查：如果使用者指定只排程，但未提供 cron 排程表達式，則報錯
    if args.schedule_only and not args.cron_schedule:
        logging.error("缺少 --cron-schedule 參數，無法進行排程")
        sys.exit(1)

    # 印出目前的設定
    logging.info("\n設定資訊:")
    logging.info("--------------")
    # 動態地印出所有解析到的參數
    for arg_name, arg_value in vars(args).items():
        logging.info(f"{arg_name}: {arg_value}")
    logging.info("--------------\n")

    # 使用 KFP 編譯器將 Python pipeline 函數編譯成 JSON 格式的 pipeline 定義檔
    compiler.Compiler().compile(pipeline_func=pipeline, package_path=PIPELINE_FILE_NAME)

    # 建立通用的 pipeline 作業參數字典
    pipeline_job_params = {
        "display_name": args.pipeline_name,  # 在 Vertex AI UI 上顯示的名稱
        "template_path": PIPELINE_FILE_NAME,  # 編譯後的 pipeline 定義檔路徑
        "pipeline_root": args.pipeline_root,  # 存放 pipeline 產物的 GCS 路徑
        "project": args.project_id,  # GCP 專案 ID
        "enable_caching": (
            not args.disable_caching
        ),  # 是否啟用快取 (與 disable_caching 相反)
        "location": args.region,  # pipeline 執行的區域
        "parameter_values": {  # 傳遞給 pipeline 內部的參數
            "project_id": args.project_id,
            "location": args.region,
            "data_store_region": args.data_store_region,
            "data_store_id": args.data_store_id,
        },
    }

    # 如果不是只排程，則立即執行 pipeline
    if not args.schedule_only:
        logging.info("正在執行 pipeline 並等待完成...")
        # 呼叫帶有重試機制的函數來提交並等待 pipeline
        submit_and_wait_pipeline(pipeline_job_params, args.service_account)
        logging.info("Pipeline 執行完成！")

    # 如果提供了 cron 排程表達式且設定為只排程
    if args.cron_schedule and args.schedule_only:
        # 建立一個用於排程的 PipelineJob 實例
        job = aiplatform.PipelineJob(**pipeline_job_params)
        # 建立 PipelineJobSchedule 物件
        pipeline_job_schedule = aiplatform.PipelineJobSchedule(
            pipeline_job=job,
            display_name=f"{args.pipeline_name} 每週資料注入作業",
        )

        # 查詢是否已存在同名的排程
        schedule_list = pipeline_job_schedule.list(
            filter=f'display_name="{args.pipeline_name} 每週資料注入作業"',
            project=args.project_id,
            location=args.region,
        )
        logging.info("查詢到的排程列表: %s", schedule_list)

        # 如果不存在同名排程，則建立新的排程
        if not schedule_list:
            pipeline_job_schedule.create(
                cron=args.cron_schedule, service_account=args.service_account
            )
            logging.info("已建立新的排程")
        # 如果已存在，則更新該排程的 cron 設定
        else:
            schedule_list[0].update(cron=args.cron_schedule)
            logging.info("已更新現有的排程")

    # 清理臨時產生的 pipeline JSON 檔案
    if os.path.exists(PIPELINE_FILE_NAME):
        os.remove(PIPELINE_FILE_NAME)
        logging.info(f"已刪除 {PIPELINE_FILE_NAME}")
