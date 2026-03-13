# 測試範例使用說明

本目錄包含 Guarding Agent 的測試情境文件和模擬審核流程的範例腳本。

## 📁 文件清單

### 1. test_scenarios.md
完整的測試對答情境文件，涵蓋所有安全防護功能：
- 低風險工具測試
- 內容過濾測試
- PII 檢測與處理測試
- 中等/高風險/關鍵工具的審核流程
- 複合場景和錯誤處理測試
- **附錄 A：如何模擬審核者通過** - 詳細說明審核機制原理和實作方法
- **附錄 B：Python 測試腳本範例** - 基礎測試腳本

### 2. simulate_approval.py
可執行的審核流程模擬腳本，演示如何在測試中模擬審核者核准或拒絕操作。

### 3. approval_demo.py
官方提供的審核流程演示腳本，展示完整的審核工作流程。

---

## 🚀 快速開始

### 環境準備

確保已安裝專案依賴：

```bash
cd /path/to/guarding-agent
pip install -e .
```

### 執行審核流程模擬

#### 1. 執行所有測試情境（推薦）

```bash
python examples/simulate_approval.py
```

這會依序執行以下測試：
- ✅ 刪除用戶（審核核准）
- ❌ 刪除用戶（審核拒絕）
- ✅ 執行付款（管理員核准）
- ❌ 執行付款（管理員拒絕）
- ✅ 批量更新（主管核准）
- ❌ 批量更新（主管拒絕）
- ✅ 修改系統配置（管理員核准）

#### 2. 執行特定測試

```bash
# 測試刪除用戶審核流程
python examples/simulate_approval.py --test delete_user

# 測試付款審核流程
python examples/simulate_approval.py --test payment

# 測試批量更新審核流程
python examples/simulate_approval.py --test bulk_update

# 測試系統配置審核流程
python examples/simulate_approval.py --test system_config
```

#### 3. 查看幫助

```bash
python examples/simulate_approval.py --help
```

---

## 📖 審核流程說明

### 工作流程圖

```
1. 用戶發起請求
   ↓
2. Agent 調用工具（第一次）
   ↓
3. 工具檢測需要審核
   ↓
4. 返回 pending 狀態 + invocation_id
   ↓
5. 查看待審核請求（可選）
   ↓
6. 審核者提交決策（核准/拒絕）
   ↓
7. 使用 invocation_id 恢復執行（第二次）
   ↓
8. 工具根據決策執行或拒絕
   ↓
9. 返回最終結果
```

### 關鍵概念

#### 1. Invocation ID
- 每次工具調用的唯一識別碼
- 用於恢復被暫停的工具執行
- 在第一次調用後從事件中獲取

#### 2. 審核決策格式
```python
{
    "approved": True/False,    # 是否核准
    "approver": "user_id",     # 審核者 ID
    "reason": "決策理由",       # 說明
}
```

#### 3. 恢復執行
使用 `invocation_id` 和審核決策內容恢復工具執行：

```python
decision_content = types.Content(
    parts=[
        types.Part(
            function_response=types.FunctionResponse(
                name="tool_name",
                response=approval_decision,
            )
        )
    ],
    role="user",
)

await runner.run_async(
    user_id=user_id,
    session_id=session_id,
    invocation_id=invocation_id,  # ← 關鍵
    new_message=decision_content,
)
```

---

## 📝 自定義測試

### 範例：建立新的測試情境

```python
async def test_my_custom_scenario():
    """自定義測試情境"""
    await simulate_approval(
        user_message="請執行我的自定義操作",
        tool_name="my_custom_tool",
        test_name="自定義測試情境",
        approval_decision={
            "approved": True,
            "approver": "custom_approver",
            "reason": "測試原因",
        },
    )

# 在 main() 中加入你的測試
if __name__ == "__main__":
    asyncio.run(test_my_custom_scenario())
```

---

## 🔍 除錯技巧

### 1. 查看完整事件流

```python
async for event in runner.run_async(...):
    print(f"Event Type: {type(event).__name__}")
    print(f"Event: {event}")

    if hasattr(event, "invocation_id"):
        print(f"Invocation ID: {event.invocation_id}")
```

### 2. 檢查 Session State

```python
session = await runner.session_service.get(...)
print("Session State:", session.state.keys())
print("Pending:", session.state.get("security:pending_approvals"))
print("History:", session.state.get("security:approval_history"))
```

### 3. 啟用詳細日誌

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 相關文件

- [test_scenarios.md](test_scenarios.md) - 完整測試情境文件
- [approval_demo.py](approval_demo.py) - 官方審核流程演示
- [../tests/test_phase2_approval.py](../tests/test_phase2_approval.py) - 單元測試
- [../README.md](../README.md) - 專案主要文件

---

## ❓ 常見問題

### Q: 為什麼我的操作沒有觸發審核？
A: 可能原因：
1. 工具的風險等級設定為 LOW（自動執行）
2. 條件未達到審核閾值（如 MEDIUM 等級的條件判斷）
3. 檢查 `config/risk_config.yaml` 中的配置

### Q: 如何修改審核閾值？
A: 編輯 `config/risk_config.yaml`：
```yaml
tools:
  update_profile:
    max_auto_approve_threshold:
      fields: 3  # 改為你想要的值
```

### Q: 可以模擬多個審核者嗎？
A: 可以！只需在不同的審核決策中使用不同的 `approver` ID：
```python
approval_decision = {
    "approved": True,
    "approver": "manager_alice",  # 第一層審核
    "reason": "初步核准",
}

# 如需第二層審核，可以實作多階段審核邏輯
```

### Q: 審核記錄儲存在哪裡？
A: 審核記錄儲存在 Session State 中：
- `security:pending_approvals` - 待審核請求
- `security:approval_history` - 審核歷史
- `security:approval_metrics` - 統計指標

---

## 🤝 貢獻

歡迎提交新的測試情境或改進現有腳本！請遵循以下規範：
1. 保持程式碼清晰易讀
2. 添加充分的註解說明
3. 測試新增的功能
4. 更新相關文件

---

## 📄 授權

本專案遵循與主專案相同的授權條款。

---

**最後更新**: 2026-03-11
**維護者**: Guarding Agent 團隊
