@echo off
setlocal

REM === CONFIG ===
REM Reemplazar estos valores antes de usar la tarea programada.
set "APP_DIR=C:\Users\Nacho\Documents\PruebaGrupo2000"
set "APP_EXE=Grupo2000.exe"
set "LOG_DIR=%APP_DIR%\logs"
set "LOG_FILE=%LOG_DIR%\last_run.log"
set "DEBUG_FILE=%LOG_DIR%\debug.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ==== RUN %date% %time% ==== >> "%DEBUG_FILE%"

if not exist "%APP_DIR%\%APP_EXE%" (
    echo ERROR: no se encontro el ejecutable en "%APP_DIR%\%APP_EXE%". >> "%DEBUG_FILE%"
    exit /b 1
)

cd /d "%APP_DIR%"

"%APP_DIR%\%APP_EXE%" --mode auto >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"

echo EXIT CODE: %EXIT_CODE% >> "%DEBUG_FILE%"

exit /b %EXIT_CODE%
