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

// Function to convert image to base64
function imageToBase64(imagePath) {
  try {
    const imageBuffer = fs.readFileSync(imagePath);
    const extension = path.extname(imagePath).substring(1);
    const mimeType = {
      'png': 'image/png',
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'gif': 'image/gif',
      'svg': 'image/svg+xml',
      'ico': 'image/x-icon'
    }[extension] || 'application/octet-stream';

    return `data:${mimeType};base64,${imageBuffer.toString('base64')}`;
  } catch (error) {
    console.warn(`Could not convert image to base64: ${imagePath}`, error);
    return '';
  }
}

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

// Add Font Awesome from CDN
standaloneHtml = standaloneHtml.replace(
  '</head>',
  `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw==" crossorigin="anonymous" referrerpolicy="no-referrer" />
</head>`
);

// Add the JavaScript content at the end of the body
standaloneHtml = standaloneHtml.replace(
  '</body>',
  `<script>
    // Force demo mode
    window.FORCE_DEMO_MODE = true;

    // Disable backend API calls
    window.STANDALONE_DEMO = true;

    // Ensure DemoModeProvider is available
    window.ENSURE_DEMO_MODE_PROVIDER = true;

    ${jsContent}
  </script>
  </body>`
);

// Find all image references in the CSS and HTML and convert them to base64
const imageRegex = /url\(['"]?(\/static\/media\/[^)"']+)['"]?\)/g;
let match;
let processedImages = new Set();

while ((match = imageRegex.exec(standaloneHtml)) !== null) {
  const imagePath = match[1];
  if (!processedImages.has(imagePath)) {
    processedImages.add(imagePath);
    const fullImagePath = path.join(buildDir, imagePath.substring(1)); // Remove leading slash
    if (fs.existsSync(fullImagePath)) {
      const base64Image = imageToBase64(fullImagePath);
      standaloneHtml = standaloneHtml.replace(new RegExp(imagePath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), base64Image);
    }
  }
}

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

// Add a banner at the top of the page
standaloneHtml = standaloneHtml.replace(
  '<div id="root"></div>',
  `<div style="background-color: #f0f9ff; padding: 10px; text-align: center; border-bottom: 1px solid #bae6fd;">
    <p style="margin: 0; font-size: 14px;">
      <strong>Workflow Builder Demo</strong> - This is a standalone demo that runs entirely in your browser. No installation required!
      <a href="https://github.com/yourusername/workflow-builder" target="_blank" style="color: #0284c7; text-decoration: underline;">View on GitHub</a>
    </p>
  </div>
  <div id="root"></div>`
);

// Write the standalone HTML file
fs.writeFileSync(path.join(buildDir, 'workflow-builder-demo.html'), standaloneHtml);

console.log('Standalone HTML file created: build/workflow-builder-demo.html');
