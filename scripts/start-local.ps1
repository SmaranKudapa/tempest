$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"

Set-Location $repoRoot
docker compose up -d postgres

Start-Process powershell.exe -WorkingDirectory $repoRoot -ArgumentList @(
  "-NoExit",
  "-Command",
  "python -m uvicorn backend.app.main:app --reload"
)

Start-Process powershell.exe -WorkingDirectory $frontendRoot -ArgumentList @(
  "-NoExit",
  "-Command",
  "npm run dev"
)

Write-Host "Started PostgreSQL, backend, and frontend."
Write-Host "Dashboard: http://localhost:3000"
Write-Host "Backend:   http://127.0.0.1:8000"
