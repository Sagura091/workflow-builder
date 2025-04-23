#!/bin/bash

# Deploy Workflow Builder to GitHub Pages
echo "Deploying Workflow Builder to GitHub Pages..."

# Step 1: Check dependencies
echo -e "\nStep 1: Checking dependencies..."
if ! npm list gh-pages >/dev/null 2>&1; then
  echo "Installing gh-pages package..."
  npm install --save-dev gh-pages
fi

# Step 2: Build for GitHub Pages
echo -e "\nStep 2: Building for GitHub Pages..."
npm run build:github

if [ $? -ne 0 ]; then
  echo "Build failed. Aborting deployment."
  exit 1
fi

# Step 3: Deploy to GitHub Pages
echo -e "\nStep 3: Deploying to GitHub Pages..."
npx gh-pages -d build

if [ $? -ne 0 ]; then
  echo "Deployment failed."
  exit 1
fi

echo -e "\nDeployment completed successfully!"
echo "Your site should be available at: https://Sagura091.github.io/workflow-builder"
echo "Note: It may take a few minutes for the changes to propagate."
