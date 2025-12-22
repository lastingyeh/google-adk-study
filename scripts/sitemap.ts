#!/usr/bin/env node

/**
 * sitemap.ts - Sitemap 工具：抓取、轉換與多格式輸出
 *
 * 使用方式：
 *   ts-node sitemap.ts fetch <url> --format <format> [--output <file>]
 *   ts-node sitemap.ts convert <input> --format <format> [--output <file>]
 *
 * 格式：yaml, json, csv, md
 *
 * 範例：
 *   ts-node sitemap.ts fetch https://example.com/sitemap.xml --format yaml
 *   ts-node sitemap.ts fetch https://example.com/sitemap.xml --format json --output output.json
 *   ts-node sitemap.ts convert data.yaml --format md --output sitemap.md
 */

import * as fs from 'fs';
import * as https from 'https';
import * as http from 'http';
import { parseString } from 'xml2js';
import * as yaml from 'js-yaml';
import * as path from 'path';

// ==================== 型別定義 ====================

type SupportedFormat = 'yaml' | 'json' | 'csv' | 'md';

interface ParsedArgs {
  command: string;
  positional: string[];
  flags: Record<string, string | boolean>;
}

interface SitemapData {
  [category: string]: string[];
}

interface Metadata {
  projectName?: string;
  siteUrl?: string;
  sourceUrl?: string;
}

interface XmlUrlEntry {
  loc: string;
}

interface XmlData {
  urlset?: {
    url?: XmlUrlEntry | XmlUrlEntry[];
  };
}

interface FetchResult {
  data: SitemapData;
  outputPath: string;
}

type Formatter = (data: SitemapData, metadata?: Metadata) => string;

// ==================== 常數設定 ====================

const SUPPORTED_FORMATS: readonly SupportedFormat[] = [
  'yaml',
  'json',
  'csv',
  'md',
];
const DEFAULT_OUTPUT_DIR = path.join(__dirname, '../docs/sitemaps');

// ==================== 輔助函式 ====================

/**
 * 解析命令行參數
 */
function parseArgs(args: string[]): ParsedArgs {
  const parsed: ParsedArgs = {
    command: args[0] || '',
    positional: [],
    flags: {},
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const value =
        args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
      parsed.flags[key] = value;
    } else if (arg.startsWith('-')) {
      const key = arg.slice(1);
      const value =
        args[i + 1] && !args[i + 1].startsWith('-') ? args[++i] : true;
      parsed.flags[key] = value;
    } else {
      parsed.positional.push(arg);
    }
  }

  return parsed;
}

/**
 * 取得檔案格式（從旗標或檔名推斷）
 */
function getFormat(
  flags: Record<string, string | boolean>,
  filename?: string
): SupportedFormat {
  if (flags.format || flags.f) {
    const format = String(flags.format || flags.f).toLowerCase();
    return format as SupportedFormat;
  }

  if (filename) {
    const ext = path.extname(filename).slice(1).toLowerCase();
    if (SUPPORTED_FORMATS.includes(ext as SupportedFormat)) {
      return ext as SupportedFormat;
    }
  }

  return 'yaml'; // 預設格式
}

/**
 * 產生輸出檔案路徑
 */
function getOutputPath(
  flags: Record<string, string | boolean>,
  format: SupportedFormat,
  defaultName: string
): string {
  if (flags.output || flags.o) {
    const outputFile = String(flags.output || flags.o);
    return path.isAbsolute(outputFile)
      ? outputFile
      : path.join(DEFAULT_OUTPUT_DIR, outputFile);
  }

  const ext = format;
  return path.join(DEFAULT_OUTPUT_DIR, `${defaultName}.${ext}`);
}

// ==================== 資料轉換 ====================

/**
 * 將 XML sitemap 資料轉換為分組結構
 */
function parseXmlToGroups(xmlData: XmlData): SitemapData {
  const groups = new Map<string, string[]>();

  if (xmlData.urlset?.url) {
    const urls = Array.isArray(xmlData.urlset.url)
      ? xmlData.urlset.url
      : [xmlData.urlset.url];

    for (const urlEntry of urls) {
      const urlObj = new URL(urlEntry.loc);
      const pathParts = urlObj.pathname.split('/').filter(Boolean);

      // 使用第一或第二個路徑段作為分組鍵
      const groupKey =
        pathParts.length > 1 ? pathParts[1] : pathParts[0] || 'root';
      const groupValue = urlEntry.loc;

      if (groups.has(groupKey)) {
        groups.get(groupKey)!.push(groupValue);
      } else {
        groups.set(groupKey, [groupValue]);
      }
    }
  }

  return Object.fromEntries(groups);
}

/**
 * 格式化器集合
 */
const formatters: Record<SupportedFormat, Formatter> = {
  yaml: (data: SitemapData): string => {
    return yaml.dump(data, {
      indent: 2,
      lineWidth: -1,
      noRefs: true,
      sortKeys: false,
    });
  },

  json: (data: SitemapData): string => {
    return JSON.stringify(data, null, 2);
  },

  csv: (data: SitemapData): string => {
    let csv = 'Category,Page Name,URL\n';

    for (const [category, urls] of Object.entries(data)) {
      const displayCategory =
        category.charAt(0).toUpperCase() + category.slice(1);

      for (const url of urls) {
        const pageName = extractPageName(url);
        csv += `${displayCategory},${pageName},${url}\n`;
      }
    }

    return csv;
  },

  md: (data: SitemapData, metadata: Metadata = {}): string => {
    const {
      projectName = 'Documentation',
      siteUrl = '',
      sourceUrl = '',
    } = metadata;
    const date = new Date().toISOString().split('T')[0].replace(/-/g, '/');

    let md = `# ${projectName} Site Map\n\n`;

    if (siteUrl) {
      md += `**網站連結 (Site URL)**: \`${siteUrl}\`\n\n`;
    }
    if (sourceUrl) {
      md += `**資源 (Web Sitemap Resource)**: \`${sourceUrl}\`\n\n`;
    }
    md += `**更新日期 (Data Updated)**: \`${date}\`\n\n`;

    md += `## 網站地圖導航 (Web-Sitemap Roadmap)\n\n`;
    md += `| # | Category | Page Name | URL |\n`;
    md += `| :--- | :--- | :--- | :--- |\n`;

    let index = 1;
    for (const [category, urls] of Object.entries(data)) {
      const displayCategory =
        category.charAt(0).toUpperCase() + category.slice(1);
      let isFirstRow = true;

      for (const url of urls) {
        const pageName = extractPageName(url);
        const categoryCell = isFirstRow ? `**${displayCategory}**` : '';
        md += `| ${index} | ${categoryCell} | ${pageName} | [${url}](${url}) |\n`;
        isFirstRow = false;
        index++;
      }
    }

    // 統計資訊
    const totalPages = Object.values(data).reduce(
      (sum, urls) => sum + urls.length,
      0
    );
    const totalCategories = Object.keys(data).length;

    md += `\n## 總結說明 (Summary) \n\n`;
    md += `- **總頁面數 (Total Pages)**: \`${totalPages}\`\n`;
    md += `- **總分類數 (Categories)**: \`${totalCategories}\`\n`;

    return md;
  },
};

/**
 * 從 URL 提取頁面名稱
 */
function extractPageName(url: string): string {
  const cleanUrl = url.endsWith('/') ? url.slice(0, -1) : url;
  const parts = cleanUrl.split('/');
  const slug = parts[parts.length - 1];

  // 如果是域名或空字串，返回 Home
  if (!slug || slug.includes('.') || slug.startsWith('http')) {
    return 'Home';
  }

  return slug
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * 轉換資料為指定格式
 */
function convertToFormat(
  data: SitemapData,
  format: SupportedFormat,
  metadata: Metadata = {}
): string {
  const formatter = formatters[format];
  if (!formatter) {
    throw new Error(`Unsupported format: ${format}`);
  }
  return formatter(data, metadata);
}

// ==================== 資料載入 ====================

/**
 * 從檔案載入資料
 */
function loadDataFromFile(filePath: string): SitemapData {
  const ext = path.extname(filePath).slice(1).toLowerCase();
  const content = fs.readFileSync(filePath, 'utf8');

  switch (ext) {
    case 'yaml':
    case 'yml':
      return yaml.load(content) as SitemapData;
    case 'json':
      return JSON.parse(content) as SitemapData;
    default:
      throw new Error(`Cannot load data from .${ext} file`);
  }
}

// ==================== 主要功能 ====================

/**
 * 從 URL 抓取 XML sitemap
 */
function fetchSitemap(
  url: string,
  format: SupportedFormat,
  outputPath: string,
  metadata: Metadata = {}
): Promise<FetchResult> {
  return new Promise((resolve, reject) => {
    console.log(`📡 Fetching sitemap from: ${url}`);

    const protocol = url.startsWith('https') ? https : http;

    protocol
      .get(url, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          console.log(`📦 Received ${data.length} bytes`);

          parseString(
            data,
            { explicitArray: false, mergeAttrs: true },
            (err, result: XmlData) => {
              if (err) {
                console.error('❌ Error parsing XML:', err);
                reject(err);
                return;
              }

              const parsedData = parseXmlToGroups(result);
              const formattedData = convertToFormat(parsedData, format, {
                ...metadata,
                sourceUrl: url,
              });

              // 確保目錄存在
              const dir = path.dirname(outputPath);
              if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
              }

              fs.writeFileSync(outputPath, formattedData, 'utf8');
              console.log(`✅ Saved ${format.toUpperCase()} to: ${outputPath}`);

              resolve({ data: parsedData, outputPath });
            }
          );
        });
      })
      .on('error', (err) => {
        console.error('❌ Error fetching URL:', err);
        reject(err);
      });
  });
}

/**
 * 轉換檔案格式
 */
function convertFile(
  inputPath: string,
  format: SupportedFormat,
  outputPath: string,
  metadata: Metadata = {}
): string {
  console.log(`📖 Reading data from: ${inputPath}`);

  const data = loadDataFromFile(inputPath);
  const formattedData = convertToFormat(data, format, metadata);

  // 確保目錄存在
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(outputPath, formattedData, 'utf8');
  console.log(`✅ Converted to ${format.toUpperCase()}: ${outputPath}`);

  return outputPath;
}

// ==================== CLI 介面 ====================

function printUsage(): void {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║              Sitemap Tool - Multi-Format Support            ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  ts-node sitemap.ts fetch <url> --format <format> [options]
  ts-node sitemap.ts convert <input-file> --format <format> [options]

Commands:
  fetch <url>           Fetch XML sitemap from URL and convert
  convert <file>        Convert existing data file to another format

Options:
  --format, -f <fmt>    Output format: yaml, json, csv, md
  --output, -o <file>   Output file path
  --name <name>         Project name (for md format)
  --url <url>           Site URL (for md format)

Supported Formats:
  yaml       YAML format (default)
  json       JSON format
  csv        CSV format with headers
  md         Markdown table format

Examples:
  # Fetch sitemap and save as YAML
  ts-node sitemap.ts fetch https://example.com/sitemap.xml -f yaml

  # Fetch and save as JSON with custom output
  ts-node sitemap.ts fetch https://example.com/sitemap.xml -f json -o output.json

  # Fetch and generate markdown
  ts-node sitemap.ts fetch https://google.github.io/adk-docs/sitemap.xml \\
    -f md --name "ADK" --url "https://google.github.io/adk-docs"

  # Convert YAML to Markdown
  ts-node sitemap.ts convert data.yaml -f md -o sitemap.md

  # Convert YAML to CSV
  ts-node sitemap.ts convert data.yaml -f csv

Quick Examples:
  # Google ADK
  ts-node sitemap.ts fetch https://google.github.io/adk-docs/sitemap.xml -f yaml

  # A2A Protocol
  ts-node sitemap.ts fetch https://a2a-protocol.org/latest/sitemap.xml -f json

  # MCP
  ts-node sitemap.ts fetch https://modelcontextprotocol.io/sitemap.xml -f md
`);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (
    args.length === 0 ||
    args[0] === 'help' ||
    args[0] === '--help' ||
    args[0] === '-h'
  ) {
    printUsage();
    process.exit(0);
  }

  const parsed = parseArgs(args);
  const { command, positional, flags } = parsed;

  try {
    switch (command) {
      case 'fetch': {
        const url = positional[0];
        if (!url) {
          console.error('❌ Error: URL is required');
          console.log(
            'Usage: ts-node sitemap.ts fetch <url> --format <format> [--output <file>]'
          );
          process.exit(1);
        }

        // 驗證 URL 格式
        try {
          new URL(url);
        } catch (e) {
          console.error('❌ Error: Invalid URL format');
          process.exit(1);
        }

        const format = getFormat(flags, flags.output as string | undefined);
        if (!SUPPORTED_FORMATS.includes(format)) {
          console.error(`❌ Error: Unsupported format "${format}"`);
          console.log(`Supported formats: ${SUPPORTED_FORMATS.join(', ')}`);
          process.exit(1);
        }

        const defaultName = extractSiteName(url);
        const outputPath = getOutputPath(flags, format, defaultName);

        const metadata: Metadata = {
          projectName: (flags.name as string) || defaultName,
          siteUrl: (flags.url as string) || url.split('/sitemap.xml')[0],
        };

        console.log(
          `\n🚀 Fetching sitemap and converting to ${format.toUpperCase()}...\n`
        );
        await fetchSitemap(url, format, outputPath, metadata);
        console.log('\n✅ Done!\n');
        break;
      }

      case 'convert': {
        const inputFile = positional[0];
        if (!inputFile) {
          console.error('❌ Error: Input file is required');
          console.log(
            'Usage: ts-node sitemap.ts convert <input-file> --format <format> [--output <file>]'
          );
          process.exit(1);
        }

        // 處理輸入檔案路徑
        let inputPath: string;
        if (path.isAbsolute(inputFile)) {
          inputPath = inputFile;
        } else if (inputFile.includes('/')) {
          // 如果包含路徑分隔符，視為相對於工作目錄
          inputPath = path.resolve(inputFile);
        } else {
          // 否則在預設目錄中尋找
          inputPath = path.join(DEFAULT_OUTPUT_DIR, inputFile);
        }

        if (!fs.existsSync(inputPath)) {
          console.error(`❌ Error: Input file not found: ${inputPath}`);
          process.exit(1);
        }

        const format = getFormat(flags, flags.output as string | undefined);
        if (!SUPPORTED_FORMATS.includes(format)) {
          console.error(`❌ Error: Unsupported format "${format}"`);
          console.log(`Supported formats: ${SUPPORTED_FORMATS.join(', ')}`);
          process.exit(1);
        }

        const defaultName = path.basename(inputFile, path.extname(inputFile));
        const outputPath = getOutputPath(flags, format, defaultName);

        const metadata: Metadata = {
          projectName: (flags.name as string) || defaultName,
          siteUrl: (flags.url as string) || '',
        };

        console.log(`\n🔄 Converting to ${format.toUpperCase()}...\n`);
        convertFile(inputPath, format, outputPath, metadata);
        console.log('\n✅ Done!\n');
        break;
      }

      default:
        console.error(`❌ Unknown command: ${command}`);
        console.log('Run "ts-node sitemap.ts help" for usage information');
        process.exit(1);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error('\n❌ Fatal error:', errorMessage);
    if (process.env.DEBUG && error instanceof Error) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

/**
 * 從 URL 提取網站名稱
 */
function extractSiteName(url: string): string {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname;
    const parts = hostname.split('.');

    // 移除 www 和頂級域名
    const filtered = parts.filter(
      (p) => p !== 'www' && !['com', 'org', 'io', 'net'].includes(p)
    );

    return filtered.length > 0 ? filtered[0] : 'sitemap';
  } catch (e) {
    return 'sitemap';
  }
}

// 執行主程式
if (require.main === module) {
  main().catch((error) => {
    console.error('❌ Unhandled error:', error);
    process.exit(1);
  });
}

// 匯出函式供其他模組使用
export {
  fetchSitemap,
  convertFile,
  parseXmlToGroups,
  convertToFormat,
  loadDataFromFile,
  formatters,
  extractPageName,
  type SupportedFormat,
  type SitemapData,
  type Metadata,
  type ParsedArgs,
  type FetchResult,
};
