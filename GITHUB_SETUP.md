# Setting Up Your GitHub Repository and Deploying to GitHub Pages

This guide will walk you through the process of setting up a GitHub repository for your Workflow Builder project and deploying the demo to GitHub Pages.

## 1. Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top-right corner and select "New repository"
3. Repository name: `workflow-builder`
4. Description: `A visual workflow builder for creating and executing workflows`
5. Make it Public
6. Do not initialize with README, .gitignore, or license (we'll add these ourselves)
7. Click "Create repository"

## 2. Initialize Your Local Repository

Open a terminal/command prompt in your project's root directory and run:

```bash
# Initialize a new Git repository
git init

# Add all files to staging
git add .

# Make the initial commit
git commit -m "Initial commit"

# Set the main branch name
git branch -M main

# Add the remote repository
git remote add origin https://github.com/Sagura091/workflow-builder.git

# Push to GitHub
git push -u origin main
```

## 3. Deploy the Demo to GitHub Pages

Now that your code is on GitHub, you can deploy the demo:

```bash
# Navigate to the frontend directory
cd frontend

# Run the direct deployment script (recommended for TypeScript 5.x)
# For Windows Command Prompt:
direct-deploy.bat

# For PowerShell:
.\direct-deploy.ps1

# Alternatively, you can use the regular deployment scripts
# For Windows Command Prompt:
deploy-demo.bat

# For PowerShell:
.\deploy-demo.ps1
```

## 4. Enable GitHub Pages in Repository Settings

1. Go to your repository on GitHub
2. Click "Settings"
3. Scroll down to "GitHub Pages" section
4. For Source, select the `gh-pages` branch
5. Click "Save"
6. Wait a few minutes for the site to be published

Your demo will be available at: `https://Sagura091.github.io/workflow-builder`

## 5. Updating the Demo

Whenever you make changes to your code:

1. Commit and push your changes to GitHub:
```bash
git add .
git commit -m "Description of changes"
git push
```

2. Run the deployment script again:
```bash
cd frontend
deploy-demo.bat  # or .\deploy-demo.ps1
```

## Notes About .gitignore

We've included two `.gitignore` files:

1. A root-level `.gitignore` for the entire project
2. A frontend-specific `.gitignore` in the frontend directory

These files prevent unnecessary files from being committed to your repository, such as:

- Node modules
- Build artifacts
- Environment files
- Editor-specific files
- Logs and cache files

## Troubleshooting

### Authentication Issues

If you encounter authentication issues when deploying:

1. Make sure you're logged in to Git with the correct credentials
2. You might need to create a Personal Access Token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Generate a new token with "repo" permissions
   - Use this token as your password when prompted

### Deployment Issues

If the deployment fails:

1. Check the error messages in the console
2. Try using the direct deployment scripts which bypass TypeScript version checks:
   ```bash
   cd frontend
   .\direct-deploy.ps1  # or direct-deploy.bat
   ```
3. If you have TypeScript version conflicts, use the `--legacy-peer-deps` flag:
   ```bash
   npm install --legacy-peer-deps
   npm run deploy
   ```
4. Make sure you have the `gh-pages` package installed:
   ```bash
   cd frontend
   npm install --save-dev gh-pages --legacy-peer-deps
   ```
5. Verify that the `homepage` field in `package.json` is correct:
   ```json
   "homepage": "https://Sagura091.github.io/workflow-builder"
   ```

### Site Not Showing Up

If your site doesn't appear after deployment:

1. Wait a few minutes (GitHub Pages can take time to update)
2. Check that the `gh-pages` branch exists in your repository
3. Verify that GitHub Pages is enabled in your repository settings
4. Check the GitHub Pages section in your repository settings for any error messages
