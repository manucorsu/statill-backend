Write-Host "Creando .venv..."
python -m venv .venv
Write-Host ""

Write-Host "Activando el entorno virtual..."
. .\.venv\Scripts\Activate.ps1
Write-Host ""

Write-Host "(Python es...)"
Get-Command python | Select-Object -ExpandProperty Source
Write-Host ""

Write-Host "Actualizando pip..."
python -m pip install --upgrade pip
Write-Host ""

Write-Host "Instalando dependencias..."
python -m pip install -r requirements.txt
Write-Host ""

Write-Host "✅ Listo."
Write-Host ""
