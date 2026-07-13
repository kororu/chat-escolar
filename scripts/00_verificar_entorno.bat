@echo off
setlocal
chcp 65001 >nul
title Verificacion de entorno - Chat Escolar

cd /d "%~dp0.."
set "HAY_ERRORES=0"

echo ==================================================
echo   Verificacion de entorno - Chat Escolar
echo ==================================================
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo Error: Git no encontrado.
    set "HAY_ERRORES=1"
) else (
    echo OK Git encontrado
    git --version
)
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo Error: Node no encontrado.
    set "HAY_ERRORES=1"
) else (
    echo OK Node encontrado
    node --version
)
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo Error: npm no encontrado.
    set "HAY_ERRORES=1"
) else (
    echo OK npm encontrado
    call npm --version
)
echo.

python --version >nul 2>&1
if not errorlevel 1 (
    echo OK Python encontrado
    python --version
) else (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python no encontrado.
        set "HAY_ERRORES=1"
    ) else (
        echo OK Python encontrado mediante el lanzador py
        py --version
    )
)
echo.

if exist "backend\" (
    echo OK backend encontrado
) else (
    echo Error: No se encontro la carpeta backend.
    set "HAY_ERRORES=1"
)

if exist "frontend\" (
    echo OK frontend encontrado
) else (
    echo Error: No se encontro la carpeta frontend.
    set "HAY_ERRORES=1"
)

if exist "frontend\package.json" (
    echo OK frontend\package.json encontrado
) else (
    echo Error: No se encontro frontend\package.json
    set "HAY_ERRORES=1"
)

if exist "backend\main.py" (
    echo OK backend\main.py encontrado
) else (
    echo Error: No se encontro backend\main.py
    set "HAY_ERRORES=1"
)

if exist "backend\.venv\Scripts\activate.bat" (
    echo OK backend\.venv encontrado
) else (
    echo Aviso: backend\.venv no existe. Ejecuta scripts\01_instalar_dependencias.bat.
)
echo.

where ollama >nul 2>&1
if errorlevel 1 (
    echo Aviso: Ollama no detectado. Chat Escolar puede funcionar en modo basico.
) else (
    echo OK Ollama encontrado
    ollama --version
)

echo.
if "%HAY_ERRORES%"=="1" (
    echo Verificacion terminada con errores. Corrige los mensajes anteriores antes de instalar.
) else (
    echo Verificacion terminada. El entorno obligatorio esta disponible.
)
echo.
pause
exit /b %HAY_ERRORES%
