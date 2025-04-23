# Workflow Builder Scripts

This directory contains various scripts used for development, deployment, and utility functions for the Workflow Builder project.

## Directory Structure

- **deployment/**: Scripts for deploying the application to various environments
  - `deploy-github-pages.bat`: Windows script for deploying to GitHub Pages
  - `deploy-github-pages.sh`: Bash script for deploying to GitHub Pages
  - `deploy-github-pages-simple.bat`: Simplified Windows script for GitHub Pages deployment
  - `deploy-standalone.bat`: Script for deploying the standalone demo version

- **utils/**: Utility scripts for development and maintenance
  - `update-index.sh`: Script to update the index.html file
  - `update-package.sh`: Script to update the package.json file
  - `fix-demo-mode.bat`: Script to fix demo mode issues
  - `direct-deploy.bat`: Direct deployment script without using package.json scripts

## Usage

### Deployment Scripts

To deploy to GitHub Pages:

```bash
# On Windows
./scripts/deployment/deploy-github-pages.bat

# On Unix/Linux/Mac
./scripts/deployment/deploy-github-pages.sh
```

### Utility Scripts

To update the index.html file:

```bash
./scripts/utils/update-index.sh
```

To update the package.json file:

```bash
./scripts/utils/update-package.sh
```
