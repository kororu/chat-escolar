@echo off
setlocal
chcp 65001 >nul
title Abrir Chat Escolar

cd /d "%~dp0.."

echo Abriendo Chat Escolar en el navegador:
echo http://localhost:5173/
start "" "http://localhost:5173/"
if errorlevel 1 (
    echo.
    echo Error: No se pudo abrir el navegador.
    echo Abre manualmente http://localhost:5173/
    pause
    exit /b 1
)

echo.
echo Si la pagina aun no carga, espera unos segundos y actualiza el navegador.
pause
exit /b 0
