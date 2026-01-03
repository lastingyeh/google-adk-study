# 詳細測試案例

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 代理程式整合測試 (`tests/integration/test_agent.py`)

此部分涵蓋對代理程式串流功能的整合測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent Stream** | **TC-INTEG-001** | 驗證代理程式串流功能是否正常運作，確認能接收到有效的串流回應。 | 需初始化 InMemorySessionService 和 Agent Runner。 | 1. 建立 InMemorySessionService。<br>2. 建立新的對話 session。<br>3. 初始化 Runner。<br>4. 發送訊息 "Why is the sky blue?"。<br>5. 收集回應事件。 | User ID="test_user", Message="Why is the sky blue?" | 收到至少一個事件，且其中包含文字內容。 |

## 伺服器端對端測試 (`tests/integration/test_server_e2e.py`)

此部分涵蓋對伺服器 API 的端對端測試，包括聊天串流、錯誤處理及回饋收集。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **API Server** | **TC-INTEG-002** | 測試聊天串流功能。 | 伺服器已啟動，Session 已建立。 | 1. 建立 Session。<br>2. 發送包含 "What's the weather in San Francisco?" 的聊天訊息。<br>3. 驗證回應狀態為 200。<br>4. 解析 SSE 事件。 | User ID="test_user_123", Message="What's the weather in San Francisco?" | 收到 SSE 事件，且包含文字內容。 |
| **API Server** | **TC-INTEG-003** | 測試聊天串流的錯誤處理。 | 伺服器已啟動。 | 1. 發送無效的訊息結構 (invalid_type)。 | Invalid input JSON. | 回應狀態碼為 422。 |
| **API Server** | **TC-INTEG-004** | 測試回饋收集端點。 | 伺服器已啟動。 | 1. 發送回饋資料 (score, invocation_id, text)。 | Score=4, Text="Great response!" | 回應狀態碼為 200。 |

## 負載測試 (`tests/load_test/load_test.py`)

此部分涵蓋對聊天串流 API 的負載測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Performance** | **TC-LOAD-001** | 模擬使用者與聊天串流 API 的互動，以測試負載。 | Locust 負載測試工具已設定。 | 1. 建立 Session。<br>2. 發送聊天訊息 "Hello! Weather in New york?"。<br>3. 解析串流回應。<br>4. 記錄回應時間與狀態。 | User ID (UUID), Message="Hello! Weather in New york?" | 回應狀態 200，且無應用層級錯誤 (code < 400)。 |

## 設定單元測試 (`tests/unit/test_config.py`)

此部分涵蓋對設定載入功能的單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Configuration** | **TC-UNIT-001** | 測試設定載入功能，確保模型設定正確。 | Config 類別已定義。 | 1. 初始化 Config 物件。<br>2. 檢查 model 設定。 | None | `agent_settings.model` 應以 "gemini" 開頭。 |

## 虛擬單元測試 (`tests/unit/test_dummy.py`)

此部分涵蓋虛擬測試，用於驗證測試環境。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dummy** | **TC-UNIT-002** | 虛擬測試，用於驗證測試環境。 | None | 1. 執行斷言 1 == 1。 | None | 通過測試。 |

## 工具單元測試 (`tests/unit/test_tools.py`)

此部分涵蓋對各種輔助工具函式的單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tools** | **TC-UNIT-003** | 測試發送通話伴侶連結。 | None | 1. 呼叫 `send_call_companion_link`。 | Phone="+1-555-123-4567" | 回傳成功狀態及訊息。 |
| **Tools** | **TC-UNIT-004** | 測試核准折扣（成功情況）。 | None | 1. 呼叫 `approve_discount`，折扣值 <= 10。 | Value=10.0 | 回傳 `status: ok`。 |
| **Tools** | **TC-UNIT-005** | 測試核准折扣（被拒絕情況）。 | None | 1. 呼叫 `approve_discount`，折扣值 > 10。 | Value=15.0 | 回傳 `status: rejected`。 |
| **Tools** | **TC-UNIT-006** | 測試更新 Salesforce CRM 記錄。 | None | 1. 呼叫 `update_salesforce_crm`。 | CustomerID="123", Details="Updated..." | 回傳成功狀態。 |
| **Tools** | **TC-UNIT-007** | 測試存取購物車資訊。 | None | 1. 呼叫 `access_cart_information`。 | CustomerID="123" | 回傳正確的購物車項目與小計。 |
| **Tools** | **TC-UNIT-008** | 測試修改購物車（新增和移除項目）。 | None | 1. 呼叫 `modify_cart`。 | Add=[tree-789], Remove=[soil-123] | 回傳成功狀態，且 items_added/removed 為 True。 |
| **Tools** | **TC-UNIT-009** | 測試獲取產品推薦（針對 Petunias）。 | None | 1. 呼叫 `get_product_recommendations`。 | Plant="petunias" | 回傳 Petunias 相關推薦產品。 |
| **Tools** | **TC-UNIT-010** | 測試獲取產品推薦（針對其他植物）。 | None | 1. 呼叫 `get_product_recommendations`。 | Plant="other" | 回傳通用推薦產品。 |
| **Tools** | **TC-UNIT-011** | 測試檢查產品庫存。 | None | 1. 呼叫 `check_product_availability`。 | ProductID="soil-123" | 回傳 available: True。 |
| **Tools** | **TC-UNIT-012** | 測試預約種植服務。 | None | 1. 呼叫 `schedule_planting_service`。 | Date="2024-07-29" | 回傳成功狀態及預約詳情。 |
| **Tools** | **TC-UNIT-013** | 測試獲取可用種植時間。 | None | 1. 呼叫 `get_available_planting_times`。 | Date="2024-07-29" | 回傳可用時間列表。 |
| **Tools** | **TC-UNIT-014** | 測試發送照護說明。 | None | 1. 呼叫 `send_care_instructions`。 | Plant="Petunias", Method="email" | 回傳成功狀態。 |
| **Tools** | **TC-UNIT-015** | 測試生成 QR Code。 | None | 1. 呼叫 `generate_qr_code`。 | Value=10.0 | 回傳成功狀態及 QR Code 數據。 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
