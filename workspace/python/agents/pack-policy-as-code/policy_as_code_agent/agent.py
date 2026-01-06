# 匯入必要的標準函式庫
import concurrent.futures  # 用於並行執行
import csv  # 用於處理 CSV 檔案
import json  # 用於處理 JSON 資料
import logging  # 用於記錄日誌
import os  # 用於與作業系統互動，例如檔案路徑
import time  # 用於時間相關操作，例如延遲
from typing import Any, Dict, List, Optional  # 用於類型提示

# 匯入第三方函式庫
import vertexai  # Google Vertex AI SDK
from google.adk.agents import Agent  # 從 ADK 匯入 Agent 類別
from google.adk.agents.callback_context import CallbackContext  # 匯入回呼上下文類別
from google.adk.tools.preload_memory_tool import (
    PreloadMemoryTool,
)  # 從 ADK 匯入記憶體預載入工具
from google.cloud import dataplex_v1, storage  # Google Cloud 客戶端函式庫
from vertexai.generative_models import (
    GenerativeModel,
)  # 從 Vertex AI SDK 匯入生成式模型

# 匯入此專案的本地模組
from .config import (
    DEFAULT_CORE_POLICIES,  # 預設核心策略
    GEMINI_MODEL_FLASH,  # Gemini 模型名稱
    LOCATION,  # Google Cloud 地區
    MAX_REMEDIATION_WORKERS,  # 修復建議的最大工作執行緒數
    PROJECT_ID,  # Google Cloud 專案 ID
    PROMPT_INSTRUCTION_FILE,  # 指令提示檔案名稱
    PROMPT_REMEDIATION_FILE,  # 修復提示檔案名稱
)
from .mcp import _get_dataplex_mcp_toolset  # Dataplex MCP 工具集
from .memory import (
    add_core_policy,
    analyze_execution_history,
    find_policy_in_memory,
    get_active_core_policies,
    get_execution_history,
    get_policy_by_id,
    list_policy_versions,
    log_policy_execution,
    prune_memory,
    rate_policy,
    remove_core_policy,
    save_core_policies,
    save_policy_to_memory,
)
from .utils.dataplex import entry_to_dict, get_project_id  # Dataplex 工具函式
from .utils.gcs import get_content_from_gcs_for_schema, load_metadata  # GCS 工具函式
from .utils.llm import (
    get_json_schema_from_content,
    llm_generate_policy_code,
)  # LLM 工具函式

# 全域初始化 Vertex AI，確保所有客戶端（包括 ADK 的記憶體服務）
# 使用正確的專案和地區。
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    logging.error(f"全域初始化 Vertex AI 失敗: {e}")

from .simulation import run_simulation  # 匯入模擬執行函式

# 取得腳本所在的目錄絕對路徑
script_dir = os.path.dirname(os.path.abspath(__file__))


def generate_policy_code_from_gcs(query: str, gcs_uri: str) -> dict:
    """
    使用 GCS 檔案中的結構描述，從自然語言查詢生成 Python 策略程式碼。

    Args:
        query (str): 自然語言查詢。
        gcs_uri (str): GCS 檔案的 URI。

    Returns:
        dict: 包含狀態和策略程式碼或錯誤訊息的字典。
    """
    logging.info(f"正在為查詢 '{query}' 從 '{gcs_uri}' 的結構描述生成策略程式碼")

    # 從 GCS 取得內容以用於結構描述
    content_response = get_content_from_gcs_for_schema(gcs_uri)
    if content_response["status"] == "error":
        return content_response

    content = content_response["content"]
    # 從內容中取得 JSON 結構描述
    schema = get_json_schema_from_content(content)

    # 將內容解析為字典列表以作為範例值
    try:
        metadata_sample = [
            json.loads(line) for line in content.splitlines() if line.strip()
        ]
    except json.JSONDecodeError:
        metadata_sample = []

    # 使用 LLM 生成策略程式碼
    policy_code = llm_generate_policy_code(query, schema, metadata_sample)

    # 檢查生成程式碼時是否發生錯誤
    if policy_code.startswith("# Error:") or policy_code.startswith(
        "# API key not configured"
    ):
        logging.error(f"生成策略程式碼時發生錯誤: {policy_code}")
        return {"status": "error", "error_message": policy_code}

    return {"status": "success", "policy_code": policy_code}


def _handle_policy_results(
    violations: list,
    policy_id: Optional[str],
    version: int,
    source: str,
    asset_count: int,
    report_message_suffix: str = "",
) -> dict:
    """
    處理模擬結果、記錄執行並格式化報告的輔助函式。

    Args:
        violations (list): 違規項目列表。
        policy_id (Optional[str]): 策略 ID。
        version (int): 策略版本。
        source (str): 資料來源 ('gcs' 或 'dataplex')。
        asset_count (int): 掃描的資產數量。
        report_message_suffix (str, optional): 附加到報告訊息的後綴。 Defaults to "".

    Returns:
        dict: 包含狀態和報告的字典。
    """
    if policy_id:
        status = "violations_found" if violations else "success"
        summary = f"掃描了 {asset_count} 個資產。發現 {len(violations)} 個違規項目。"
        # 傳遞完整的違規列表以記錄特定資源
        log_policy_execution(policy_id, version, status, source, violations, summary)

    if violations:
        return {
            "status": "success",
            "report": {
                "violations_found": True,
                "violations": violations,
                "message": f"{report_message_suffix}",
            },
        }
    else:
        return {
            "status": "success",
            "report": {
                "violations_found": False,
                "message": f"未發現策略違規。 {report_message_suffix}",
            },
        }


def run_policy_from_gcs(
    policy_code: str, gcs_uri: str, policy_id: Optional[str] = None, version: int = 0
) -> dict:
    """
    針對 GCS 中的元數據檔案或目錄執行策略模擬。

    Args:
        policy_code (str): 要執行的 Python 策略程式碼。
        gcs_uri (str): GCS 檔案或目錄的 URI。
        policy_id (Optional[str], optional): 策略 ID，用於記錄。 Defaults to None.
        version (int, optional): 策略版本，用於記錄。 Defaults to 0.

    Returns:
        dict: 包含狀態和結果的字典。
    """
    try:
        storage_client = storage.Client()
        gcs_path = gcs_uri.replace("gs://", "")
        path_parts = gcs_path.split("/", 1)
        bucket_name = path_parts[0]
        blob_prefix = path_parts[1] if len(path_parts) > 1 else ""
        bucket = storage_client.bucket(bucket_name)
        blobs = list(storage_client.list_blobs(bucket_name, prefix=blob_prefix))
        is_directory = len(blobs) > 1 or (
            len(blobs) == 1 and blobs[0].name.endswith("/")
        )
        is_file = not is_directory

    except Exception as e:
        if policy_id:
            log_policy_execution(
                policy_id, version, "failure", "gcs", summary=f"GCS 存取錯誤: {e}"
            )
        return {
            "status": "error",
            "error_message": f"存取 GCS URI {gcs_uri} 時發生錯誤: {e}",
        }

    if is_directory:
        # 處理目錄
        all_blobs_in_dir = list(storage_client.list_blobs(bucket, prefix=blob_prefix))
        files_to_process = [
            f"gs://{bucket_name}/{b.name}"
            for b in all_blobs_in_dir
            if not b.name.endswith("/") and b.name[len(blob_prefix) :].count("/") == 0
        ]

        if not files_to_process:
            if policy_id:
                log_policy_execution(
                    policy_id,
                    version,
                    "failure",
                    "gcs",
                    summary="在 GCS 目錄中找不到檔案",
                )
            return {
                "status": "error",
                "error_message": f"在 GCS 目錄 {gcs_uri} 中找不到檔案",
            }

        all_violations = []

        def process_file(file_uri):
            """處理單一檔案的內部函式"""
            metadata = load_metadata(gcs_uri=file_uri)
            if isinstance(metadata, dict) and "error" in metadata:
                return [
                    {
                        "source_file": file_uri,
                        "policy": "載入錯誤",
                        "violation": metadata["error"],
                    }
                ]

            violations = run_simulation(policy_code, metadata)
            for v in violations:
                v["source_file"] = file_uri
            return violations

        # 使用執行緒池並行處理檔案
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {
                executor.submit(process_file, file_uri): file_uri
                for file_uri in files_to_process
            }
            for future in concurrent.futures.as_completed(future_to_file):
                file_uri = future_to_file[future]
                try:
                    violations_from_file = future.result()
                    all_violations.extend(violations_from_file)
                except Exception as exc:
                    all_violations.append(
                        {
                            "source_file": file_uri,
                            "policy": "執行錯誤",
                            "violation": f"處理過程中發生例外: {exc}",
                        }
                    )

        report_message = (
            f"這是一個目錄。策略檢查在根層級的 {len(files_to_process)} 個檔案上執行。"
        )
        return _handle_policy_results(
            all_violations,
            policy_id,
            version,
            "gcs",
            len(files_to_process),
            report_message,
        )

    elif is_file:
        # 處理單一檔案
        metadata = load_metadata(gcs_uri=gcs_uri)
        if isinstance(metadata, dict) and "error" in metadata:
            if policy_id:
                log_policy_execution(
                    policy_id,
                    version,
                    "failure",
                    "gcs",
                    summary=f"元數據載入錯誤: {metadata['error']}",
                )
            return {"status": "error", "error_message": metadata["error"]}

        violations = run_simulation(policy_code, metadata)

        if violations and violations[0].get("policy") == "Configuration Error":
            if policy_id:
                log_policy_execution(
                    policy_id,
                    version,
                    "failure",
                    "gcs",
                    summary=f"設定錯誤: {violations[0]['violation']}",
                )
            return {"status": "error", "error_message": violations[0]["violation"]}

        return _handle_policy_results(violations, policy_id, version, "gcs", 1)

    else:
        return {
            "status": "error",
            "error_message": f"無法處理 GCS URI {gcs_uri}。",
        }


def _get_remediation_with_retry(model, violation, max_retries=3):
    """
    為單一違規項目取得修復建議，並採用指數退避重試機制。

    Args:
        model: 用於生成建議的生成式模型。
        violation (dict): 違規項目詳情。
        max_retries (int, optional): 最大重試次數。 Defaults to 3.

    Returns:
        dict: 包含違規項目和建議的字典。
    """
    base_delay = 1

    try:
        prompt_path = os.path.join(script_dir, "prompts", PROMPT_REMEDIATION_FILE)
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return {
            "violation": violation,
            "suggestion": "錯誤：找不到修復提示檔案。",
        }

    for i in range(max_retries):
        try:
            prompt = prompt_template.replace(
                "{{VIOLATION_DETAILS}}", json.dumps(violation, indent=2)
            )
            response = model.generate_content(prompt)
            return {"violation": violation, "suggestion": response.text.strip()}
        except Exception as e:
            logging.warning(
                f"為違規項目 {violation.get('resource_name')} 取得修復建議時發生錯誤: {e}。將在 {base_delay} 秒後重試..."
            )
            time.sleep(base_delay)
            base_delay *= 2

    logging.error(
        f"在 {max_retries} 次重試後，仍無法為違規項目 {violation.get('resource_name')} 取得修復建議。"
    )
    return {
        "violation": violation,
        "suggestion": "錯誤：無法生成修復建議。",
    }


def suggest_remediation(violations: List[Dict[str, Any]]) -> dict:
    """
    並行地為策略違規列表建議修復措施。

    Args:
        violations (List[Dict[str, Any]]): 違規項目字典的列表。

    Returns:
        dict: 包含狀態和修復建議的字典。
    """
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(GEMINI_MODEL_FLASH)
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"初始化 Vertex AI 時發生錯誤: {e}",
        }

    remediation_suggestions = []
    # 使用執行緒池並行取得修復建議
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_REMEDIATION_WORKERS
    ) as executor:
        future_to_violation = {
            executor.submit(_get_remediation_with_retry, model, v): v
            for v in violations
        }
        for future in concurrent.futures.as_completed(future_to_violation):
            try:
                suggestion = future.result()
                remediation_suggestions.append(suggestion)
            except Exception as exc:
                violation = future_to_violation[future]
                logging.error(
                    f"處理違規項目 {violation.get('resource_name')} 時發生例外: {exc}"
                )
                remediation_suggestions.append(
                    {
                        "violation": violation,
                        "suggestion": "錯誤：在生成修復建議期間發生未預期的例外。",
                    }
                )

    return {"status": "success", "remediation_suggestions": remediation_suggestions}


def get_supported_examples() -> dict:
    """返回範例策略查詢的列表"""
    return DEFAULT_CORE_POLICIES


def generate_policy_code_from_dataplex(policy_query: str, dataplex_query: str) -> dict:
    """
    透過從 Dataplex 查詢中擷取元數據範例來生成策略程式碼。

    Args:
        policy_query (str): 自然語言策略查詢。
        dataplex_query (str): 用於搜尋資產的 Dataplex 查詢。

    Returns:
        dict: 包含狀態和策略程式碼或錯誤訊息的字典。
    """
    project_id, error_message = get_project_id()
    if error_message:
        return {"status": "error", "error_message": error_message}

    try:
        with dataplex_v1.CatalogServiceClient() as client:
            # 搜尋 Dataplex 項目以取得範例
            search_request = dataplex_v1.SearchEntriesRequest(
                name=f"projects/{project_id}/locations/global",
                scope=f"projects/{project_id}",
                query=dataplex_query,
                page_size=5,  # 限制範例數量
            )
            sample_results = list(client.search_entries(request=search_request))

            if not sample_results:
                return {
                    "status": "error",
                    "error_message": "在 Dataplex 中找不到符合查詢的資產。",
                }

            metadata_sample = []
            # 並行擷取完整項目詳細資訊
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_name = {
                    executor.submit(
                        client.get_entry, name=res.dataplex_entry.name
                    ): res.dataplex_entry.name
                    for res in sample_results
                }
                for future in concurrent.futures.as_completed(future_to_name):
                    try:
                        full_entry = future.result()
                        metadata_sample.append(entry_to_dict(full_entry))
                    except Exception as e:
                        logging.error(
                            f"無法擷取範例項目 {future_to_name[future]} 的詳細資訊: {e}"
                        )

            if not metadata_sample:
                return {
                    "status": "error",
                    "error_message": "在搜尋中找到資產，但無法擷取其完整詳細資訊以生成結構描述。",
                }

            # 生成結構描述和策略程式碼
            schema = get_json_schema_from_content(json.dumps(metadata_sample))
            policy_code = llm_generate_policy_code(
                policy_query, schema, metadata_sample
            )

            if policy_code.startswith("# Error:"):
                return {"status": "error", "error_message": policy_code}

            return {"status": "success", "policy_code": policy_code}

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"發生未預期的錯誤: {type(e).__name__}: {e}",
        }


def run_policy_on_dataplex(
    policy_code: str,
    dataplex_query: str,
    policy_id: Optional[str] = None,
    version: int = 0,
) -> dict:
    """
    針對來自 Dataplex 搜尋的完整資產集執行策略。

    Args:
        policy_code (str): 要執行的 Python 策略程式碼。
        dataplex_query (str): 用於搜尋資產的 Dataplex 查詢。
        policy_id: Optional[str], optional): 策略 ID，用於記錄。 Defaults to None.
        version (int, optional): 策略版本，用於記錄。 Defaults to 0.

    Returns:
        dict: 包含狀態和報告的字典。
    """
    project_id, error_message = get_project_id()
    if error_message:
        if policy_id:
            log_policy_execution(
                policy_id,
                version,
                "failure",
                "dataplex",
                summary=f"專案 ID 錯誤: {error_message}",
            )
        return {"status": "error", "error_message": error_message}

    try:
        with dataplex_v1.CatalogServiceClient() as client:
            # 搜尋所有符合的 Dataplex 項目
            search_request = dataplex_v1.SearchEntriesRequest(
                name=f"projects/{project_id}/locations/global",
                scope=f"projects/{project_id}",
                query=dataplex_query,
            )
            all_results = list(client.search_entries(request=search_request))

            if not all_results:
                if policy_id:
                    log_policy_execution(
                        policy_id,
                        version,
                        "success",
                        "dataplex",
                        summary="找不到要檢查的資產。",
                    )
                return {
                    "status": "success",
                    "report": {
                        "violations_found": False,
                        "message": "在 Dataplex 中找不到符合查詢的資產。",
                    },
                }

            metadata = []
            # 並行擷取所有項目的完整詳細資訊
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_name = {
                    executor.submit(
                        client.get_entry, name=res.dataplex_entry.name
                    ): res.dataplex_entry.name
                    for res in all_results
                }
                for future in concurrent.futures.as_completed(future_to_name):
                    try:
                        full_entry = future.result()
                        metadata.append(entry_to_dict(full_entry))
                    except Exception as e:
                        logging.error(
                            f"無法擷取項目 {future_to_name[future]} 的詳細資訊: {e}"
                        )

            if not metadata:
                if policy_id:
                    log_policy_execution(
                        policy_id,
                        version,
                        "failure",
                        "dataplex",
                        summary="找到資產但無法擷取詳細資訊。",
                    )
                return {
                    "status": "error",
                    "error_message": "在搜尋中找到資產，但無法擷取其完整詳細資訊。",
                }

            # 執行模擬並處理結果
            violations = run_simulation(policy_code, metadata)

            return _handle_policy_results(
                violations, policy_id, version, "dataplex", len(metadata)
            )

    except Exception as e:
        if policy_id:
            log_policy_execution(
                policy_id,
                version,
                "failure",
                "dataplex",
                summary=f"未預期的錯誤: {e}",
            )
        return {
            "status": "error",
            "error_message": f"發生未預期的錯誤: {type(e).__name__}: {e}",
        }


def generate_compliance_scorecard(source_type: str, source_target: str) -> dict:
    """
    針對資料集執行一組核心策略，並計算合規性分數。

    Args:
        source_type (str): 'gcs' 或 'dataplex'
        source_target (str): GCS URI 或 Dataplex 搜尋查詢

    Returns:
        dict: 包含狀態和計分卡的字典。
    """

    # 從記憶體中擷取核心策略
    mem_response = get_active_core_policies()
    policies_to_run = []

    if mem_response.get("status") == "success":
        policies_to_run = mem_response.get("policies", [])

    # 如果為空或不可用，則使用預設值
    if not policies_to_run:
        policies_to_run = DEFAULT_CORE_POLICIES

    results = []
    passed_count = 0

    # 迭代執行每個策略
    for query in policies_to_run:
        policy_code = ""
        if source_type == "gcs":
            # 從 GCS 生成和執行
            res = generate_policy_code_from_gcs(query, source_target)
            if res.get("status") == "error":
                results.append(
                    {
                        "policy": query,
                        "status": "Error",
                        "details": res.get("error_message"),
                    }
                )
                continue
            policy_code = res.get("policy_code")

            run_res = run_policy_from_gcs(policy_code, source_target)

        elif source_type == "dataplex":
            # 從 Dataplex 生成和執行
            res = generate_policy_code_from_dataplex(query, source_target)
            if res.get("status") == "error":
                results.append(
                    {
                        "policy": query,
                        "status": "Error",
                        "details": res.get("error_message"),
                    }
                )
                continue
            policy_code = res.get("policy_code")

            run_res = run_policy_on_dataplex(policy_code, source_target)

        else:
            return {
                "status": "error",
                "message": "無效的 source_type。必須是 'gcs' 或 'dataplex'。",
            }

        # 檢查執行結果
        if run_res.get("status") == "error":
            results.append(
                {
                    "policy": query,
                    "status": "Error",
                    "details": run_res.get("error_message"),
                }
            )
        else:
            report = run_res.get("report", {})
            violations = report.get("violations", [])
            if violations:
                results.append(
                    {
                        "policy": query,
                        "status": "Failed",
                        "violations_count": len(violations),
                    }
                )
            else:
                results.append({"policy": query, "status": "Passed"})
                passed_count += 1

    # 計算最終分數
    total_policies = len(policies_to_run)
    score = (passed_count / total_policies) * 100 if total_policies > 0 else 0

    return {
        "status": "success",
        "scorecard": {
            "compliance_score": f"{score:.1f}%",
            "policies_passed": passed_count,
            "total_policies": total_policies,
            "details": results,
        },
    }


def export_report(
    violations: List[Dict[str, Any]],
    format: str = "csv",
    filename: str = "report",
    destination: Optional[str] = None,
) -> dict:
    """
    將違規列表匯出為 CSV 或 HTML 檔案。可選擇上傳到 GCS。

    Args:
        violations (List[Dict[str, Any]]): 違規字典的列表。
        format (str, optional): 'csv' 或 'html'。 Defaults to "csv".
        filename (str, optional): 基本檔案名稱（將自動添加副檔名）。 Defaults to "report".
        destination (Optional[str], optional): 可選的 GCS URI (例如, 'gs://my-bucket/reports/')。 Defaults to None.

    Returns:
        dict: 包含操作狀態和訊息的字典。
    """
    if not violations:
        return {"status": "error", "message": "沒有要匯出的違規項目。"}

    # 標準化檔案名稱
    filename = os.path.basename(filename)
    if not filename:
        filename = "report"

    # 如果使用者提供了副檔名，則去除它
    if filename.lower().endswith(f".{format.lower()}"):
        filename = filename.rsplit(".", 1)[0]

    file_path = f"{filename}.{format.lower()}"

    try:
        if format.lower() == "csv":
            # 寫入 CSV 檔案
            with open(file_path, "w", newline="") as csvfile:
                if not violations:
                    fieldnames = ["policy", "violation"]
                else:
                    fieldnames = list(violations[0].keys())

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for v in violations:
                    # 確保每一行都包含所有鍵
                    row = {k: v.get(k, "") for k in fieldnames}
                    writer.writerow(row)

        elif format.lower() == "html":
            # 生成簡單的 HTML 表格
            html = "<html><head><style>table {border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;} th, td {text-align: left; padding: 8px; border: 1px solid #ddd;} tr:nth-child(even){background-color: #f2f2f2} th {background-color: #4CAF50; color: white;}</style></head><body>"
            html += "<h2>合規性報告</h2>"
            html += "<table><thead><tr>"

            keys = list(violations[0].keys()) if violations else ["Policy", "Violation"]
            for k in keys:
                html += f"<th>{k}</th>"
            html += "</tr></thead><tbody>"

            for v in violations:
                html += "<tr>"
                for k in keys:
                    val = v.get(k, "")
                    html += f"<td>{val}</td>"
                html += "</tr>"

            html += "</tbody></table></body></html>"

            with open(file_path, "w") as f:
                f.write(html)
        else:
            return {
                "status": "error",
                "message": "不支援的格式。請使用 'csv' 或 'html'。",
            }

        # 處理 GCS 上傳
        if destination and destination.startswith("gs://"):
            try:
                storage_client = storage.Client()

                # 解析 bucket 和 blob 名稱
                gcs_path = destination.replace("gs://", "")
                path_parts = gcs_path.split("/", 1)
                bucket_name = path_parts[0]

                # 處理目的地是目錄或完整路徑的情況
                if len(path_parts) > 1:
                    blob_prefix = path_parts[1]
                    if blob_prefix.endswith("/"):
                        blob_name = f"{blob_prefix}{os.path.basename(file_path)}"
                    else:
                        # 如果使用者給了完整路徑，就使用它，但要確保副檔名匹配
                        blob_name = blob_prefix
                        if not blob_name.lower().endswith(f".{format.lower()}"):
                            blob_name += f".{format.lower()}"
                else:
                    blob_name = os.path.basename(file_path)

                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(file_path)

                final_uri = f"gs://{bucket_name}/{blob_name}"

                # 上傳後清理本地檔案
                os.remove(file_path)

                return {
                    "status": "success",
                    "message": f"報告已匯出至 GCS: {final_uri}",
                    "gcs_uri": final_uri,
                    "download_instruction": "您可以從 Google Cloud Console UI 或透過 gsutil 下載此檔案。",
                }

            except Exception as e:
                return {"status": "error", "message": f"上傳到 GCS 失敗: {e}"}

        return {
            "status": "success",
            "file_path": os.path.abspath(file_path),
            "message": "報告已儲存至本地。",
        }

    except Exception as e:
        return {"status": "error", "message": f"匯出報告失敗: {e}"}


async def auto_save_session_to_memory_callback(callback_context: CallbackContext):
    """
    一個異步回呼函式，在 agent 執行後自動將會話儲存到記憶體中。
    """
    if (
        hasattr(callback_context._invocation_context, "memory_service")
        and callback_context._invocation_context.memory_service
    ):
        await callback_context._invocation_context.memory_service.add_session_to_memory(
            callback_context._invocation_context.session
        )


# 定義 agent 可用的工具列表
agent_tools = [
    find_policy_in_memory,
    save_policy_to_memory,
    list_policy_versions,
    get_policy_by_id,
    prune_memory,
    rate_policy,
    generate_policy_code_from_gcs,
    run_policy_from_gcs,
    generate_policy_code_from_dataplex,
    run_policy_on_dataplex,
    get_supported_examples,
    suggest_remediation,
    get_execution_history,
    analyze_execution_history,
    generate_compliance_scorecard,
    export_report,
    get_active_core_policies,
    save_core_policies,
    add_core_policy,
    remove_core_policy,
    PreloadMemoryTool(),
]

# 嘗試加入 MCP 工具
mcp_toolset = _get_dataplex_mcp_toolset()
if mcp_toolset:
    agent_tools.append(mcp_toolset)
    logging.info("成功註冊 Dataplex MCP 工具集。")
else:
    logging.warning("由於驗證失敗，無法註冊 Dataplex MCP 工具集。")

# 從檔案載入指令
try:
    instruction_path = os.path.join(script_dir, "prompts", PROMPT_INSTRUCTION_FILE)
    with open(instruction_path, "r") as f:
        agent_instruction = f.read()
except FileNotFoundError:
    logging.error("找不到指令檔案。使用備用指令。")
    agent_instruction = "您是一個用於檢查資料策略的有用代理。"

# 建立根 agent
root_agent = Agent(
    name="policy_as_code",
    model=GEMINI_MODEL_FLASH,
    description="用於針對 GCS 或即時 Dataplex 搜尋的元數據模擬資料策略的代理。",
    instruction=agent_instruction,
    tools=agent_tools,
    after_agent_callback=auto_save_session_to_memory_callback,
)

# 從 ADK 應用程式框架匯入 App
from google.adk.apps.app import App

# 建立應用程式實例
app = App(root_agent=root_agent, name="policy_as_code_agent")
