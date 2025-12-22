# Sitemap 工具使用指南

基於 TypeScript 的多功能 sitemap 工具，支援從 XML sitemap 抓取資料並轉換為多種格式。

## 功能特色

- ✅ 支援多種輸出格式：YAML, JSON, CSV, MD
- ✅ 靈活的命令行參數介面
- ✅ 自動分類與格式化
- ✅ 支援格式轉換（在不同格式間互轉）
- ✅ TypeScript 型別安全
- ✅ 完整的型別定義匯出

## 安裝依賴

```bash
npm install
```

## 使用方式

### 1. 從 URL 抓取 Sitemap

#### 基本用法

```bash
# 抓取並儲存為 YAML（預設格式）
npm run sitemap -- fetch https://example.com/sitemap.xml

# 指定輸出格式
npm run sitemap -- fetch https://example.com/sitemap.xml --format json
npm run sitemap -- fetch https://example.com/sitemap.xml -f csv
npm run sitemap -- fetch https://example.com/sitemap.xml -f md
```

#### 自訂輸出檔案

```bash
# 使用 --output 或 -o 指定輸出檔案
npm run sitemap -- fetch https://example.com/sitemap.xml -f json -o custom-name.json
```

#### 完整範例（帶 metadata）

```bash
# 生成 Markdown 並指定專案名稱和網址
npm run sitemap -- fetch https://google.github.io/adk-docs/sitemap.xml \
  --format md \
  --name "Google ADK Documentation" \
  --url "https://google.github.io/adk-docs"
```

### 2. 轉換現有檔案

```bash
# 從 YAML 轉換為 JSON
npm run sitemap -- convert adk-sitemap.yaml -f json

# 從 JSON 轉換為 CSV
npm run sitemap -- convert data.json -f csv -o output.csv

# 從 YAML 轉換為 Markdown
npm run sitemap -- convert data.yaml -f md \
  --name "My Project" \
  --url "https://example.com"
```

## 快速開始 - 預設命令

使用預先配置的 NPM scripts 快速抓取常用文檔：

```bash
# Google ADK
npm run sitemap:adk       # YAML 格式
npm run sitemap:adk:md    # Markdown 格式

# A2A Protocol
npm run sitemap:a2a       # YAML 格式
npm run sitemap:a2a:md    # Markdown 格式

# Model Context Protocol (MCP)
npm run sitemap:mcp       # YAML 格式
npm run sitemap:mcp:md    # Markdown 格式
```

## 常見使用案例

### Google ADK 文檔

```bash
# 使用預設命令快速抓取
npm run sitemap:adk       # YAML 格式
npm run sitemap:adk:md    # Markdown 格式
```

### A2A Protocol

```bash
npm run sitemap:a2a       # YAML 格式
npm run sitemap:a2a:md    # Markdown 格式
```

### Model Context Protocol (MCP)

```bash
npm run sitemap:mcp       # YAML 格式
npm run sitemap:mcp:md    # Markdown 格式
```

## 支援的格式

| 格式 | 副檔名  | 說明                         |
| ---- | ------- | ---------------------------- |
| YAML | `.yaml` | 結構化資料，易讀易寫         |
| JSON | `.json` | 標準 JSON 格式，適合程式處理 |
| CSV  | `.csv`  | 表格格式，可用 Excel 開啟    |
| MD   | `.md`   | 文檔格式，包含表格和統計資訊 |

## 命令參數說明

### 通用選項

- `--format, -f <format>`: 指定輸出格式（yaml, json, csv, md）
- `--output, -o <file>`: 指定輸出檔案路徑
- `--name <name>`: 專案名稱（用於 MD 格式）
- `--url <url>`: 網站 URL（用於 MD 格式）

### 命令

- `fetch <url>`: 從 URL 抓取 XML sitemap
- `convert <file>`: 轉換現有檔案格式
- `help`: 顯示說明

## 輸出檔案位置

預設輸出目錄：`docs/sitemaps/`

- 相對路徑會自動加上預設目錄
- 可使用絕對路徑指定任意位置

## 範例輸出

### YAML 格式

```yaml
agents:
  - https://example.com/agents/
  - https://example.com/agents/config/
tutorials:
  - https://example.com/tutorials/
  - https://example.com/tutorials/quickstart/
```

### JSON 格式

```json
{
  "agents": [
    "https://example.com/agents/",
    "https://example.com/agents/config/"
  ],
  "tutorials": [
    "https://example.com/tutorials/",
    "https://example.com/tutorials/quickstart/"
  ]
}
```

### CSV 格式

```csv
Category,Page Name,URL
Agents,Agents,https://example.com/agents/
Agents,Config,https://example.com/agents/config/
Tutorials,Tutorials,https://example.com/tutorials/
Tutorials,Quickstart,https://example.com/tutorials/quickstart/
```

### MD 格式

```markdown
# Documentation Site Map

**Site**: `https://example.com`
**Generated**: `2025/12/22`

## Site Map Table

| #   | Category   | Page Name | URL                                                                      |
| :-- | :--------- | :-------- | :----------------------------------------------------------------------- |
| 1   | **Agents** | Agents    | [https://example.com/agents/](https://example.com/agents/)               |
| 2   |            | Config    | [https://example.com/agents/config/](https://example.com/agents/config/) |

...

## Summary

- **Total Pages**: `4`
- **Categories**: `2`
```

## 疑難排解

### 常見錯誤

1. **URL 格式錯誤**

   ```
   ❌ Error: Invalid URL format
   ```

   確認 URL 是否正確且包含協議（http:// 或 https://）

2. **檔案不存在**

   ```
   ❌ Error: Input file not found
   ```

   檢查檔案路徑是否正確

3. **不支援的格式**
   ```
   ❌ Error: Unsupported format
   ```
   使用支援的格式：yaml, json, csv, md

### Debug 模式

啟用詳細錯誤訊息：

```bash
DEBUG=1 npm run sitemap -- fetch <url>
```

## TypeScript 在其他專案中使用

此工具匯出完整的型別定義，可在其他 TypeScript 專案中使用：

```typescript
import {
  fetchSitemap,
  convertToFormat,
  type SitemapData,
  type SupportedFormat,
  type Metadata,
} from './scripts/sitemap';

async function example() {
  // 完整的型別支援
  const format: SupportedFormat = 'yaml';
  const result = await fetchSitemap(
    'https://example.com/sitemap.xml',
    format,
    './output.yaml'
  );

  // result.data 的型別是 SitemapData
  const data: SitemapData = result.data;

  // 轉換格式，有型別檢查
  const json = convertToFormat(data, 'json');
}
```

## 編譯

如需編譯成純 JavaScript：

```bash
npm run build
```

編譯輸出位於 `dist/` 目錄，包含：

- `sitemap.js` - 編譯後的 JavaScript
- `sitemap.d.ts` - 型別定義檔
- `sitemap.js.map` - Source map

## 更新歷史

### v2.1.0 (2025-12-22)

- ✨ 完整改寫為 TypeScript
- ✨ 新增完整的型別定義和匯出
- ✨ 改進 IDE 支援和開發體驗
- 🔧 移除 JavaScript 版本，專注於 TypeScript

### v2.0.0 (2025-12-22)

- ✨ 重構命令行介面，使用更清晰的參數格式
- ✨ 新增 `convert` 命令支援格式轉換
- ✨ 支援 4 種輸出格式（YAML, JSON, CSV, MD）
- ✨ 改進錯誤處理和使用者提示
