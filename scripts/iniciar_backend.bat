@echo off
chcp 65001 >nul
title Backend Chat Escolar

echo ==================================================
echo   Backend Chat Escolar
echo ==================================================
echo.

cd /d "%~dp0.."

if not exist "backend\" (
    echo [ERROR] No se encontró la carpeta backend.
    goto :error
)

cd /d "backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No se encontró el entorno virtual del backend.
    echo Primero ejecuta scripts\instalar_dependencias.bat
    goto :error
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual.
    goto :error
)

echo Backend disponible en http://127.0.0.1:8000
echo Para detenerlo, presiona Ctrl + C.
echo.
uvicorn main:app --reload

echo.
echo El backend se detuvo.
echo Presiona una tecla para cerrar esta ventana...
pause >nul
exit /b 0

:error
echo.
echo Presiona una tecla para salir...
pause >nul
exit /b 1

