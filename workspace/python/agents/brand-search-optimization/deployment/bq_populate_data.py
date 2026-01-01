# 匯入 BigQuery 客戶端函式庫
from google.cloud import bigquery

# 從共用函式庫匯入常數
from brand_search_optimization.shared_libraries import constants

# 從常數檔案中讀取設定
PROJECT = constants.PROJECT
TABLE_ID = constants.TABLE_ID
LOCATION = constants.LOCATION
DATASET_ID = constants.DATASET_ID
TABLE_ID = constants.TABLE_ID

# 初始化 BigQuery 客戶端，並指定專案
client = bigquery.Client(project=PROJECT)

# 準備要插入的範例資料
data_to_insert = [
    {
        "Title": "兒童慢跑褲",
        "Description": "為好動的孩子設計的舒適且具支撐性的跑鞋。透氣的網布鞋面能保持足部涼爽，耐用的外底則提供絕佳的抓地力。",
        "Attributes": "Size: 10 Toddler, Color: Blue/Green",
        "Brand": "BSOAgentTestBrand",
    },
    {
        "Title": "發光運動鞋",
        "Description": "有趣又時尚的運動鞋，具有孩子們會喜歡的發光功能。具支撐性且舒適，適合整天玩耍。",
        "Attributes": "Size: 13 Toddler, Color: Silver",
        "Brand": "BSOAgentTestBrand",
    },
    {
        "Title": "學校鞋",
        "Description": "多功能且舒適的鞋子，非常適合在學校日常穿著。結構耐用，設計具支撐性。",
        "Attributes": "Size: 12 Preschool, Color: Black",
        "Brand": "BSOAgentTestBrand",
    },
]


def create_dataset_if_not_exists():
    """如果 BigQuery 資料集不存在，則建立它。"""
    # 建立 BigQuery 客戶端物件。
    # 完整的資料集 ID 格式為 'project.dataset_id'
    dataset_id = f"{client.project}.{DATASET_ID}"
    # 建立一個 Dataset 物件
    dataset = bigquery.Dataset(dataset_id)
    # 設定資料集的位置
    dataset.location = "US"
    # 刪除已存在的資料集（包含內容），確保是一個乾淨的開始
    client.delete_dataset(
        dataset_id, delete_contents=True, not_found_ok=True
    )  # 發出 API 請求。
    # 建立新的資料集
    dataset = client.create_dataset(dataset)  # 發出 API 請求。
    print("已建立資料集 {}.{}".format(client.project, dataset.dataset_id))
    return dataset


def populate_bigquery_table():
    """使用提供的資料填入 BigQuery 資料表。"""
    # 建立資料集
    dataset_ref = create_dataset_if_not_exists()
    if not dataset_ref:
        return

    # 根據您的 CREATE TABLE 陳述式定義結構 (schema)
    schema = [
        bigquery.SchemaField("Title", "STRING"),
        bigquery.SchemaField("Description", "STRING"),
        bigquery.SchemaField("Attributes", "STRING"),
        bigquery.SchemaField("Brand", "STRING"),
    ]
    # 完整的資料表 ID 格式為 'project.dataset_id.table_id'
    table_id = f"{PROJECT}.{DATASET_ID}.{TABLE_ID}"
    # 建立一個 Table 物件
    table = bigquery.Table(table_id, schema=schema)
    # 刪除已存在的資料表，確保是一個乾淨的開始
    client.delete_table(table_id, not_found_ok=True)  # 發出 API 請求。
    print("已刪除資料表 '{}'。".format(table_id))
    # 建立新的資料表
    table = client.create_table(table)  # 發出 API 請求。
    print("已建立資料表 {}.{}.{}".format(PROJECT, table.dataset_id, table.table_id))

    # 使用 JSON 格式將資料插入資料表
    errors = client.insert_rows_json(table=table, json_rows=data_to_insert)

    # 檢查是否有錯誤發生
    if errors == []:
        print(
            f"已成功將 {len(data_to_insert)} 筆資料插入至 {PROJECT}.{DATASET_ID}.{TABLE_ID}"
        )
    else:
        print("插入資料時發生錯誤：")
        for error in errors:
            print(error)


# 當此腳本被直接執行時，會執行以下程式碼
if __name__ == "__main__":
    populate_bigquery_table()
    print("\n--- 有關如何為 BQ 資料表新增權限的說明，請參閱 customization.md 檔案 ---")
