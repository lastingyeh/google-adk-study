# Math Agent 詳細測試案例

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。

## Math Agent 測試 (`tests/test_agent.py`)

此部分涵蓋 Math Agent 的數學工具功能、OpenTelemetry 初始化與整合測試。

### 測試群組: 基本數學工具功能 (TestToolFunctions)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **基本數學工具** | **TC-MATH-001** | 測試正數相加 | 無 | 呼叫 `add_numbers(5, 3)` | 5, 3 | 返回 8 |
| **基本數學工具** | **TC-MATH-002** | 測試負數相加 | 無 | 呼叫 `add_numbers(-5, 3)` | -5, 3 | 返回 -2 |
| **基本數學工具** | **TC-MATH-003** | 測試與零相加 | 無 | 呼叫 `add_numbers(0, 5)` | 0, 5 | 返回 5 |
| **基本數學工具** | **TC-MATH-004** | 測試浮點數相加 | 無 | 呼叫 `add_numbers(1.5, 2.3)` | 1.5, 2.3 | 返回接近 3.8 |
| **基本數學工具** | **TC-MATH-005** | 測試正數相減 | 無 | 呼叫 `subtract_numbers(10, 3)` | 10, 3 | 返回 7 |
| **基本數學工具** | **TC-MATH-006** | 測試相減結果為負數 | 無 | 呼叫 `subtract_numbers(3, 10)` | 3, 10 | 返回 -7 |
| **基本數學工具** | **TC-MATH-007** | 測試與零相減 | 無 | 呼叫 `subtract_numbers(5, 0)` | 5, 0 | 返回 5 |
| **基本數學工具** | **TC-MATH-008** | 測試浮點數相減 | 無 | 呼叫 `subtract_numbers(5.5, 2.3)` | 5.5, 2.3 | 返回接近 3.2 |
| **基本數學工具** | **TC-MATH-009** | 測試正數相乘 | 無 | 呼叫 `multiply_numbers(4, 5)` | 4, 5 | 返回 20 |
| **基本數學工具** | **TC-MATH-010** | 測試乘以零 | 無 | 呼叫 `multiply_numbers(5, 0)` | 5, 0 | 返回 0 |
| **基本數學工具** | **TC-MATH-011** | 測試負數相乘 | 無 | 呼叫 `multiply_numbers(-3, 4)` | -3, 4 | 返回 -12 |
| **基本數學工具** | **TC-MATH-012** | 測試浮點數相乘 | 無 | 呼叫 `multiply_numbers(2.5, 4.0)` | 2.5, 4.0 | 返回 10.0 |
| **基本數學工具** | **TC-MATH-013** | 測試正數相除 | 無 | 呼叫 `divide_numbers(10, 2)` | 10, 2 | 返回 5 |
| **基本數學工具** | **TC-MATH-014** | 測試相除結果為浮點數 | 無 | 呼叫 `divide_numbers(10, 3)` | 10, 3 | 返回接近 3.333333 |
| **基本數學工具** | **TC-MATH-015** | 測試負數相除 | 無 | 呼叫 `divide_numbers(-10, 2)` | -10, 2 | 返回 -5 |
| **基本數學工具** | **TC-MATH-016** | 測試除以零會引發 ValueError | 無 | 呼叫 `divide_numbers(10, 0)` | 10, 0 | 引發 ValueError (Cannot divide by zero) |
| **基本數學工具** | **TC-MATH-017** | 測試浮點數相除 | 無 | 呼叫 `divide_numbers(7.5, 2.5)` | 7.5, 2.5 | 返回接近 3.0 |

### 測試群組: OpenTelemetry 初始化 (TestOpenTelemetryInitialization)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OTel 初始化** | **TC-OTEL-001** | 測試 initialize_otel 返回 TracerProvider 實例 | OTel 庫可用 | 呼叫 `initialize_otel()` | 無 | 返回非 None 的 provider |
| **OTel 初始化** | **TC-OTEL-002** | 測試使用自訂服務名稱進行 OTel 初始化 | OTel 庫可用 | 呼叫 `initialize_otel(service_name="custom-service", force_reinit=True)` | service_name="custom-service" | Resource 屬性包含 "service.name": "custom-service" |
| **OTel 初始化** | **TC-OTEL-003** | 測試使用自訂版本進行 OTel 初始化 | OTel 庫可用 | 呼叫 `initialize_otel(service_version="1.0.0", force_reinit=True)` | service_version="1.0.0" | Resource 屬性包含 "service.version": "1.0.0" |
| **OTel 初始化** | **TC-OTEL-004** | 測試使用自訂 Jaeger 端點進行 OTel 初始化 | OTel 庫可用 | 呼叫 `initialize_otel(jaeger_endpoint=..., force_reinit=True)` | jaeger_endpoint="..." | 返回非 None 的 provider |
| **OTel 初始化** | **TC-OTEL-005** | 測試 initialize_otel 設定所需的環境變數 | OTel 庫可用 | 呼叫 `initialize_otel()` | 無 | 環境變數 OTEL_EXPORTER_OTLP_PROTOCOL 等被正確設定 |
| **OTel 初始化** | **TC-OTEL-006** | 測試 OTel 資源具有正確的屬性 | OTel 庫可用 | 呼叫 `initialize_otel()` | 無 | Resource 屬性包含預設的 service.name 和 version |
| **OTel 初始化** | **TC-OTEL-007** | 測試 initialize_otel 可以安全地多次呼叫 | OTel 庫可用 | 多次呼叫 `initialize_otel()` | 無 | 每次都返回有效的 provider |

### 測試群組: OTel 整合測試 (TestOTelConfigIntegration)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OTel 整合** | **TC-OTEL-008** | 測試 span 處理器已正確設定 | OTel 庫可用 | 初始化 OTel | 無 | Provider 和 Resource 被正確初始化 |
| **OTel 整合** | **TC-OTEL-009** | 測試可以從 provider 建立 tracer | OTel 庫可用 | 設定 provider 並獲取 tracer | 無 | 成功獲取 tracer 實例 |
| **OTel 整合** | **TC-OTEL-010** | 測試建立一個簡單的 span | OTel 庫可用 | 使用 tracer 建立 span 並設定屬性 | "test.key", "test_value" | Span 建立成功且不為 None |

### 測試群組: 工具文件 (TestToolDocumentation)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **文件** | **TC-DOC-001** | 測試 add_numbers 有文件說明 | 無 | 檢查 `add_numbers.__doc__` | 無 | Docstring 存在且包含 "Add" |
| **文件** | **TC-DOC-002** | 測試 subtract_numbers 有文件說明 | 無 | 檢查 `subtract_numbers.__doc__` | 無 | Docstring 存在且包含 "Subtract" |
| **文件** | **TC-DOC-003** | 測試 multiply_numbers 有文件說明 | 無 | 檢查 `multiply_numbers.__doc__` | 無 | Docstring 存在且包含 "Multiply" |
| **文件** | **TC-DOC-004** | 測試 divide_numbers 有文件說明 | 無 | 檢查 `divide_numbers.__doc__` | 無 | Docstring 存在且包含 "Divide" |

### 測試群組: 邊界情況 (TestEdgeCases)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **邊界情況** | **TC-EDGE-001** | 測試非常大的數字相加 | 無 | 呼叫 `add_numbers(1e10, 1e10)` | 1e10, 1e10 | 返回 2e10 |
| **邊界情況** | **TC-EDGE-002** | 測試數字減去自身 | 無 | 呼叫 `subtract_numbers(42, 42)` | 42, 42 | 返回 0 |
| **邊界情況** | **TC-EDGE-003** | 測試乘以 1 返回相同的數字 | 無 | 呼叫 `multiply_numbers(42, 1)` | 42, 1 | 返回 42 |
| **邊界情況** | **TC-EDGE-004** | 測試除以 1 返回相同的數字 | 無 | 呼叫 `divide_numbers(42, 1)` | 42, 1 | 返回 42 |
| **邊界情況** | **TC-EDGE-005** | 測試非常小的浮點數相加 | 無 | 呼叫 `add_numbers(1e-10, 1e-10)` | 1e-10, 1e-10 | 返回 > 0 |
| **邊界情況** | **TC-EDGE-006** | 測試兩個負數相乘 | 無 | 呼叫 `multiply_numbers(-3, -4)` | -3, -4 | 返回 12 |
| **邊界情況** | **TC-EDGE-007** | 測試兩個負數相除 | 無 | 呼叫 `divide_numbers(-10, -2)` | -10, -2 | 返回 5 |

### 測試群組: 型別處理 (TestToolTypes)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **型別處理** | **TC-TYPE-001** | 測試整數和浮點數相加 | 無 | 呼叫 `add_numbers(5, 2.5)` | 5, 2.5 | 返回接近 7.5 |
| **型別處理** | **TC-TYPE-002** | 測試浮點數和整數相減 | 無 | 呼叫 `subtract_numbers(10.5, 3)` | 10.5, 3 | 返回接近 7.5 |
| **型別處理** | **TC-TYPE-003** | 測試混合型別相乘 | 無 | 呼叫 `multiply_numbers(3, 2.5)` | 3, 2.5 | 返回接近 7.5 |
| **型別處理** | **TC-TYPE-004** | 測試混合型別相除 | 無 | 呼叫 `divide_numbers(15, 2)` | 15, 2 | 返回接近 7.5 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
