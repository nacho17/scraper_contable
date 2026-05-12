# README - Grupo2000 - Automatizacion Contable

## Descripcion

Grupo2000 es una automatizacion para descargar datasets desde una plataforma web, procesarlos y consolidarlos en Excels maestros.

El proyecto esta pensado para ejecutarse desde consola y puede compilarse como ejecutable independiente para Windows y macOS.

## Caracteristicas

- Script CLI.
- Logging estructurado a consola y archivo.
- Compatible con Windows y macOS.
- Compilable con PyInstaller.
- Preparado para ejecucion manual o programada.
- En modo `auto`, macOS y Windows ejecutan el navegador en headless.
- Tolera fallos parciales por usuario o dataset sin abortar toda la corrida.
- Si un rango valido no tiene datos para exportar, lo registra y continua.

## Requisitos de desarrollo

- Python 3.10 o superior.
- `pip`.
- Entorno virtual recomendado.

Las dependencias estan definidas en `requirements.txt`.

## Requisito adicional: LibreOffice para archivos `.xls`

Para procesar correctamente archivos `.xls`, es obligatorio tener LibreOffice instalado en el sistema.

El proyecto busca estas rutas tipicas:

- Windows: `C:\Program Files\LibreOffice\program\soffice.exe`
- macOS: `/Applications/LibreOffice.app/Contents/MacOS/soffice`

Si LibreOffice no esta disponible, el programa registrara un error en el log durante la conversion.

Descarga oficial:

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

Ejecutar tests:

```bash
pytest -q
```

O con Makefile:

```bash
make test
```

No se ejecutan tests E2E con Selenium ni pruebas dependientes de internet.

## Comandos de desarrollo

```bash
make install
make test
make lint
make build-win
make build-mac
```

## Logging

El sistema escribe logs en la carpeta `logs/` del directorio de ejecucion.

- Log principal: `logs/last_run.log`
- Log auxiliar de automatizacion: `logs/debug.log`

En los logs tambien quedan registrados:

- datasets sin datos para el rango solicitado
- fallos parciales por dataset
- fallos parciales por usuario

## Build para Windows

Desde la raiz del proyecto:

```powershell
pip install pyinstaller
build\windows\build_windows.bat
```

Se genera:

```text
dist\Grupo2000.exe
```

Luego del build, el script intenta copiar automaticamente `config.json` a `dist\`.

## Build para macOS

El build debe realizarse en macOS para generar binario compatible.

```bash
pip3 install -r requirements.txt
pip3 install pyinstaller
chmod +x build/mac/build_mac.sh
./build/mac/build_mac.sh
```

Se genera:

```text
dist/Grupo2000
```

## Instalacion en macOS

La instalacion en macOS ejecuta el proyecto como script Python dentro de `.venv`.

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

Esto:

- Verifica Python y LibreOffice.
- Crea `.venv` si no existe.
- Instala dependencias.
- Da permisos a `run.command` y `run_auto.command`.
- Crea acceso directo a `run.command`.

## Archivos requeridos junto al ejecutable

Para ejecutar el programa fuera del entorno de desarrollo, deben estar en la misma carpeta:

- `Grupo2000.exe`
- `config.json` (o `config_example.json` como plantilla)
- `run_auto_windows.bat` si se va a programar la ejecucion automatica en Windows

## Ejecucion manual

En Windows:

```powershell
dist\Grupo2000.exe
```

En macOS:

```bash
./run.command
```

O, si se usa el binario compilado:

```bash
./dist/Grupo2000
```

## Ejecucion automatica en macOS

Referencia rapida:

- Si usa instalacion con `.venv`, programe `run_auto.command`.
- Si distribuye binario compilado, puede programar `dist/Grupo2000`.

Ejemplo de `cron`:

```cron
0 8 * * * /bin/bash /Users/usuario/Grupo2000/run_auto.command
```

## Ejecucion automatica en Windows

Referencia rapida:

- Editar `run_auto_windows.bat` y completar `APP_DIR` y `APP_EXE`.
- Programar `run_auto_windows.bat` en el Programador de tareas.
- En modo `auto`, Windows ejecuta el navegador en headless.
- Si la tarea debe correr sin sesion iniciada, la cuenta configurada necesita contrasena.
- Si un dataset falla pero otros pueden procesarse, la corrida continua y el fallo queda en log.
- Si un rango tiene fecha valida pero no hay registros para exportar, la corrida no queda colgada.

## Nota sobre el Excel maestro

El Excel maestro debe estar preparado previamente.
No debe contener formulas matriciales en las columnas donde el sistema inserta datos.

## Manejo de errores de autenticacion

Si el programa muestra:

`ERROR: Problema de autenticacion. Revise usuario/contrasena en config.json.`

Se debe:

- Abrir `config.json`.
- Actualizar usuario y/o contrasena.
- Guardar cambios.
- Ejecutar nuevamente.

## Estructura del proyecto

```text
main.py
utils/
web/
excel/
tests/
build/
docs/
run_auto_windows.bat
```

## Estado del proyecto

Proyecto preparado para distribucion y ejecucion automatizada en Windows, manteniendo soporte operativo para macOS.
