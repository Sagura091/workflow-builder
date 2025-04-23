const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('Building for GitHub Pages...');

// Paths
const srcDir = path.resolve(__dirname, '../src');
const buildDir = path.resolve(__dirname, '../build');
const entryPointsDir = path.resolve(srcDir, 'entry-points');
const indexPath = path.resolve(srcDir, 'index.js');
const indexBackupPath = path.resolve(srcDir, 'index.js.original');

// Backup the original index.js
console.log('Backing up original index.js...');
fs.copyFileSync(indexPath, indexBackupPath);

try {
  // Create a custom index.js file for GitHub Pages
  console.log('Creating custom index.js for GitHub Pages...');

  const customIndexContent = `// GitHub Pages Entry Point
import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import DemoApp from './pages/DemoApp';
import { DemoModeProvider } from './contexts/DemoModeContext';

// Force demo mode for GitHub Pages
window.FORCE_DEMO_MODE = true;
window.STANDALONE_DEMO = true;
window.ENSURE_DEMO_MODE_PROVIDER = true;

// Disable features that require a backend
if (typeof window !== 'undefined') {
  // Use a variable to avoid TypeScript errors
  const win = window;

  if (win.FEATURES) {
    win.FEATURES = {
      ...win.FEATURES,
      WEBSOCKETS_ENABLED: false,
      ENABLE_SCHEDULING: false
    };
  } else {
    // If FEATURES doesn't exist yet, create it
    win.FEATURES = {
      WEBSOCKETS_ENABLED: false,
      ENABLE_SCHEDULING: false,
      NODE_INSTANCES_ENABLED: true,
      LAZY_LOADING_ENABLED: true,
      ENABLE_TEMPLATES: true,
      ENABLE_CACHING: true,
      ENABLE_PARTIAL_EXECUTION: true,
      ENABLE_TYPE_VALIDATION: true,
      ENABLE_DARK_MODE: true
    };
  }
}

// Log that we're using the GitHub Pages entry point
console.log('Using GitHub Pages entry point');
console.log('Demo mode enabled: standalone demo with no backend requirements');

const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the app with DemoModeProvider explicitly wrapped around it
root.render(
  <React.StrictMode>
    <DemoModeProvider>
      <DemoApp />
    </DemoModeProvider>
  </React.StrictMode>
);
`;

  // Replace the index.js with our custom entry
  console.log('Replacing index.js with GitHub Pages entry...');
  fs.writeFileSync(indexPath, customIndexContent);

  // Build the application
  console.log('Building the application...');
  execSync('npm run build --legacy-peer-deps', { stdio: 'inherit' });

  // Create a demo-specific index.html that sets up demo mode
  console.log('Creating demo-specific index.html...');
  const indexHtmlPath = path.resolve(buildDir, 'index.html');
  let indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');

  // Add demo mode flags before the main script loads
  indexHtml = indexHtml.replace(
    '<head>',
    `<head>
    <!-- Demo Mode Configuration -->
    <script>
      // Use a variable to avoid TypeScript errors
      var win = window;
      win.FORCE_DEMO_MODE = true;
      win.STANDALONE_DEMO = true;
      win.ENSURE_DEMO_MODE_PROVIDER = true;

      // Set feature flags
      win.FEATURES = {
        WEBSOCKETS_ENABLED: false,
        ENABLE_SCHEDULING: false,
        NODE_INSTANCES_ENABLED: true,
        LAZY_LOADING_ENABLED: true,
        ENABLE_TEMPLATES: true,
        ENABLE_CACHING: true,
        ENABLE_PARTIAL_EXECUTION: true,
        ENABLE_TYPE_VALIDATION: true,
        ENABLE_DARK_MODE: true
      };

      console.log('Demo mode enabled for GitHub Pages');
    </script>`
  );

  // Add a demo banner
  indexHtml = indexHtml.replace(
    '<body>',
    `<body>
    <div style="background-color: #f0f9ff; padding: 10px; text-align: center; border-bottom: 1px solid #bae6fd; position: relative; z-index: 1000;">
      <p style="margin: 0; font-size: 14px;">
        <strong>Workflow Builder Demo</strong> - This is a standalone demo that runs entirely in your browser.
        <a href="https://github.com/Sagura091/workflow-builder" target="_blank" style="color: #0284c7; text-decoration: underline; margin-left: 8px;">View on GitHub</a>
      </p>
    </div>`
  );

  // Write the modified index.html
  fs.writeFileSync(indexHtmlPath, indexHtml);

  console.log('Build for GitHub Pages completed successfully!');
} catch (error) {
  console.error('Error building for GitHub Pages:', error);
  process.exit(1);
} finally {
  // Keep the GitHub Pages index.js for deployment
  console.log('Keeping GitHub Pages index.js for deployment...');

  // Just remove the backup file
  if (fs.existsSync(indexBackupPath)) {
    fs.unlinkSync(indexBackupPath);
  }
}
