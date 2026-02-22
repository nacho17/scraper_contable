@echo off
setlocal

cd /d "%~dp0\..\.."

pyinstaller --onefile --clean --name Grupo2000 main.py

if exist config.json (
    copy /Y config.json dist\ >nul
    echo config.json copiado en dist\
) else (
    echo AVISO: no se encontro config.json en la raiz del proyecto. No se pudo copiar a dist\
)

echo.
echo Build finalizado. Ejecutable generado en dist\Grupo2000.exe
pause
