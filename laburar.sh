echo "Creando .venv..."
python -m venv .venv
echo

echo "Activando .venv..."
source .venv/Scripts/activate
echo

echo "(Python es...)"
which python
echo

echo "Actualizando pip..."
python -m pip install --upgrade pip
echo

echo "Instalando dependencias..."
python -m pip install -r requirements.txt
python -m pip install -U black
echo

echo "✅ Listo. No te olvides de importar el .env"
echo
