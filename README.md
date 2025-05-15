# statill-backend

## Para documentación ver `/docs`


## ¿CÓMO LABURAR?

1. Clonar el repositorio y abirirlo en VSCode. Cambiar a la branch correspondiente (`dev`) en general

2. Abrir una terminal. Para hacerlo dentro de VSCode, el shortcut predeterminado es `Ctrl+Ñ`. Independientemente de donde se haya abierto, **se debe usar esa terminal para todo el trabajo de esa sesión**.

## Si arriba al costado aparece `bash`:
3. Ejecutar `source ./laburar.sh` y esperar a que termine de hacer sus cosas.
4. ✅ Listo.

## Si arriba al costado aparece `powershell`:

3. Ejecutar `. .\laburar.ps1` (sí, son necesarios ambos puntos, no es un typo) y esperar a que termien de hacer sus cosas.
    * Solo si aparece un error terminado en `UnauthorizedAccess`, ejecutar `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` aceptando la advertencia y luego repetir paso 2 o alternativamente cambiar el perfil de la terminal a Git Bash y seguir los pasos para `bash`.
3. ✅ Listo.


## Si arriba al costado aparece `cmd`, `wsl` o cualquier otra cosa (no debería):
Debés tocar en la flechita al lado del + en, cambiar a la opción **Git Bash**, y luego seguir los pasos para `bash`.

(También podés cambiar a **PowerShell** y seguir sus respectivos pasos, pero es más fácil en Git Bash)
