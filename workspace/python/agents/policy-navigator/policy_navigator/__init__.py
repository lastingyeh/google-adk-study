"""
Policy Navigator - 企業合規與政策導航器
教學 37：使用 Gemini File Search API 的 Google ADK

一個生產就緒的多代理人系統，使用 Google Gemini File Search API 進行原生的檢索增強生成 (RAG)，
用於搜尋和分析公司政策。
"""

__version__ = "0.1.0"
__author__ = "Google ADK Training"
__description__ = "Enterprise Compliance & Policy Navigator using Gemini File Search"

# 從 agent 模組匯入根代理人
from policy_navigator.agent import root_agent

# 從 tools 模組匯入各種政策處理工具
from policy_navigator.tools import (
    upload_policy_documents,      # 上傳政策文件
    search_policies,              # 搜尋政策
    filter_policies_by_metadata,  # 依 metadata 過濾政策
    compare_policies,             # 比較政策
    check_compliance_risk,        # 檢查合規風險
    extract_policy_requirements,  # 擷取政策需求
    generate_policy_summary,      # 產生政策摘要
    create_audit_trail,           # 建立稽核追蹤
)

# 從 stores 模組匯入 store 管理功能
from policy_navigator.stores import (
    create_policy_store,          # 建立政策 store
    get_store_info,               # 取得 store 資訊
    list_stores,                  # 列出所有 stores
    delete_store,                 # 刪除 store
)

# 定義公開匯出的成員
__all__ = [
    "root_agent",
    "upload_policy_documents",
    "search_policies",
    "filter_policies_by_metadata",
    "compare_policies",
    "check_compliance_risk",
    "extract_policy_requirements",
    "generate_policy_summary",
    "create_audit_trail",
    "create_policy_store",
    "get_store_info",
    "list_stores",
    "delete_store",
]
