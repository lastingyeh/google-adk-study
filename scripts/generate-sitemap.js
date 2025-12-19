const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

const yamlPath = path.join(__dirname, '../adk-sitemap.yaml');
const templatePath = path.join(__dirname, '../templates/sitemap.md');
const outputPath = path.join(__dirname, '../adk-sitemap.md');

try {
    const fileContents = fs.readFileSync(yamlPath, 'utf8');
    const data = yaml.load(fileContents);

    // Project Info
    const projectName = "Google ADK Docs";
    const siteUrl = "https://google.github.io/adk-docs/";
    const date = new Date().toISOString().split('T')[0].replace(/-/g, '/'); // YYYY/MM/DD

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
    let categoryMap = {};

    let index = 1;

    for (const [category, urls] of Object.entries(data)) {
        categoryMap[category] = urls.length;

        // Capitalize and format category name
        const displayCategory = category.charAt(0).toUpperCase() + category.slice(1);

        let firstRow = true;

        for (const url of urls) {
            totalPages++;

            // Infer page name from URL
            // Remove trailing slash
            let cleanUrl = url.endsWith('/') ? url.slice(0, -1) : url;
            let parts = cleanUrl.split('/');
            let slug = parts[parts.length - 1];

            // Format page name: replace hyphens with spaces, capitalize words
            let pageName = slug.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            if (pageName === '') pageName = 'Home';

            // For mapping logic to match template visual style (First row has category, others empty)
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
    console.log(`Successfully generated ${outputPath}`);

} catch (e) {
    console.error(e);
}
