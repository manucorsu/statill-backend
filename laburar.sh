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
pip install -r requirements.txt
echo

echo "✅ Listo."
echo
