const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Build the React application
console.log('Building React application...');
execSync('npm run build', { stdio: 'inherit' });

// Path to the build directory
const buildDir = path.join(__dirname, '..', 'build');

// Read the index.html file
const indexHtml = fs.readFileSync(path.join(buildDir, 'index.html'), 'utf8');

// Find all JavaScript files in the build directory
const jsFiles = fs.readdirSync(path.join(buildDir, 'static', 'js'))
  .filter(file => file.endsWith('.js'))
  .map(file => path.join('static', 'js', file));

// Find all CSS files in the build directory
const cssFiles = fs.readdirSync(path.join(buildDir, 'static', 'css'))
  .filter(file => file.endsWith('.css'))
  .map(file => path.join('static', 'css', file));

// Read the content of each JavaScript file
const jsContent = jsFiles.map(file => {
  return fs.readFileSync(path.join(buildDir, file), 'utf8');
}).join('\n');

// Read the content of each CSS file
const cssContent = cssFiles.map(file => {
  return fs.readFileSync(path.join(buildDir, file), 'utf8');
}).join('\n');

// Create a standalone HTML file
let standaloneHtml = indexHtml;

// Replace the CSS links with inline CSS
standaloneHtml = standaloneHtml.replace(
  /<link[^>]*href="\/static\/css\/[^"]*"[^>]*>/g,
  `<style>${cssContent}</style>`
);

// Replace the JavaScript script tags with inline JavaScript
standaloneHtml = standaloneHtml.replace(
  /<script[^>]*src="\/static\/js\/[^"]*"[^>]*><\/script>/g,
  ''
);

// Add the JavaScript content at the end of the body
standaloneHtml = standaloneHtml.replace(
  '</body>',
  `<script>
    // Force demo mode
    window.FORCE_DEMO_MODE = true;
    
    ${jsContent}
  </script>
  </body>`
);

// Update paths to be relative instead of absolute
standaloneHtml = standaloneHtml.replace(/href="\//g, 'href="');
standaloneHtml = standaloneHtml.replace(/src="\//g, 'src="');

// Add a title specific to the standalone demo
standaloneHtml = standaloneHtml.replace(
  /<title>.*?<\/title>/,
  '<title>Workflow Builder Demo</title>'
);

// Add a meta description
standaloneHtml = standaloneHtml.replace(
  /<meta name="description".*?>/,
  '<meta name="description" content="Standalone demo of the Workflow Builder. No installation required.">'
);

// Write the standalone HTML file
fs.writeFileSync(path.join(buildDir, 'workflow-builder-demo.html'), standaloneHtml);

console.log('Standalone HTML file created: build/workflow-builder-demo.html');
