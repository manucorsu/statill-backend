@echo off
chcp 65001
cls

echo Creando .venv...
python -m venv .venv
echo.

echo Activando el entorno virtual...
call .\.venv\Scripts\activate.bat
echo.

echo (Python es...)
python -c "import sys; print(sys.executable)"
echo.

echo Actualizando pip...
python -m pip install --upgrade pip
echo.

echo Instalando dependencias...
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
pre-commit install
echo.

echo ✅ Listo. No te olvides de importar el .env
echo.

