# 從 kfp.dsl 模組匯入 Dataset, Input, 和 component，這些是用於定義 Kubeflow Pipelines 元件的類別和裝飾器。
from kfp.dsl import Dataset, Input, component


# @component 裝飾器將這個 Python 函數轉換為一個獨立的 Kubeflow Pipeline 元件。
# base_image 指定了執行此元件的 Docker 容器映像。
@component(
    base_image="us-docker.pkg.dev/production-ai-template/starter-pack/data_processing:0.2"
)
def ingest_data(
    project_id: str,
    data_store_region: str,
    input_files: Input[Dataset],
    data_store_id: str,
    embedding_dimension: int = 768,
    embedding_column: str = "embedding",
) -> None:
    """將文件處理並匯入至 Vertex AI Search 資料儲存區。

    Args:
        project_id: Google Cloud 專案 ID。
        data_store_region: Vertex AI Search 的所在區域。
        input_files: 包含文件的輸入資料集，這是一個 KFP 的 Input[Dataset] 物件，指向 GCS 中的檔案。
        data_store_id: 目標資料儲存區的 ID。
        embedding_dimension: 向量嵌入的維度，預設為 768。
        embedding_column: 結構中向量嵌入欄位的名稱，預設為 "embedding"。
    """
    # 匯入必要的標準函式庫和第三方函式庫。
    import json
    import logging
    import time

    # 從 google.api_core 匯入 ClientOptions，用於設定 API 客戶端的端點。
    from google.api_core.client_options import ClientOptions

    # 從 google.cloud 匯入 discoveryengine，這是 Vertex AI Search 的 Python 客戶端函式庫。
    from google.cloud import discoveryengine

    def update_schema_as_json(
        original_schema: str,
        embedding_dimension: int,
        field_name: str | None = None,
    ) -> str:
        """更新資料儲存區的 JSON 結構以包含向量嵌入欄位。

        Args:
            original_schema: 原始的 JSON 結構字串。
            embedding_dimension: 向量嵌入的維度。
            field_name: 要新增的向量嵌入欄位名稱。

        Returns:
            更新後的 JSON 結構字串。
        """
        # 將原始的 JSON 結構字串解析為 Python 字典。
        original_schema_dict = json.loads(original_schema)

        # 檢查 'properties' 鍵是否存在，如果不存在則初始化為一個空字典。
        if original_schema_dict.get("properties") is None:
            original_schema_dict["properties"] = {}

        # 如果提供了欄位名稱，則新增一個用於向量嵌入的欄位結構。
        if field_name:
            field_schema = {
                "type": "array",
                "keyPropertyMapping": "embedding_vector",  # 指定此欄位為向量嵌入。
                "dimension": embedding_dimension,  # 設定向量的維度。
                "items": {"type": "number"},  # 陣列中的每個元素都是數字。
            }
            # 將新的欄位結構加入到 'properties' 中。
            original_schema_dict["properties"][field_name] = field_schema

        # 將更新後的 Python 字典轉換回 JSON 格式的字串並返回。
        return json.dumps(original_schema_dict)

    def update_data_store_schema(
        project_id: str,
        location: str,
        data_store_id: str,
        field_name: str | None = None,
        client_options: ClientOptions | None = None,
    ) -> None:
        """更新資料儲存區的結構以包含向量嵌入欄位。

        Args:
            project_id: Google Cloud 專案 ID。
            location: Google Cloud 的位置。
            data_store_id: 目標資料儲存區的 ID。
            field_name: 向量嵌入欄位的名稱。
            client_options: API 的客戶端選項。
        """
        # 初始化 SchemaServiceClient，用於與 Vertex AI Search 的結構服務互動。
        schema_client = discoveryengine.SchemaServiceClient(
            client_options=client_options
        )
        collection = "default_collection"

        # 構建結構的完整資源名稱。
        name = f"projects/{project_id}/locations/{location}/collections/{collection}/dataStores/{data_store_id}/schemas/default_schema"

        # 獲取目前的結構。
        schema = schema_client.get_schema(
            request=discoveryengine.GetSchemaRequest(name=name)
        )
        # 使用輔助函數生成新的 JSON 結構字串。
        new_schema_json = update_schema_as_json(
            original_schema=schema.json_schema,
            embedding_dimension=embedding_dimension,
            field_name=field_name,
        )
        # 創建一個新的 Schema 物件，包含更新後的 JSON 結構。
        new_schema = discoveryengine.Schema(json_schema=new_schema_json, name=name)

        # 發送更新結構的請求。這是一個長時間運行的操作。
        operation = schema_client.update_schema(
            request=discoveryengine.UpdateSchemaRequest(
                schema=new_schema, allow_missing=True
            ),
            timeout=1800,  # 設定操作的超時時間為 1800 秒 (30 分鐘)。
        )
        logging.info(f"等待結構更新操作完成：{operation.operation.name}")
        # 等待操作完成。
        operation.result()

    def add_data_in_store(
        project_id: str,
        location: str,
        data_store_id: str,
        input_files_uri: str,
        client_options: ClientOptions | None = None,
    ) -> None:
        """將文件匯入至資料儲存區。

        Args:
            project_id: Google Cloud 專案 ID。
            location: Google Cloud 的位置。
            data_store_id: 目標資料儲存區的 ID。
            input_files_uri: 輸入檔案的 GCS URI。
            client_options: API 的客戶端選項。
        """
        # 初始化 DocumentServiceClient，用於與文件服務互動。
        client = discoveryengine.DocumentServiceClient(client_options=client_options)

        # 構建目標資料儲存區分支的路徑。
        parent = client.branch_path(
            project=project_id,
            location=location,
            data_store=data_store_id,
            branch="default_branch",
        )

        # 創建匯入文件的請求。
        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            # 指定來源為 GCS。
            gcs_source=discoveryengine.GcsSource(
                input_uris=[input_files_uri],  # GCS 檔案的 URI 列表。
                data_schema="document",  # 指定資料結構為 'document'。
            ),
            # 設定協調模式為 FULL，表示完全替換現有資料。
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
        )

        # 發送匯入文件的請求。這是一個長時間運行的操作。
        operation = client.import_documents(request=request)
        logging.info(f"等待匯入操作完成：{operation.operation.name}")
        # 等待操作完成。
        operation.result()

    # 根據指定的區域設定 API 端點。
    client_options = ClientOptions(
        api_endpoint=f"{data_store_region}-discoveryengine.googleapis.com"
    )

    # 記錄日誌，表示開始更新資料儲存區的結構。
    logging.info("正在更新資料儲存區結構...")
    # 呼叫函數以更新結構，加入嵌入欄位。
    update_data_store_schema(
        project_id=project_id,
        location=data_store_region,
        data_store_id=data_store_id,
        field_name=embedding_column,
        client_options=client_options,
    )
    logging.info("結構更新成功")

    # 記錄日誌，表示開始將資料匯入儲存區。
    logging.info("正在將資料匯入儲存區...")
    # 呼叫函數以從 GCS 匯入資料。
    add_data_in_store(
        project_id=project_id,
        location=data_store_region,
        data_store_id=data_store_id,
        client_options=client_options,
        input_files_uri=input_files.uri,  # 從 KFP 輸入物件中獲取 GCS URI。
    )
    logging.info("資料匯入完成")

    # 為了讓 Vertex AI Search 有足夠的時間為新匯入的資料建立索引，暫停執行。
    logging.info("暫停 3 分鐘，以允許 Vertex AI Search 正確地為資料建立索引...")
    time.sleep(180)  # 暫停 180 秒 (3 分鐘)。
    logging.info("暫停結束。資料索引應已建立完成。")
