# 教學 21：多模態與影像處理

本教學完整實作了教學 21，展示了具備影像處理能力的視覺化 AI 代理 (Agent)。

### 重點摘要
- **核心概念**：建立一個能夠理解、分析並生成產品圖片的 AI 代理。
- **關鍵技術**：使用 Gemini 視覺模型、多模態內容 (`types.Part`) 處理、成品管理 (Artifact management) 以及透過 Makefile 實現自動化。
- **重要結論**：本專案展示如何結合多種 AI 技術來解決實際的商業問題，例如自動生成產品目錄。
- **行動項目**：依照快速入門指南，設定環境、下載範例圖片並啟動代理，以體驗其完整功能。

## 概覽

這個實作展示了：
- 使用 Gemini 視覺模型處理圖片
- 使用 `types.Part` 處理多模態內容
- 建立基於視覺的產品目錄分析器
- 處理多個圖片輸入
- 產品目錄條目的成品管理

## 專案結構

```
tutorial21/
├── Makefile                    # 包含說明系統的易用建置自動化工具
├── requirements.txt            # Python 依賴套件
├── pyproject.toml             # 套件組態設定
├── .env.example               # 環境變數範本
├── vision_catalog_agent/      # 主要代理套件
│   ├── __init__.py
│   └── agent.py              # 視覺目錄代理 (5 個工具)
├── _sample_images/            # 範例產品圖片 (_ 前綴可避免 ADK 發現)
├── download_images.py         # 從 Unsplash 下載範例圖片
├── analyze_samples.py         # 批次分析所有範例圖片
├── generate_mockups.py        # 生成合成產品模型 ⭐
├── demo.py                    # 互動式示範腳本
└── tests/                     # 完整的測試套件 (70 個測試)
    ├── test_agent.py          # 代理組態設定測試
    ├── test_imports.py        # 匯入驗證
    ├── test_structure.py      # 專案結構驗證
    └── test_multimodal.py     # 多模態功能測試
```

### 自動化腳本

**download_images.py**：從 Unsplash 下載範例產品圖片
- 取得高品質的產品照片 (筆記型電腦、耳機、智慧手錶)
- 儲存至 `_sample_images/` 目錄
- 可根據 Unsplash 授權免費使用
- 執行方式：`make download-images` 或 `python download_images.py`

**analyze_samples.py**：批次分析所有範例圖片
- 使用正確的多模態內容處理方式載入每張圖片
- 使用 Gemini 2.0 Flash Exp 視覺模型進行分析
- 生成專業的產品目錄條目
- 顯示包含產品詳細資訊的格式化結果
- 執行方式：`make analyze` 或 `python analyze_samples.py`

**generate_mockups.py**：生成合成產品模型 ⭐ 新功能
- 使用 Gemini 2.5 Flash Image 進行文字轉圖片
- 建立 3 種產品：桌燈、皮革錢包、電競滑鼠
- 每種產品使用不同的長寬比 (1:1, 4:3, 16:9)
- 自動分析生成的圖片
- 端到端工作流程示範
- 執行方式：`make generate` 或 `python generate_mockups.py`

**demo.py**：互動式示範腳本 (舊版)
- 命令列示範代理功能
- 注意：建議使用 `make demo` 以獲得更全面的範例

## 功能

### 🎨 合成影像生成 ⭐ 新功能
- 使用 Gemini 2.5 Flash Image 生成產品模型
- 非常適合在拍攝前進行原型設計
- 文字轉圖片，具有專業的產品攝影風格
- 多種長寬比 (1:1, 16:9, 4:3, 3:2 等)
- 適合測試目錄設計和概念

### 影像處理
- 從檔案載入圖片 (PNG, JPEG, WEBP, HEIC)
- 最佳化圖片以提高 API 效率
- 處理多種圖片格式
- 建立用於測試的範例圖片

### 視覺分析
- 使用 Gemini 視覺分析產品圖片
- 提取視覺特徵和特性
- 識別產品及其屬性
- 比較多張圖片

### 目錄生成
- 生成專業的產品描述
- 將目錄條目儲存為成品 (artifacts)
- 結構化的 markdown 輸出
- 可直接用於行銷的內容

### 多代理工作流程
1.  **視覺分析器 (Vision Analyzer)**：分析圖片並提取資訊
2.  **目錄生成器 (Catalog Generator)**：建立專業的目錄條目
3.  **影像生成器 (Image Generator)**：建立合成的產品模型
4.  **協調器 (Coordinator)**：協調整個工作流程

## 快速入門

### 首次設定

```bash
# 1. 查看所有可用指令
make                # 或: make help

# 2. 安裝依賴套件
make setup

# 3. 設定您的 API 金鑰 (擇一即可)
export GOOGLE_API_KEY=your_api_key_here

# 4. 下載範例圖片
make download-images

# 5. 啟動代理
make dev
```

Makefile 包含一個完整的說明系統。只需執行 `make` 即可查看所有可用指令！

### 可用指令

```bash
make                  # 顯示說明 (預設)
make setup            # 安裝依賴套件
make download-images  # 從 Unsplash 取得範例產品圖片
make dev              # 啟動 ADK 網站介面 (http://localhost:8000)
make demo             # 顯示完整的使用範例

# 影像分析
make analyze          # 批次分析所有範例圖片
make generate         # 生成合成產品模型 ⭐

# 開發與測試
make test             # 執行所有測試
make coverage         # 執行測試並產出覆蓋率報告
make lint             # 執行程式碼檢查工具
make clean            # 清除生成的檔案
```

### 環境驗證

Makefile 會在執行需要驗證的指令前自動檢查。如果未設定，您將看到包含設定說明的實用錯誤訊息。

**驗證方式：**

1.  **API 金鑰 (建議開發時使用)**：
    ```bash
    export GOOGLE_API_KEY=your_api_key_here
    # 在此取得免費金鑰：https://aistudio.google.com/app/apikey
    ```

2.  **服務帳戶 (用於生產環境)**：
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    export GOOGLE_CLOUD_PROJECT=your_project_id
    ```

## 使用範例

### 分析單一產品圖片

```python
from google.adk.agents import Runner
from vision_catalog_agent import root_agent

runner = Runner()
result = await runner.run_async(
    "分析 sample_images/laptop.jpg 並建立一個目錄條目",
    agent=root_agent
)
print(result.content.parts[0].text)
```

### 比較多張圖片

```python
result = await runner.run_async(
    "比較 sample_images/ 中的筆記型電腦和耳機圖片",
    agent=root_agent
)
```

### 批次處理產品

代理可以依序分析多個產品：

```python
result = await runner.run_async(
    "分析 sample_images/ 目錄中的所有圖片",
    agent=root_agent
)
```

## 範例提示

在 ADK 網站介面中試試這些提示：

### 使用上傳的圖片 (建議)

使用此代理最簡單的方式是在網站介面中直接上傳圖片：

1.  **上傳並分析** (拖放或貼上圖片)：

    ```text
    分析這張筆記型電腦圖片並建立一個目錄條目
    ```

    -   只需將圖片拖放到聊天室中
    -   或從剪貼簿貼上圖片
    -   代理將自動分析上傳的圖片

2.  **多張上傳圖片**：

    ```text
    比較這兩張產品圖片
    ```

    -   透過將多張圖片一起拖曳來上傳
    -   代理可以比較並分析它們

3.  **專業目錄**：

    ```text
    為此項目建立一個專業的產品目錄條目
    ```

    -   上傳一張產品圖片
    -   取得可用於行銷的描述

### 使用檔案路徑

如果您已將圖片儲存在本機，可以透過路徑引用它們：

1.  **基本分析**：

    ```text
    分析筆記型電腦圖片並描述你看到了什麼
    ```

2.  **目錄條目**：

    ```text
    為耳機圖片建立一個專業的目錄條目
    ```

3.  **比較**：

    ```text
    比較筆記型電腦和智慧手錶的圖片
    ```

4.  **批次處理**：

    ```text
    分析所有產品圖片並生成目錄條目
    ```

### 自動化批次分析

若要以程式化方式分析所有範例圖片，請使用提供的腳本：

```bash
# 一個指令分析所有範例圖片
python analyze_samples.py
```

此腳本將會：
-   分析所有三張範例產品圖片 (筆記型電腦、耳機、智慧手錶)
-   為每個產品生成專業的目錄條目
-   顯示詳細的視覺分析和市場定位
-   以乾淨、格式化的輸出顯示結果

**輸出內容包括**：
-   產品識別與類別
-   視覺特徵 (顏色、設計、材質)
-   品質指標與結構細節
-   獨特功能與賣點
-   市場定位與目標客群
-   專業的行銷描述

**範例輸出**：

```
================================================================================
圖片 1/3：專業筆記型電腦 (laptop.jpg)
產品 ID：LAPTOP-001
================================================================================

產品分析：專業筆記型電腦 (LAPTOP-001)

1. 產品識別：用於專業用途的高階筆記型電腦

2. 視覺特徵：
   - 顏色：時尚的銀/灰色鋁製外殼，黑色鍵盤
   - 設計：現代、極簡、輕薄外型 (13-15 吋)
   - 材質：鋁合金機身，高品質鍵盤

3. 品質指標：堅固的結構，平滑的表面，穩固的轉軸

4. 獨特功能：窄邊框，高階外觀，高解析度顯示器

5. 市場定位：針對專業人士和創意工作者的高階市場

目錄條目：
[接著是專業的行銷描述...]
```

**優點**：
-   一個指令即可分析所有範例
-   無需手動操作網站介面
-   非常適合示範與測試
-   生成可用於生產環境的目錄條目
-   展示代理的多模態能力

### 合成影像生成 ⭐ 新功能

當您還沒有真實照片時，生成專業的產品模型：

```bash
# 生成合成產品圖片
python generate_mockups.py

# 或使用 Makefile 目標
make generate
```

此功能使用 **Gemini 2.5 Flash Image** 從文字描述建立逼真的產品圖片。

**會生成什麼**：
-   極簡風格桌燈 (現代、鋁製、LED)
-   高級皮革錢包 (棕色皮革、金色縫線)
-   無線電競滑鼠 (RGB 燈效、人體工學)

**在 ADK 網站介面中**：

```text
生成一張帶有髮絲紋鋁製表面的極簡風格桌燈的合成圖片
```

代理將會：
1.  使用 `generate_product_mockup()` 工具
2.  建立一張逼真的產品圖片
3.  將其儲存至 `_sample_images/`
4.  自動分析生成的圖片
5.  提供一個專業的目錄條目

**使用案例**：
-   🎨 **快速原型製作**：在投入攝影前測試目錄設計
-   💡 **概念視覺化**：向客戶展示產品可能的外觀
-   🔄 **變化版本**：快速生成多種風格/顏色的變化版本
-   📐 **版面測試**：為不同的長寬比建立模型
-   💰 **節省成本**：無需攝影棚設備或攝影師

**範例提示**：
```text
• "生成一個帶有筆電隔層的高級皮革背包模型"
• "建立一個帶有 LED 顯示器的智慧水瓶的合成圖片"
• "為一個極簡風格的無線充電器生成產品攝影"
• "製作一個霧面黑的降噪耳塞模型"
```

**支援的風格**：
-   逼真的產品攝影 (預設)
-   攝影棚燈光搭配白色/乾淨背景
-   生活風格/情境攝影
-   藝術/創意產品照
-   自訂燈光與角度

**可用的長寬比**：
-   1:1 (1024x1024) - 適合社群媒體
-   16:9 (1344x768) - 寬幅產品照
-   4:3 (1184x864) - 標準產品照
-   3:2 (1248x832) - 專業攝影
-   以及更多 (請參閱 Gemini 2.5 Flash Image 文件)

## 架構

### 元件

1.  **圖片工具**
    -   `load_image_from_file()`：將圖片載入為 types.Part
    -   `optimize_image()`：最佳化圖片大小
    -   `create_sample_image()`：生成測試圖片

2.  **視覺分析器代理 (Vision Analyzer Agent)**
    -   模型：`gemini-2.0-flash-exp`
    -   溫度 (Temperature)：0.3 (事實分析)
    -   分析產品圖片
    -   提取視覺特徵

3.  **目錄生成器代理 (Catalog Generator Agent)**
    -   模型：`gemini-2.0-flash-exp`
    -   溫度 (Temperature)：0.6 (創意寫作)
    -   生成行銷內容
    -   儲存成品

4.  **根代理 (Coordinator)**
    -   協調工作流程
    -   將請求路由到適當的工具
    -   管理多圖片操作

### 工具 (5 個可用)

`vision_catalog_agent` 提供了 5 個專門的工具：

1.  **`list_sample_images()`**：發現可用的範例圖片
    -   列出 `_sample_images/` 目錄中的圖片
    -   顯示檔案名稱與路徑
    -   幫助使用者探索可用的範例
    -   範例："你有什麼範例圖片？"

2.  **`generate_product_mockup()`**：生成合成產品圖片 ⭐ 新功能
    -   使用 Gemini 2.5 Flash Image 模型
    -   建立逼真的產品攝影
    -   可設定長寬比 (1:1, 16:9, 4:3, 3:2 等)
    -   可自訂風格 (逼真、攝影棚、生活風格)
    -   儲存至 `_sample_images/` 目錄
    -   回傳圖片路徑以供進一步分析
    -   範例："生成一個極簡風格桌燈的模型"

3.  **`analyze_uploaded_image()`**：從網站介面分析圖片
    -   提供拖放上傳的指引
    -   指導使用者如何使用網站介面
    -   互動式分析的最佳方法
    -   無需檔案路徑
    -   範例：[上傳圖片] "分析這個產品"

4.  **`analyze_product_image(path: str)`**：針對檔案的完整分析流程
    -   接受檔案路徑作為輸入
    -   使用多模態內容處理方式載入圖片
    -   使用 Gemini 2.0 Flash Exp 視覺進行分析
    -   生成專業的目錄條目
    -   將結果儲存為成品
    -   回傳詳細的產品資訊
    -   範例："分析 _sample_images/laptop.jpg"

5.  **`compare_product_images(paths: List[str])`**：多圖片比較
    -   比較多張產品圖片
    -   識別相似點與差異點
    -   分析跨產品的視覺特徵
    -   提供比較性的見解
    -   適用於產品線分析
    -   範例："比較筆記型電腦和耳機的圖片"

### 子代理 (Sub-Agents)

協調器使用專門的子代理來執行不同任務：

-   **視覺分析器代理 (Vision Analyzer Agent)**：分析圖片並提取視覺資訊
    -   模型：`gemini-2.0-flash-exp`
    -   溫度 (Temperature)：0.3 (事實、精確的分析)
    -   專注於客觀的視覺特徵

-   **目錄生成器代理 (Catalog Generator Agent)**：建立專業的目錄條目
    -   模型：`gemini-2.0-flash-exp`
    -   溫度 (Temperature)：0.6 (創意、引人入勝的內容)
    -   生成可用於行銷的描述
    -   將結果儲存為成品

## 測試

完整的測試套件，包含 **70 個測試** 和 **63% 的覆蓋率**：

```bash
# 執行所有測試 (包含環境驗證)
make test

# 執行並產出詳細的覆蓋率報告
make coverage

# 手動執行測試
pytest tests/ -v

# 執行特定的測試檔案
pytest tests/test_multimodal.py -v

# 執行並計算覆蓋率 (手動)
pytest tests/ --cov=vision_catalog_agent --cov-report=html --cov-report=term
```

### 測試類別

1.  **匯入測試** (`test_imports.py`)：
    -   驗證所有匯入是否正常
    -   驗證工具函式匯入
    -   檢查代理是否可用

2.  **代理組態設定** (`test_agent.py`)：
    -   檢查代理設定與屬性
    -   驗證工具數量 (5 個工具)
    -   測試工具簽章與可呼叫性
    -   驗證模型組態設定

3.  **結構測試** (`test_structure.py`)：
    -   驗證專案結構
    -   檢查必要檔案是否存在
    -   驗證套件安裝

4.  **多模態測試** (`test_multimodal.py`)：
    -   測試圖片處理工具
    -   驗證多模態內容處理
    -   檢查圖片格式支援

### 測試結果

```bash
$ make test
🧪 正在執行測試...
pytest tests/ -v --tb=short

======================== 測試會話開始 =========================
收集到 70 個項目

tests/test_agent.py::TestAgentConfig::test_agent_exists PASSED    [  1%]
tests/test_agent.py::TestAgentConfig::test_agent_type PASSED      [  2%]
...
tests/test_multimodal.py::TestMultimodal::test_all PASSED         [100%]

========================= 70 個通過，耗時 2.45 秒 =========================
```

### 覆蓋率報告

執行 `make coverage` 以生成詳細的 HTML 覆蓋率報告：

```bash
$ make coverage
🧪 正在執行測試並計算覆蓋率...

覆蓋率：63%
✅ 覆蓋率報告已生成！
📊 開啟 htmlcov/index.html 查看詳細報告
```

## Makefile 功能

本教學包含一個功能完整的 Makefile：

### 🚀 說明系統

執行 `make` 或 `make help` 查看所有可用指令，並分為：

-   **快速入門指令**：設定、下載範例、啟動代理
-   **影像分析指令**：批次分析、生成合成模型
-   **進階指令**：測試、覆蓋率、檢查、清除

### ✅ 環境驗證

Makefile 會在執行指令前自動驗證：

-   檢查 `GOOGLE_API_KEY` 或 `GOOGLE_APPLICATION_CREDENTIALS`
-   顯示包含設定說明的清晰錯誤訊息
-   支援 Gemini API 和 Vertex AI 驗證
-   防止常見的組態設定錯誤

### 📊 視覺化輸出

所有指令都提供清晰、帶有表情符號的回饋：

-   操作過程中的進度指示
-   包含後續步驟的成功確認
-   詳細的工作流程描述
-   互動式指令的範例提示

### 🎯 範例工作流程

**首次使用者路徑：**
```bash
make                      # 查看所有指令
make setup                # 安裝依賴套件
export GOOGLE_API_KEY=... # 設定驗證
make download-images      # 取得範例圖片
make dev                  # 啟動互動式代理
```

**開發工作流程：**
```bash
make generate    # 生成合成模型
make analyze     # 分析所有範例
make test        # 執行測試
make coverage    # 檢查覆蓋率
```

**生產工作流程：**
```bash
make lint        # 驗證程式碼
make test        # 執行完整測試套件
make clean       # 清除成品
```

## 組態設定

### 環境變數

```bash
# 必要 (擇一即可)
GOOGLE_API_KEY=your_api_key_here

# 或用於 Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# 選用：Vertex AI 區域
GOOGLE_CLOUD_LOCATION=us-central1
```

### 模型選擇

目前模型：

-   `gemini-2.0-flash-exp`：最新支援視覺的版本
-   替代方案：`gemini-1.5-pro`、`gemini-1.5-flash`

## 最佳實踐

### 圖片最佳化

-   保持圖片小於 500KB
-   調整大圖片尺寸 (最大 1024px)
-   使用 JPEG 以獲得最佳化大小
-   必要時將 RGBA 轉換為 RGB

### 多模態內容

-   為圖片提供清晰的上下文
-   使用結構化的查詢格式
-   清楚標示多張圖片
-   使用各種圖片格式進行測試

### 錯誤處理

-   驗證檔案是否存在
-   檢查 MIME 類型
-   優雅地處理 PIL/Pillow
-   提供有意義的錯誤訊息

## 疑難排解

### 常見問題

**問題**：PIL/Pillow 的匯入錯誤

```bash
pip install Pillow
```

**問題**：在 ADK 網站中找不到代理

```bash
pip install -e .
```

**問題**：ADK 嘗試將目錄作為代理載入

-   解決方案：對非代理目錄使用 `_` 前綴 (`_sample_images`)
-   ADK 會自動忽略以 `_` 或 `.` 開頭的目錄
-   從下拉選單中選擇 `vision_catalog_agent`

**問題**：不支援的圖片格式

-   確保副檔名與內容相符
-   轉換為 PNG 或 JPEG
-   檢查 MIME 類型偵測

**問題**：未設定 API 金鑰

```bash
export GOOGLE_API_KEY=your_key
```

## 效能考量

-   圖片最佳化可降低 API 成本
-   對多張圖片進行批次處理
-   適當時快取分析結果
-   監控大圖片的 token 使用量

## 限制

-   最大圖片大小：約 20MB
-   支援格式：PNG, JPEG, WEBP, HEIC
-   適用 API 速率限制
-   大圖片的 token 限制

## 未來增強功能

-   [ ] 使用 Imagen 生成圖片
-   [ ] 影片影格分析
-   [ ] 即時攝影機整合
-   [ ] 進階 OCR 功能
-   [ ] 自訂視覺模型

## 範例圖片

`_sample_images/` 目錄包含用於示範的範例產品圖片：

-   **laptop.jpg**：現代筆記型電腦
-   **headphones.jpg**：無線耳機
-   **smartwatch.jpg**：智慧手錶裝置

**圖片來源**：範例圖片來自 [Unsplash](https://unsplash.com)。
可根據 [Unsplash 授權](https://unsplash.com/license) 免費使用。

若要下載新的範例圖片，請執行：

```bash
python download_images.py
```

## 資源

-   [教學文件](../../docs/tutorial/21_multimodal_image.md)
-   [Gemini Vision 文件](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/overview)
-   [ADK 文件](https://github.com/google/adk-python)
-   [Types.Part 參考](https://ai.google.dev/api/python/google/generativeai/protos/Part)
-   [Unsplash](https://unsplash.com) - 免費高品質圖片

## 授權

ADK 訓練專案的一部分。有關授權詳細資訊，請參閱主儲存庫。

範例圖片來自 Unsplash，並根據 Unsplash 授權使用。

## 支援

如有問題或疑問：

1.  查看現有測試以獲取範例
2.  檢閱教學文件
3.  查閱 ADK 文件
4.  在主儲存庫中開啟一個 issue
