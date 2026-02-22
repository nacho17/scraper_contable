# README - Grupo2000 - Automatización Contable

## Descripción

Grupo2000 es un script de automatización para procesamiento y consolidación de datos contables.

El proyecto está diseñado para ejecutarse desde consola (sin interfaz gráfica) y puede compilarse como ejecutable independiente para Windows y macOS.

## Características

- Script 100% CLI (sin UI)
- Logging estructurado (archivo + consola)
- Compatible con Windows y macOS
- Compilable con PyInstaller (modo onefile)
- Preparado para ejecución manual o programada (cron en macOS)

## Requisitos de desarrollo

- Python 3.10 o superior
- pip
- Entorno virtual recomendado

Las dependencias están definidas en `requirements.txt`.

## Entorno de desarrollo

En Windows:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

En macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Testing

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar `pytest` manualmente:

```bash
pytest -q
```

Ejecutar tests con Makefile:

```bash
make test
```

Qué se testea:

- Lógica interna de procesamiento de datos (fechas, ordenamiento y transformaciones de `DataFrame`).
- Validaciones de rangos y condiciones inválidas sin romper flujo.
- Lectura/parsing de archivo y utilidades de manejo de archivos temporales.
- Inserción en Excel y detección de última fila de datos.

No se ejecutan tests E2E con Selenium ni pruebas dependientes de internet.

## Comandos de desarrollo (Makefile)

```bash
make install    # crea venv (si no existe) e instala dependencias
make test       # corre pytest
make lint       # validación sintáctica básica con py_compile
make build-win  # ejecuta build/windows/build_windows.bat
make build-mac  # ejecuta build/mac/build_mac.sh
```

## Logging

El sistema utiliza logging estructurado.

- Nivel configurable mediante variable de entorno `LOG_LEVEL`.
- Salida a consola.
- Salida a archivo dentro de carpeta `logs`.

Formato de log:

```text
%(asctime)s - %(levelname)s - %(message)s
```

Los logs se generan en el mismo directorio donde se encuentra el ejecutable.

## Build para Windows

Desde la raíz del proyecto:

Instalar PyInstaller:

```powershell
pip install pyinstaller
```

Ejecutar script de build:

```powershell
build\windows\build_windows.bat
```

Se genera:

```text
dist\Grupo2000.exe
```

Características del build:

- onefile
- clean
- Sin modo windowed
- Ejecutable de consola
- No requiere instalación

## Build para macOS

En la Mac del usuario:

Instalar Python si no está instalado:

```bash
brew install python
```

Instalar dependencias:

```bash
pip3 install -r requirements.txt
pip3 install pyinstaller
```

Dar permisos al script:

```bash
chmod +x build/mac/build_mac.sh
```

Ejecutar build:

```bash
./build/mac/build_mac.sh
```

Se genera:

```text
dist/Grupo2000
```

Importante:
El build debe realizarse en macOS para generar binario compatible con macOS.

## Ejecución manual

En Windows:

```powershell
dist\Grupo2000.exe
```

En macOS:

```bash
./dist/Grupo2000
```

## Ejecución automática en macOS (cron)

Para ejecutar diariamente mientras la Mac esté encendida:

Abrir terminal:

```bash
crontab -e
```

Agregar una línea como ejemplo (8:00 AM):

```cron
0 8 * * * /ruta/completa/dist/Grupo2000 >> /ruta/completa/cron.log 2>&1
```

Si la máquina está apagada en el horario programado, la ejecución se omite.
El usuario puede ejecutar el programa manualmente luego y el sistema procesará lo pendiente según su lógica interna.

## Estructura del proyecto

```text
main.py
utils/
  logger.py
  reader.py
  dates.py
  converter.py
web/
  downloader.py
excel/
  updater.py
tests/
  test_reader.py
  test_utils_dates.py
  test_data_processing.py
build/
  windows/
    build_windows.bat
  mac/
    build_mac.sh
logs/
Makefile
```

## Buenas prácticas del repositorio

- No se versionan binarios (`dist/`)
- No se versionan artefactos de PyInstaller
- No se versionan entornos virtuales
- El repositorio contiene solo código fuente y scripts de build

## Distribución

Opciones recomendadas:

- Compilar en cada sistema operativo desde el código fuente.
- Entregar el ejecutable generado.
- No es necesario instalador. El ejecutable es portable.

## Notas técnicas

- Proyecto CLI, sin interfaz gráfica.
- No utiliza modo windowed.
- Puede requerir autorización inicial en macOS si Gatekeeper lo solicita.
- No requiere firma para ejecución desde terminal.

## Estado del proyecto

Proyecto preparado para fase de compilación y pruebas en Windows y macOS.
