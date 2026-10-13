# ==========================================
# CHURCH PLATFORM - Ambiente de desenvolvimento
# ==========================================
# Uso: .\dev.ps1
#
# - Vai para a pasta backend
# - Ativa a .venv
# - Mostra atalhos úteis
# ==========================================

$RaizProjeto = $PSScriptRoot
$Backend = Join-Path $RaizProjeto "backend"

if (-not (Test-Path $Backend)) {
    Write-Host "ERRO: pasta backend nao encontrada em $RaizProjeto" -ForegroundColor Red
    exit 1
}

Set-Location $Backend

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "ERRO: ambiente virtual nao encontrado." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "CHURCH PLATFORM - ambiente de desenvolvimento" -ForegroundColor Cyan
Write-Host "Diretorio: $(Get-Location)" -ForegroundColor Green
Write-Host "Python: $(python --version)" -ForegroundColor Green
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --reload       -> inicia o backend (porta 8000)"
Write-Host "  alembic upgrade head                -> aplica migrations pendentes"
Write-Host "  alembic revision --autogenerate     -> cria nova migration"
Write-Host "  psql ...                            -> acessa o banco"
Write-Host ""
Write-Host "Para iniciar TUDO (backend + frontend):" -ForegroundColor Cyan
Write-Host "  cd .. ; .\iniciar.ps1" -ForegroundColor Yellow
Write-Host ""