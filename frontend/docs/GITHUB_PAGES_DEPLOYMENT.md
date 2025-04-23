# GitHub Pages Deployment Guide

This document explains how to deploy the Workflow Builder demo to GitHub Pages.

## Overview

The GitHub Pages deployment creates a standalone demo version of the Workflow Builder that runs entirely in the browser without requiring a backend. This makes it easy to showcase the application's capabilities to users who don't want to set up the full development environment.

## Features of the GitHub Pages Demo

- Runs completely in the browser with no backend requirements
- Uses mock data for nodes, plugins, and workflow execution
- Includes all core UI functionality (drag and drop, node configuration, etc.)
- Simulates workflow execution with realistic feedback

## Deployment Instructions

### Automatic Deployment

The easiest way to deploy to GitHub Pages is to use the provided script:

```bash
# From the frontend directory
npm run deploy:github
```

This script will:
1. Build the application with the GitHub Pages entry point
2. Configure the build for standalone demo mode
3. Deploy the build to the gh-pages branch of your repository

### Manual Deployment

If you prefer to deploy manually, you can follow these steps:

1. Build the application for GitHub Pages:
   ```bash
   npm run build:github
   ```

2. Deploy the build to GitHub Pages:
   ```bash
   npx gh-pages -d build
   ```

## How It Works

The GitHub Pages deployment uses a special entry point (`GithubPagesEntry.tsx`) that:

1. Forces demo mode by setting global flags:
   ```javascript
   window.FORCE_DEMO_MODE = true;
   window.STANDALONE_DEMO = true;
   window.ENSURE_DEMO_MODE_PROVIDER = true;
   ```

2. Disables features that require a backend:
   ```javascript
   window.FEATURES = {
     ...window.FEATURES,
     WEBSOCKETS_ENABLED: false,
     ENABLE_SCHEDULING: false
   };
   ```

3. Uses the `DemoApp` component which is specifically designed for standalone operation

## Troubleshooting

If you encounter issues with the GitHub Pages deployment:

1. **404 Errors**: Make sure the `homepage` field in `package.json` is set correctly to your GitHub Pages URL.

2. **Missing Assets**: Check that all assets are being properly included in the build.

3. **JavaScript Errors**: Open the browser console to check for any JavaScript errors that might be occurring.

4. **Blank Page**: Ensure that the entry point is correctly configured and that the demo mode flags are being set.

## Customizing the Demo

To customize what appears in the GitHub Pages demo:

1. Modify the mock data in `src/services/mockData.ts` to include different nodes, plugins, or sample workflows.

2. Update the `DemoApp` component in `src/pages/DemoApp.tsx` to change the layout or included components.

3. Adjust the demo welcome message or other UI elements specific to the demo mode.

## Updating the Demo

After making changes to the application, you can update the GitHub Pages demo by running the deployment script again:

```bash
npm run deploy:github
```

This will build and deploy the latest version of your application to GitHub Pages.
