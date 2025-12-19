#!/usr/bin/env node

/**
 * parse.js - Fetch URL and convert XML response to JSON
 * Usage: node parse.js <url> [output-file.json]
 */

const fs = require('fs');
const https = require('https');
const http = require('http');
const { parseString } = require('xml2js');
const yaml = require('js-yaml');

// Get URL from command line arguments
const url = process.argv[2];
// Determine output file name
const outputFile = process.argv[3] || 'output.json';

if (!url) {
  console.error('Usage: node parse.js <url> [output-file.json]');
  process.exit(1);
}

console.log(`Fetching URL: ${url}`);

// Determine protocol
const protocol = url.startsWith('https') ? https : http;

function urlConverter(data) {
  const groups = new Map();

  if (data.urlset.url && data.urlset.url.length > 0) {
    for (const urlEntry of data.urlset.url) {
      const urls = new URL(urlEntry.loc);
      const groupSet = urls.pathname.split('/');

      groupKey = groupSet[2] === '' ? 'root' : groupSet[2];
      groupValue = urlEntry.loc;

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
 * Convert data object to YAML format
 * @param {Object} data - Data object to convert
 * @returns {string} YAML formatted string
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
    console.error('Error converting to YAML:', error);
    throw error;
  }
}

// Make HTTP request
protocol
  .get(url, (res) => {
    let data = '';

    // Check content type
    const contentType = res.headers['content-type'] || '';
    console.log(`Content-Type: ${contentType}`);

    // Collect data chunks
    res.on('data', (chunk) => {
      data += chunk;
    });

    // Process complete response
    res.on('end', () => {
      console.log(`Received ${data.length} bytes`);

      // Check if response is XML
      if (contentType.includes('xml') || data.trim().startsWith('<')) {
        console.log('Detected XML format, converting to JSON...');

        // Parse XML to JSON
        parseString(
          data,
          { explicitArray: false, mergeAttrs: true },
          (err, result) => {
            if (err) {
              console.error('Error parsing XML:', err);
              process.exit(1);
            }

            const groups = urlConverter(result);
            const dataObject = Object.fromEntries(groups);

            console.log(groups);

            // Determine output format based on file extension
            const isYamlOutput =
              outputFile.endsWith('.yaml') || outputFile.endsWith('.yml');

            if (isYamlOutput) {
              // Save to YAML file
              const yamlData = dataToYaml(dataObject);
              fs.writeFileSync(outputFile, yamlData);
              console.log(`✓ Saved YAML to: ${outputFile}`);
            } else {
              // Save to JSON file
              const jsonData = JSON.stringify(dataObject, null, 2);
              fs.writeFileSync(outputFile, jsonData);
              console.log(`✓ Saved JSON to: ${outputFile}`);
            }
          }
        );
      } else {
        console.log('Response is not XML format');

        // Try to parse as JSON
        try {
          const jsonData = JSON.parse(data);
          fs.writeFileSync(outputFile, JSON.stringify(jsonData, null, 2));
          console.log(`✓ Saved JSON to: ${outputFile}`);
        } catch (e) {
          // Save raw data
          fs.writeFileSync(outputFile.replace('.json', '.txt'), data);
          console.log(
            `✓ Saved raw response to: ${outputFile.replace('.json', '.txt')}`
          );
        }
      }
    });
  })
  .on('error', (err) => {
    console.error('Error fetching URL:', err);
    process.exit(1);
  });
