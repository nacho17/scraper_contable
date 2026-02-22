@echo off
setlocal

cd /d "%~dp0\..\.."

pyinstaller --onefile --clean --name Grupo2000 main.py

echo.
echo Build finalizado. Ejecutable generado en dist\Grupo2000.exe
pause
