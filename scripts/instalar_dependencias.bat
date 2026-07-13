@echo off
rem Compatibilidad con el nombre anterior.
call "%~dp001_instalar_dependencias.bat"
exit /b %ERRORLEVEL%
