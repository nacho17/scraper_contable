@echo off
setlocal

cd /d "%~dp0\..\.."

pyinstaller --onefile --clean --name Grupo2000 main.py

if exist config.json (
    copy /Y config.json dist\ >nul
    echo config.json copiado en dist\
) else if exist config_example.json (
    copy /Y config_example.json dist\ >nul
    echo AVISO: no se encontro config.json. Se copio config_example.json en dist\
) else (
    echo AVISO: no se encontro config.json ni config_example.json en la raiz del proyecto.
)

echo.
echo Build finalizado. Ejecutable generado en dist\Grupo2000.exe
pause