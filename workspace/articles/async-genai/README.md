# Python 非同步程式設計與生成式 AI 架構

## 一、核心概念

| # | 主題 | 說明 |
|---|------|------|
| 1.1 | [非同步 I/O](./01-async_core_principles/async_io_principles.md) | 非阻塞 Socket、事件循環、單執行緒非同步模型 |
| 1.2 | [關鍵語法](./01-async_core_principles/async_core_concepts.md) | 協程、任務、期約、可等待物件 |
| 1.3 | [併發 vs 並行](./01-async_core_principles/concurrency_vs_parallelism.md) | 多執行緒、多進程、GIL 機制 |

## 二、開發框架與工具

| # | 類別 | 框架/工具 | 說明 |
|---|------|---------|------|
| 2.1 | [Web 框架](./02-async_framework_design/framework_design_best_practices.md) | FastAPI、Django 4.x、Quart & Flask 3.x | 非同步 Web 框架開發 |
| 2.2 | [非同步庫](./02-async_framework_design/async_libraries_architectural_perspective.md) | aiohttp、asyncpg、Trio | 非同步 HTTP、資料庫、生命週期管理 |

## 三、生成式 AI 設計模式

| # | 模式 | 技術 | 說明 |
|---|------|------|------|
| 3.1 | 內容控制 | Logits Masking | 規則控制 |
| 3.2 | 內容控制 | Grammar | 格式約束 |
| 3.3 | 內容控制 | Style Transfer | 風格轉換 |
| 3.4 | 知識增強 | RAG | 檢索增強生成 |
| 3.5 | 知識增強 | Semantic Indexing | 語意索引 |
| 3.6 | 知識增強 | Deep Search | 深度檢索 |
| 3.7 | 模型擴展 | Chain of Thought | 思維鏈 |
| 3.8 | 模型擴展 | Tree of Thoughts | 思維樹 |
| 3.9 | 模型擴展 | Adapter Tuning | 輕量微調 |

## 四、實際應用與部署

| # | 領域 | 技術 | 說明 |
|---|------|------|------|
| 4.1 | 數據工程 | ETL / ELT | 管道設計 |
| 4.2 | 數據工程 | GraphRAG | 圖譜檢索 |
| 4.3 | AI 代理 | Tool Calling | 工具調用 |
| 4.4 | AI 代理 | Multi-agent | 多代理協作 |
| 4.5 | AI 代理 | MCP 協議 | 標準通訊 |
| 4.6 | 效能優化 | 模型量化 | Quantization |
| 4.7 | 效能優化 | 推測解碼 | Speculative Decoding |
| 4.8 | 效能優化 | 提示詞快取 | Prompt Caching |

## 五、系統安全與穩定性

| # | 面向 | 技術 | 說明 |
|---|------|------|------|
| 5.1 | 安全性 | 提示詞注入 | Prompt Injection 防護 |
| 5.2 | 安全性 | Guardrails | 防護機制 |
| 5.3 | 測試監控 | LLM-as-Judge | 模型評估 |
| 5.4 | 測試監控 | 退化測試 | Degradation Testing |
| 5.5 | 測試監控 | 漂移檢測 | Drift Detection |

## 參考資源
- **Asynchronous Programming in Python (Packt)**
    *   官方書籍連結：[www.packtpub.com](https://www.packtpub.com/en-tw/product/asynchronous-programming-in-python-9781836646600)
    *   官方程式碼：[GitHub - PacktPublishing/Asynchronous-Programming-in-Python](https://github.com/PacktPublishing/Asynchronous-Programming-in-Python)

- **Generative AI Design Patterns (O'Reilly)**
    *   官方書籍連結：[oreil.ly/genAI-design-patterns](https://oreil.ly/genAI-design-patterns)
    *   官方程式碼：[GitHub - lakshmanok/generative-ai-design-patterns](https://github.com/lakshmanok/generative-ai-design-patterns)

- **Building Generative AI Services with FastAPI (O'Reilly)**
    *   官方書籍連結：[oreil.ly/building-gen-ai-fastAPI](https://oreil.ly/building-gen-ai-fastAPI)
    *   書籍配套網站：[buildinggenai.com](https://buildinggenai.com)
    *   官方程式碼：[GitHub - Ali-Parandeh/building-generative-ai-services](https://github.com/Ali-Parandeh/building-generative-ai-services)

- **GenAI on Google Cloud (O'Reilly)**
    *   官方書籍連結：[oreil.ly/GenAI_on_Google](https://oreil.ly/GenAI_on_Google)
    *   官方程式碼：[GitHub - ayoisio/genai-on-google-cloud](https://github.com/ayoisio/genai-on-google-cloud)

- **Python Concurrency with asyncio (Manning)**
    *   官方書籍連結：[manning.com/books/python-concurrency-with-asyncio](https://www.manning.com/books/python-concurrency-with-asyncio)
    *   官方程式碼：[GitHub - concurrency-in-python-with-asyncio](https://github.com/concurrency-in-python-with-asyncio)

## 【免責聲明與版權聲明】
本文內容係基於個人學習筆記及多本技術書籍、官方文件與網路資源彙整而成。旨在分享技術經驗，不構成任何形式的專業建議。

- **內容準確性**： 本人已盡力確保內容之正確性，但技術環境變化迅速，內容可能隨時間而過時或存在疏漏。
- **實作風險**： 讀者在參照本文進行實作（如修改代碼、調整系統設定）時，應自行承擔相關風險。本人對於因使用本文資訊而導致的任何直接或間接損失，概不負責。
- **版權說明**： 文中引用之技術資源版權均屬原作者或出版社所有。若有**侵權疑慮**，請聯繫本人進行移除或修正。