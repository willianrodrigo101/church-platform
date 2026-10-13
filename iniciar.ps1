# ==========================================
# CHURCH PLATFORM - Inicia backend + frontend
# ==========================================
# Uso:
#   .\iniciar.ps1
#
# Abre 2 janelas do PowerShell:
#   1) uvicorn (backend) na porta 8000
#   2) servir_frontend.py na porta 5500
# ==========================================

$RaizProjeto = $PSScriptRoot
$Backend = Join-Path $RaizProjeto "backend"
$Servidor = Join-Path $RaizProjeto "servir_frontend.py"

if (-not (Test-Path $Backend)) {
    Write-Host "ERRO: pasta backend nao encontrada em $RaizProjeto" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $Servidor)) {
    Write-Host "ERRO: servir_frontend.py nao encontrado em $RaizProjeto" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "CHURCH PLATFORM - iniciando..." -ForegroundColor Cyan
Write-Host ""

# Comando 1 - Backend
$cmdBackend = "Set-Location '$Backend'; & '.\.venv\Scripts\Activate.ps1'; Write-Host 'BACKEND - porta 8000' -ForegroundColor Green; uvicorn app.main:app --reload"

# Comando 2 - Frontend HTTP
$cmdFrontend = "Set-Location '$Backend'; & '.\.venv\Scripts\Activate.ps1'; Write-Host 'FRONTEND - porta 5500' -ForegroundColor Green; python ..\servir_frontend.py"

Write-Host "Abrindo janela do BACKEND..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmdBackend

Start-Sleep -Seconds 2

Write-Host "Abrindo janela do FRONTEND..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmdFrontend

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "CHURCH PLATFORM esta no ar!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Acesse no navegador:" -ForegroundColor White
Write-Host "  http://localhost:5500/index.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "Os 2 servidores abriram em janelas separadas." -ForegroundColor Gray
Write-Host "Para parar tudo: feche as 2 janelas." -ForegroundColor Gray
Write-Host ""

# Abre o navegador automaticamente
Start-Sleep -Seconds 3
Start-Process "http://localhost:5500/index.html"