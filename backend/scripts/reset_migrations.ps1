$ErrorActionPreference = "Stop"

$BackendRoot = Split-Path -Parent $PSScriptRoot
Set-Location $BackendRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CLEAN MIGRATION RESET" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$AppsRoot = Join-Path $BackendRoot "apps"

Get-ChildItem -Path $AppsRoot -Directory | ForEach-Object {
    $MigrationsPath = Join-Path $_.FullName "migrations"

    if (Test-Path $MigrationsPath) {
        Write-Host "Cleaning: $MigrationsPath" -ForegroundColor Yellow

        Get-ChildItem -Path $MigrationsPath -File -Filter "*.py" |
            Where-Object {
                $_.Name -ne "__init__.py"
            } |
            Remove-Item -Force
    }
}

Write-Host ""
Write-Host "Old migrations removed." -ForegroundColor Green
Write-Host ""