# Render Backend Deploy Script
# Usage: .\deploy-backend.ps1 -ApiKey "rnd_XXXXXXXXXXXX"

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey
)

$headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Content-Type"  = "application/json"
}

Write-Host "`n=== Checking existing Render services ===" -ForegroundColor Cyan
$services = Invoke-RestMethod -Uri "https://api.render.com/v1/services?limit=20" -Headers $headers -Method Get

$backendService = $services.service | Where-Object { $_.name -eq "ai-app-architect-backend" }

if ($backendService) {
    $serviceId = $backendService.id
    Write-Host "Found existing backend service: $serviceId" -ForegroundColor Green

    Write-Host "`n=== Triggering new deploy ===" -ForegroundColor Cyan
    $deploy = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/deploys" `
        -Headers $headers -Method Post -Body "{}"

    Write-Host "Deploy triggered! ID: $($deploy.id)" -ForegroundColor Green
    Write-Host "Status: $($deploy.status)" -ForegroundColor Yellow
    Write-Host "Backend URL: https://ai-app-architect-backend.onrender.com" -ForegroundColor Cyan
} else {
    Write-Host "No existing service found. Creating via Blueprint..." -ForegroundColor Yellow

    # Read render.yaml
    $repoUrl = "https://github.com/officialkrishna2455-tech/AI-App-Architect"

    Write-Host "`nTo deploy via Blueprint:" -ForegroundColor Cyan
    Write-Host "1. Go to https://dashboard.render.com/blueprints/new" -ForegroundColor White
    Write-Host "2. Connect repo: $repoUrl" -ForegroundColor White
    Write-Host "3. Click 'Apply' — render.yaml does the rest!" -ForegroundColor White
}

Write-Host "`n=== Your Live URLs ===" -ForegroundColor Green
Write-Host "Frontend: https://frontend-krishna2455.vercel.app" -ForegroundColor Cyan
Write-Host "Backend:  https://ai-app-architect-backend.onrender.com" -ForegroundColor Cyan
