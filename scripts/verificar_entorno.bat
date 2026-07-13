@echo off
chcp 65001 >nul
title Verificación de entorno - Chat Escolar

cd /d "%~dp0.."

echo ==================================================
echo   Verificación de entorno - Chat Escolar
echo ==================================================
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo [FALTA] Git no encontrado.
) else (
    echo [OK] Git disponible:
    git --version
)
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo [FALTA] Node.js no encontrado.
) else (
    echo [OK] Node.js disponible:
    node --version
)
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo [FALTA] npm no encontrado.
) else (
    echo [OK] npm disponible:
    call npm --version
)
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [FALTA] Python no encontrado.
) else (
    echo [OK] Python disponible:
    python --version
)
echo.

where pip >nul 2>&1
if errorlevel 1 (
    echo [FALTA] pip no encontrado.
) else (
    echo [OK] pip disponible:
    pip --version
)
echo.

where code >nul 2>&1
if errorlevel 1 (
    echo [FALTA] VS Code no encontrado.
) else (
    echo [OK] VS Code disponible:
    call code --version
)

echo.
if exist "backend\main.py" (
    echo [OK] backend\main.py encontrado.
) else (
    echo [ERROR] No se encontro backend\main.py.
)
if exist "frontend\package.json" (
    echo [OK] frontend\package.json encontrado.
) else (
    echo [ERROR] No se encontro frontend\package.json.
)
if exist "backend\.venv\Scripts\activate.bat" (
    echo [OK] Entorno virtual backend\.venv encontrado.
) else (
    echo [AVISO] No existe backend\.venv. Ejecuta scripts\01_instalar_dependencias.bat.
)
echo.
where ollama >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Ollama no detectado. Chat Escolar puede funcionar en modo basico.
) else (
    echo [OK] Ollama disponible:
    ollama --version
)

echo.
echo Presiona una tecla para salir...
pause >nul
