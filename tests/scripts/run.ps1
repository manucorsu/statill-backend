pytest --cov=app --cov-report=html

$reportPath = Join-Path -Path (Get-Location) -ChildPath "htmlcov\index.html"

if (Test-Path $reportPath) {
    Write-Host "Coverage report generated at:`n$reportPath"
} else {
    Write-Host "Coverage report not found. Please check if pytest ran successfully."
}
