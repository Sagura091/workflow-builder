const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('Deploying to GitHub Pages...');

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

// Main deployment function
async function deploy() {
  try {
    // Step 1: Install gh-pages if not already installed
    console.log('\nStep 1: Checking dependencies...');
    runCommand('npm list gh-pages || npm install --save-dev gh-pages');
    
    // Step 2: Build for GitHub Pages
    console.log('\nStep 2: Building for GitHub Pages...');
    const buildSuccess = runCommand('npm run build:github');
    
    if (!buildSuccess) {
      throw new Error('Build failed');
    }
    
    // Step 3: Deploy to GitHub Pages
    console.log('\nStep 3: Deploying to GitHub Pages...');
    const deploySuccess = runCommand('npx gh-pages -d build');
    
    if (!deploySuccess) {
      throw new Error('Deployment failed');
    }
    
    console.log('\nDeployment completed successfully!');
    console.log('Your site should be available at: https://Sagura091.github.io/workflow-builder');
    console.log('Note: It may take a few minutes for the changes to propagate.');
    
  } catch (error) {
    console.error('\nDeployment failed:', error.message);
    process.exit(1);
  }
}

// Run the deployment
deploy();
