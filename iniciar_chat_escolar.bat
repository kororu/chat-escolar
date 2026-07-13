@echo off
setlocal
chcp 65001 >nul
title Iniciar Chat Escolar

cd /d "%~dp0"

echo ==================================================
echo   Iniciar Chat Escolar
echo ==================================================
echo.

if not exist "scripts\02_iniciar_backend.bat" (
    echo Error: No se encontro scripts\02_iniciar_backend.bat
    goto :error
)
if not exist "scripts\03_iniciar_frontend.bat" (
    echo Error: No se encontro scripts\03_iniciar_frontend.bat
    goto :error
)
if not exist "backend\.venv\Scripts\activate.bat" (
    echo Error: No se encontro backend\.venv
    echo Ejecuta primero scripts\01_instalar_dependencias.bat
    goto :error
)
if not exist "frontend\node_modules\" (
    echo Error: No se encontro frontend\node_modules
    echo Ejecuta primero scripts\01_instalar_dependencias.bat
    goto :error
)

echo Abriendo backend y frontend en ventanas separadas...
start "Chat Escolar Backend" "%ComSpec%" /k call "%~dp0scripts\02_iniciar_backend.bat"
if errorlevel 1 (
    echo Error: No se pudo abrir la ventana del backend.
    goto :error
)
start "Chat Escolar Frontend" "%ComSpec%" /k call "%~dp0scripts\03_iniciar_frontend.bat"
if errorlevel 1 (
    echo Error: No se pudo abrir la ventana del frontend.
    goto :error
)

echo Esperando 5 segundos para iniciar los servicios...
timeout /t 5 /nobreak >nul

echo Abriendo http://localhost:5173/ en el navegador...
start "" "http://localhost:5173/"

echo.
echo Chat Escolar quedara ejecutandose en las dos ventanas nuevas.
echo Si no carga de inmediato, espera unos segundos y actualiza la pagina.
echo Para detenerlo, presiona Ctrl+C en Backend y Frontend o cierra ambas ventanas.
echo.
pause
exit /b 0

:error
echo.
echo No se pudo completar el inicio de Chat Escolar.
pause
exit /b 1
