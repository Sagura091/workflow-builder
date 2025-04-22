# Workflow Builder Demo Deployment

This guide explains how to deploy the Workflow Builder Demo to GitHub Pages so that users can access it via a URL without any installation.

## Why GitHub Pages?

GitHub Pages provides free hosting for static websites directly from your GitHub repository. This is perfect for our demo as:

1. It's completely free
2. It's easy to set up and deploy
3. It's accessible via a public URL
4. It automatically updates when you push changes

## Setup Instructions

### 1. Update the Repository URL

Before deploying, you need to update the `homepage` field in `package.json` to match your GitHub repository:

```json
"homepage": "https://Sagura091.github.io/workflow-builder",
```

This is already set to your GitHub username (Sagura091).

### 2. Deploy Using the Script

#### Windows:
Run the `deploy-demo.bat` script:
```
deploy-demo.bat
```

#### PowerShell:
Run the `deploy-demo.ps1` script:
```
.\deploy-demo.ps1
```

#### Manual Deployment:
If you prefer to deploy manually, run:
```
npm install
npm run deploy
```

### 3. Enable GitHub Pages in Repository Settings

After deploying, you need to enable GitHub Pages in your repository settings:

1. Go to your repository on GitHub
2. Click on "Settings"
3. Scroll down to the "GitHub Pages" section
4. Select the `gh-pages` branch as the source
5. Click "Save"

## Accessing the Demo

Once deployed, the demo will be available at:
```
https://Sagura091.github.io/workflow-builder
```

This URL is already configured with your GitHub username.

## How It Works

The deployment process:

1. Builds the React application with `npm run build`
2. Pushes the built files to the `gh-pages` branch of your repository
3. GitHub automatically serves these files as a static website

The demo automatically runs in demo mode when accessed via GitHub Pages, thanks to the `setupDemoMode.js` script that detects when the app is running on GitHub Pages.

## Updating the Demo

To update the demo after making changes:

1. Make your changes to the code
2. Run the deployment script again
3. The changes will be automatically deployed to GitHub Pages

## Troubleshooting

If you encounter issues:

1. Make sure you have the correct permissions to push to the repository
2. Check that the `gh-pages` branch exists and is set as the source in GitHub Pages settings
3. Wait a few minutes for the changes to propagate
4. Clear your browser cache if you don't see the updates

## Alternative Hosting Options

If you prefer not to use GitHub Pages, you can also deploy to:

1. **Netlify**: Connect your GitHub repository to Netlify for automatic deployments
2. **Vercel**: Similar to Netlify, with a generous free tier
3. **Firebase Hosting**: Google's hosting service with a free tier
4. **AWS Amplify**: Amazon's hosting service for web applications
