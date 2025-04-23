# Script to update just the standalone demo HTML file on GitHub Pages

# Navigate to the frontend directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $scriptDir ".."
Set-Location $frontendDir

Write-Host "Starting standalone demo update..." -ForegroundColor Green

# Create a temporary directory
Write-Host "Creating temporary directory..." -ForegroundColor Yellow
$tempDir = Join-Path $env:TEMP "standalone-demo-update-$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy the standalone demo HTML file
Write-Host "Copying standalone demo HTML file..." -ForegroundColor Yellow
$examplesDir = Join-Path $tempDir "examples"
New-Item -ItemType Directory -Path $examplesDir -Force | Out-Null
Copy-Item -Path "..\docs\examples\standalone-demo.html" -Destination $examplesDir

# Switch to gh-pages branch
Write-Host "Switching to gh-pages branch..." -ForegroundColor Yellow
git checkout gh-pages

# Create examples directory if it doesn't exist
Write-Host "Ensuring examples directory exists..." -ForegroundColor Yellow
$ghPagesExamplesDir = "examples"
if (-not (Test-Path $ghPagesExamplesDir)) {
    New-Item -ItemType Directory -Path $ghPagesExamplesDir -Force | Out-Null
}

# Copy the standalone demo HTML file to gh-pages
Write-Host "Updating standalone demo HTML file..." -ForegroundColor Yellow
Copy-Item -Path "$examplesDir\standalone-demo.html" -Destination $ghPagesExamplesDir -Force

# Add the file to git
Write-Host "Adding file to git..." -ForegroundColor Yellow
git add "examples/standalone-demo.html"

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Update standalone demo HTML with enhanced feedback system"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin gh-pages

# Clean up
Write-Host "Cleaning up..." -ForegroundColor Yellow
Remove-Item -Path $tempDir -Recurse -Force

# Switch back to main branch
Write-Host "Switching back to main branch..." -ForegroundColor Yellow
git checkout main

Write-Host "Update complete! The standalone demo has been updated with the enhanced feedback system." -ForegroundColor Green
Write-Host "Visit https://sagura091.github.io/workflow-builder/examples/standalone-demo.html to see the updated demo." -ForegroundColor Cyan
