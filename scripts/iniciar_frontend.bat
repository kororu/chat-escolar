@echo off
chcp 65001 >nul
title Frontend Chat Escolar

echo ==================================================
echo   Frontend Chat Escolar
echo ==================================================
echo.

cd /d "%~dp0.."

if not exist "frontend\" (
    echo [ERROR] No se encontró la carpeta frontend.
    goto :error
)

cd /d "frontend"

if not exist "node_modules\" (
    echo [ERROR] No se encontró node_modules.
    echo Primero ejecuta scripts\instalar_dependencias.bat
    goto :error
)

echo Frontend disponible en http://localhost:5173
echo Para detenerlo, presiona Ctrl + C.
echo.
call npm run dev

echo.
echo El frontend se detuvo.
echo Presiona una tecla para cerrar esta ventana...
pause >nul
exit /b 0

:error
echo.
echo Presiona una tecla para salir...
pause >nul
exit /b 1

