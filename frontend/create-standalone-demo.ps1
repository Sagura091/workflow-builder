Write-Host "Creating standalone demo HTML file..." -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "Error installing dependencies. Please check your npm installation."
    }

    Write-Host ""
    Write-Host "Step 2: Building and bundling the application..." -ForegroundColor Yellow
    npm run create-standalone
    if ($LASTEXITCODE -ne 0) {
        throw "Error building the application. Please check the error messages above."
    }

    Write-Host ""
    Write-Host "Step 3: Copying the file to the root directory..." -ForegroundColor Yellow
    if (-not (Test-Path "build\workflow-builder-demo.html")) {
        throw "Error: The standalone HTML file was not created."
    }

    Copy-Item -Path "build\workflow-builder-demo.html" -Destination "."
    if (-not (Test-Path "workflow-builder-demo.html")) {
        throw "Error copying the file. Please check if you have write permissions."
    }

    Write-Host ""
    Write-Host "Standalone demo created successfully!" -ForegroundColor Green
    Write-Host "You can now open workflow-builder-demo.html in any browser." -ForegroundColor Green
    Write-Host ""

    $openDemo = Read-Host "Would you like to open the demo now? (Y/N)"
    if ($openDemo -eq "Y" -or $openDemo -eq "y") {
        Start-Process "workflow-builder-demo.html"
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Read-Host "Press Enter to continue..."
}
