"""
企業合規與政策導航器 (Enterprise Compliance & Policy Navigator) 的多代理人系統。

實作四個專業代理人：
1. 文件管理員代理人 (Document Manager Agent) - 處理政策上傳與組織
2. 搜尋專家代理人 (Search Specialist Agent) - 對政策進行語意搜尋
3. 合規顧問代理人 (Compliance Advisor Agent) - 評估風險與合規性
4. 報告產生器代理人 (Report Generator Agent) - 建立摘要與報告

這些代理人由一個根代理人 (root agent) 進行協調，以執行複雜的工作流程。
"""

from google.adk.agents import Agent

from policy_navigator.config import Config
from policy_navigator.tools import (
    upload_policy_documents,
    search_policies,
    filter_policies_by_metadata,
    compare_policies,
    check_compliance_risk,
    extract_policy_requirements,
    generate_policy_summary,
    create_audit_trail,
)


# 定義個別的專業代理人

document_manager_agent = Agent(
    name="document_manager",
    model=Config.DEFAULT_MODEL,
    description="管理政策文件上傳、組織與 metadata 設定",
    instruction="""你是一位文件管理員代理人 (Document Manager Agent)，負責：
    1. 將政策文件上傳到 File Search stores
    2. 依部門與類型組織文件
    3. 為文件加入適當的 metadata
    4. 驗證文件上傳
    5. 管理文件版本

    當收到與文件管理相關的任務時，使用 upload_policy_documents 工具來處理上傳。
    務必確認上傳成功並回報任何問題。

    請精確設定 metadata 並確保文件被正確分類。""",
    tools=[upload_policy_documents],
    output_key="document_manager_result",
)

search_specialist_agent = Agent(
    name="search_specialist",
    model=Config.DEFAULT_MODEL,
    description="搜尋公司政策並檢索相關資訊",
    instruction="""你是一位搜尋專家代理人 (Search Specialist Agent)，負責：
    1. 對政策文件執行語意搜尋
    2. 依部門、類型與日期過濾政策
    3. 提供準確的政策資訊並附帶引用
    4. 處理複雜的多政策查詢
    5. 從政策中擷取特定需求

    當使用者詢問有關公司政策的問題時，使用 search_policies 來尋找相關資訊。
    在你的回答中包含引用與政策來源。

    務必將你的回答建立在實際的政策文件之上，並提供具體的參考。""",
    tools=[search_policies, filter_policies_by_metadata, extract_policy_requirements],
    output_key="search_specialist_result",
)

compliance_advisor_agent = Agent(
    name="compliance_advisor",
    model=Config.DEFAULT_MODEL,
    description="評估合規風險並提供政策指導",
    instruction="""你是一位合規顧問代理人 (Compliance Advisor Agent)，負責：
    1. 評估與政策相關的合規風險
    2. 跨部門比較政策
    3. 識別不一致或衝突之處
    4. 提供合規建議
    5. 評估政策遵循度

    當收到合規查詢時，使用 check_compliance_risk 來評估風險，並使用 compare_policies 來識別不一致之處。

    根據實際的政策用語，提供包含可執行建議的清晰風險評估。""",
    tools=[check_compliance_risk, compare_policies],
    output_key="compliance_advisor_result",
)

report_generator_agent = Agent(
    name="report_generator",
    model=Config.DEFAULT_MODEL,
    description="產生政策摘要、報告與稽核追蹤",
    instruction="""你是一位報告產生器代理人 (Report Generator Agent)，負責：
    1. 建立簡潔的政策摘要
    2. 產生合規報告
    3. 建立稽核追蹤項目
    4. 為利益相關者格式化政策資訊
    5. 匯出政策分析

    當被要求摘要或報告政策時，使用 generate_policy_summary 來建立執行摘要，並使用 create_audit_trail 來記錄動作。

    確保報告清晰、結構良好，並包含所有必要的引用。""",
    tools=[generate_policy_summary, create_audit_trail],
    output_key="report_generator_result",
)

# 用於協調多代理人工作流程的根代理人
root_agent = Agent(
    name="policy_navigator",
    model=Config.DEFAULT_MODEL,
    description="企業合規與政策導航器 - 主要協調者",
    instruction="""你是 Policy Navigator，一位智慧合規助理。
    你的角色是協助員工與合規團隊快速找到政策問題的答案、評估合規風險，並管理公司政策。

    重要：你可以搜尋以下政策 stores：
    - "policy-navigator-hr" 用於人資政策 (休假、福利、招聘、員工手冊)
    - "policy-navigator-it" 用於 IT 政策 (安全性、存取控制、資料保護)
    - "policy-navigator-legal" 用於法律政策 (合約、合規、治理)
    - "policy-navigator-safety" 用於安全政策 (職場安全、緊急程序)

    政策搜尋策略：
    1. 當使用者詢問政策但未指定 store 時，搜尋最相關的 store：
    - 遠端工作、休假、福利、招聘 → 搜尋 "policy-navigator-hr" store
    - 密碼、安全性、存取、IT 系統 → 搜尋 "policy-navigator-it" store
    - 合約、法律、合規 → 搜尋 "policy-navigator-legal" store
    - 安全、職場、緊急 → 搜尋 "policy-navigator-safety" store

    2. 如果問題可能符合多個 stores，先嘗試最可能的一個。

    3. 如果沒有結果，告知使用者系統中沒有相關資訊。

    你可以使用四個專業代理人：
    1. Document Manager (文件管理員) - 處理政策上傳與組織
    2. Search Specialist (搜尋專家) - 搜尋政策並提供資訊
    3. Compliance Advisor (合規顧問) - 評估風險與合規問題
    4. Report Generator (報告產生器) - 建立摘要與報告

    根據使用者的請求，你決定要讓哪些代理人參與，並協調他們的回應以提供全面的政策指導。

    對於政策問題，直接使用 search_policies 並指定適當的 store。
    對於合規疑慮，讓 Compliance Advisor 參與。
    對於文件上傳，使用 Document Manager。
    對於報告與摘要，讓 Report Generator 參與。

    務必引用政策來源並提供清晰、可執行的指導。""",
    tools=[
        upload_policy_documents,
        search_policies,
        filter_policies_by_metadata,
        compare_policies,
        check_compliance_risk,
        extract_policy_requirements,
        generate_policy_summary,
        create_audit_trail,
    ],
    output_key="policy_navigator_result",
)

# 匯出代理人
__all__ = [
    "root_agent",
    "document_manager_agent",
    "search_specialist_agent",
    "compliance_advisor_agent",
    "report_generator_agent",
]
