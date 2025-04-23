const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Path to the original index.js
const originalIndexPath = path.resolve(__dirname, '../src/index.js');
// Path to the GitHub Pages entry point
const githubPagesEntryPath = path.resolve(__dirname, '../src/GithubPagesEntry.tsx');
// Backup path for the original index.js
const backupIndexPath = path.resolve(__dirname, '../src/index.js.backup');

// Function to run a command and log output
function runCommand(command) {
  console.log(`Running: ${command}`);
  try {
    execSync(command, { stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error(`Command failed: ${command}`);
    console.error(error.message);
    return false;
  }
}

// Main function
async function main() {
  try {
    // Backup the original index.js
    console.log('Backing up original index.js...');
    fs.copyFileSync(originalIndexPath, backupIndexPath);

    // Replace index.js with GithubPagesEntry.tsx content
    console.log('Replacing index.js with GithubPagesEntry.tsx for GitHub Pages build...');
    const githubPagesContent = fs.readFileSync(githubPagesEntryPath, 'utf8');
    
    // Create a JavaScript version of the entry point
    const jsContent = `// Auto-generated from GithubPagesEntry.tsx
${githubPagesContent.replace(/import React/g, 'import * as React')}`;
    
    fs.writeFileSync(originalIndexPath, jsContent);

    // Run the build command
    console.log('Building the application...');
    const buildSuccess = runCommand('npm run build --legacy-peer-deps');
    
    if (!buildSuccess) {
      throw new Error('Build failed');
    }

    console.log('Build completed successfully!');
    
    // Deploy to GitHub Pages
    console.log('Deploying to GitHub Pages...');
    const deploySuccess = runCommand('npx gh-pages -d build');
    
    if (!deploySuccess) {
      throw new Error('Deployment failed');
    }
    
    console.log('Deployment completed successfully!');
    console.log('Your site should be available at: https://Sagura091.github.io/workflow-builder');
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    // Restore the original index.js
    console.log('Restoring original index.js...');
    if (fs.existsSync(backupIndexPath)) {
      fs.copyFileSync(backupIndexPath, originalIndexPath);
      fs.unlinkSync(backupIndexPath);
      console.log('Original index.js restored.');
    } else {
      console.warn('Could not restore original index.js: backup file not found.');
    }
  }
}

// Run the main function
main();
