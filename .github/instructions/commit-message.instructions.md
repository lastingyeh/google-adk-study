---
applyTo: '**'
---
# Commit Message 指南 (Based on README `Day x`)

使用根目錄 `README.md` 中的對應章節標題 (e.g. "Day 3") 作為每次提交開頭，確保訊息可追溯到學習日次與內容主題。

## 格式
```
Day <x>: <簡短主題>/<子範圍> - <一句話摘要>
```

## 範例
```
Day 5: sensor-api - 新增溫溼度讀取與錯誤處理
```

## 內文建議 (可選)
- 背景：本次異動目的 (如：增強、修正、重構)
- 位置摘要：說明主要影響的目錄/模組
- 變更類型：feat / fix / refactor / docs / chore / test / perf / build
- 依賴：新增或調整的外部套件 (若有)

## Changed Files 區塊
以清單列出檔案與簡述：
```
Changed:
- src/sensors/temperature.ts: 新增溫度讀取函式
- src/sensors/humidity.ts: 抽離共用解析邏輯
- README.md: 更新 Day 5 說明
```

## 命名與語氣
- 摘要使用動詞原形或過去式皆可，保持一致
- 不使用冗長敘述與主觀語氣
- 避免含糊字詞 (e.g. "misc", "update stuff")

## 驗收清單 (可選)
```
Checklist:
- [ ] 已更新 README Day <x> 區段
- [ ] 相關測試新增或通過
- [ ] 無破壞既有 API
```

## 快速模板
```
Day <x>: <scope> - <summary>

<optional background / rationale>

Changed:
- <file>: <reason>
- <file>: <reason>

Checklist:
- [ ] README Day <x> updated
- [ ] Tests pass
```

保持單一提交專注於同一 Day 的合理範圍，跨日內容請分開提交。