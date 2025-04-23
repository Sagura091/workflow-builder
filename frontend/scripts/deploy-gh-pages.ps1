# Script to deploy the React app to GitHub Pages with the enhanced feedback system

# Navigate to the frontend directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $scriptDir ".."
Set-Location $frontendDir

Write-Host "Starting GitHub Pages deployment..." -ForegroundColor Green

# Build the React app
Write-Host "Building the React app..." -ForegroundColor Yellow
npm run build

# Create a temporary directory for deployment
Write-Host "Creating temporary directory for deployment..." -ForegroundColor Yellow
$tempDir = Join-Path $env:TEMP "gh-pages-deploy-$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir | Out-Null
Copy-Item -Path "build\*" -Destination $tempDir -Recurse

# Copy the standalone demo HTML file
Write-Host "Copying standalone demo HTML file..." -ForegroundColor Yellow
$examplesDir = Join-Path $tempDir "examples"
New-Item -ItemType Directory -Path $examplesDir -Force | Out-Null
Copy-Item -Path "..\docs\examples\standalone-demo.html" -Destination $examplesDir

# Copy the feedback setup documentation
Write-Host "Copying feedback documentation..." -ForegroundColor Yellow
$docsDir = Join-Path $tempDir "docs"
New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
Copy-Item -Path "..\docs\FEEDBACK_SETUP.md" -Destination $docsDir

# Switch to gh-pages branch
Write-Host "Switching to gh-pages branch..." -ForegroundColor Yellow
git checkout gh-pages

# Remove existing files (except .git)
Write-Host "Cleaning gh-pages branch..." -ForegroundColor Yellow
Get-ChildItem -Path . -Exclude .git | Remove-Item -Recurse -Force

# Copy the built files
Write-Host "Copying built files to gh-pages branch..." -ForegroundColor Yellow
Copy-Item -Path "$tempDir\*" -Destination . -Recurse

# Add all files to git
Write-Host "Adding files to git..." -ForegroundColor Yellow
git add .

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Update GitHub Pages demo with enhanced feedback system"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin gh-pages

# Clean up
Write-Host "Cleaning up..." -ForegroundColor Yellow
Remove-Item -Path $tempDir -Recurse -Force

# Switch back to main branch
Write-Host "Switching back to main branch..." -ForegroundColor Yellow
git checkout main

Write-Host "Deployment complete! Your demo is now live with the enhanced feedback system." -ForegroundColor Green
Write-Host "Visit https://sagura091.github.io/workflow-builder/ to see the deployed demo." -ForegroundColor Cyan
