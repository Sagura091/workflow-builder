Write-Host "Deploying Workflow Builder Demo to GitHub Pages..." -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "Error installing dependencies. Please check your npm installation."
    }

    Write-Host ""
    Write-Host "Step 2: Building and deploying the application..." -ForegroundColor Yellow
    npm run deploy
    if ($LASTEXITCODE -ne 0) {
        throw "Error deploying the application. Please check the error messages above."
    }

    Write-Host ""
    Write-Host "Demo successfully deployed to GitHub Pages!" -ForegroundColor Green
    Write-Host "You can now access it at: https://Sagura091.github.io/workflow-builder" -ForegroundColor Green
    Write-Host ""
    Write-Host "Note: It may take a few minutes for the changes to propagate." -ForegroundColor Yellow
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Read-Host "Press Enter to continue..."
}
