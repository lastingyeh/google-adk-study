# 匯入標準函式庫
import json  # 用於處理 JSON 資料
import os  # 用於檔案與路徑操作
import re  # 用於正則表達式處理

# 匯入 Vertex AI SDK
import vertexai
from vertexai.generative_models import GenerativeModel

# 匯入專案設定與工具
from ..config import GEMINI_MODEL_PRO, LOCATION, PROJECT_ID, PROMPT_CODE_GENERATION_FILE
from .json_tools import traverse

# 取得目前檔案的上層目錄，作為 script_dir
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_sample_values_str(metadata_sample: list) -> str:
    """
    從中繼資料產生範例值的字串。
    會選擇最具代表性的項目（以 JSON 字串長度最大者為代表），
    並用 traverse 將其展平成 sample_values 字典，最後轉成格式化 JSON 字串。
    Args:
        metadata_sample (list): 中繼資料的樣本列表。
    Returns:
        str: 代表性項目的展平 JSON 字串。
    """
    if not metadata_sample:
        # 若無資料則回傳空物件
        return "{}"

    # 尋找最具代表性的項目（最大者）來產生範例值。
    # 這樣可以避免用到像 'entrygroup' 這種稀疏的項目，而優先選擇像 'table' 這種較豐富的項目。
    try:
        most_representative_entry = max(
            metadata_sample, key=lambda item: len(json.dumps(item))
        )
    except (TypeError, ValueError):
        # 如果 max 發生錯誤，則退回使用第一個項目
        most_representative_entry = metadata_sample[0]

    sample_values = {}
    # 使用 traverse 將物件展平成 key-value 結構
    traverse(most_representative_entry, sample_values)

    # 轉成格式化 JSON 字串
    return json.dumps(sample_values, indent=2)


# | 比較項目   | JSON (Standard)                  | JSONL (JSON Lines)                  |
# |------------|--------------------------------|--------------------------------------|
# | 檔案結構   | 單一根節點（通常為陣列 []）      | 每一行為獨立物件，無根節點                |
# | 解析方式   | 整份載入：需讀取全檔後才可解析   | 逐行解析：讀一行處理一行（Stream）         |
# | 寫入效能   | 低：新增資料需重寫整個檔案       | 高：可直接在檔案末端追加（Append）         |
# | 記憶體佔用 | 高：檔案越大，佔用記憶體越多     | 極低：僅需足以存放單行的記憶體             |
# | 錯誤韌性   | 一處損壞，整份檔案通常無法讀取   | 某行損壞，不影響其他行讀取                |
# | 主要用途   | Web API、設定檔、小型資料交換    | 日誌（Log）、大數據處理、AI 訓練集       |


def get_json_schema_from_content(content: str):
    """
    讀取 JSON/JSONL 字串並回傳所有物件的結構描述（schema）。
    會自動判斷是 JSONL（每行一個物件）或 JSON（整個陣列），
    並遞迴產生所有物件的 schema，最後合併所有物件的 schema。
    Args:
        content (str): JSON 或 JSONL 格式的字串。
    Returns:
        dict: 合併後的 schema 結構。
    """
    try:
        # 檢查內容是 JSONL 還是 JSON
        if content.strip().startswith("["):
            # 若以 [ 開頭，視為 JSON 陣列
            data = json.loads(content)
        else:
            # 否則視為 JSONL，每行一個物件
            data = [json.loads(line) for line in content.splitlines() if line.strip()]
    except json.JSONDecodeError:
        # 若解析失敗則回傳空 dict
        return {}

    if not data:
        # 若資料為空則回傳空 dict
        return {}

    def merge_schemas(schema1, schema2):
        """
        合併兩個 schema 結構。
        若為 dict 則遞迴合併 key，若為 list 則合併第一個元素。
        其他型態則以 schema2 為主。
        """
        if isinstance(schema1, dict) and isinstance(schema2, dict):
            merged = schema1.copy()
            for key, value in schema2.items():
                if key in merged:
                    merged[key] = merge_schemas(merged[key], value)
                else:
                    merged[key] = value
            return merged
        elif isinstance(schema1, list) and isinstance(schema2, list):
            if schema1 and schema2:
                return [merge_schemas(schema1[0], schema2[0])]
            elif schema2:
                return schema2
            else:
                return schema1
        else:
            return schema2

    def generate_schema_from_obj(obj):
        """
        遞迴產生單一物件的 schema。
        dict 會遞迴處理每個 key，list 則合併所有元素的 schema，
        其他型態則回傳型態名稱。
        """
        if isinstance(obj, dict):
            schema = {}
            for k, v in obj.items():
                schema[k] = generate_schema_from_obj(v)
            return schema
        elif isinstance(obj, list):
            if obj:
                # 為了讓 schema 更全面，合併所有項目的 schema
                item_schemas = [generate_schema_from_obj(item) for item in obj]
                if not item_schemas:
                    return []
                merged_item_schema = item_schemas[0]
                for item_schema in item_schemas[1:]:
                    merged_item_schema = merge_schemas(merged_item_schema, item_schema)
                return [merged_item_schema]
            else:
                return []
        else:
            # 回傳型態名稱（如 str, int, float, bool, NoneType）
            return type(obj).__name__

    # 若資料不是 list，直接產生 schema
    if not isinstance(data, list):
        return generate_schema_from_obj(data)

    # 產生所有物件的 schema
    all_schemas = [
        generate_schema_from_obj(item) for item in data if isinstance(item, dict)
    ]
    if not all_schemas:
        return {}

    # 合併所有 schema
    final_schema = all_schemas[0]
    for schema in all_schemas[1:]:
        final_schema = merge_schemas(final_schema, schema)

    return final_schema


def llm_generate_policy_code(query: str, schema: dict, metadata_sample: list) -> str:
    """
    使用 Vertex AI 產生評估政策查詢的 Python 函式。
    會將 schema、query、sample values 帶入 prompt template，
    並呼叫 Gemini LLM 產生對應的 Python 程式碼。
    Args:
        query (str): 使用者輸入的政策查詢。
        schema (dict): 推論出的 JSON schema。
        metadata_sample (list): 中繼資料樣本。
    Returns:
        str: 產生的 Python 程式碼，或錯誤訊息。
    """
    try:
        # 初始化 Vertex AI 服務
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(GEMINI_MODEL_PRO)
    except Exception as e:
        # 若初始化失敗則回傳錯誤訊息
        return f"# 錯誤：初始化 Vertex AI 失敗: {e}"

    # 將 schema 與 sample values 轉為格式化字串
    schema_str = json.dumps(schema, indent=2)
    sample_values_str = generate_sample_values_str(metadata_sample)

    # 從檔案載入 prompt template
    try:
        prompt_path = os.path.join(script_dir, "prompts", PROMPT_CODE_GENERATION_FILE)

        with open(prompt_path, "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        # 找不到 prompt 檔案時回傳錯誤
        return f"# 錯誤：找不到提示詞檔案於 prompts/{PROMPT_CODE_GENERATION_FILE}"

    # 替換 prompt template 中的佔位符
    prompt = prompt_template.replace("{{INFERRED_JSON_SCHEMA}}", schema_str)
    prompt = prompt.replace("{{USER_POLICY_QUERY}}", query)
    prompt = prompt.replace("{{SAMPLE_VALUES}}", sample_values_str)

    # 呼叫 LLM 產生內容
    response = model.generate_content(prompt)
    # 嘗試從回應中擷取 markdown 格式的 python 程式碼
    match = re.search(r"```python\n(.*)\n```", response.text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        # 若 LLM 沒有使用 markdown，則退回直接取代
        code = response.text.strip()
        if "def check_policy" in code:
            return code
        # 若無法擷取到程式碼則回傳錯誤與原始回應
        return f"# 錯誤：無法從 LLM 回應中擷取 Python 程式碼。\n# 回應內容:\n# {response.text}"
