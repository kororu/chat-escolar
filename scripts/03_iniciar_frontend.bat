@echo off
setlocal
chcp 65001 >nul
title Frontend de Chat Escolar

cd /d "%~dp0.."

echo ==================================================
echo   Frontend de Chat Escolar
echo ==================================================
echo.

if not exist "frontend\package.json" (
    echo Error: No se encontro frontend\package.json
    goto :error
)
if not exist "frontend\node_modules\" (
    echo Error: No se encontro frontend\node_modules
    echo Ejecuta primero scripts\01_instalar_dependencias.bat
    goto :error
)
where npm >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js y npm no estan instalados o no estan disponibles desde PATH.
    goto :error
)

pushd "frontend"
echo Frontend de Chat Escolar iniciado en:
echo http://localhost:5173/
echo Para detenerlo, presiona Ctrl+C.
echo.
call npm run dev -- --host localhost --port 5173 --strictPort
set "VITE_RESULT=%ERRORLEVEL%"
popd

if not "%VITE_RESULT%"=="0" (
    echo.
    echo Error: Vite no pudo iniciar o termino con un error.
    echo Comprueba que el puerto 5173 este libre y que las dependencias esten instaladas.
    goto :error
)

echo.
echo El frontend se detuvo.
pause
exit /b 0

:error
echo.
pause
exit /b 1
