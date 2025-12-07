# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Policy Navigator 核心測試 (`tests/test_core.py`)

此部分涵蓋 Policy Navigator 工具和實用程式的單元測試與整合測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **元數據模式生成** | **TC-META-001** | 測試模式定義 | None | 1. 呼叫 `MetadataSchema.get_schema()`<br>2. 驗證返回的模式結構 | None | 返回包含 department, policy_type, effective_date 的字典 |
| **元數據模式生成** | **TC-META-002** | 測試元數據建立 | None | 1. 呼叫 `MetadataSchema.create_metadata`<br>2. 驗證返回的列表和欄位值 | department="HR", policy_type="handbook", ... | 返回包含正確鍵值對的列表 |
| **元數據模式生成** | **TC-META-003** | 測試 HR 元數據預設值 | None | 1. 呼叫 `MetadataSchema.hr_metadata()` | None | 返回 department 為 "HR" 的元數據列表 |
| **元數據模式生成** | **TC-META-004** | 測試 IT 元數據預設值 | None | 1. 呼叫 `MetadataSchema.it_metadata()` | None | 返回 department 為 "IT" 的元數據列表 |
| **元數據模式生成** | **TC-META-005** | 測試行為準則元數據預設值 | None | 1. 呼叫 `MetadataSchema.code_of_conduct_metadata()` | None | 返回 policy_type 為 "code_of_conduct" 的元數據列表 |
| **元數據模式生成** | **TC-META-006** | 測試建立單一元數據過濾器 | None | 1. 呼叫 `MetadataSchema.build_metadata_filter(department="HR")` | department="HR" | 返回包含 "department=HR" 的過濾字串 |
| **元數據模式生成** | **TC-META-007** | 測試建立多個元數據過濾器 | None | 1. 呼叫 `MetadataSchema.build_metadata_filter` 帶入多個參數 | department="HR", policy_type="handbook", ... | 返回包含所有條件且用 AND 連接的字串 |
| **元數據模式生成** | **TC-META-008** | 測試建立空白元數據過濾器 | None | 1. 呼叫 `MetadataSchema.build_metadata_filter()` | None | 返回空字串 |
| **實用程式功能** | **TC-UTIL-001** | 測試取得範例策略目錄 | None | 1. 呼叫 `get_sample_policies_dir()` | None | 返回包含 "sample_policies" 的路徑字串 |
| **實用程式功能** | **TC-UTIL-002** | 測試 HR 策略的儲存區名稱偵測 | None | 1. 呼叫 `get_store_name_for_policy("hr_handbook.md")` | "hr_handbook.md" | 返回包含 "hr" 的儲存區名稱 |
| **實用程式功能** | **TC-UTIL-003** | 測試 IT 策略的儲存區名稱偵測 | None | 1. 呼叫 `get_store_name_for_policy("it_security_policy.pdf")` | "it_security_policy.pdf" | 返回包含 "it" 的儲存區名稱 |
| **實用程式功能** | **TC-UTIL-004** | 測試遠端工作策略的儲存區名稱偵測 | None | 1. 呼叫 `get_store_name_for_policy("remote_work_policy.md")` | "remote_work_policy.md" | 返回包含 "hr" 的儲存區名稱 |
| **實用程式功能** | **TC-UTIL-005** | 測試行為準則的儲存區名稱偵測 | None | 1. 呼叫 `get_store_name_for_policy("code_of_conduct.md")` | "code_of_conduct.md" | 返回包含 "safety" 或 "general" 的儲存區名稱 |
| **實用程式功能** | **TC-UTIL-006** | 測試格式化成功回應 | None | 1. 呼叫 `format_response` 帶入 success 狀態 | "success", "Operation completed", ... | 返回包含 "✓" 和訊息的字串 |
| **實用程式功能** | **TC-UTIL-007** | 測試格式化錯誤回應 | None | 1. 呼叫 `format_response` 帶入 error 狀態 | "error", "Operation failed", ... | 返回包含 "✗" 和訊息的字串 |
| **實用程式功能** | **TC-UTIL-008** | 測試格式化警告回應 | None | 1. 呼叫 `format_response` 帶入 warning 狀態 | "warning", "Check this", ... | 返回包含 "⚠" 和訊息的字串 |
| **列舉定義** | **TC-ENUM-001** | 測試 PolicyDepartment 列舉 | None | 1. 存取 `PolicyDepartment` 成員值 | None | 值與預期字串 ("HR", "IT", ...) 相符 |
| **列舉定義** | **TC-ENUM-002** | 測試 PolicyType 列舉 | None | 1. 存取 `PolicyType` 成員值 | None | 值與預期字串 ("handbook", "procedure", ...) 相符 |
| **配置** | **TC-CONF-001** | 測試配置是否有 API 金鑰設定 | None | 1. 檢查 `Config` 類別屬性 | None | 存在 GOOGLE_API_KEY, DEFAULT_MODEL, LOG_LEVEL |
| **配置** | **TC-CONF-002** | 測試取得所有儲存區名稱 | None | 1. 呼叫 `Config.get_store_names()` | None | 返回包含 "hr", "it", "legal", "safety" 的字典 |
| **StoreManager 整合** | **TC-STORE-001** | 測試列出儲存區返回列表 | StoreManager 實例 | 1. 呼叫 `store_manager.list_stores()` | None | 返回列表類型 |
| **StoreManager 整合** | **TC-STORE-002** | 測試使用模擬 API 的 list_documents 方法 | Mock API | 1. 模擬 API 回應<br>2. 呼叫 `store_manager.list_documents` | 'fileSearchStores/123' | 返回包含文件資訊的列表 |
| **StoreManager 整合** | **TC-STORE-003** | 測試使用模擬 API 的 find_document_by_display_name | Mock API | 1. 模擬 API 回應<br>2. 呼叫 `find_document_by_display_name` | 'fileSearchStores/123', 'policy1.md' | 返回正確的文件名稱 |
| **StoreManager 整合** | **TC-STORE-004** | 測試當文件未找到時的 find_document_by_display_name | Mock API | 1. 模擬 API 空回應<br>2. 呼叫 `find_document_by_display_name` | 'fileSearchStores/123', 'nonexistent.md' | 返回 None |
| **StoreManager 整合** | **TC-STORE-005** | 測試使用模擬 API 的 delete_document 方法 | Mock API | 1. 模擬 API 回應<br>2. 呼叫 `store_manager.delete_document` | 'fileSearchStores/123/documents/abc' | 返回 True |
| **StoreManager 整合** | **TC-STORE-006** | 測試當文件不存在時的 upsert (新上傳) | Mock API | 1. 模擬文件不存在<br>2. 呼叫 `upsert_file_to_store` | temp_file, 'fileSearchStores/123', 'test.md' | 只呼叫 upload，不呼叫 delete，返回 True |
| **StoreManager 整合** | **TC-STORE-007** | 測試當文件存在時的 upsert (替換) | Mock API | 1. 模擬文件存在<br>2. 呼叫 `upsert_file_to_store` | temp_file, 'fileSearchStores/123', 'test.md' | 呼叫 delete 後呼叫 upload，返回 True |
| **PolicyTools 整合** | **TC-TOOL-001** | 測試搜尋返回格式正確的字典 | PolicyTools 實例 | 1. 呼叫 `policy_tools.search_policies` (目前為 pass) | None | 驗證返回格式 (目前略過) |
