import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional

import vertexai
from google.api_core.exceptions import FailedPrecondition
from google.cloud import firestore  # type: ignore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector
from vertexai.language_models import TextEmbeddingModel

from .config import (
    CORE_POLICIES_DOC_REF,
    EMBEDDING_MODEL_NAME,
    ENABLE_MEMORY_BANK,
    FIRESTORE_COLLECTION_EXECUTIONS,
    FIRESTORE_COLLECTION_POLICIES,
    FIRESTORE_DATABASE,
    LOCATION,
    PROJECT_ID,
)

# 初始化 Firestore 客戶端
db = None

if ENABLE_MEMORY_BANK:
    try:
        db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE)
        logging.info(
            f"Firestore 已為專案 {db.project} 初始化並驗證，資料庫：{FIRESTORE_DATABASE}"
        )
    except Exception as e:
        logging.warning(
            f"Firestore 初始化失敗或找不到資料庫。記憶庫將被停用。錯誤：{e}"
        )
        db = None
else:
    logging.info("記憶庫已透過設定停用。")

COLLECTION_NAME = FIRESTORE_COLLECTION_POLICIES


def _get_embedding(text: str) -> List[float]:
    """使用 Vertex AI 為給定文字產生向量嵌入。"""
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL_NAME)
        embeddings = model.get_embeddings([text])
        return embeddings[0].values
    except Exception as e:
        logging.error(f"產生嵌入時發生錯誤：{e}")
        return []


def _policy_to_dict(doc) -> dict:
    """將 Firestore 文件轉換為字典的輔助函式。"""
    data = doc.to_dict()
    # 將 Firestore 時間戳記轉換為 ISO 字串以便 JSON 序列化
    if "created_at" in data and isinstance(data["created_at"], datetime.datetime):
        data["created_at"] = data["created_at"].isoformat()
    if "last_used" in data and isinstance(data["last_used"], datetime.datetime):
        data["last_used"] = data["last_used"].isoformat()
    # 從輸出中移除嵌入向量以減少雜訊
    if "embedding" in data:
        del data["embedding"]
    return data


def get_active_core_policies() -> dict:
    """從 Firestore 檢索設定的核心策略。如果未設定，則返回預設狀態。"""
    if not db:
        return {
            "status": "success",
            "source": "default",
            "message": "記憶庫已停用。使用預設核心策略。",
            "policies": [],
        }

    try:
        doc = db.document(CORE_POLICIES_DOC_REF).get()
        if doc.exists:
            return {
                "status": "success",
                "source": "firestore",
                "policies": doc.to_dict().get("policies", []),
            }
        else:
            return {
                "status": "success",
                "source": "default",
                "message": "記憶庫中未儲存核心策略。使用預設值。",
                "policies": [],  # 代理程式邏輯將在需要時使用預設值填充
            }
    except Exception as e:
        return {"status": "error", "message": f"擷取核心策略時發生錯誤：{e}"}


def save_core_policies(policies: List[str]) -> dict:
    """在 Firestore 中儲存或覆寫核心策略列表。"""
    if not db:
        return {"status": "error", "message": "記憶庫已停用。"}

    try:
        db.document(CORE_POLICIES_DOC_REF).set(
            {"policies": policies, "updated_at": datetime.datetime.now()}
        )
        return {
            "status": "success",
            "message": "核心策略儲存成功。",
            "policies": policies,
        }
    except Exception as e:
        return {"status": "error", "message": f"儲存核心策略失敗：{e}"}


def add_core_policy(policy: str) -> dict:
    """將單一策略新增至核心策略列表。"""
    if not db:
        return {"status": "error", "message": "記憶庫已停用。"}

    try:
        doc_ref = db.document(CORE_POLICIES_DOC_REF)

        # 使用 array_union 新增唯一值
        doc_ref.set(
            {
                "policies": firestore.ArrayUnion([policy]),
                "updated_at": datetime.datetime.now(),
            },
            merge=True,
        )

        # 擷取更新後的列表以返回
        updated_doc = doc_ref.get()
        policies = updated_doc.to_dict().get("policies", [])

        return {
            "status": "success",
            "message": f"已新增策略：'{policy}'",
            "policies": policies,
        }
    except Exception as e:
        return {"status": "error", "message": f"新增核心策略失敗：{e}"}


def remove_core_policy(policy: str) -> dict:
    """從核心策略列表中移除單一策略。"""
    if not db:
        return {"status": "error", "message": "記憶庫已停用。"}

    try:
        doc_ref = db.document(CORE_POLICIES_DOC_REF)

        # 使用 array_remove
        doc_ref.set(
            {
                "policies": firestore.ArrayRemove([policy]),
                "updated_at": datetime.datetime.now(),
            },
            merge=True,
        )

        updated_doc = doc_ref.get()
        policies = updated_doc.to_dict().get("policies", [])

        return {
            "status": "success",
            "message": f"已移除策略：'{policy}'",
            "policies": policies,
        }
    except Exception as e:
        return {"status": "error", "message": f"移除核心策略失敗：{e}"}


def find_policy_in_memory(
    query: str,
    source: str,
    author: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """
    使用向量搜尋在 Firestore 中尋找相似的策略。

    Args:
        query: 策略的自然語言查詢。
        source: 策略的來源（'gcs' 或 'dataplex'）。
        author: 可選的作者篩選條件。
        start_date: 可選的 ISO 格式開始日期。
        end_date: 可選的 ISO 格式結束日期。
    """
    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    query_embedding = _get_embedding(query)
    if not query_embedding:
        return {"status": "error", "message": "無法為查詢產生嵌入。"}

    # 基本集合參考
    policies_ref = db.collection(COLLECTION_NAME)

    # 注意：Firestore 向量搜尋目前需要向量索引。
    # 預篩選（where 子句）需要與向量欄位的複合索引。
    # 為求簡單/穩健，如果結果集很小，我們將先進行向量搜尋，然後在記憶體中篩選，
    # 或者如果使用者設定了複合索引，我們就依賴它。

    # 讓我們嘗試嚴格按 'source' 篩選，因為它是一個主要分區。
    # 需要：複合索引 (source ASC, embedding VECTOR)

    try:
        # 向量搜尋查詢
        vector_query = policies_ref.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=10,  # 擷取前 10 個相符項目
            distance_result_field="similarity_distance",  # 返回距離（在 Firestore 中，對於 COSINE 來說，值越低越好？不，餘弦距離是 1 - 相似度）
            # Firestore 餘弦距離：範圍 [0, 2]。0 表示完全相同。
        )

        # 執行查詢
        results = list(vector_query.stream())

    except FailedPrecondition as e:
        if "index" in str(e).lower():
            return {
                "status": "error",
                "message": f"缺少 Firestore 向量索引。請使用日誌中的連結建立索引。錯誤：{e}",
            }
        return {"status": "error", "message": f"向量搜尋失敗：{e}"}
    except Exception as e:
        return {"status": "error", "message": f"發生未預期的錯誤：{e}"}

    if not results:
        return {"status": "not_found", "message": "找不到任何策略。"}

    matches = []
    for doc in results:
        data = _policy_to_dict(doc)
        distance = doc.get("similarity_distance")
        # 將距離轉換為相似度分數（約略值，供使用者顯示）
        # 餘弦距離 = 1 - 餘弦相似度。所以 相似度 = 1 - 距離
        similarity = 1.0 - distance if distance is not None else 0.0
        data["similarity"] = similarity
        matches.append(data)

    # 在 Python 中套用篩選器（後篩選）
    # 對於原型來說，這比複雜的複合索引更安全
    filtered_matches = [m for m in matches if m.get("source") == source]

    if author:
        filtered_matches = [m for m in filtered_matches if m.get("author") == author]

    if start_date and end_date:
        try:
            start = datetime.datetime.fromisoformat(start_date)
            end = datetime.datetime.fromisoformat(end_date)
            # 如果需要，將字串轉換回日期時間進行比較，或者如果 data['created_at'] 是 ISO 字串，則直接比較字串
            # data['created_at'] 現在是來自 _policy_to_dict 的字串
            filtered_matches = [
                m
                for m in filtered_matches
                if start <= datetime.datetime.fromisoformat(m["created_at"]) <= end
            ]
        except Exception:
            pass  # 忽略篩選中的日期錯誤

    if not filtered_matches:
        return {
            "status": "not_found",
            "message": "向量搜尋後找不到符合條件的策略。",
        }

    # 按相似度排序（降序）
    filtered_matches.sort(key=lambda x: x["similarity"], reverse=True)

    best_match = filtered_matches[0]

    # 更新 last_used
    try:
        doc_ref = (
            db.collection(COLLECTION_NAME)
            .where("policy_id", "==", best_match["policy_id"])
            .where("version", "==", best_match["version"])
            .limit(1)
            .get()
        )
        if doc_ref:
            doc_ref[0].reference.update({"last_used": datetime.datetime.now()})
    except Exception:
        pass  # 非關鍵更新

    return {
        "status": "found",
        "similarity": best_match["similarity"],
        "policy": best_match,
    }


def save_policy_to_memory(
    natural_language_query: str,
    policy_code: str,
    source: str,
    author: str = "user",
    policy_id: Optional[str] = None,
) -> dict:
    """
    將新策略或現有策略的新版本儲存到 Firestore。
    """
    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    now = datetime.datetime.now()
    embedding_list = _get_embedding(natural_language_query)

    if not embedding_list:
        return {
            "status": "error",
            "message": "無法為策略產生嵌入。",
        }

    new_version = 1

    if policy_id:
        # 檢查現有版本
        existing_versions = list(
            db.collection(COLLECTION_NAME).where("policy_id", "==", policy_id).stream()
        )
        if existing_versions:
            versions = [d.get("version") for d in existing_versions if d.get("version")]
            if versions:
                new_version = max(versions) + 1
        else:
            # 提供了 ID 但找不到？視為新的還是錯誤？讓我們將其視為具有該 ID 的新項目。
            pass
    else:
        policy_id = str(uuid.uuid4())

    doc_data = {
        "policy_id": policy_id,
        "version": new_version,
        "query": natural_language_query,
        "embedding": Vector(embedding_list),
        "code": policy_code,
        "source": source,
        "author": author,
        "last_used": now,
        "created_at": now,
        "ratings": [],
        "feedback": [],
    }

    try:
        # 為每個版本使用一個新文件
        db.collection(COLLECTION_NAME).add(doc_data)
        return {
            "status": "success",
            "message": f"策略已儲存為版本 {new_version}，ID 為 {policy_id}。",
            "policy_id": policy_id,
            "version": new_version,
        }
    except Exception as e:
        return {"status": "error", "message": f"儲存策略失敗：{e}"}


def list_policy_versions(policy_id: str) -> dict:
    """從 Firestore 列出給定策略 ID 的所有可用版本。"""
    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    try:
        docs = (
            db.collection(COLLECTION_NAME).where("policy_id", "==", policy_id).stream()
        )
        versions = []
        for doc in docs:
            versions.append(_policy_to_dict(doc))

        if not versions:
            return {
                "status": "not_found",
                "message": f"找不到 ID 為 '{policy_id}' 的策略。",
            }

        versions.sort(key=lambda p: p["version"], reverse=True)
        return {"status": "success", "versions": versions}
    except Exception as e:
        return {"status": "error", "message": f"列出版本時發生錯誤：{e}"}


def get_policy_by_id(policy_id: str, version: int) -> dict:
    """從 Firestore 依 ID 檢索特定版本的策略。"""
    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    try:
        docs = list(
            db.collection(COLLECTION_NAME)
            .where("policy_id", "==", policy_id)
            .where("version", "==", int(version))
            .limit(1)
            .stream()
        )

        if not docs:
            return {
                "status": "not_found",
                "message": f"找不到 ID 為 '{policy_id}' 且版本為 '{version}' 的策略。",
            }

        policy = _policy_to_dict(docs[0])

        # 更新 last_used
        docs[0].reference.update({"last_used": datetime.datetime.now()})

        return {"status": "success", "policy": policy}

    except Exception as e:
        return {"status": "error", "message": f"檢索策略時發生錯誤：{e}"}


def prune_memory(days_to_keep: int = 30) -> dict:
    """移除在過去 `days_to_keep` 天內未使用的策略。"""
    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)

    try:
        # 查詢在截止日期之前存取的策略
        # 注意：需要在 'last_used' 上建立索引
        docs = (
            db.collection(COLLECTION_NAME).where("last_used", "<", cutoff_date).stream()
        )

        deleted_count = 0
        batch = db.batch()

        for doc in docs:
            batch.delete(doc.reference)
            deleted_count += 1
            if deleted_count % 400 == 0:  # 每 400 個提交一次批次
                batch.commit()
                batch = db.batch()

        if deleted_count % 400 != 0:
            batch.commit()

        return {
            "status": "success",
            "message": f"已刪除 {deleted_count} 個舊策略。",
        }
    except Exception as e:
        return {"status": "error", "message": f"刪除記憶體時發生錯誤：{e}"}


def rate_policy(
    policy_id: str, version: int, rating: int, feedback: Optional[str] = None
) -> dict:
    """在 Firestore 中對策略進行評分並新增回饋。"""
    if not 1 <= rating <= 5:
        return {"status": "error", "message": "評分必須介於 1 到 5 之間。"}

    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    try:
        docs = list(
            db.collection(COLLECTION_NAME)
            .where("policy_id", "==", policy_id)
            .where("version", "==", int(version))
            .limit(1)
            .stream()
        )

        if not docs:
            return {
                "status": "not_found",
                "message": f"找不到 ID 為 '{policy_id}' 且版本為 '{version}' 的策略。",
            }

        doc_ref = docs[0].reference

        # 以原子方式更新陣列
        updates = {"ratings": firestore.ArrayUnion([rating])}
        if feedback:
            updates["feedback"] = firestore.ArrayUnion([feedback])

        doc_ref.update(updates)

        return {"status": "success", "message": "感謝您的回饋！"}

    except Exception as e:
        return {"status": "error", "message": f"提交評分時發生錯誤：{e}"}


def log_policy_execution(
    policy_id: str,
    version: int,
    status: str,
    source: str,
    violations: Optional[List[Dict[str, Any]]] = None,
    summary: str = "",
) -> dict:
    """
    將策略的執行記錄到 Firestore 並更新匯總統計資料。

    Args:
        violations: 違規物件的列表。如果提供，將從中提取 'violation_count' 和 'violated_resources'。
    """
    if not db:
        return {
            "status": "success",
            "message": "記憶庫已停用。未記錄執行。",
        }

    now = datetime.datetime.now()

    violation_count = len(violations) if violations else 0

    # 提取唯一的違規資源
    violated_resources = set()
    if violations:
        for v in violations:
            # 從通用欄位中提取資源識別碼，並提供備用方案
            res_name = (
                v.get("resource_name")
                or v.get("table_name")
                or v.get("asset_name")
                or v.get("dataset_name")
            )
            if res_name:
                violated_resources.add(str(res_name))

    # 1. 建立執行日誌
    execution_data = {
        "policy_id": policy_id,
        "version": version,
        "timestamp": now,
        "status": status,  # 'success', 'failure', 'violations_found'
        "violation_count": violation_count,
        "source": source,
        "summary": summary,
        "violated_resources": list(violated_resources),  # 儲存為陣列以便查詢
    }

    try:
        # 新增至 'policy_executions' 集合
        db.collection(FIRESTORE_COLLECTION_EXECUTIONS).add(execution_data)

        # 2. 更新策略文件上的匯總統計資料
        # 尋找要更新的特定策略版本文件
        docs = list(
            db.collection(COLLECTION_NAME)
            .where("policy_id", "==", policy_id)
            .where("version", "==", int(version))
            .limit(1)
            .stream()
        )

        if docs:
            doc_ref = docs[0].reference
            updates = {"total_runs": firestore.Increment(1), "last_run": now}

            if status == "violations_found":
                updates["total_violations_detected"] = firestore.Increment(
                    violation_count
                )

            if status == "failure":
                updates["last_failure"] = now

            doc_ref.update(updates)

        return {"status": "success", "message": "已記錄執行。"}

    except Exception as e:
        logging.error(f"記錄執行失敗：{e}")
        return {"status": "error", "message": f"記錄執行失敗：{e}"}


def analyze_execution_history(
    query_type: str = "summary",
    days: int = 30,
    resource_name: Optional[str] = None,
) -> dict:
    """
    對策略執行歷史記錄執行進階分析。

    Args:
        query_type: 分析類型：'summary'、'top_violations'、'resource_search'、'top_violated_resources'。
        days: 要分析的過去天數。
        resource_name: (用於 'resource_search') 要檢查的資源名稱。
    """
    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    # 確保 cutoff_date 是時區感知的 (UTC)，以符合 Firestore 時間戳記
    cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=days
    )

    try:
        if query_type == "resource_search":
            if not resource_name:
                return {
                    "status": "error",
                    "message": "resource_search 需要 resource_name。",
                }

            # 搜尋策略：擷取最近的日誌並在 Python 中執行不區分大小寫的子字串比對。
            # Firestore 'array-contains' 需要完全相符，不支援部分名稱
            # (例如 'quarterly_earnings' 找不到 'project.dataset.quarterly_earnings')。

            query = db.collection(FIRESTORE_COLLECTION_EXECUTIONS).where(
                "timestamp", ">=", cutoff_date
            )
            # 為了效率，按時間戳記降序排序
            query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)

            results = query.stream()

            matches = []
            resource_name_lower = resource_name.lower()

            for doc in results:
                data = doc.to_dict()
                violated_resources = data.get("violated_resources", [])

                # 略過沒有記錄違規的記錄
                if not violated_resources:
                    continue

                # 檢查是否有任何違規資源字串包含搜尋詞
                # 為了效率，我們使用產生器運算式
                if any(
                    resource_name_lower in str(r).lower() for r in violated_resources
                ):
                    if "timestamp" in data and isinstance(
                        data["timestamp"], datetime.datetime
                    ):
                        data["timestamp"] = data["timestamp"].isoformat()
                    matches.append(data)

            matches.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # 使用策略查詢豐富相符項目
            policy_cache = {}

            for m in matches:
                pid = m.get("policy_id")
                ver = m.get("version")
                if not pid or ver is None:
                    continue

                cache_key = (pid, ver)
                if cache_key not in policy_cache:
                    # 擷取策略以取得自然語言查詢
                    try:
                        docs = list(
                            db.collection(COLLECTION_NAME)
                            .where("policy_id", "==", pid)
                            .where("version", "==", int(ver))
                            .limit(1)
                            .stream()
                        )
                        if docs:
                            policy_cache[cache_key] = docs[0].to_dict().get("query")
                        else:
                            policy_cache[cache_key] = None
                    except Exception:
                        policy_cache[cache_key] = None

                if policy_cache[cache_key]:
                    m["policy_query"] = policy_cache[cache_key]

            return {"status": "success", "data": matches}

        elif query_type == "top_violations":
            # 從 *policies* 集合（預先匯總）按策略匯總總違規數
            # 或從執行日誌匯總？
            # 在 'policies' 文件上預先匯總是更快的。

            # 我們掃描最近使用/更新的策略？還是全部？
            # 讓我們掃描所有策略，按 total_violations_detected 降序排序。
            query = (
                db.collection(COLLECTION_NAME)
                .order_by(
                    "total_violations_detected", direction=firestore.Query.DESCENDING
                )
                .limit(10)
            )
            results = query.stream()

            top_policies = []
            for doc in results:
                p = _policy_to_dict(doc)
                if p.get("total_violations_detected", 0) > 0:
                    top_policies.append(
                        {
                            "policy_id": p.get("policy_id"),
                            "query": p.get("query"),
                            "total_violations": p.get("total_violations_detected"),
                            "last_run": p.get("last_run"),
                        }
                    )

            return {"status": "success", "data": top_policies}

        elif query_type == "top_violated_resources":
            # 掃描過去 X 天的執行以計算資源違規次數
            query = db.collection(FIRESTORE_COLLECTION_EXECUTIONS).where(
                "timestamp", ">=", cutoff_date
            )
            results = query.stream()

            resource_counts: dict[str, int] = {}

            for doc in results:
                data = doc.to_dict()
                # 在此執行中違反策略的資源列表
                violated_resources = data.get("violated_resources", [])

                for res in violated_resources:
                    res_str = str(res)
                    resource_counts[res_str] = resource_counts.get(res_str, 0) + 1

            # 按計數降序排序
            sorted_resources = sorted(
                resource_counts.items(), key=lambda item: item[1], reverse=True
            )

            # 格式化前 10 名
            top_resources = [
                {"resource_name": r[0], "total_violations": r[1]}
                for r in sorted_resources[:10]
            ]

            return {"status": "success", "data": top_resources}

        else:  # "summary" 或預設
            # 返回每日執行次數和違規次數的計數
            # 掃描過去 X 天的執行
            query = db.collection(FIRESTORE_COLLECTION_EXECUTIONS).where(
                "timestamp", ">=", cutoff_date
            )
            results = query.stream()

            daily_stats = {}

            for doc in results:
                data = doc.to_dict()
                ts = data.get("timestamp")
                if not ts:
                    continue

                day_str = ts.strftime("%Y-%m-%d")
                if day_str not in daily_stats:
                    daily_stats[day_str] = {"executions": 0, "violations_detected": 0}

                daily_stats[day_str]["executions"] += 1
                daily_stats[day_str]["violations_detected"] += data.get(
                    "violation_count", 0
                )

            return {"status": "success", "data": daily_stats}

    except Exception as e:
        return {"status": "error", "message": f"分析失敗：{e}"}


def get_execution_history(
    days: int = 7, status: Optional[str] = None, policy_id: Optional[str] = None
) -> dict:
    """
    從 Firestore 檢索策略執行歷史記錄。

    Args:
        days: 要檢索的過去天數（預設 7）。
        status: 按狀態篩選（'success'、'failure'、'violations_found'）。
        policy_id: 按特定策略 ID 篩選。
    """
    if not db:
        return {
            "status": "error",
            "message": "記憶庫已停用。若要啟用長期程序記憶，請在 .env 中設定 ENABLE_MEMORY_BANK=True 並設定 Firestore。詳情請參閱 docs/MEMORY_INTEGRATION.md。",
        }

    # 確保 cutoff_date 是時區感知的 (UTC)，以符合 Firestore 時間戳記
    cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=days
    )

    try:
        # 僅按時間戳記查詢以利用預設的單一欄位索引。
        # 複合篩選器（例如，時間戳記 + 狀態）需要在 Firestore 中自訂索引。
        # 為了維持「開箱即用」的可用性而無需手動設定主控台，
        # 我們檢索最近的歷史記錄並在記憶體中進行篩選。
        query = db.collection(FIRESTORE_COLLECTION_EXECUTIONS).where(
            "timestamp", ">=", cutoff_date
        )

        # 按時間戳記降序排序
        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)

        results = query.stream()
        history = []

        for doc in results:
            data = doc.to_dict()

            # 記憶體中篩選
            if status and data.get("status") != status:
                continue

            if policy_id and data.get("policy_id") != policy_id:
                continue

            # 序列化時間戳記
            if "timestamp" in data:
                data["timestamp"] = data["timestamp"].isoformat()
            history.append(data)

        if not history:
            return {
                "status": "success",
                "history": [],
                "message": "找不到此條件的執行歷史記錄。",
            }

        return {"status": "success", "history": history}

    except Exception as e:
        return {"status": "error", "message": f"檢索歷史記錄時發生錯誤：{e}"}
