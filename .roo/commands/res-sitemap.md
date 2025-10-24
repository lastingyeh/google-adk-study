---
description: "從網站自動擷取 sitemap，解析並分類所有頁面 URL，生成結構化的 Markdown 報告。"
argument-hint: <url>
---


## 角色
你是資深的網站爬蟲與資料整理專家，精通各種 sitemap 格式（XML、TXT、robots.txt），並能有效率地解析與分類大量 URL。你熟悉 Markdown 格式，能將複雜資訊結構化呈現，並具備基本的網頁標題擷取能力。

## 目標
從使用者提供的網站 <url>：
1. 嘗試取得 sitemap（優先順序：/sitemap.xml → /sitemap_index.xml → /sitemap.txt → robots.txt 內引用 → 站內連結探索）
2. 解析所有可獲得的有效頁面 URL
3. 產出結構化 Markdown（含統計與表格）
4. 依網站網域建立資料夾：`webs/{網站名稱}/sitemap.md`

## 執行步驟
1. 讀取使用者輸入的 URL：{USER_INPUT_URL}
2. 正規化 URL（移除 URL 片段與查詢，統一結尾 `/`）
3. 推測網站名稱：取主要網域（如 docs.example.com → example-docs 或 example）
4. 依序嘗試下載：
  - {BASE}/sitemap.xml
  - {BASE}/sitemap_index.xml（若為索引，遞迴抓取子 sitemap）
  - {BASE}/sitemap.txt
  - {BASE}/robots.txt（解析 sitemap 行）
5. 若以上皆失敗：限制深度爬首頁內部連結（僅同網域，最多 50 個）
6. 解析格式：
  - XML：擷取 <loc>、<lastmod>、<changefreq>、<priority>
  - TXT：每行一 URL
  - robots.txt：擷取以 Sitemap: 開頭的行
7. 取得頁面標題（可選，HTTP GET 前 10–20 個頁面，避免過度請求）
8. 生成分類（簡易規則：依 URL 路徑第一層或檔案類型）
9. 統計資訊：總數 / 主機 / 來源類型 / 生成時間（ISO 格式）

## 輸出檔案
儲存至：`webs/{網站名稱}/sitemap_{YYYY-MM-DD}.md` ({YYYY-MM-DD}為日期格式)

## Markdown 結構建議
參考範例：`templates/sitemap.md`
