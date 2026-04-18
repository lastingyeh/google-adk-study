import puppeteer from 'puppeteer';
import { resolve } from 'path';

const [, , inputFile, outputFile] = process.argv;

if (!inputFile || !outputFile) {
  console.error('Usage: node html-to-png.mjs <input.html> <output.png>');
  process.exit(1);
}

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});

const page = await browser.newPage();

// 1920px wide landscape, enough height to avoid clipping
await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });

const fileUrl = `file://${resolve(inputFile)}`;
await page.goto(fileUrl, { waitUntil: 'networkidle0' });

// Get full page height
const bodyHeight = await page.evaluate(() => document.body.scrollHeight);

// Resize viewport to full content height
await page.setViewport({
  width: 1920,
  height: bodyHeight,
  deviceScaleFactor: 2,
});

await page.screenshot({
  path: outputFile,
  fullPage: true,
  type: 'png',
});

await browser.close();
console.log(`Saved: ${outputFile} (1920 × ${bodyHeight}px @2x)`);
