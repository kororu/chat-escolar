@echo off
chcp 65001 >nul
title Iniciar Chat Escolar

echo ==================================================
echo   Iniciar Chat Escolar
echo ==================================================
echo.

cd /d "%~dp0.."

if not exist "scripts\iniciar_backend.bat" (
    echo [ERROR] No se encontró scripts\iniciar_backend.bat
    goto :error
)

if not exist "scripts\iniciar_frontend.bat" (
    echo [ERROR] No se encontró scripts\iniciar_frontend.bat
    goto :error
)

echo Abriendo backend y frontend en ventanas separadas...
start "Backend Chat Escolar" cmd /k call "%~dp0iniciar_backend.bat"
start "Frontend Chat Escolar" cmd /k call "%~dp0iniciar_frontend.bat"

echo Esperando a que los servicios inicien...
timeout /t 5 /nobreak >nul

echo Abriendo Chat Escolar en el navegador...
start "" "http://localhost:5173"

echo.
echo Si la app no carga de inmediato, espera unos segundos y recarga la página.
echo Para detener Chat Escolar, usa Ctrl + C o cierra las ventanas del backend y frontend.
echo Los perfiles y el historial local no serán borrados.
echo.
echo Presiona una tecla para cerrar este asistente...
pause >nul
exit /b 0

:error
echo.
echo Presiona una tecla para salir...
pause >nul
exit /b 1

