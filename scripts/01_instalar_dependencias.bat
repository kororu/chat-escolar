@echo off
setlocal
chcp 65001 >nul
title Instalacion de dependencias - Chat Escolar

cd /d "%~dp0.."

echo ==================================================
echo   Instalacion de dependencias - Chat Escolar
echo ==================================================
echo.

if not exist "backend\" (
    echo Error: No se encontro la carpeta backend.
    goto :error
)
if not exist "backend\main.py" (
    echo Error: No se encontro backend\main.py
    goto :error
)
if not exist "frontend\" (
    echo Error: No se encontro la carpeta frontend.
    goto :error
)
if not exist "frontend\package.json" (
    echo Error: No se encontro frontend\package.json
    goto :error
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
) else (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python no esta instalado o no esta disponible como python o py.
        goto :error
    )
    set "PYTHON_CMD=py"
)

where npm >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js y npm no estan instalados o no estan disponibles desde PATH.
    goto :error
)

echo [1/2] Preparando el backend...
pushd "backend"

if not exist "requirements.txt" (
    echo Aviso: No existe backend\requirements.txt. Se creara con las dependencias minimas.
    > "requirements.txt" echo fastapi
    >> "requirements.txt" echo uvicorn
    if errorlevel 1 (
        popd
        echo Error: No se pudo crear backend\requirements.txt
        goto :error
    )
)

if not exist ".venv\Scripts\activate.bat" (
    echo Creando el entorno virtual backend\.venv...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        popd
        echo Error: No se pudo crear backend\.venv
        goto :error
    )
) else (
    echo OK backend\.venv ya existe
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    popd
    echo Error: No se pudo activar backend\.venv
    goto :error
)

echo Instalando dependencias Python desde backend\requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    popd
    echo Error: pip install fallo.
    goto :error
)
popd

echo.
echo [2/2] Preparando el frontend...
pushd "frontend"
call npm install
if errorlevel 1 (
    popd
    echo Error: npm install fallo.
    goto :error
)
popd

echo.
echo Dependencias instaladas correctamente.
echo Ya puedes ejecutar iniciar_chat_escolar.bat
echo Los perfiles y el historial local no fueron eliminados ni reemplazados.
echo.
pause
exit /b 0

:error
echo.
echo La instalacion se detuvo. Revisa el mensaje anterior y vuelve a intentarlo.
echo Tambien puedes ejecutar scripts\00_verificar_entorno.bat para revisar el equipo.
echo.
pause
exit /b 1
