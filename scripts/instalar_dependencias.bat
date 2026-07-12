@echo off
chcp 65001 >nul
title Instalación de dependencias - Chat Escolar

echo ==================================================
echo   Instalación de dependencias - Chat Escolar
echo ==================================================
echo.

cd /d "%~dp0.."

if not exist "frontend\" goto :frontend_missing
if not exist "backend\" goto :backend_missing

where npm >nul 2>&1
if errorlevel 1 goto :npm_missing

where python >nul 2>&1
if errorlevel 1 goto :python_missing

echo Instalando dependencias del frontend...
pushd "frontend"
call npm install
if errorlevel 1 goto :frontend_error
popd

echo.
echo Preparando dependencias del backend...
pushd "backend"

if not exist ".venv\Scripts\activate.bat" (
    echo Creando entorno virtual de Python...
    python -m venv .venv
    if errorlevel 1 goto :venv_error
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto :activate_error

pip install -r requirements.txt
if errorlevel 1 goto :backend_error

popd
echo.
echo Dependencias instaladas correctamente.
echo La base local backend\chat_escolar.db no fue eliminada ni reemplazada.
echo.
echo Presiona una tecla para salir...
pause >nul
exit /b 0

:frontend_missing
echo [ERROR] No se encontró la carpeta frontend.
goto :error_pause

:backend_missing
echo [ERROR] No se encontró la carpeta backend.
goto :error_pause

:npm_missing
echo [ERROR] npm no está disponible. Instala Node.js y vuelve a intentarlo.
goto :error_pause

:python_missing
echo [ERROR] Python no está disponible. Instala Python y vuelve a intentarlo.
goto :error_pause

:frontend_error
popd
echo [ERROR] No se pudieron instalar las dependencias del frontend.
goto :error_pause

:venv_error
popd
echo [ERROR] No se pudo crear el entorno virtual del backend.
goto :error_pause

:activate_error
popd
echo [ERROR] No se pudo activar el entorno virtual del backend.
goto :error_pause

:backend_error
popd
echo [ERROR] No se pudieron instalar las dependencias del backend.
goto :error_pause

:error_pause
echo.
echo Revisa el mensaje anterior y vuelve a ejecutar este archivo.
echo Presiona una tecla para salir...
pause >nul
exit /b 1

