@echo off
setlocal
chcp 65001 >nul
title Backend de Chat Escolar

cd /d "%~dp0.."

echo ==================================================
echo   Backend de Chat Escolar
echo ==================================================
echo.

if not exist "backend\main.py" (
    echo Error: No se encontro backend\main.py
    goto :error
)
if not exist "backend\.venv\Scripts\activate.bat" (
    echo Error: No se encontro backend\.venv
    echo Ejecuta primero scripts\01_instalar_dependencias.bat
    goto :error
)

pushd "backend"
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    popd
    echo Error: No se pudo activar backend\.venv
    goto :error
)

echo Backend de Chat Escolar iniciado en:
echo http://127.0.0.1:8000
echo Para detenerlo, presiona Ctrl+C.
echo.
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
set "UVICORN_RESULT=%ERRORLEVEL%"
popd

if not "%UVICORN_RESULT%"=="0" (
    echo.
    echo Error: Uvicorn no pudo iniciar o termino con un error.
    echo Comprueba que el puerto 8000 este libre y que las dependencias esten instaladas.
    goto :error
)

echo.
echo El backend se detuvo.
pause
exit /b 0

:error
echo.
pause
exit /b 1
