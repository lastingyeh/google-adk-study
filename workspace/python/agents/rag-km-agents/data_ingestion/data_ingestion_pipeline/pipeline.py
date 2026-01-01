# 從自訂元件中匯入 ingest_data 函式，用於將資料匯入 Vertex AI Search
from data_ingestion_pipeline.components.ingest_data import ingest_data

# 從自訂元件中匯入 process_data 函式，用於處理資料並產生嵌入
from data_ingestion_pipeline.components.process_data import process_data

# 從 Kubeflow Pipelines (KFP) SDK 匯入 dsl 模組，用於定義管線
from kfp import dsl


@dsl.pipeline(description="一個將新資料匯入資料儲存區的管線")
def pipeline(
    project_id: str,
    location: str,
    is_incremental: bool = True,
    look_back_days: int = 1,
    chunk_size: int = 1500,
    chunk_overlap: int = 20,
    destination_table: str = "incremental_questions_embeddings",
    deduped_table: str = "questions_embeddings",
    destination_dataset: str = "rag_km_agents_stackoverflow_data",
    data_store_region: str = "",
    data_store_id: str = "",
) -> None:
    """
    定義一個 KFP 管線，用於處理資料並將其匯入到資料儲存區，以供 RAG 檢索使用。

    Args:
        project_id (str): 您的 Google Cloud 專案 ID。
        location (str): 執行管線的 Google Cloud 地區。
        is_incremental (bool): 是否執行增量載入。預設為 True。
        look_back_days (int): 增量載入時要回溯的天數。預設為 1。
        chunk_size (int): 將文件分割成塊時，每個塊的大小（字元數）。預設為 1500。
        chunk_overlap (int): 相鄰塊之間的重疊字元數。預設為 20。
        destination_table (str): 儲存增量問題嵌入的目標 BigQuery 表格名稱。
        deduped_table (str): 儲存去重後問題嵌入的 BigQuery 表格名稱。
        destination_dataset (str): 目標 BigQuery 資料集名稱。
        data_store_region (str): Vertex AI Search 資料儲存區所在的地區。
        data_store_id (str): Vertex AI Search 資料儲存區的 ID。
    """

    # 步驟一：處理資料並產生嵌入
    # 呼叫 process_data 元件來執行資料前處理、分塊（chunking）和嵌入生成
    processed_data = process_data(
        project_id=project_id,
        # 使用 KFP 內建的佔位符來獲取排程執行的時間
        schedule_time=dsl.PIPELINE_JOB_SCHEDULE_TIME_UTC_PLACEHOLDER,
        is_incremental=is_incremental,
        look_back_days=look_back_days,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        destination_dataset=destination_dataset,
        destination_table=destination_table,
        deduped_table=deduped_table,
        location=location,
        embedding_column="embedding",  # 指定包含嵌入向量的欄位名稱
    ).set_retry(
        num_retries=2
    )  # 設定此步驟在失敗時最多重試 2 次

    # 步驟二：將處理後的資料匯入 Vertex AI Search 資料儲存區
    # 呼叫 ingest_data 元件，將上一步驟產生的檔案匯入
    ingest_data(
        project_id=project_id,
        data_store_region=data_store_region,
        # 將上一個步驟 (processed_data) 的輸出作為此步驟的輸入
        input_files=processed_data.output,
        data_store_id=data_store_id,
        embedding_column="embedding",  # 指定包含嵌入向量的欄位名稱
    ).set_retry(
        num_retries=2
    )  # 設定此步驟在失敗時最多重試 2 次
