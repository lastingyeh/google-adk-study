# 電腦使用代理 (Computer Use Agent)

此目錄包含一個能操作瀏覽器以完成使用者任務的電腦使用代理。該代理使用 Playwright 控制 Chromium 瀏覽器，並可透過擷取螢幕截圖、點擊、輸入與導航與網頁互動。

此代理用於展示 `ComputerUseToolset` 的使用。

## 概述

電腦使用代理包含：
- `agent.py`：主要代理設定，使用 Google's `gemini-2.5-computer-use-preview-10-2025` 模型
- `playwright.py`：基於 Playwright 的瀏覽器自動化實作
- `requirements.txt`：Python 相依套件

## 設定

### 1. 安裝 Python 相依套件

從 requirements 檔案安裝所需的 Python 套件：

```bash
uv pip install -r requirements.txt
```

### 2. 安裝 Playwright 相依項目

為 Chromium 安裝 Playwright 的系統相依項目：

```bash
playwright install-deps chromium
```

### 3. 安裝 Chromium 瀏覽器

為 Playwright 安裝 Chromium 瀏覽器：

```bash
playwright install chromium
```

## 使用方式

### 啟動代理

要啟動電腦使用代理，從專案根目錄執行以下指令：

```bash
adk web
```

這會啟動 ADK 網頁介面，您可以在其中與 `computer_use` 代理互動。

### 範例查詢

代理啟動後，您可以發送如下一類查詢：

請幫我找一張從舊金山（SF）到夏威夷的機票，出發在下週一，回程在下週五。請先直接前往 flights.google.com。

該代理會：
1. 開啟瀏覽器視窗
2. 導航到指定網站
3. 與頁面元素互動以完成任務
4. 提供其進度更新

### 其他範例任務

- 訂房
- 在線搜尋商品
- 填寫表單
- 瀏覽複雜網站
- 在多個頁面間蒐集資訊

## 技術細節

- **模型**：使用 Google's `gemini-2.5-computer-use-preview-10-2025` 模型來提供電腦操作能力
- **瀏覽器**：透過 Playwright 自動化 Chromium 瀏覽器
- **畫面解析度**：設定為 600x800
- **工具**：使用 `ComputerUseToolset` 進行螢幕擷取、點擊、輸入與捲動

## 疑難排解

若遇到問題：

1. **找不到 Playwright**：確認已執行 `playwright install-deps chromium` 與 `playwright install chromium`
2. **相依套件遺失**：確認已安裝 `requirements.txt` 中的所有套件
3. **瀏覽器當機**：檢查系統是否支援 Chromium 並確認資源充足
4. **權限錯誤**：確認使用者有執行瀏覽器自動化工具的權限

## 注意事項

- 代理在受控瀏覽器環境中運作
- 會擷取螢幕截圖以協助代理理解當前狀態
- 代理會在執行動作時提供進度更新
- 複雜任務可能需要一些時間，請耐心等候

## 更多說明

#### 實現操作功能表整理，細節請參閱 [playwright.py](./computer_use/playwright.py)。

| 工具名稱 | 功能描述 |
| :--- | :--- |
| `open_web_browser` | 開啟並初始化網頁瀏覽器實例。 |
| `click_at` | 在指定的 (x, y) 座標執行滑鼠點擊。 |
| `hover_at` | 將滑鼠游標移動到指定的 (x, y) 座標。 |
| `type_text_at` | 在指定座標點擊並輸入文字，可選擇是否按下 Enter 或在輸入前清空。 |
| `scroll_document` | 根據方向（上、下、左、右）捲動整個網頁文件。 |
| `scroll_at` | 在特定座標點執行指定方向與強度的滾輪捲動。 |
| `wait` | 讓代理暫停指定秒數。 |
| `go_back` | 導航回瀏覽歷史記錄中的前一個頁面。 |
| `go_forward` | 導航至瀏覽歷史記錄中的下一個頁面。 |
| `search` | 開啟預設的搜尋引擎頁面。 |
| `navigate` | 導航至指定的網址 (URL)。 |
| `key_combination` | 模擬按下組合鍵（如 Ctrl+A, Delete 等）。 |
| `drag_and_drop` | 將元素從起始座標拖曳並投放到目標座標。 |

## 參考資料
- [[ADK-Samples] Computer Use](https://github.com/google/adk-python/tree/main/contributing/samples/computer_use)
- [Gemini API 模型文件](https://ai.google.dev/gemini-api/docs/computer-use)