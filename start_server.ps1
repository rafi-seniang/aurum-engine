# QuantGold OS - Unified Startup Script
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor DarkYellow
Write-Host "         QUANTGOLD OS - STARTUP LAUNCHER                  " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor DarkYellow

# Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python is not installed or not in PATH."
}

# Run tunnel runner
python .\scripts\tunnel_runner.py
