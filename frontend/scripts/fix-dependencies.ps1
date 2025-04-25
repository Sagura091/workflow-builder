# Script to fix dependencies for the workflow builder

Write-Host "Fixing dependencies for the workflow builder..." -ForegroundColor Green

# Navigate to the root directory
Set-Location -Path (Join-Path $PSScriptRoot "..")
Set-Location -Path (Join-Path (Get-Location) "..")

# Remove node_modules and package-lock.json
Write-Host "Removing existing node_modules and package-lock.json..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Path "node_modules" -Recurse -Force
}
if (Test-Path "package-lock.json") {
    Remove-Item -Path "package-lock.json" -Force
}

# Install specific versions of problematic dependencies
Write-Host "Installing specific versions of dependencies..." -ForegroundColor Yellow
npm install --save ajv@8.12.0
npm install --save ajv-keywords@5.1.0

# Install all dependencies
Write-Host "Installing all dependencies..." -ForegroundColor Yellow
npm install

Write-Host "Dependency fix complete! Try running npm start or npm build now." -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
