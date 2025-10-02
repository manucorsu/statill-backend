#!/bin/bash
# Solo testeado en Linux Mint 22.1

read -p "Ingresá el comando de python que usás [default: python3]: " python_cmd
python_cmd=${python_cmd:-python3}

if ! command -v "$python_cmd" &>/dev/null; then
    echo "Error: '$python_cmd' no existe/no está en PATH"
    read -p "Presioná Enter para salir."
    return 1 2>/dev/null || exit 1
fi

if ! "$python_cmd" -m venv --help &>/dev/null; then
    echo "Error: '$python_cmd' no tiene venv instalado"
    read -p "Presioná Enter para salir."
    return 1 2>/dev/null || exit 1
fi


tmp_dir=$(mktemp -d)
if ! "$python_cmd" -m venv "$tmp_dir/test_venv" &> /dev/null; then
    echo "Error: venv está instalado para '$python_cmd', pero no funciona correctamente."
    echo "Muy probablemente falte instalar '${python_cmd}-venv'."
    read -p "Presioná Enter para salir."
    rm -rf "$tmp_dir"
    return 1 2>/dev/null || exit 1
fi
rm -rf "$tmp_dir"

echo "Creando .venv..."
"$python_cmd" -m venv .venv
echo

echo "Activando .venv..."
source .venv/bin/activate
echo

echo "(Python es...)"
which "$python_cmd"
echo

echo "Actualizando pip..."
"$python_cmd" -m pip install --upgrade pip
echo

echo "Instalando dependencias..."
"$python_cmd" -m pip install -r requirements.txt
"$python_cmd" -m pip install -r requirements-dev.txt
pre-commit install
echo

echo "✅ Listo. No te olvides de importar el .env"
echo
