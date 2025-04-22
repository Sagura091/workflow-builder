Write-Host "Directly deploying Workflow Builder Demo to GitHub Pages..." -ForegroundColor Cyan
Write-Host "This script bypasses TypeScript version checks" -ForegroundColor Yellow
Write-Host ""

try {
    # Install gh-pages if not already installed
    Write-Host "Making sure gh-pages is installed..." -ForegroundColor Yellow
    npm install --no-save --legacy-peer-deps gh-pages
    
    # Build the app with legacy peer deps
    Write-Host "Building the application..." -ForegroundColor Yellow
    $env:NODE_OPTIONS="--openssl-legacy-provider"
    npx react-scripts build --legacy-peer-deps
    
    # Deploy to GitHub Pages
    Write-Host "Deploying to GitHub Pages..." -ForegroundColor Yellow
    npx gh-pages -d build
    
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
