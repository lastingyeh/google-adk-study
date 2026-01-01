"""
此 Kubeflow Pipelines (KFP) 元件衍生自以下筆記本：
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/retrieval-augmented-generation/scalable_rag_with_bigframes.ipynb

它利用 BigQuery 進行資料處理。我們也建議研究遠端函數以增強可擴展性。
"""

# 從 kfp.dsl 匯入，用於定義 Kubeflow Pipelines 的元件、輸入和輸出
from kfp.dsl import Dataset, Output, component


@component(
    # 指定此元件在 Kubeflow Pipelines 中執行時使用的基礎 Docker 映像
    base_image="us-docker.pkg.dev/production-ai-template/starter-pack/data_processing:0.2"
)
def process_data(
    project_id: str,
    schedule_time: str,
    output_files: Output[Dataset],
    is_incremental: bool = True,
    look_back_days: int = 1,
    chunk_size: int = 1500,
    chunk_overlap: int = 20,
    destination_dataset: str = "stackoverflow_data",
    destination_table: str = "incremental_questions_embeddings",
    deduped_table: str = "questions_embeddings",
    location: str = "us-central1",
    embedding_column: str = "embedding",
) -> None:
    """處理 StackOverflow 的問題與答案，步驟如下：
    1. 從 BigQuery 獲取資料
    2. 將 HTML 轉換為 Markdown
    3. 將文本分割成塊 (chunks)
    4. 生成嵌入 (embeddings)
    5. 將結果儲存回 BigQuery
    6. 匯出為 JSONL 格式

    Args:
        project_id: Google Cloud 專案 ID。
        schedule_time: 管線執行的排程時間 (ISO 格式)。
        output_files: 輸出資料集的路徑，用於儲存匯出的 JSONL 檔案。
        is_incremental: 是否僅處理最近的資料 (增量處理)。
        look_back_days: 增量處理時要回溯的天數。
        chunk_size: 文本塊的大小。
        chunk_overlap: 文本塊之間的重疊字數。
        destination_dataset: 用於儲存結果的 BigQuery 資料集。
        destination_table: 用於儲存增量結果的資料表。
        deduped_table: 用於儲存去重後結果的資料表。
        location: BigQuery 資料集的位置。
        embedding_column: 儲存嵌入向量的欄位名稱。
    """
    # 匯入必要的函式庫
    import logging
    from datetime import datetime, timedelta

    import backoff  # 用於在發生異常時自動重試
    import bigframes.ml.llm as llm  # BigFrames 的機器學習大型語言模型模組
    import bigframes.pandas as bpd  # BigFrames 的 Pandas API，用於在 BigQuery 上操作資料
    import google.api_core.exceptions  # Google Cloud API 核心異常
    import swifter  # 用於加速 Pandas apply 操作
    from google.cloud import bigquery  # Google Cloud BigQuery 客戶端
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
    )  # 用於遞迴分割文本
    from markdownify import markdownify  # 用於將 HTML 轉換為 Markdown

    # 初始化日誌記錄
    logging.basicConfig(level=logging.INFO)
    logging.info(f"使用 {swifter} 進行 apply 操作。")

    # 初始化客戶端
    logging.info("正在初始化客戶端...")
    bq_client = bigquery.Client(project=project_id, location=location)
    bpd.options.bigquery.project = project_id
    bpd.options.bigquery.location = location
    logging.info("客戶端初始化完成。")

    # 設定資料獲取的日期範圍
    # 從 ISO 格式的字串解析排程時間
    schedule_time_dt: datetime = datetime.fromisoformat(
        schedule_time.replace("Z", "+00:00")
    )
    # 如果排程時間是預設的 1970 年，表示管線未設定排程，則使用當前時間
    if schedule_time_dt.year == 1970:
        logging.warning("管線排程未設定。將 schedule_time 設定為當前日期。")
        schedule_time_dt = datetime.now()

    # 注意：以下這行將排程時間回溯 5 年，以確保範例資料存在。
    # 在您的實際應用中，請註解掉下面這行，以使用實際的排程時間。
    schedule_time_dt = schedule_time_dt - timedelta(days=5 * 365)

    # 設定資料處理的時間窗口
    START_DATE: datetime = schedule_time_dt - timedelta(days=look_back_days)  # 開始日期
    END_DATE: datetime = schedule_time_dt  # 結束日期

    logging.info(f"日期範圍已設定：START_DATE={START_DATE}, END_DATE={END_DATE}")

    def fetch_stackoverflow_data(
        dataset_suffix: str, start_date: str, end_date: str
    ) -> bpd.DataFrame:
        """從 BigQuery 獲取 StackOverflow 資料。"""
        query = f"""
            SELECT
                creation_date,
                last_edit_date,
                question_id,
                question_title,
                question_body AS question_text,
                answers
            FROM `production-ai-template.stackoverflow_qa_{dataset_suffix}.stackoverflow_python_questions_and_answers`
            WHERE TRUE
                -- 如果是增量模式，則加入日期過濾條件
                {f'AND TIMESTAMP_TRUNC(creation_date, DAY) BETWEEN TIMESTAMP("{start_date}") AND TIMESTAMP("{end_date}")' if is_incremental else ""}
        """
        logging.info("正在從 BigQuery 獲取 StackOverflow 資料...")
        return bpd.read_gbq(query)

    def convert_html_to_markdown(html: str) -> str:
        """將 HTML 轉換為 Markdown，以便於解析和在 LLM 回應後呈現。"""
        return markdownify(html).strip()

    def create_answers_markdown(answers: list) -> str:
        """將每個答案的 HTML 轉換為 Markdown，並串接成單一的 Markdown 文本。"""
        answers_md = ""
        for index, answer_record in enumerate(answers):
            answers_md += f"\n\n## Answer {index + 1}:\n"  # 答案編號使用 H2 標題大小
            answers_md += convert_html_to_markdown(answer_record["body"])
        return answers_md

    def create_table_if_not_exist(
        df: bpd.DataFrame,
        project_id: str,
        dataset_id: str,
        table_id: str,
        partition_column: str,
        location: str = location,
    ) -> None:
        """如果 BigQuery 資料表不存在，則創建一個帶有時間分區的資料表。"""
        # 從 BigFrames DataFrame 推斷 BigQuery 表的結構 (schema)
        table_schema = bq_client.get_table(df.head(0).to_gbq()).schema
        table = bigquery.Table(
            f"{project_id}.{dataset_id}.{table_id}", schema=table_schema
        )
        # 設定時間分區，按日分區
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY, field=partition_column
        )

        # 創建資料集 (如果不存在)
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = location
        bq_client.create_dataset(dataset, exists_ok=True)
        # 創建資料表 (如果不存在)
        bq_client.create_table(table=table, exists_ok=True)

    # 獲取並預處理資料
    logging.info("正在獲取並預處理資料...")
    df = fetch_stackoverflow_data(
        start_date=START_DATE.strftime("%Y-%m-%d"),
        end_date=END_DATE.strftime("%Y-%m-%d"),
        dataset_suffix=location.lower().replace("-", "_"),
    )
    # 根據最後編輯日期排序，並對 question_id 去重，保留最新的記錄
    df = (
        df.sort_values("last_edit_date", ascending=False)
        .drop_duplicates("question_id")
        .reset_index(drop=True)
    )
    logging.info("資料獲取與預處理完成。")

    # 將內容轉換為 Markdown
    logging.info("正在將內容轉換為 Markdown...")

    # 高效地創建 Markdown 欄位
    df["question_title_md"] = "# " + df["question_title"] + "\n"  # 標題使用 H1 標題大小
    # 使用 swifter 加速 apply 操作，將問題內文轉換為 Markdown
    df["question_text_md"] = (
        df["question_text"].to_pandas().swifter.apply(convert_html_to_markdown) + "\n"
    )
    # 使用 swifter 加速 apply 操作，將答案轉換為 Markdown
    df["answers_md"] = df["answers"].to_pandas().swifter.apply(create_answers_markdown)

    # 創建一個包含完整 Markdown 文本的欄位
    df["full_text_md"] = (
        df["question_title_md"] + df["question_text_md"] + df["answers_md"]
    )
    logging.info("內容已轉換為 Markdown。")

    # 僅保留必要的欄位
    df = df[["last_edit_date", "question_id", "question_text", "full_text_md"]]

    # 將文本分割成塊
    logging.info("正在將文本分割成塊...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # 每個塊的大小
        chunk_overlap=chunk_overlap,  # 塊之間的重疊部分
        length_function=len,  # 計算長度的函數
    )

    # 將 full_text_md 欄位分割成文本塊列表
    df["text_chunk"] = (
        df["full_text_md"]
        .to_pandas()
        .astype(object)
        .swifter.apply(text_splitter.split_text)
    )
    logging.info("文本已分割成塊。")

    # 創建塊 ID 並將塊展開為多行
    logging.info("正在創建塊 ID 並將塊展開為多行...")
    # 為每個塊生成一個索引
    chunk_ids = [
        str(idx) for text_chunk in df["text_chunk"] for idx in range(len(text_chunk))
    ]
    # 使用 explode 將每個文本塊列表展開成單獨的行
    df = df.explode("text_chunk").reset_index(drop=True)
    # 創建唯一的塊 ID (question_id + 塊索引)
    df["chunk_id"] = df["question_id"].astype("string") + "__" + chunk_ids
    logging.info("塊 ID 創建完成，塊已展開。")

    # 生成嵌入 (Embeddings)
    logging.info("正在生成嵌入...")

    # 使用 backoff 裝飾器，在新專案中首次調用可能因權限傳播延遲而失敗時進行重試
    @backoff.on_exception(
        backoff.expo, google.api_core.exceptions.InvalidArgument, max_tries=10
    )
    def create_embedder() -> llm.TextEmbeddingGenerator:
        """創建文本嵌入生成器實例。"""
        return llm.TextEmbeddingGenerator(model_name="text-embedding-005")

    embedder = create_embedder()

    # 使用 BigFrames 的 predict 方法為每個文本塊生成嵌入
    embeddings_df = embedder.predict(df["text_chunk"])
    logging.info("嵌入生成完成。")

    # 將生成的嵌入及相關統計資訊合併回主 DataFrame
    df = df.assign(
        embedding=embeddings_df["ml_generate_embedding_result"],
        embedding_statistics=embeddings_df["ml_generate_embedding_statistics"],
        embedding_status=embeddings_df["ml_generate_embedding_status"],
        creation_timestamp=datetime.now(),
    )

    # 將結果儲存到 BigQuery
    PARTITION_DATE_COLUMN = "creation_timestamp"

    # 創建並填充增量資料表
    logging.info("正在創建並填充增量資料表...")
    create_table_if_not_exist(
        df=df,
        project_id=project_id,
        dataset_id=destination_dataset,
        table_id=destination_table,
        partition_column=PARTITION_DATE_COLUMN,
    )

    # 根據是否為增量模式決定寫入方式 ('append' 或 'replace')
    if_exists_mode = "append" if is_incremental else "replace"
    df.to_gbq(
        destination_table=f"{destination_dataset}.{destination_table}",
        if_exists=if_exists_mode,
    )
    logging.info("增量資料表創建並填充完成。")

    # 創建去重後的資料表
    logging.info("正在創建去重後的資料表...")
    # 從增量表中讀取所有資料
    df_questions = bpd.read_gbq(
        f"{destination_dataset}.{destination_table}", use_cache=False
    )
    # 按 question_id 分組，找到每個問題最新的 creation_timestamp
    max_date_df = (
        df_questions.groupby("question_id")["creation_timestamp"].max().reset_index()
    )
    # 將最新時間戳的記錄與原始資料合併，以獲取每個問題的最新版本
    df_questions_dedup = max_date_df.merge(
        df_questions, how="inner", on=["question_id", "creation_timestamp"]
    )

    # 為去重後的資料表創建結構
    create_table_if_not_exist(
        df=df_questions_dedup,
        project_id=project_id,
        dataset_id=destination_dataset,
        table_id=deduped_table,
        partition_column=PARTITION_DATE_COLUMN,
    )

    # 將去重後的資料寫入新表，每次都替換舊表
    df_questions_dedup.to_gbq(
        destination_table=f"{destination_dataset}.{deduped_table}",
        if_exists="replace",
    )
    logging.info("去重後的資料表創建並填充完成。")

    # 匯出為 JSONL 格式 (常用於 Vertex AI Vector Search)
    logging.info("正在匯出為 JSONL...")

    # 構建匯出查詢，將資料轉換為 JSON 格式
    export_query = f"""
    SELECT
        chunk_id as id,
        TO_JSON_STRING(STRUCT(
            chunk_id as id,
            embedding as {embedding_column},
            text_chunk as content,
            question_id,
            CAST(creation_timestamp AS STRING) as creation_timestamp,
            CAST(last_edit_date AS STRING) as last_edit_date,
            question_text,
            full_text_md
        )) as json_data
    FROM
        `{project_id}.{destination_dataset}.{deduped_table}`
    WHERE
        chunk_id IS NOT NULL
        AND embedding IS NOT NULL
    """
    # 執行查詢並將結果存入一個臨時 BigQuery 表
    export_df_id = bpd.read_gbq(export_query).to_gbq()

    # 設定 KFP 元件的輸出 URI
    output_files.uri = output_files.uri + "*.jsonl"

    # 設定 BigQuery 匯出作業的配置
    job_config = bigquery.ExtractJobConfig()
    job_config.destination_format = bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON

    # 執行匯出作業，將臨時表的內容匯出到 GCS
    extract_job = bq_client.extract_table(
        export_df_id, output_files.uri, job_config=job_config
    )
    extract_job.result()  # 等待作業完成
    logging.info("已匯出為 JSONL。")
