# statill-backend
Repositorio de la API de Statill.

## ¿CÓMO LABURAR?
*Esta guía habla de cómo configurar el entorno de desarollo para trabajar en la API. Para ver cómo usarla (su documentación), ver `/docs` o `/redoc`.*

1. Clonar el repositorio y abirirlo en VSCode.
2. Cambiar a la branch que corresponda (`dev`, en general) por cualquier medio (GitHub Desktop, VS Code Source Control o `git checkout` en la terminal)
3. Abrir una terminal. Para hacerlo dentro de VSCode, el shortcut predeterminado es `Ctrl+Ñ`. Independientemente de donde se haya abierto, **se debe usar esa terminal para todo el trabajo de esa sesión**.



### En Windows:
4. Ejecutar el script `laburar` de la manera requerida por la shell.

| Shell | Comando |
| :------- | :------: | 
| cmd  | `call laburar.cmd`  | 
| PowerShell  | `. .\laburar.ps1`  | 
| Git Bash (NO WSL) | `source laburar.sh` |

### En Linux/macOS:
4. `source laburar-nix.sh`.

### Luego (en cualquer plataforma):
5. Verificar que aparece `(.venv)` al costado de la ruta (ej en cmd. `(.venv) C:\Users\Manu\Repositories\statill-backend>`), o abajo de cada comando ejecutado si se está usando Git Bash.
6. Poner el `.env` en el root del directorio del proyecto.
7. Probar `fastapi dev`
8. (opcional pero altamente recomendado) Al abrir un archivo de Python, VSCode te va a preguntar si querés instalar las extensiones recomendadas para el lenguaje. Por tu salud mental, decile que **sí**, lo va hacer en el fondo sin interrumpirte. 

### Si algo no funciona:
* Verificar que se esté usando el entorno virtual ejecutando el comdando que ves en la tabla para tu shell. Si el path que aparece a Python (`python.exe` en Windows) **NO ESTÁ EN EL DIRECTORIO `statill-backend/.venv`**, o el entorno virtual no se creó y activó correctamente o no se estando la misma terminal que se usó para ejecutar el script. Repetir todo desde el paso 2.

| Shell | Comando |
| :------- | :------: | 
| cmd  | `python -c "import sys; print(sys.executable)"`  | 
| PowerShell  | `Get-Command python`  | 
| bash | `which python` |

