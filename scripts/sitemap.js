#!/usr/bin/env node

/**
 * sitemap.js - 整合 XML sitemap 抓取、解析與 Markdown 生成
 *
 * 使用方式：
 *   node sitemap.js fetch <url> [output.yaml]          # 抓取並解析 XML sitemap
 *   node sitemap.js generate [input.yaml] [output.md]  # 從 YAML 生成 Markdown
 *   node sitemap.js all <url> [yaml-file] [md-file]    # 完整流程
 *
 * 範例：
 *   node sitemap.js fetch https://example.com/sitemap.xml adk-sitemap.yaml
 *   node sitemap.js generate adk-sitemap.yaml adk-sitemap.md
 *   node sitemap.js all https://example.com/sitemap.xml
 */

// 1. google-adk: npm run sitemap https://google.github.io/adk-docs/sitemap.xml adk-sitemap.yaml adk-sitemap.md
// 2. a2a: npm run sitemap https://a2a-protocol.org/latest/sitemap.xml a2a-sitemap.yaml a2a-sitemap.md
// 3. mcp: npm run sitemap https://modelcontextprotocol.io/sitemap.xml mcp-sitemap.yaml mcp-sitemap.md

const fs = require('fs');
const https = require('https');
const http = require('http');
const { parseString } = require('xml2js');
const yaml = require('js-yaml');
const path = require('path');

// ==================== 設定 ====================
const DEFAULT_YAML_PATH = path.join(
  __dirname,
  '../docs/sitemaps',
  'adk-sitemap.yaml'
);
const DEFAULT_MD_PATH = path.join(
  __dirname,
  '../docs/sitemaps',
  'adk-sitemap.md'
);

// ==================== XML 抓取與解析 ====================

/**
 * 將 XML sitemap 資料轉換為分組結構
 */
function urlConverter(data) {
  const groups = new Map();

  if (data.urlset && data.urlset.url && data.urlset.url.length > 0) {
    for (const urlEntry of data.urlset.url) {
      const urls = new URL(urlEntry.loc);
      const groupSet = urls.pathname.split('/');

      const groupKey = !groupSet[2]  ? groupSet[1] : groupSet[2];
      const groupValue = urlEntry.loc;

      if (groups.has(groupKey)) {
        const values = groups.get(groupKey);
        if (Array.isArray(values)) {
          values.push(groupValue);
        }
      } else {
        groups.set(groupKey, [groupValue]);
      }
    }
  }
  return groups;
}

/**
 * 將資料物件轉換為 YAML 格式
 */
function dataToYaml(data) {
  try {
    return yaml.dump(data, {
      indent: 2,
      lineWidth: -1,
      noRefs: true,
      sortKeys: false,
    });
  } catch (error) {
    console.error('❌ Error converting to YAML:', error);
    throw error;
  }
}

/**
 * 從 URL 抓取 XML sitemap 並儲存為 YAML
 */
function fetchSitemap(url, outputFile) {
  return new Promise((resolve, reject) => {
    console.log(`📡 Fetching URL: ${url}`);

    const protocol = url.startsWith('https') ? https : http;

    protocol
      .get(url, (res) => {
        let data = '';

        const contentType = res.headers['content-type'] || '';
        console.log(`📄 Content-Type: ${contentType}`);

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          console.log(`📦 Received ${data.length} bytes`);

          if (contentType.includes('xml') || data.trim().startsWith('<')) {
            console.log('🔄 Parsing XML...');

            parseString(
              data,
              { explicitArray: false, mergeAttrs: true },
              (err, result) => {
                if (err) {
                  console.error('❌ Error parsing XML:', err);
                  reject(err);
                  return;
                }

                const groups = urlConverter(result);
                const dataObject = Object.fromEntries(groups);

                const outputFilePath = path.join(
                  __dirname,
                  '../docs/sitemaps',
                  outputFile
                );

                const yamlData = dataToYaml(dataObject);
                fs.writeFileSync(outputFilePath, yamlData);
                console.log(`✅ Saved YAML to: ${outputFilePath}`);
                resolve(outputFilePath);
              }
            );
          } else {
            const error = new Error('Response is not XML format');
            console.error('❌', error.message);
            reject(error);
          }
        });
      })
      .on('error', (err) => {
        console.error('❌ Error fetching URL:', err);
        reject(err);
      });
  });
}

// ==================== Markdown 生成 ====================

/**
 * 從 YAML 檔案生成 Markdown sitemap
 */
function generateMarkdown(docName, url, yamlPath, outputPath) {
  try {
    console.log(`📖 Reading YAML from: ${yamlPath}`);
    const fileContents = fs.readFileSync(yamlPath, 'utf8');
    const data = yaml.load(fileContents);

    // 專案資訊
    const projectName = `${docName} Documentation`;
    const siteUrl = url;
    const date = new Date().toISOString().split('T')[0].replace(/-/g, '/');

    let markdownContent = `# ${projectName} 文檔網站地圖

本文檔包含 ${projectName} 官方文檔網站的完整網站地圖。

**網站**: \`${siteUrl}\`
**最後更新**: \`${date}\`

## 網站地圖表格

| 編號 | 分類 | 頁面名稱 | URL |
| :--- | :--- | :--- | :--- |
`;

    let csvContent = `分類,頁面名稱,URL\n`;

    let totalPages = 0;
    let categories = Object.keys(data);
    let totalCategories = categories.length;
    let index = 1;

    for (const [category, urls] of Object.entries(data)) {
      const displayCategory =
        category.charAt(0).toUpperCase() + category.slice(1);
      let firstRow = true;

      for (const url of urls) {
        totalPages++;

        // 從 URL 推斷頁面名稱
        let cleanUrl = url.endsWith('/') ? url.slice(0, -1) : url;
        let parts = cleanUrl.split('/');
        let slug = parts[parts.length - 1];

        let pageName = slug
          .split('-')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        if (pageName === '') pageName = 'Home';

        let tableCategory = firstRow ? `**${displayCategory}**` : '';

        markdownContent += `| ${index} | ${tableCategory} | ${pageName} | [${url}](${url}) |\n`;
        csvContent += `${displayCategory},${pageName},${url}\n`;

        firstRow = false;
        index++;
      }
    }

    markdownContent += `
## CSV 格式

\`\`\`csv
${csvContent}\`\`\`

## 摘要

- **總計頁面數**: \`${totalPages}\`
- **主要分類**: \`${totalCategories}\`
- **功能涵蓋**: \`Core Concepts, Agents, Deploy, Observability, Tools, Tutorials\`
- **支援語言**: \`Go, Java, Python, TypeScript\`
- **部署選項**: \`Cloud Run, GKE, Agent Engine\`
- **監控工具**: \`Cloud Trace, Logging, MLflow, Phoenix, Weave\`

此文檔為開發者提供了使用 ${projectName} 的完整指南。
`;

    fs.writeFileSync(outputPath, markdownContent);
    console.log(`✅ Successfully generated ${outputPath}`);

    return outputPath;
  } catch (e) {
    console.error('❌ Error generating markdown:', e);
    throw e;
  }
}

// ==================== CLI 介面 ====================

function printUsage() {
  console.log(`
Usage:
  node sitemap.js fetch <url> [output.yaml]
    從 URL 抓取 XML sitemap 並儲存為 YAML

  node sitemap.js generate [input.yaml] [output.md]
    從 YAML 檔案生成 Markdown sitemap

  node sitemap.js all <url> [yaml-file] [md-file]
    執行完整流程（fetch + generate）

Examples:
  node sitemap.js fetch https://google.github.io/adk-docs/sitemap.xml
  node sitemap.js generate
  node sitemap.js all https://google.github.io/adk-docs/sitemap.xml
`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === 'help' || command === '--help') {
    printUsage();
    process.exit(0);
  }

  try {
    switch (command) {
      case 'fetch': {
        const url = args[1];
        if (!url) {
          console.error('❌ Error: URL is required for fetch command');
          printUsage();
          process.exit(1);
        }
        const outputFile = args[2] || path.basename(DEFAULT_YAML_PATH);
        await fetchSitemap(url, outputFile);
        break;
      }

      case 'generate': {
        const yamlFile = args[1] || path.basename(DEFAULT_YAML_PATH);
        const mdFile = args[2] || path.basename(DEFAULT_MD_PATH);
        const yamlPath = path.join(__dirname, '../docs/sitemaps', yamlFile);
        const mdPath = path.join(__dirname, '../docs/sitemaps', mdFile);
        generateMarkdown(
          path.basename(args[2],'.yaml').toLocaleUpperCase(),
          args[1],
          yamlPath,
          mdPath
        );
        break;
      }

      case 'all': {
        const url = args[1];
        if (!url) {
          console.error('❌ Error: URL is required for all command');
          printUsage();
          process.exit(1);
        }
        const yamlFile = args[2] || path.basename(DEFAULT_YAML_PATH);
        const mdFile = args[3] || path.basename(DEFAULT_MD_PATH);
        const yamlPath = path.join(__dirname, '../docs/sitemaps', yamlFile);
        const mdPath = path.join(__dirname, '../docs/sitemaps', mdFile);

        console.log('🚀 Starting complete sitemap workflow...\n');
        await fetchSitemap(url, yamlFile);
        console.log('');
        generateMarkdown(
          path.basename(args[2],'.yaml').toLocaleUpperCase(),
          args[1],
          yamlPath,
          mdPath
        );
        console.log('\n🎉 Complete!');
        break;
      }

      default:
        console.error(`❌ Unknown command: ${command}`);
        printUsage();
        process.exit(1);
    }
  } catch (error) {
    console.error('❌ Fatal error:', error);
    process.exit(1);
  }
}

// 執行主程式
if (require.main === module) {
  main();
}

// 匯出函式供其他模組使用
module.exports = {
  fetchSitemap,
  generateMarkdown,
  urlConverter,
  dataToYaml,
};
