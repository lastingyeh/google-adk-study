# Human Tool Confirmation Agent - 技術文件

🔔 **更新日期：2026-01-13**

## 目錄

- [專案概述](#專案概述)
- [核心功能](#核心功能)
- [架構設計](#架構設計)
- [程式碼詳解](#程式碼詳解)
- [使用範例](#使用範例)
- [API 參考](#api-參考)
- [已知限制](#已知限制)
- [相關資源](#相關資源)

## 專案概述

**Human Tool Confirmation Agent** 是一個基於 Google ADK (Agent Development Kit) 的實驗性專案，展示如何在代理工具執行流程中整合人機確認機制。此專案實作了兩種確認模式：

1. **布林確認 (Boolean Confirmation)** - 簡單的是/否確認
2. **進階確認 (Advanced Confirmation)** - 結構化數據回應確認

### 適用場景

- 需要人工審批的財務操作（報銷、轉帳等）
- 需要主管核准的請假申請
- 需要二次確認的敏感操作
- 需要額外輸入數據才能繼續的工作流程

### 技術規格

- **ADK 版本**: Python v1.14.0+
- **狀態**: Experimental
- **模型**: Gemini 2.5 Flash
- **特性**: 支援 Resumability（可恢復性）

## 核心功能

### 1. 報銷工具 (`reimburse`)

**功能描述**：處理員工報銷申請，並根據金額門檻決定是否需要確認。

**確認邏輯**：
- 金額 ≤ 1000：自動核准，無需確認
- 金額 > 1000：需要人工確認

**實作方式**：使用 `confirmation_threshold` 函數動態判斷

```python
async def confirmation_threshold(amount: int, tool_context: ToolContext) -> bool:
    """若金額大於 1000，則需經過確認。"""
    return amount > 1000
```

### 2. 請假申請工具 (`request_time_off`)

**功能描述**：處理員工請假申請，根據天數自動或手動核准。

**核准邏輯**：
- 天數 ≤ 0：回傳錯誤
- 天數 ≤ 2：自動核准
- 天數 > 2：需要主管確認（使用進階確認機制）

**確認流程**：
1. 發起確認請求，包含提示訊息與 payload 結構
2. 等待主管回應
3. 根據回應中的 `approved_days` 決定最終核准天數

## 架構設計

### 系統架構圖

```
┌──────────────────────────────────────────────────────┐
│                    User Input                        │
└───────────────────┬──────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│           Time Off Agent (root_agent)                │
│  ┌────────────────────────────────────────────────┐  │
│  │  Model: Gemini 2.5 Flash                      │  │
│  │  Temperature: 0.1                             │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌───────────────────┐
│   reimburse   │       │ request_time_off  │
│  (FunctionTool)│       │   (FunctionTool)  │
└───────┬───────┘       └─────────┬─────────┘
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────────┐
│ Boolean Confirm  │      │ Advanced Confirm     │
│ (threshold fn)   │      │ (request_confirmation)│
└──────────────────┘      └──────────────────────┘
```

### 資料流程

#### 布林確認流程

```
User → Agent → Tool (reimburse)
              ↓
        Check amount > 1000?
              ↓
         Yes → Request Boolean Confirmation
              ↓
         User Response (Yes/No)
              ↓
         Execute Tool → Return Result
```

#### 進階確認流程

```
User → Agent → Tool (request_time_off)
              ↓
        Check days > 2?
              ↓
         Yes → Request Advanced Confirmation
              ↓
              tool_context.request_confirmation(
                hint="...",
                payload={"approved_days": 0}
              )
              ↓
         Return {"status": "需主管核准。"}
              ↓
         Wait for Manager Response
              ↓
         Receive ToolConfirmation with payload
              ↓
         Extract approved_days from payload
              ↓
         Execute Tool → Return Result
```

## 程式碼詳解

### 檔案結構

```
human_tool_confirmation/
├── __init__.py          # 模組初始化
└── agent.py            # 主要代理邏輯
```

### agent.py 核心組件

#### 1. 導入依賴

```python
from google.adk import Agent
from google.adk.apps import App
from google.adk.apps import ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_confirmation import ToolConfirmation
from google.adk.tools.tool_context import ToolContext
from google.genai import types
```

**關鍵類別說明**：
- `Agent`: 代理主體
- `App`: ADK 應用程式容器
- `FunctionTool`: 函數工具包裝器
- `ToolContext`: 工具執行上下文（包含確認請求方法）
- `ToolConfirmation`: 確認回應數據結構

#### 2. reimburse 工具實作

```python
def reimburse(amount: int, tool_context: ToolContext) -> str:
    """根據金額為員工報銷。"""
    return {'status': 'ok'}
```

**設計特點**：
- 簡單的報銷邏輯
- 確認邏輯由外部 `confirmation_threshold` 控制
- 回傳結構化結果

#### 3. 確認門檻函數

```python
async def confirmation_threshold(amount: int, tool_context: ToolContext) -> bool:
    """若金額大於 1000，則需經過確認。"""
    return amount > 1000
```

**技術細節**：
- 使用 `async` 支援異步操作
- 接收與工具相同的參數（`amount`, `tool_context`）
- 回傳布林值決定是否需要確認

#### 4. request_time_off 工具實作

```python
def request_time_off(days: int, tool_context: ToolContext):
    """員工請假申請。"""
    if days <= 0:
        return {'status': '請假天數無效。'}

    if days <= 2:
        # 2 天以內自動核准
        return {
            'status': 'ok',
            'approved_days': days,
        }

    # 超過 2 天需主管確認
    tool_confirmation = tool_context.tool_confirmation
    if not tool_confirmation:
        # 首次呼叫：發起確認請求
        tool_context.request_confirmation(
            hint=(
                '請主管核准或拒絕 request_time_off() 工具呼叫，'
                '並以 FunctionResponse 回覆，內容需包含 ToolConfirmation payload。'
            ),
            payload={
                'approved_days': 0,
            },
        )
        return {'status': '需主管核準。'}

    # 第二次呼叫：處理確認回應
    approved_days = tool_confirmation.payload['approved_days']
    approved_days = min(approved_days, days)
    if approved_days == 0:
        return {'status': '請假申請被拒絕。', 'approved_days': 0}
    return {
        'status': 'ok',
        'approved_days': approved_days,
    }
```

**執行邏輯分析**：

1. **第一階段（請求確認）**：
   - 檢查 `tool_context.tool_confirmation` 是否為 `None`
   - 若為 `None`，表示尚未取得確認
   - 呼叫 `request_confirmation()` 發起請求
   - 回傳中間狀態訊息

2. **第二階段（處理確認）**：
   - `tool_confirmation` 不為 `None`，表示已收到確認回應
   - 從 `tool_confirmation.payload['approved_days']` 取得核准天數
   - 使用 `min()` 確保核准天數不超過申請天數
   - 根據核准天數回傳結果

#### 5. Agent 配置

```python
root_agent = Agent(
    model='gemini-2.5-flash',
    name='time_off_agent',
    instruction="""
    你是一位能協助員工報銷及請假申請的助理。
    - 報銷請使用 `reimburse` 工具。
    - 請假申請請使用 `request_time_off` 工具。
    - 優先使用工具來完成使用者需求。
    - 回覆時請務必提供工具執行結果。
    """,
    tools=[
        FunctionTool(
            reimburse,
            require_confirmation=confirmation_threshold,
        ),
        request_time_off,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
```

**配置重點**：
- **Model**: 使用 Gemini 2.5 Flash（快速回應）
- **Temperature**: 0.1（低隨機性，確保一致性）
- **Tools**:
  - `reimburse` 使用 `FunctionTool` 包裝，配置確認門檻函數
  - `request_time_off` 直接註冊（內部處理確認邏輯）

#### 6. App 配置

```python
app = App(
    name='human_tool_confirmation',
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
)
```

**Resumability 的重要性**：
- 確認過程可能需要等待人工回應（可能長達數分鐘或數小時）
- 啟用 `is_resumable=True` 允許工作流程在等待期間暫停
- 收到確認後可從暫停點恢復執行

## 使用範例

### 範例 1：小額報銷（無需確認）

**使用者輸入**：
```
我需要報銷 500 元的交通費
```

**執行流程**：
1. Agent 呼叫 `reimburse(amount=500)`
2. `confirmation_threshold(500)` 回傳 `False`（不需確認）
3. 直接執行報銷
4. 回傳 `{'status': 'ok'}`

**Agent 回應**：
```
已為您處理 500 元的報銷申請，狀態：成功核准。
```

### 範例 2：大額報銷（需要確認）

**使用者輸入**：
```
我需要報銷 1500 元的會議費用
```

**執行流程**：
1. Agent 呼叫 `reimburse(amount=1500)`
2. `confirmation_threshold(1500)` 回傳 `True`（需要確認）
3. 系統暫停並顯示確認對話框
4. 主管點擊「確認」或「拒絕」
5. 根據回應執行或取消報銷

**確認 UI 顯示**：
```
┌─────────────────────────────────────┐
│ 工具確認請求                        │
├─────────────────────────────────────┤
│ 工具: reimburse                     │
│ 參數: amount=1500                   │
│                                     │
│ 是否核准此工具呼叫？                 │
│                                     │
│  [確認]  [拒絕]                     │
└─────────────────────────────────────┘
```

### 範例 3：短期請假（自動核准）

**使用者輸入**：
```
我想請假 1 天
```

**執行流程**：
1. Agent 呼叫 `request_time_off(days=1)`
2. 檢查 `days <= 2`，條件成立
3. 自動核准
4. 回傳 `{'status': 'ok', 'approved_days': 1}`

**Agent 回應**：
```
您的 1 天請假申請已自動核准。核准天數：1 天。
```

### 範例 4：長期請假（需要確認）

**使用者輸入**：
```
我想請假 5 天
```

**執行流程**：
1. Agent 呼叫 `request_time_off(days=5)`
2. 檢查 `days > 2`，需要確認
3. 呼叫 `tool_context.request_confirmation()`
4. 回傳 `{'status': '需主管核准。'}`
5. 系統顯示確認對話框（包含 payload 輸入欄位）
6. 主管輸入 `approved_days: 3`
7. 工具收到確認，回傳 `{'status': 'ok', 'approved_days': 3}`

**確認 UI 顯示**：
```
┌─────────────────────────────────────┐
│ 工具確認請求                        │
├─────────────────────────────────────┤
│ 工具: request_time_off              │
│ 參數: days=5                        │
│                                     │
│ 提示：請主管核准或拒絕 request_time_off() │
│ 工具呼叫，並以 FunctionResponse 回覆， │
│ 內容需包含 ToolConfirmation payload。 │
│                                     │
│ Payload 結構：                       │
│ {                                   │
│   "approved_days": 0                │
│ }                                   │
│                                     │
│ 請輸入確認數據：                     │
│ ┌─────────────────────────────┐     │
│ │ {                           │     │
│ │   "approved_days": 3        │     │
│ │ }                           │     │
│ └─────────────────────────────┘     │
│                                     │
│  [提交確認]  [拒絕]                  │
└─────────────────────────────────────┘
```

**Agent 最終回應**：
```
您的 5 天請假申請已由主管核准 3 天。核准天數：3 天。
```

## API 參考

### 工具函數

#### `reimburse(amount: int, tool_context: ToolContext) -> dict`

處理報銷申請。

**參數**：
- `amount` (int): 報銷金額
- `tool_context` (ToolContext): 工具執行上下文

**回傳**：
- `dict`: 包含 `status` 欄位的字典

**範例**：
```python
result = reimburse(amount=500, tool_context=context)
# {'status': 'ok'}
```

#### `confirmation_threshold(amount: int, tool_context: ToolContext) -> bool`

判斷是否需要確認。

**參數**：
- `amount` (int): 報銷金額
- `tool_context` (ToolContext): 工具執行上下文

**回傳**：
- `bool`: `True` 表示需要確認，`False` 表示不需要

**邏輯**：
```python
return amount > 1000
```

#### `request_time_off(days: int, tool_context: ToolContext) -> dict`

處理請假申請。

**參數**：
- `days` (int): 請假天數
- `tool_context` (ToolContext): 工具執行上下文

**回傳**：
- `dict`: 包含 `status` 和可選的 `approved_days` 欄位

**回傳範例**：
```python
# 無效天數
{'status': '請假天數無效。'}

# 自動核准
{'status': 'ok', 'approved_days': 2}

# 等待確認
{'status': '需主管核准。'}

# 確認後核准
{'status': 'ok', 'approved_days': 3}

# 確認後拒絕
{'status': '請假申請被拒絕。', 'approved_days': 0}
```

### ToolContext 方法

#### `tool_context.request_confirmation(hint: str, payload: Any) -> None`

發起進階確認請求。

**參數**：
- `hint` (str): 給使用者的提示訊息，說明需要什麼資訊
- `payload` (Any): 預期回應的數據結構（必須可序列化為 JSON）

**使用範例**：
```python
tool_context.request_confirmation(
    hint="請輸入核准天數",
    payload={
        'approved_days': 0,
        'reason': ''
    }
)
```

#### `tool_context.tool_confirmation`

取得確認回應數據。

**型別**: `ToolConfirmation | None`

**屬性**：
- `payload` (dict): 使用者提供的確認數據

**使用範例**：
```python
if tool_context.tool_confirmation:
    approved_days = tool_context.tool_confirmation.payload['approved_days']
```

## REST API 遠端確認

### 確認請求格式

當工具請求確認時，系統會生成一個 `FunctionCall` 事件：

```json
{
  "function_call": {
    "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
    "name": "adk_request_confirmation",
    "args": {
      "hint": "請主管核准或拒絕...",
      "payload": {
        "approved_days": 0
      }
    }
  }
}
```

### 確認回應格式

使用 `curl` 發送確認回應到 `/run_sse` 端點：

#### 布林確認回應

```bash
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "new_message": {
      "parts": [
        {
          "function_response": {
            "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
            "name": "adk_request_confirmation",
            "response": {
              "confirmed": true
            }
          }
        }
      ],
      "role": "user"
    }
  }'
```

#### 進階確認回應

```bash
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "new_message": {
      "parts": [
        {
          "function_response": {
            "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
            "name": "adk_request_confirmation",
            "response": {
              "confirmed": true,
              "payload": {
                "approved_days": 3
              }
            }
          }
        }
      ],
      "role": "user"
    }
  }'
```

### 回應欄位說明

| 欄位 | 必填 | 說明 |
|------|------|------|
| `app_name` | ✓ | 應用程式名稱 (`human_tool_confirmation`) |
| `user_id` | ✓ | 使用者 ID |
| `session_id` | ✓ | 會話 ID（從確認請求中取得） |
| `function_response.id` | ✓ | 必須與 `FunctionCall` 的 `id` 相符 |
| `function_response.name` | ✓ | 固定為 `adk_request_confirmation` |
| `response.confirmed` | ✓ | 布林值，表示是否確認 |
| `response.payload` | - | 進階確認的額外數據（可選） |

### 搭配 Resumability 使用

如果啟用 Resumability，還需包含 `invocation_id`：

```bash
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "invocation_id": "inv-12345",
    "new_message": {
      "parts": [
        {
          "function_response": {
            "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
            "name": "adk_request_confirmation",
            "response": {
              "confirmed": true,
              "payload": {
                "approved_days": 3
              }
            }
          }
        }
      ],
      "role": "user"
    }
  }'
```

## 已知限制

根據 ADK v1.14.0 文件，工具確認功能目前有以下限制：

### 1. 不支援 DatabaseSessionService

❌ 無法與 `DatabaseSessionService` 搭配使用

```python
# 不支援的配置
from google.adk.sessions import DatabaseSessionService

app = App(
    name='human_tool_confirmation',
    root_agent=root_agent,
    session_service=DatabaseSessionService(...)  # 不支援
)
```

### 2. 不支援 VertexAiSessionService

❌ 無法與 `VertexAiSessionService` 搭配使用

```python
# 不支援的配置
from google.adk.sessions import VertexAiSessionService

app = App(
    name='human_tool_confirmation',
    root_agent=root_agent,
    session_service=VertexAiSessionService(...)  # 不支援
)
```

### 3. 實驗性功能

⚠️ 此功能目前處於實驗階段，API 可能在未來版本中變更。

### 4. Session 管理限制

- 確認請求與回應必須在同一個 session 中
- Session ID 必須一致
- 使用 Resumability 時需正確傳遞 `invocation_id`

## 最佳實踐

### 1. 確認邏輯分離

將確認邏輯與業務邏輯分離，提高可維護性：

```python
# ✅ 推薦：分離確認邏輯
async def confirmation_threshold(amount: int, tool_context: ToolContext) -> bool:
    return amount > THRESHOLD

FunctionTool(reimburse, require_confirmation=confirmation_threshold)
```

```python
# ❌ 不推薦：混合邏輯
def reimburse(amount: int, tool_context: ToolContext):
    if amount > THRESHOLD:
        # 在工具內部處理確認...
        pass
```

### 2. 提供清晰的提示訊息

```python
# ✅ 推薦：清晰的提示
tool_context.request_confirmation(
    hint="請主管核准或拒絕請假申請，並輸入實際核准天數（0 表示拒絕）",
    payload={'approved_days': 0}
)
```

```python
# ❌ 不推薦：模糊的提示
tool_context.request_confirmation(
    hint="請確認",
    payload={'data': None}
)
```

### 3. 驗證確認數據

```python
# ✅ 推薦：驗證數據合法性
approved_days = tool_confirmation.payload.get('approved_days', 0)
approved_days = max(0, min(approved_days, days))  # 限制範圍
```

### 4. 處理邊界情況

```python
# ✅ 推薦：完整的邊界處理
if days <= 0:
    return {'status': '請假天數無效。'}

if not tool_confirmation:
    # 發起確認
    return {'status': '需主管核准。'}

# 處理確認回應
approved_days = tool_confirmation.payload.get('approved_days', 0)
if approved_days == 0:
    return {'status': '請假申請被拒絕。', 'approved_days': 0}
```

### 5. 使用結構化回傳

```python
# ✅ 推薦：結構化回傳
return {
    'status': 'ok',
    'approved_days': approved_days,
    'approved_at': datetime.now().isoformat()
}
```

```python
# ❌ 不推薦：字串回傳
return "請假申請已核准 3 天"
```

### 6. 啟用 Resumability

```python
# ✅ 推薦：啟用可恢復性（適合長時間等待確認）
app = App(
    name='human_tool_confirmation',
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)
```

## 測試建議

### 單元測試範例

```python
import pytest
from human_tool_confirmation.agent import (
    reimburse,
    confirmation_threshold,
    request_time_off
)

class TestReimburse:
    def test_small_amount_no_confirmation(self):
        """測試小額報銷無需確認"""
        # Mock ToolContext
        mock_context = MockToolContext()

        # 執行
        result = reimburse(amount=500, tool_context=mock_context)

        # 驗證
        assert result['status'] == 'ok'
        assert not mock_context.confirmation_requested

class TestConfirmationThreshold:
    @pytest.mark.asyncio
    async def test_threshold_1000(self):
        """測試門檻值為 1000"""
        mock_context = MockToolContext()

        # 小於門檻
        assert not await confirmation_threshold(1000, mock_context)

        # 超過門檻
        assert await confirmation_threshold(1001, mock_context)

class TestRequestTimeOff:
    def test_auto_approve_short_leave(self):
        """測試短期請假自動核准"""
        mock_context = MockToolContext()

        result = request_time_off(days=2, tool_context=mock_context)

        assert result['status'] == 'ok'
        assert result['approved_days'] == 2

    def test_require_confirmation_long_leave(self):
        """測試長期請假需要確認"""
        mock_context = MockToolContext()

        # 第一次呼叫：發起確認
        result = request_time_off(days=5, tool_context=mock_context)

        assert result['status'] == '需主管核准。'
        assert mock_context.confirmation_requested

    def test_approved_with_confirmation(self):
        """測試確認後核准"""
        # 模擬已收到確認
        mock_context = MockToolContext(
            tool_confirmation={'approved_days': 3}
        )

        result = request_time_off(days=5, tool_context=mock_context)

        assert result['status'] == 'ok'
        assert result['approved_days'] == 3
```

### 整合測試範例

```python
class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_workflow_with_confirmation(self):
        """測試完整的確認工作流程"""
        # 1. 啟動 agent
        # 2. 發送請求
        # 3. 驗證確認請求
        # 4. 發送確認回應
        # 5. 驗證最終結果
        pass
```

## 故障排除

### 常見問題

#### Q1: 確認請求沒有顯示？

**可能原因**：
- Session ID 不一致
- 前端未正確處理 `FunctionCall` 事件
- 工具執行失敗

**解決方法**：
```python
# 檢查 tool_context 是否正確傳遞
if not tool_context:
    raise ValueError("ToolContext is required")

# 記錄確認請求
import logging
logging.info(f"Requesting confirmation with hint: {hint}")
```

#### Q2: 確認回應無效？

**可能原因**：
- `function_response.id` 與 `function_call.id` 不一致
- `name` 不是 `adk_request_confirmation`
- JSON 格式錯誤

**解決方法**：
```bash
# 檢查 ID 是否一致
# 從確認請求中複製正確的 ID

# 驗證 JSON 格式
echo '{"response": {...}}' | jq .
```

#### Q3: Resumability 無法正常工作？

**可能原因**：
- 未配置 `ResumabilityConfig`
- `invocation_id` 未正確傳遞

**解決方法**：
```python
# 確保啟用 Resumability
app = App(
    name='human_tool_confirmation',
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)
```

## 相關資源

### 官方文件

- [ADK 工具確認文件](https://google.github.io/adk-docs/tools-custom/confirmation/)
- [ADK Function Tools 概述](https://google.github.io/adk-docs/tools-custom/function-tools/)
- [ADK Resumability 文件](https://google.github.io/adk-docs/runtime/resume/)
- [ADK Python API 參考](https://google.github.io/adk-docs/api-reference/python/)

### 程式碼範例

- [human_tool_confirmation 官方範例](https://github.com/google/adk-python/tree/main/contributing/samples/human_tool_confirmation)
- [ADK Python Samples](https://github.com/google/adk-python/tree/main/contributing/samples)
