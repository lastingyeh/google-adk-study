"""
Policy Navigator 的核心工具。

實作 File Search 整合工具，用於上傳、搜尋、
過濾、分析和回報政策文件。
"""

import os
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types
from loguru import logger

from policy_navigator.config import Config
from policy_navigator.metadata import MetadataSchema
from policy_navigator.stores import StoreManager


class PolicyTools:
    """政策管理與分析的工具集合。"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 PolicyTools。

        Args:
            api_key: Google API 金鑰 (若未提供則使用 Config.GOOGLE_API_KEY)
        """
        self.api_key = api_key or Config.GOOGLE_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        self.store_manager = StoreManager(api_key)

    def upload_policy_documents(
        self,
        file_paths: str,
        store_name: str,
    ) -> Dict[str, Any]:
        """
        以上傳並更新 (upsert) 的語意上傳政策文件到 File Search Store。

        如果具有相同名稱的文件已存在，它將被取代。

        Args:
            file_paths: 以逗號分隔的要上傳檔案路徑
            store_name: 目標 File Search Store 名稱

        Returns:
            dict 包含狀態、上傳數量與詳細資訊
        """
        # 解析以逗號分隔的檔案路徑
        paths = [p.strip() for p in file_paths.split(",")]
        try:
            logger.info(f"正在上傳 {len(paths)} 份文件到 {store_name}...")

            uploaded = 0
            failed = 0
            details = []

            for file_path in paths:
                if not os.path.exists(file_path):
                    logger.error(f"找不到檔案: {file_path}")
                    failed += 1
                    details.append({"file": file_path, "status": "error", "reason": "找不到檔案"})
                    continue

                try:
                    display_name = os.path.basename(file_path)

                    # 使用 upsert 代替 upload 以取代現有文件
                    if self.store_manager.upsert_file_to_store(
                        file_path, store_name, display_name, None
                    ):
                        uploaded += 1
                        details.append(
                            {"file": file_path, "status": "success", "mode": "upsert"}
                        )
                    else:
                        failed += 1
                        details.append(
                            {"file": file_path, "status": "error", "reason": "Upsert 失敗"}
                        )

                except Exception as e:
                    logger.error(f"Upsert {file_path} 失敗: {str(e)}")
                    failed += 1
                    details.append(
                        {"file": file_path, "status": "error", "reason": str(e)}
                    )

            return {
                "status": "success" if uploaded > 0 else "error",
                "uploaded": uploaded,
                "failed": failed,
                "total": len(paths),
                "details": details,
                "report": f"成功更新 (Upserted) {uploaded}/{len(paths)} 份文件",
            }

        except Exception as e:
            logger.error(f"上傳失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"上傳文件失敗: {str(e)}",
            }

    def search_policies(
        self,
        query: str,
        store_name: str,
        metadata_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        使用 File Search 對政策進行語意搜尋。

        Args:
            query: 搜尋查詢 (使用者關於政策的問題)
            store_name: File Search Store 顯示名稱或完整名稱
            metadata_filter: 選擇性的 AIP-160 metadata 過濾器

        Returns:
            dict 包含答案、引用和 metadata
        """
        try:
            logger.info(f"正在搜尋政策: {query}")

            # 如果 store 名稱是顯示名稱，則進行解析
            full_store_name = store_name
            if not store_name.startswith("fileSearchStores/"):
                resolved_name = self.store_manager.get_store_by_display_name(store_name)
                if not resolved_name:
                    return {
                        "status": "error",
                        "error": f"找不到 File Search store '{store_name}'",
                        "report": f"找不到 Store '{store_name}'。請先使用 demo_upload.py 建立它",
                    }
                full_store_name = resolved_name

            # 建構 File Search 工具設定
            file_search_tool_config = {
                "file_search_store_names": [full_store_name]
            }
            if metadata_filter:
                file_search_tool_config["metadata_filter"] = metadata_filter

            # 執行搜尋
            try:
                response = self.client.models.generate_content(
                    model=Config.DEFAULT_MODEL,
                    contents=query,
                    config=types.GenerateContentConfig(
                        tools=[{
                            "file_search": file_search_tool_config
                        }]
                    ),
                )
            except Exception as e:
                # 如果 File Search stores 不存在，提供有用的訊息
                if "not found" in str(e).lower() or "fileSearchStore" in str(e):
                    logger.warning(f"File Search store '{store_name}' 找不到。請先使用 client.file_search_stores.create() 建立它")
                raise

            # 擷取引用 (citations)
            citations = []
            grounding = response.candidates[0].grounding_metadata if response.candidates else None

            if grounding and hasattr(grounding, "grounding_chunks"):
                for chunk in grounding.grounding_chunks:
                    citations.append({
                        "source": str(chunk),
                        "text": getattr(chunk, "text", "")[:200] + "..."
                    })

            return {
                "status": "success",
                "answer": response.text,
                "citations": citations,
                "source_count": len(citations),
                "report": f"找到答案並包含 {len(citations)} 個來源",
            }

        except Exception as e:
            logger.error(f"搜尋失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"搜尋失敗: {str(e)}",
            }

    def filter_policies_by_metadata(
        self,
        store_name: str,
        department: Optional[str] = None,
        policy_type: Optional[str] = None,
        sensitivity: Optional[str] = None,
        jurisdiction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        依 metadata 屬性過濾政策。

        Args:
            store_name: File Search Store 顯示名稱或完整名稱
            department: 依部門過濾 (HR, IT, Legal, Safety)
            policy_type: 依政策類型過濾 (handbook, procedure, etc.)
            sensitivity: 依敏感度過濾 (public, internal, confidential)
            jurisdiction: 依管轄區過濾 (US, EU, etc.)

        Returns:
            dict 包含過濾後的政策查詢和使用的過濾器
        """
        try:
            # 如果 store 名稱是顯示名稱，則進行解析
            full_store_name = store_name
            if not store_name.startswith("fileSearchStores/"):
                resolved_name = self.store_manager.get_store_by_display_name(store_name)
                if not resolved_name:
                    return {
                        "status": "error",
                        "error": f"找不到 File Search store '{store_name}'",
                        "report": f"找不到 Store '{store_name}'。請先使用 demo_upload.py 建立它",
                    }
                full_store_name = resolved_name

            metadata_filter = MetadataSchema.build_metadata_filter(
                department=department,
                policy_type=policy_type,
                sensitivity=sensitivity,
                jurisdiction=jurisdiction,
            )

            logger.info(f"使用以下條件過濾政策: {metadata_filter}")

            # 執行過濾後的搜尋
            query = f"Show me all {policy_type or 'policies'} from {department or 'all departments'}"
            response = self.client.models.generate_content(
                model=Config.DEFAULT_MODEL,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[{
                        "file_search": {
                            "file_search_store_names": [full_store_name],
                            **({"metadata_filter": metadata_filter} if metadata_filter else {})
                        }
                    }]
                ),
            )

            return {
                "status": "success",
                "query": query,
                "filter": metadata_filter,
                "results": response.text,
                "report": "過濾後的政策檢索成功",
            }

        except Exception as e:
            logger.error(f"過濾失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"過濾失敗: {str(e)}",
            }

    def compare_policies(
        self,
        query: str,
        store_names: List[str],
    ) -> Dict[str, Any]:
        """
        跨多個文件或 store 比較政策。

        Args:
            query: 比較查詢 (例如："比較休假政策")
            store_names: File Search Store 顯示名稱或完整名稱的列表

        Returns:
            dict 包含比較結果與分析
        """
        try:
            logger.info(f"正在比較政策: {query}")

            # 解析所有 store 名稱
            full_store_names = []
            for store_name in store_names:
                if store_name.startswith("fileSearchStores/"):
                    full_store_names.append(store_name)
                else:
                    resolved_name = self.store_manager.get_store_by_display_name(store_name)
                    if not resolved_name:
                        return {
                            "status": "error",
                            "error": f"找不到 File Search store '{store_name}'",
                            "report": f"找不到 Store '{store_name}'。請先使用 demo_upload.py 建立它",
                        }
                    full_store_names.append(resolved_name)

            response = self.client.models.generate_content(
                model=Config.DEFAULT_MODEL,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[{
                        "file_search": {
                            "file_search_store_names": full_store_names
                        }
                    }]
                ),
            )

            return {
                "status": "success",
                "query": query,
                "comparison": response.text,
                "stores_compared": len(store_names),
                "report": "政策比較完成",
            }

        except Exception as e:
            logger.error(f"比較失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"比較失敗: {str(e)}",
            }

    def check_compliance_risk(
        self,
        query: str,
        store_name: str,
    ) -> Dict[str, Any]:
        """
        檢查合規性並根據政策評估風險。

        Args:
            query: 風險評估查詢
            store_name: File Search Store 顯示名稱或完整名稱

        Returns:
            dict 包含風險評估與建議
        """
        try:
            logger.info(f"正在評估合規風險: {query}")

            # 如果 store 名稱是顯示名稱，則進行解析
            full_store_name = store_name
            if not store_name.startswith("fileSearchStores/"):
                resolved_name = self.store_manager.get_store_by_display_name(store_name)
                if not resolved_name:
                    return {
                        "status": "error",
                        "error": f"找不到 File Search store '{store_name}'",
                        "report": f"找不到 Store '{store_name}'。請先使用 demo_upload.py 建立它",
                    }
                full_store_name = resolved_name

            # 將合規背景資訊加入查詢
            compliance_query = f"""
            Based on company policies, assess the following compliance question:
            {query}

            Provide:
            1. Direct policy answer
            2. Risk level (Low/Medium/High)
            3. Specific policy references
            4. Recommendations for compliance
            """

            response = self.client.models.generate_content(
                model=Config.DEFAULT_MODEL,
                contents=compliance_query,
                config=types.GenerateContentConfig(
                    tools=[{
                        "file_search": {
                            "file_search_store_names": [full_store_name]
                        }
                    }]
                ),
            )

            return {
                "status": "success",
                "query": query,
                "assessment": response.text,
                "report": "合規風險評估完成",
            }

        except Exception as e:
            logger.error(f"風險評估失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"風險評估失敗: {str(e)}",
            }

    def extract_policy_requirements(
        self,
        query: str,
        store_name: str,
    ) -> Dict[str, Any]:
        """
        從政策中擷取特定需求。

        Args:
            query: 特定需求的查詢 (例如："密碼需求")
            store_name: File Search Store 顯示名稱或完整名稱

        Returns:
            dict 包含結構化格式的擷取需求
        """
        try:
            logger.info(f"正在擷取需求: {query}")

            # 如果 store 名稱是顯示名稱，則進行解析
            full_store_name = store_name
            if not store_name.startswith("fileSearchStores/"):
                resolved_name = self.store_manager.get_store_by_display_name(store_name)
                if not resolved_name:
                    return {
                        "status": "error",
                        "error": f"找不到 File Search store '{store_name}'",
                        "report": f"找不到 Store '{store_name}'。請先使用 demo_upload.py 建立它",
                    }
                full_store_name = resolved_name

            extraction_query = f"""
            擷取以下項目的具體要求：{query}

            以包含以下內容的結構化列表格式化：
            - 需求描述
            - 政策來源
            - 執行機制
            - 例外情況 (若有)
            """

            response = self.client.models.generate_content(
                model=Config.DEFAULT_MODEL,
                contents=extraction_query,
                config=types.GenerateContentConfig(
                    tools=[{
                        "file_search": {
                            "file_search_store_names": [full_store_name]
                        }
                    }]
                ),
            )

            return {
                "status": "success",
                "query": query,
                "requirements": response.text,
                "report": "需求擷取成功",
            }

        except Exception as e:
            logger.error(f"擷取失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"擷取失敗: {str(e)}",
            }

    def generate_policy_summary(
        self,
        query: str,
        store_name: str,
    ) -> Dict[str, Any]:
        """
        產生政策資訊的摘要。

        Args:
            query: 要摘要的主題 (例如："遠端工作福利")
            store_name: File Search Store 顯示名稱或完整名稱

        Returns:
            dict 包含摘要與重點
        """
        try:
            logger.info(f"正在產生摘要: {query}")

            # 如果 store 名稱是顯示名稱，則進行解析
            full_store_name = store_name
            if not store_name.startswith("fileSearchStores/"):
                resolved_name = self.store_manager.get_store_by_display_name(store_name)
                if not resolved_name:
                    return {
                        "status": "error",
                        "error": f"找不到 File Search store '{store_name}'",
                        "report": f"找不到 Store '{store_name}'。請先使用 demo_upload.py 建立它",
                    }
                full_store_name = resolved_name

            summary_query = f"""
            為以下主題建立簡潔的摘要：{query}

            包含：
            1. 重點 (3-5 點)
            2. 適用對象
            3. 流程或要求
            4. 重要注意事項

            保持簡潔且可執行。
            """

            response = self.client.models.generate_content(
                model=Config.DEFAULT_MODEL,
                contents=summary_query,
                config=types.GenerateContentConfig(
                    tools=[{
                        "file_search": {
                            "file_search_store_names": [full_store_name]
                        }
                    }]
                ),
            )

            return {
                "status": "success",
                "query": query,
                "summary": response.text,
                "report": "摘要產生成功",
            }

        except Exception as e:
            logger.error(f"摘要產生失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"摘要產生失敗: {str(e)}",
            }

    def create_audit_trail(
        self,
        action: str,
        user: str,
        query: str,
        result_summary: str,
    ) -> Dict[str, Any]:
        """
        為政策存取建立稽核追蹤項目。

        Args:
            action: 動作類型 (search, upload, update)
            user: 執行動作的使用者
            query: 查詢或動作詳細資訊
            result_summary: 結果摘要

        Returns:
            dict 包含稽核追蹤項目
        """
        try:
            from datetime import datetime

            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "user": user,
                "query": query,
                "result_summary": result_summary,
                "status": "logged",
            }

            logger.info(f"稽核追蹤已建立: {action} by {user}")

            return {
                "status": "success",
                "audit_entry": audit_entry,
                "report": "稽核追蹤項目已建立",
            }

        except Exception as e:
            logger.error(f"建立稽核追蹤失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": f"建立稽核追蹤失敗: {str(e)}",
            }


# 全域實例
_policy_tools: Optional[PolicyTools] = None


def _get_tools() -> PolicyTools:
    """取得或建立 PolicyTools 實例。"""
    global _policy_tools
    if _policy_tools is None:
        _policy_tools = PolicyTools()
    return _policy_tools


# 匯出工具函式
def upload_policy_documents(
    file_paths: str,
    store_name: str,
) -> Dict[str, Any]:
    """上傳政策文件到 File Search store。"""
    return _get_tools().upload_policy_documents(file_paths, store_name)


def search_policies(
    query: str,
    store_name: str,
    metadata_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """使用語意搜尋來搜尋政策。"""
    return _get_tools().search_policies(query, store_name, metadata_filter)


def filter_policies_by_metadata(
    store_name: str,
    department: Optional[str] = None,
    policy_type: Optional[str] = None,
    sensitivity: Optional[str] = None,
    jurisdiction: Optional[str] = None,
) -> Dict[str, Any]:
    """依 metadata 過濾政策。"""
    return _get_tools().filter_policies_by_metadata(
        store_name, department, policy_type, sensitivity, jurisdiction
    )


def compare_policies(
    query: str,
    store_names: List[str],
) -> Dict[str, Any]:
    """跨 stores 比較政策。"""
    return _get_tools().compare_policies(query, store_names)


def check_compliance_risk(
    query: str,
    store_name: str,
) -> Dict[str, Any]:
    """檢查合規性並評估風險。"""
    return _get_tools().check_compliance_risk(query, store_name)


def extract_policy_requirements(
    query: str,
    store_name: str,
) -> Dict[str, Any]:
    """從政策中擷取特定需求。"""
    return _get_tools().extract_policy_requirements(query, store_name)


def generate_policy_summary(
    query: str,
    store_name: str,
) -> Dict[str, Any]:
    """產生政策摘要。"""
    return _get_tools().generate_policy_summary(query, store_name)


def create_audit_trail(
    action: str,
    user: str,
    query: str,
    result_summary: str,
) -> Dict[str, Any]:
    """建立稽核追蹤項目。"""
    return _get_tools().create_audit_trail(action, user, query, result_summary)
