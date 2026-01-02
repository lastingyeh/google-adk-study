from google.cloud import bigquery
from google.adk.tools.tool_context import ToolContext

from ..shared_libraries.constants import PROJECT, DATASET_ID, TABLE_ID

try:
    client = bigquery.Client()
except Exception as e:
    print("BigQuery Client 初始化失敗，請確認環境設定是否正確：{e}")
    client = None


def get_product_details_for_brand(tool_context: ToolContext):
    """
    根據 tool_context 從 BigQuery 表格中擷取產品詳細資訊（標題、描述、屬性和品牌）。

    Args:
        tool_context (ToolContext): 包含要搜尋的品牌資訊的 tool_context 物件。

    Returns:
        str: 一個包含產品詳細資訊的 markdown 表格，如果 BigQuery 客戶端初始化失敗，則返回錯誤訊息。
             該表格包含 'Title'、'Description'、'Attributes' 和 'Brand' 等欄位。
             最多返回 3 筆結果。

    範例:
        >>> get_product_details_for_brand(tool_context)
        '| Title | Description | Attributes | Brand |\\n|---|---|---|---|\\n| Nike Air Max | 舒適的跑鞋 | 尺寸: 10, 顏色: 藍色 | Nike\\n| Nike Sportswear T-Shirt | 棉混紡，短袖 | 尺寸: L, 顏色: 黑色 | Nike\\n| Nike Pro Training Shorts | 吸濕排汗布料 | 尺寸: M, 顏色: 灰色 | Nike\\n'
    """

    brand = tool_context.user_content.parts[0].text
    if client is None:
        return "BigQuery Client 初始化失敗，請確認環境設定是否正確。"

    query = f"""
      SELECT
          title,
          description,
          attributes,
          brand
      FROM
          {PROJECT}.{DATASET_ID}.{TABLE_ID}
      WHERE brand LIKE '%{brand}%'
      LIMIT 3
    """
    query_job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("parameter1", "STRING", brand)]
    )

    query_job = client.query(query, job_config=query_job_config)
    query_job = client.query(query)
    results = query_job.result()

    markdown_table = "| Title | Description | Attributes | Brand |\n|---|---|---|---|\n"
    markdown_table += "|---|---|---|---|\n"

    for row in results:
        title = row.Title
        description = row.Description if row.Description else "N/A"
        attributes = row.Attributes if row.Attributes else "N/A"

        markdown_table += f"| {title} | {description} | {attributes} | {brand}\n"

    return markdown_table
