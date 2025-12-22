# Sitemap NPM Scripts 快速參考

## 快速使用

直接使用 npm 執行預定義的 sitemap 任務。

## 可用命令

### 顯示幫助

```bash
npm run sitemap -- help
```

### Google ADK 文檔

```bash
# 抓取並儲存為 YAML
npm run sitemap:adk

# 抓取並生成 Markdown
npm run sitemap:adk:md
```

### A2A Protocol 文檔

```bash
# 抓取並儲存為 YAML
npm run sitemap:a2a

# 抓取並生成 Markdown
npm run sitemap:a2a:md
```

### Model Context Protocol (MCP) 文檔

```bash
# 抓取並儲存為 YAML
npm run sitemap:mcp

# 抓取並生成 Markdown
npm run sitemap:mcp:md
```

## 自訂命令

如果需要使用其他參數，可以直接執行腳本：

```bash
# 傳遞額外參數
npm run sitemap -- fetch <url> --format <format> [options]

# 或直接使用 node
node scripts/sitemap.js fetch <url> --format <format> [options]
```

## 範例

### 快速抓取所有文檔為 YAML 格式

```bash
npm run sitemap:adk
npm run sitemap:a2a
npm run sitemap:mcp
```

### 快速生成所有 Markdown 文檔

```bash
npm run sitemap:adk:md
npm run sitemap:a2a:md
npm run sitemap:mcp:md
```

### 自訂輸出

```bash
# 輸出為 JSON
node scripts/sitemap.js fetch https://example.com/sitemap.xml -f json -o my-sitemap.json

# 輸出為 CSV
node scripts/sitemap.js fetch https://example.com/sitemap.xml -f csv -o my-sitemap.csv
```

## 輸出位置

所有生成的檔案會儲存在：`docs/sitemaps/`

## 更多資訊

詳細用法請參考：[scripts/README.md](./README.md)
