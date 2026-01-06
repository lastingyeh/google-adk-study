# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Dataplex 工具測試 (`tests/unit/test_dataplex.py`)

此部分涵蓋對 Dataplex 相關工具函數的單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Proto 轉換** | **TC-UNIT-DATAPLEX-001** | 測試將簡單的 proto 對象轉換為字典 | 無 | 1. 建立 Mock Proto<br>2. 呼叫 convert_proto_to_dict | proto={"key": "value"} | 返回相應的字典結構 |
| **Proto 轉換** | **TC-UNIT-DATAPLEX-002** | 測試將重複的 proto 對象（列表）轉換為字典 | 無 | 1. 建立 Mock Proto List<br>2. 呼叫 convert_proto_to_dict | proto=[{"a": 1}, {"b": 2}] | 返回相應的列表字典結構 |
| **Entry 轉換** | **TC-UNIT-DATAPLEX-003** | 測試將 Dataplex Entry 對象轉換為字典 | 無 | 1. 建立 Mock Entry<br>2. 呼叫 entry_to_dict | Mock Dataplex Entry Object | 返回包含所有屬性的字典結構 |

## 虛擬測試 (`tests/unit/test_dummy.py`)

此部分為佔位符測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **基礎檢查** | **TC-UNIT-DUMMY-001** | 佔位符測試 | 無 | 1. 執行斷言 | 無 | 1 == 1 |

## LLM 工具測試 (`tests/unit/test_llm.py`)

此部分涵蓋對 LLM 輔助函數的測試，如樣本生成和 Schema 提取。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **樣本生成** | **TC-UNIT-LLM-001** | 測試從清單中選擇最具代表性的項目 | 無 | 1. 提供包含簡單和複雜對象的列表<br>2. 生成樣本字串 | [sparse_entry, rich_entry] | 選擇欄位較多的 rich_entry |
| **樣本生成** | **TC-UNIT-LLM-002** | 測試空清單處理 | 無 | 1. 提供空列表 | [] | 返回 "{}" |
| **樣本生成** | **TC-UNIT-LLM-003** | 測試巢狀結構遍歷 | 無 | 1. 提供巢狀資料<br>2. 生成樣本 | nested data structure | 正確提取深層欄位 |
| **Schema 提取** | **TC-UNIT-LLM-004** | 測試簡單內容 Schema 提取 | 無 | 1. 提供簡單 JSON 字串 | [{"name": "Alice", "age": 30}] | {"name": "str", "age": "int"} |
| **Schema 提取** | **TC-UNIT-LLM-005** | 測試巢狀內容 Schema 提取 | 無 | 1. 提供巢狀 JSON 字串 | nested json string | 正確反映巢狀結構類型 |
| **Schema 提取** | **TC-UNIT-LLM-006** | 測試列表內容 Schema 提取 | 無 | 1. 提供包含列表的 JSON | list in json | 正確反映列表元素類型 |
| **Schema 提取** | **TC-UNIT-LLM-007** | 測試 JSONL 格式 Schema 提取 | 無 | 1. 提供 JSONL 字串 | jsonl string | 合併多行鍵值 |

## 記憶體模組測試 (`tests/unit/test_memory.py`)

此部分涵蓋對 Firestore 記憶體操作的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **策略檢索** | **TC-UNIT-MEMORY-001** | 測試在記憶體中成功找到策略 | Mock Firestore & Embedding | 1. 模擬 Embedding<br>2. 模擬向量查詢結果<br>3. 執行 find_policy_in_memory | query="test", source="gcs" | 返回 status="found" 及策略資料 |
| **策略儲存** | **TC-UNIT-MEMORY-002** | 測試將策略成功儲存到記憶體 | Mock Firestore & Embedding | 1. 模擬 Embedding<br>2. 執行 save_policy_to_memory | query="new", code="print", source="gcs" | 呼叫 Firestore add 方法，返回 success |
| **版本管理** | **TC-UNIT-MEMORY-003** | 測試列出策略版本 | Mock Firestore Query | 1. 模擬多個版本文件<br>2. 執行 list_policy_versions | policy_id="123" | 返回包含所有版本的列表 |
| **執行記錄** | **TC-UNIT-MEMORY-004** | 測試記錄策略執行結果 | Mock Firestore | 1. 執行 log_policy_execution | violations list | 新增執行記錄並更新策略統計數據 |
| **歷史查詢** | **TC-UNIT-MEMORY-005** | 測試獲取策略執行歷史記錄 | Mock Firestore Query | 1. 模擬歷史記錄查詢結果<br>2. 執行 get_execution_history | days=7, policy_id="123" | 返回歷史記錄列表 |

## 安全性測試 (`tests/unit/test_security.py`)

此部分涵蓋對程式碼安全驗證機制的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代碼驗證** | **TC-UNIT-SECURITY-001** | 測試安全且允許的程式碼 | 無 | 1. 驗證安全函數定義 | simple function definition | 無錯誤返回 |
| **代碼驗證** | **TC-UNIT-SECURITY-002** | 測試不安全的導入語句 | 無 | 1. 驗證包含 import os 等語句 | import os, sys, etc. | 返回 Security Violation 錯誤 |
| **代碼驗證** | **TC-UNIT-SECURITY-003** | 測試不安全的內建函數 | 無 | 1. 驗證包含 eval, exec 等語句 | eval(), exec(), open() | 返回 Security Violation 錯誤 |
