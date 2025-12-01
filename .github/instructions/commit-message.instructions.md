---
applyTo: '**'
---
# Commit Message 生成提示

請根據以下規則，為本次提交生成一則符合規範的 Commit Message。

## 核心邏輯

1.  **分析 `README.md`**：
  -   檢查 `README.md` 是否在本次異動檔案清單中。
  -   若是，找出 `README.md` 中被修改的**最新** `Day <x>` 章節標題。
  -   將 `Day <x>` 作為 Commit Message 的開頭。
  -   根據該 `Day <x>` 章節的內容，生成一個簡潔的摘要 (summary)。

2.  **若 `README.md` 未變動**：
  -   如果 `README.md` 不在異動清單中，或沒有 `Day <x>` 相關的更新。
  -   請分析**其他**被修改的檔案 (`{{changed_files}}`)。
  -   從檔案變更中推斷出一個合適的 `<scope>` 和 `<summary>`。
  -   Commit Message 開頭**不使用** `Day <x>`。

## 輸出格式

### 情況一：`README.md` 已更新 `Day <x>`

```
Day <x>: <scope> - <summary>

背景：根據 Day <x> 的學習內容，實作/更新/修正相關功能。

Changed:
{{#each changed_files}}
- {{path}}: {{summary}}
{{/each}}

Checklist:
- [x] README Day <x> updated
- [ ] Tests pass
```
- `<x>`: `README.md` 中最新的天數。
- `<scope>`: 根據 Day <x> 內容推斷出的主要模組或主題。
- `<summary>`: 對 Day <x> 內容的高度概括。

### 情況二：其他變更

```
<scope> - <summary>

背景：<說明本次異動的目的，例如：修正錯誤、重構程式碼等>

Changed:
{{#each changed_files}}
- {{path}}: {{summary}}
{{/each}}
```
- `<scope>`: 從異動檔案推斷出的影響範圍。
- `<summary>`: 總結本次所有檔案的變更。

---
**範例情境**

假設本次提交包含以下檔案變更：
- `README.md` (新增了 `## Day 5: Sensor API` 內容)
- `src/sensors/temperature.ts` (新增讀取函式)
- `src/sensors/humidity.ts` (新增讀取函式)

**預期生成的 Commit Message:**

```
Day 5: sensor-api - 實作溫溼度感測器 API

背景：根據 Day 5 的學習內容，實作溫溼度感測器的讀取功能。

Changed:
- README.md: 新增 Day 5 學習進度與 Sensor API 說明
- src/sensors/temperature.ts: 新增溫度感測器讀取函式
- src/sensors/humidity.ts: 新增溼度感測器讀取函式

Checklist:
- [x] README Day 5 updated
- [ ] Tests pass
```