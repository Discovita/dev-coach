#!/usr/bin/env node

/**
 * Script to find and fix relative links in Docusaurus documentation
 * 
 * This script scans markdown files for relative links and suggests
 * absolute path replacements to prevent broken links when files are moved.
 */

const fs = require('fs');
const path = require('path');

// Configuration
const DOCS_DIR = path.join(__dirname, '../docs');

// Link patterns to find
const RELATIVE_LINK_PATTERNS = [
  /\[([^\]]+)\]\(([^)]+)\)/g, // Markdown links
  /\[([^\]]+)\]\(([^)]+)\)/g, // Reference links
];

// Patterns that indicate relative links (not absolute or external)
const RELATIVE_INDICATORS = [
  /^[^\/][^:]*\.md/, // Starts with non-slash, ends with .md
  /^\.\.\//, // Starts with ../
  /^\.\//, // Starts with ./
  /^[a-zA-Z][^\/]*\//, // Starts with letter, has slash
];

function isRelativeLink(link) {
  // Skip external links
  if (link.startsWith('http://') || link.startsWith('https://') || link.startsWith('mailto:')) {
    return false;
  }
  
  // Skip absolute paths
  if (link.startsWith('/docs/')) {
    return false;
  }
  
  // Check if it matches relative patterns
  return RELATIVE_INDICATORS.some(pattern => pattern.test(link));
}

function findRelativeLinks(content, filePath) {
  const issues = [];
  const relativePath = path.relative(DOCS_DIR, filePath);
  const fileDir = path.dirname(relativePath);
  
  // Find all markdown links
  const linkMatches = content.match(/\[([^\]]+)\]\(([^)]+)\)/g) || [];
  
  for (const match of linkMatches) {
    const linkMatch = match.match(/\[([^\]]+)\]\(([^)]+)\)/);
    if (!linkMatch) continue;
    
    const [, linkText, linkUrl] = linkMatch;
    
    if (isRelativeLink(linkUrl)) {
      // Calculate the correct Docusaurus path
      let suggestion = '';
      
      if (linkUrl.endsWith('.md')) {
        // Remove .md extension for Docusaurus
        const cleanUrl = linkUrl.replace(/\.md$/, '');
        const resolvedPath = path.join(fileDir, cleanUrl);
        suggestion = `/docs/${resolvedPath}`;
      } else {
        const resolvedPath = path.join(fileDir, linkUrl);
        suggestion = `/docs/${resolvedPath}`;
      }
      
      // Normalize path separators for web URLs
      suggestion = suggestion.replace(/\\/g, '/');
      
      issues.push({
        file: relativePath,
        line: content.substring(0, content.indexOf(match)).split('\n').length,
        original: match,
        linkText,
        linkUrl,
        suggestion: `[${linkText}](${suggestion})`
      });
    }
  }
  
  return issues;
}

function scanFiles() {
  const allIssues = [];
  
  function scanDirectory(dir) {
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        scanDirectory(fullPath);
      } else if (stat.isFile() && (item.endsWith('.md') || item.endsWith('.mdx'))) {
        const relativePath = path.relative(DOCS_DIR, fullPath);
        const content = fs.readFileSync(fullPath, 'utf8');
        const issues = findRelativeLinks(content, fullPath);
        allIssues.push(...issues);
      }
    }
  }
  
  scanDirectory(DOCS_DIR);
  return allIssues;
}

function generateReport(issues) {
  if (issues.length === 0) {
    console.log('✅ No relative links found! All links are using absolute paths.');
    return;
  }
  
  console.log(`\n🔍 Found ${issues.length} relative links that should be converted to absolute paths:\n`);
  
  // Group by file
  const issuesByFile = issues.reduce((acc, issue) => {
    if (!acc[issue.file]) acc[issue.file] = [];
    acc[issue.file].push(issue);
    return acc;
  }, {});
  
  Object.entries(issuesByFile).forEach(([file, fileIssues]) => {
    console.log(`📄 ${file}:`);
    fileIssues.forEach(issue => {
      console.log(`   Line ${issue.line}:`);
      console.log(`   ❌ ${issue.original}`);
      console.log(`   ✅ ${issue.suggestion}`);
      console.log('');
    });
  });
  
  console.log('\n💡 To fix these issues:');
  console.log('1. Replace the relative links with absolute paths starting with /docs/');
  console.log('2. Remove .md extensions from internal links');
  console.log('3. Run this script again to verify all links are fixed');
}

function main() {
  console.log('🔍 Scanning for relative links in documentation...\n');
  
  try {
    const issues = scanFiles();
    generateReport(issues);
  } catch (error) {
    console.error('❌ Error scanning files:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { scanFiles, findRelativeLinks };
