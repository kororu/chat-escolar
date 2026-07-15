@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

rem Solicita al backend descargar el modelo y cerrar solo el Ollama que el mismo inició.
rem No ejecuta taskkill global sobre ollama.exe, node.exe o python.exe.
powershell -NoProfile -Command "try { Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/ai/shutdown' -TimeoutSec 5 | Out-Null; Write-Host 'Cierre limpio de IA local solicitado.' } catch { Write-Host 'Backend no disponible: no hay IA local que cerrar desde este script.' }"

echo.
echo Cierra las ventanas Backend y Frontend de Chat Escolar con Ctrl+C.
echo El script no finaliza procesos globales de Ollama.
pause
