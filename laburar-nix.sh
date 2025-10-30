#!/bin/bash
# Solo testeado en Linux Mint 22.2

read -p "Ingresá el comando de python que usás [default: python3]: " python_cmd
python_cmd=${python_cmd:-python3}

if ! command -v "$python_cmd" &>/dev/null; then
    echo "Error: '$python_cmd' no existe/no está en PATH"
    read -p "Presioná Enter para salir."
    return 1 2>/dev/null || exit 1
fi

PYTHON_VERSION_OUTPUT=$("$python_cmd" --version 2>&1) || {
  echo "❌ No se pudo ejecutar $python_cmd. Asegúrate de que esté instalado."
  exit 1
}

# Extraer el número de versión (ejemplo: "3.10.8")
PYTHON_VERSION=$(echo "$PYTHON_VERSION_OUTPUT" | awk '{print $2}')

# Extraer la versión mayor y menor
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

# Verificar rango permitido
if [[ "$MAJOR" -ne 3 ]] || [[ "$MINOR" -lt 9 || "$MINOR" -gt 13 ]]; then
  echo "❌ Versión de Python incompatible: $PYTHON_VERSION"
  echo "   Se requiere Python entre 3.9 y 3.13 (inclusive)."
  exit 1
fi

echo "✅ Versión de Python válida: $PYTHON_VERSION"
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
echo

echo "✅ Listo. No te olvides de importar el .env"
echo
