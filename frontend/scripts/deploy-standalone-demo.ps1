# Script to deploy just the standalone demo to GitHub Pages

# Navigate to the frontend directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $scriptDir ".."
Set-Location $frontendDir

Write-Host "Starting standalone demo deployment..." -ForegroundColor Green

# Switch to gh-pages branch
Write-Host "Switching to gh-pages branch..." -ForegroundColor Yellow
git checkout gh-pages

# Create examples directory if it doesn't exist
Write-Host "Ensuring examples directory exists..." -ForegroundColor Yellow
if (-not (Test-Path "examples")) {
    New-Item -ItemType Directory -Path "examples" -Force | Out-Null
}

# Copy the standalone demo HTML file from main branch
Write-Host "Copying standalone demo HTML file from main branch..." -ForegroundColor Yellow
git checkout main -- ../docs/examples/standalone-demo.html
Copy-Item -Path "../docs/examples/standalone-demo.html" -Destination "examples/" -Force

# Add the file to git
Write-Host "Adding file to git..." -ForegroundColor Yellow
git add "examples/standalone-demo.html"

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Update standalone demo HTML with enhanced workflow operations"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin gh-pages

# Switch back to main branch
Write-Host "Switching back to main branch..." -ForegroundColor Yellow
git checkout main

Write-Host "Deployment complete! The standalone demo has been updated with enhanced workflow operations." -ForegroundColor Green
Write-Host "Visit https://sagura091.github.io/workflow-builder/examples/standalone-demo.html to see the updated demo." -ForegroundColor Cyan
