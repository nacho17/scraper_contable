# README - Grupo2000 - Automatizacion Contable

## Descripcion

Grupo2000 es un script de automatizacion para procesamiento y consolidacion de datos contables.

El proyecto esta disenado para ejecutarse desde consola (sin interfaz grafica) y puede compilarse como ejecutable independiente para Windows y macOS.

## Caracteristicas

- Script 100% CLI (sin UI)
- Logging estructurado (archivo + consola)
- Compatible con Windows y macOS
- Compilable con PyInstaller (modo onefile)
- Preparado para ejecucion manual o programada (cron en macOS)

## Requisitos de desarrollo

- Python 3.10 o superior
- pip
- Entorno virtual recomendado

Las dependencias estan definidas en `requirements.txt`.

## Requisito adicional: LibreOffice para archivos .xls

Para procesar correctamente archivos con extension `.xls`, es obligatorio tener LibreOffice instalado en el sistema.

Esto se debe a que la conversion de `.xls` a `.xlsx` depende de las funciones `obtener_comando_libreoffice` y `convertir_xls_a_xlsx` en `utils/converter.py`, que buscan y ejecutan `libreoffice`/`soffice`.

Rutas tipicas detectadas por el proyecto:

- Windows: `C:\Program Files\LibreOffice\program\soffice.exe`
- macOS: `/Applications/LibreOffice.app`

Si LibreOffice no esta disponible, el programa registrara un error en el log durante la conversion.

Descarga oficial de LibreOffice:

- https://www.libreoffice.org/download/download-libreoffice/

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

Que se testea:

- Logica interna de procesamiento de datos (fechas, ordenamiento y transformaciones de `DataFrame`).
- Validaciones de rangos y condiciones invalidas sin romper flujo.
- Lectura/parsing de archivo y utilidades de manejo de archivos temporales.
- Insercion en Excel y deteccion de ultima fila de datos.

No se ejecutan tests E2E con Selenium ni pruebas dependientes de internet.

## Comandos de desarrollo (Makefile)

```bash
make install    # crea venv (si no existe) e instala dependencias
make test       # corre pytest
make lint       # validacion sintactica basica con py_compile
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

Desde la raiz del proyecto:

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

Luego del build, el script intenta copiar automaticamente `config.json` en `dist\`.
Si `config.json` no existe en la raiz del proyecto, muestra un aviso y el build continua.

Caracteristicas del build:

- onefile
- clean
- Sin modo windowed
- Ejecutable de consola
- No requiere instalacion

## Build para macOS

En la Mac del usuario:

Instalar Python si no esta instalado:

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

## Archivos requeridos junto al ejecutable

Para ejecutar el programa fuera del entorno de desarrollo, deben estar en la misma carpeta:

- `Grupo2000.exe`
- `config.json`

## Nota sobre preparacion del Excel Maestro

El Excel maestro debe estar preparado previamente.
No debe contener formulas matriciales en las columnas donde el sistema inserta datos.
Esta es una condicion inicial del archivo y no es modificada automaticamente por el programa.

## Manejo de errores de autenticacion

Si el programa muestra el siguiente mensaje:

`ERROR: Problema de autenticación. Revise usuario/contraseña en config.json.`

Debe:

- Abrir `config.json`
- Actualizar usuario y/o contraseña
- Guardar cambios
- Ejecutar nuevamente

## Ejecucion manual

En Windows:

```powershell
dist\Grupo2000.exe
```

En macOS:

```bash
./dist/Grupo2000
```

## Ejecucion automatica en macOS (cron)

Para ejecutar diariamente mientras la Mac este encendida:

Abrir terminal:

```bash
crontab -e
```

Agregar una linea como ejemplo (8:00 AM):

```cron
0 8 * * * /ruta/completa/dist/Grupo2000 >> /ruta/completa/cron.log 2>&1
```

Si la maquina esta apagada en el horario programado, la ejecucion se omite.
El usuario puede ejecutar el programa manualmente luego y el sistema procesara lo pendiente segun su logica interna.

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

## Buenas practicas del repositorio

- No se versionan binarios (`dist/`)
- No se versionan artefactos de PyInstaller
- No se versionan entornos virtuales
- El repositorio contiene solo codigo fuente y scripts de build

## Distribucion

Opciones recomendadas:

- Compilar en cada sistema operativo desde el codigo fuente.
- Entregar el ejecutable generado.
- No es necesario instalador. El ejecutable es portable.

## Notas tecnicas

- Proyecto CLI, sin interfaz grafica.
- No utiliza modo windowed.
- Puede requerir autorizacion inicial en macOS si Gatekeeper lo solicita.
- No requiere firma para ejecucion desde terminal.

## Estado del proyecto

Proyecto preparado para fase de compilacion y pruebas en Windows y macOS.
