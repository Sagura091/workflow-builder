#!/bin/bash

# Script to deploy the React app to GitHub Pages with the enhanced feedback system

# Exit on error
set -e

echo "Starting GitHub Pages deployment..."

# Navigate to the frontend directory
cd "$(dirname "$0")/.."
FRONTEND_DIR=$(pwd)

# Build the React app
echo "Building the React app..."
npm run build

# Create a temporary directory for deployment
echo "Creating temporary directory for deployment..."
TEMP_DIR=$(mktemp -d)
cp -r build/* $TEMP_DIR/

# Copy the standalone demo HTML file
echo "Copying standalone demo HTML file..."
mkdir -p $TEMP_DIR/examples
cp ../docs/examples/standalone-demo.html $TEMP_DIR/examples/

# Copy the feedback setup documentation
echo "Copying feedback documentation..."
mkdir -p $TEMP_DIR/docs
cp ../docs/FEEDBACK_SETUP.md $TEMP_DIR/docs/

# Switch to gh-pages branch
echo "Switching to gh-pages branch..."
git checkout gh-pages

# Remove existing files (except .git)
echo "Cleaning gh-pages branch..."
find . -maxdepth 1 -not -path "./.git" -not -path "." -exec rm -rf {} \;

# Copy the built files
echo "Copying built files to gh-pages branch..."
cp -r $TEMP_DIR/* .

# Add all files to git
echo "Adding files to git..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Update GitHub Pages demo with enhanced feedback system"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin gh-pages

# Clean up
echo "Cleaning up..."
rm -rf $TEMP_DIR

# Switch back to main branch
echo "Switching back to main branch..."
git checkout main

echo "Deployment complete! Your demo is now live with the enhanced feedback system."
echo "Visit https://sagura091.github.io/workflow-builder/ to see the deployed demo."
