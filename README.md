# statill-backend
Repositorio de la API de Statill.

## ¿CÓMO LABURAR?
*Esta guía habla de cómo configurar el entorno de desarollo para trabajar en la API. Para ver cómo usarla (su documentación), ver `/docs` o `/redoc`.*

1. Clonar el repositorio y abirirlo en VSCode.
2. Cambiar a la branch que corresponda (`dev`, en general) por cualquier medio (GitHub Desktop, VS Code Source Control o `git checkout` en la terminal)
3. Abrir una terminal. Para hacerlo dentro de VSCode, el shortcut predeterminado es `Ctrl+Ñ`. Independientemente de donde se haya abierto, **se debe usar esa terminal para todo el trabajo de esa sesión**.
   * Solo hice scripts para **PowerShell** y **bash para Windows (Git Bash)**. En caso de que aparezca otra shell (cmd, bash de WSL), cambiar el perfil de la terminal a PowerShell o Git Bash (si es la terminal de VSCode), o abrir una nueva de PowerShell o Git Bash

### Si es PowerShell:
(Estás usando PowerShell si):
* Aparece `PS` al lado del path del directorio actual
* Es la terminal de VSCode y arriba a la derecha de la terminal aparece `powershell`
* Es una terminal en una ventana aparte que tiene [este ícono](https://upload.wikimedia.org/wikipedia/commons/2/2f/PowerShell_5.0_icon.png) y un fondo azul

4. Ejecutar `. .\laburar.ps1` y esperar a que de termine de hacer sus cosas.
    * *Solo si* aparece un error terminado en **`UnauthorizedAccess`**, ejecutar `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` aceptando la advertencia y luego repetir el paso 2 o alternativamente cambiar el perfil de la terminal a Git Bash y seguir los pasos para `bash`.
5. Debería aparecer `✅ Listo.`, y luego `(.venv)` en verde a la izquierda de `PS`. **Seguir desde [acá](#luego)**



### Si es Git Bash:
(Estás usando Git Bash si):
* Es la terminal de VSCode y arriba a la derecha de la terminal aparece `bash`
* Es una terminal en una ventana aparte que tiene [este ícono](https://gitforwindows.org/img/gwindows_logo.png)
* Se ve como el bash de Linux en general

4. Ejecutar `source ./laburar.sh` y esperar a que termine de hacer sus cosas.
5. Debería aparecer `✅ Listo.`, y luego `(.venv)` abajo del resultado de cada comando que se ejecute. **Seguir desde [acá](#luego)**


### Luego:
6. Poner el `.env` en el root del directorio del proyecto.
7. Probar `fastapi dev app/main.py`
8. (opcional pero altamente recomendado) Al abrir un archivo de Python, VSCode te va a preguntar si querés instalar las extensiones recomendadas para el lenguaje. Por tu salud mental, decile que **sí**, lo va hacer en el fondo sin interrumpirte. 

### Si algo no funciona:
* Verificar que se esté usando el entorno virtual ejecutando `which python` (bash) o `Get-Command python` (PowerShell). Si el path que aparece a `python.exe` **NO ESTÁ EN EL DIRECTORIO `statill-backend/.venv`**, o el entorno virtual no se creó y activó correctamente o no se estando la misma terminal que se usó para ejecutar el script. Repetir todo desde el paso 2.
