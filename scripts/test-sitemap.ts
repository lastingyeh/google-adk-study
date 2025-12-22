#!/usr/bin/env node

/**
 * 簡單的測試腳本，驗證 sitemap.ts 的主要功能
 */

import { strict as assert } from 'assert';
import * as fs from 'fs';
import * as path from 'path';
import * as sitemap from './sitemap';

const TEST_DIR = path.join(__dirname, '../docs/sitemaps/test');

// 確保測試目錄存在
if (!fs.existsSync(TEST_DIR)) {
  fs.mkdirSync(TEST_DIR, { recursive: true });
}

console.log('🧪 Running sitemap.ts tests...\n');

// 測試資料
const testData: sitemap.SitemapData = {
  agents: ['https://example.com/agents/', 'https://example.com/agents/config/'],
  tutorials: [
    'https://example.com/tutorials/',
    'https://example.com/tutorials/quickstart/',
  ],
};

// Test 1: YAML 格式化
console.log('Test 1: YAML formatting...');
try {
  const yaml = sitemap.formatters.yaml(testData);
  assert(yaml.includes('agents:'));
  assert(yaml.includes('tutorials:'));
  console.log('✅ YAML formatting works\n');
} catch (e) {
  const error = e as Error;
  console.error('❌ YAML formatting failed:', error.message);
  process.exit(1);
}

// Test 2: JSON 格式化
console.log('Test 2: JSON formatting...');
try {
  const json = sitemap.formatters.json(testData);
  const parsed = JSON.parse(json);
  assert(parsed.agents.length === 2);
  assert(parsed.tutorials.length === 2);
  console.log('✅ JSON formatting works\n');
} catch (e) {
  const error = e as Error;
  console.error('❌ JSON formatting failed:', error.message);
  process.exit(1);
}

// Test 3: CSV 格式化
console.log('Test 3: CSV formatting...');
try {
  const csv = sitemap.formatters.csv(testData);
  assert(csv.includes('Category,Page Name,URL'));
  assert(csv.includes('Agents'));
  assert(csv.includes('Tutorials'));
  const lines = csv.split('\n').filter((l) => l.trim());
  assert(lines.length === 5); // header + 4 data rows
  console.log('✅ CSV formatting works\n');
} catch (e) {
  const error = e as Error;
  console.error('❌ CSV formatting failed:', error.message);
  process.exit(1);
}

// Test 4: Markdown 格式化
console.log('Test 4: Markdown formatting...');
try {
  const md = sitemap.formatters.md(testData, {
    projectName: 'Test Project',
    siteUrl: 'https://example.com',
  });
  assert(md.includes('# Test Project Site Map'));
  assert(md.includes('**網站連結 (Site URL)**: `https://example.com`'));
  assert(md.includes('## 網站地圖導航 (Web-Sitemap Roadmap)'));
  assert(md.includes('## 總結說明 (Summary)'));
  console.log('✅ Markdown formatting works\n');
} catch (e) {
  const error = e as Error;
  console.error('❌ Markdown formatting failed:', error.message);
  process.exit(1);
}

// Test 5: 頁面名稱提取
console.log('Test 5: Page name extraction...');
try {
  assert(
    sitemap.extractPageName('https://example.com/quick-start/') ===
      'Quick Start'
  );
  assert(
    sitemap.extractPageName('https://example.com/api-reference/') ===
      'Api Reference'
  );
  assert(sitemap.extractPageName('https://example.com/') === 'Home');
  console.log('✅ Page name extraction works\n');
} catch (e) {
  const error = e as Error;
  console.error('❌ Page name extraction failed:', error.message);
  process.exit(1);
}

// Test 6: 檔案讀寫
console.log('Test 6: File I/O...');
try {
  const yamlPath = path.join(TEST_DIR, 'test-data.yaml');
  const jsonPath = path.join(TEST_DIR, 'test-data.json');

  // 寫入 YAML
  const yamlContent = sitemap.formatters.yaml(testData);
  fs.writeFileSync(yamlPath, yamlContent);

  // 讀取 YAML
  const loadedData = sitemap.loadDataFromFile(yamlPath);
  assert.deepStrictEqual(loadedData, testData);

  // 轉換為 JSON
  const jsonContent = sitemap.convertToFormat(loadedData, 'json');
  fs.writeFileSync(jsonPath, jsonContent);

  // 讀取 JSON
  const loadedJson = sitemap.loadDataFromFile(jsonPath);
  assert.deepStrictEqual(loadedJson, testData);

  console.log('✅ File I/O works\n');
} catch (e) {
  const error = e as Error;
  console.error('❌ File I/O failed:', error.message);
  process.exit(1);
}

// Test 7: TypeScript 型別檢查
console.log('Test 7: TypeScript type checking...');
try {
  // 確保型別正確匯出
  const metadata: sitemap.Metadata = {
    projectName: 'Test',
    siteUrl: 'https://example.com',
  };

  const format: sitemap.SupportedFormat = 'yaml';
  const converted = sitemap.convertToFormat(testData, format, metadata);
  assert(typeof converted === 'string');
  console.log('✅ TypeScript type checking works\n');
} catch (e) {
  const error = e as Error;
  console.error('❌ TypeScript type checking failed:', error.message);
  process.exit(1);
}

// 清理測試檔案
console.log('🧹 Cleaning up test files...');
try {
  fs.rmSync(TEST_DIR, { recursive: true, force: true });
  console.log('✅ Cleanup complete\n');
} catch (e) {
  const error = e as Error;
  console.warn('⚠️  Cleanup warning:', error.message);
}

console.log('🎉 All tests passed!');
