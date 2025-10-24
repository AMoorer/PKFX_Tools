# Install GitHub CLI
# This script downloads and installs the latest GitHub CLI for Windows

Write-Host "Installing GitHub CLI..." -ForegroundColor Green

# Download the installer
$installerUrl = "https://github.com/cli/cli/releases/latest/download/gh_windows_amd64.msi"
$installerPath = "$env:TEMP\gh_installer.msi"

Write-Host "Downloading GitHub CLI installer..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

Write-Host "Running installer..." -ForegroundColor Cyan
Start-Process msiexec.exe -Wait -ArgumentList "/i `"$installerPath`" /quiet /norestart"

Write-Host "Cleaning up..." -ForegroundColor Cyan
Remove-Item $installerPath

Write-Host ""
Write-Host "GitHub CLI installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close and reopen your terminal to refresh PATH"
Write-Host "2. Run: gh auth login"
Write-Host "3. Follow the prompts to authenticate with GitHub"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  gh repo view           - View repository info"
Write-Host "  gh release list        - List releases"
Write-Host "  gh release create      - Create a new release"
Write-Host "  gh issue list          - List issues"
Write-Host "  gh pr list             - List pull requests"
